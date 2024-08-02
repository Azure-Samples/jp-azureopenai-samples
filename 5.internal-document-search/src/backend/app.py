import os
import time
import mimetypes
import urllib.parse
from flask import Flask, request, jsonify

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from approaches.chatlogging import get_user_name, write_error
from approaches.chatreadretrieveread import ChatReadRetrieveReadApproach
from approaches.chatread import ChatReadApproach
from core.openaiclienthelper import get_openai_clients

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.flask import FlaskInstrumentor


# Replace these with your own values, either in environment variables or directly here
AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER")

AZURE_SEARCH_SERVICE = os.environ.get("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX")

KB_FIELDS_CONTENT = os.environ.get("KB_FIELDS_CONTENT") or "content"
KB_FIELDS_CATEGORY = os.environ.get("KB_FIELDS_CATEGORY") or "category"
KB_FIELDS_SOURCEPAGE = os.environ.get("KB_FIELDS_SOURCEPAGE") or "sourcepage"

AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE")

# Use the current user identity to authenticate with Azure OpenAI, Cognitive Search and Blob Storage (no secrets needed, 
# just use 'az login' locally, and managed identity when deployed on Azure). If you need to use keys, use separate AzureKeyCredential instances with the 
# keys for each service
# If you encounter a blocking error during a DefaultAzureCredntial resolution, you can exclude the problematic credential by using a parameter (ex. exclude_shared_token_cache_credential=True)
azure_credential = DefaultAzureCredential()
openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")

openai_clients = get_openai_clients(openai_token.token, azure_credential)

# Set up clients for Cognitive Search and Storage
search_client = SearchClient(
    endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
    index_name=AZURE_SEARCH_INDEX,
    credential=azure_credential)
blob_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net", 
    credential=azure_credential)
blob_container = blob_client.get_container_client(AZURE_STORAGE_CONTAINER)

chat_approaches = {
    "rrr": ChatReadRetrieveReadApproach(
        search_client, 
        KB_FIELDS_SOURCEPAGE, 
        KB_FIELDS_CONTENT
    ),
    "r": ChatReadApproach()
}

configure_azure_monitor()

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_file(path):
    return app.send_static_file(path)

# Serve content files from blob storage from within the app to keep the example self-contained. 
# *** NOTE *** this assumes that the content files are public, or at least that all users of the app
# can access all the files. This is also slow and memory hungry.
@app.route("/content/<path>")
def content_file(path):
    try:
        path = path.strip()

        blob = blob_client.get_blob_client(container=AZURE_STORAGE_CONTAINER, blob=path)
        properties = blob.get_blob_properties()

        if properties.size < 1024 * 1024: # 1MB
            blob = blob_container.get_blob_client(path).download_blob()

            mime_type = blob.properties["content_settings"]["content_type"]
            if mime_type == "application/octet-stream":
                mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"

            _, ext = os.path.splitext(path)
            ext = ext[1:].lower()
            extensions = ["doc", "docs", "xls", "xlsx", "ppt", "pptx"]
            if ext in extensions:
                mode = "attachment"
            else:
                mode = "inline"
            
            return blob.readall(), 200, {"Content-Type": mime_type, "Content-Disposition": f"{mode}; filename={urllib.parse.quote(path)}"}
        else:
            html = f"<!DOCTYPE html><html><head><title>oversize file</title></head><body><p>Subject file cannot be previewed due to the size limit, {properties.size} bytes. See [Supporting content] tab.</p></body></html>"
            return html, 403, {"Content-Type": "text/html"}

    except Exception as e:
        user_name = get_user_name(request)
        write_error("content", user_name, str(e))
        return jsonify({"error": str(e)}), 500

# Chat
@app.route("/chat", methods=["POST"])
def chat():
    ensure_openai_token()
    approach = request.json["approach"]
    user_name = get_user_name(request)
    overrides = request.json.get("overrides")

    try:
        impl = chat_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(openai_clients, user_name, request.json["history"], overrides)
        return jsonify(r)
    except Exception as e:
        write_error("chat", user_name, str(e))
        return jsonify({"error": str(e)}), 500

# Document Search
@app.route("/docsearch", methods=["POST"])
def docsearch():
    ensure_openai_token()
    approach = request.json["approach"]
    user_name = get_user_name(request)
    overrides = request.json.get("overrides")

    try:
        impl = chat_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(openai_clients, user_name, request.json["history"], overrides)
        return jsonify(r)
    except Exception as e:
        write_error("docsearch", user_name, str(e))
        return jsonify({"error": str(e)}), 500

def ensure_openai_token():
    global openai_token
    if openai_token.expires_on < int(time.time()) - 60:
        openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
        for openai_client in list(openai_clients.keys()):
            openai_client.api_key = openai_token.token

if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0')
