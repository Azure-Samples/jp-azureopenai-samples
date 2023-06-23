import datetime
import json
import os
import re
import urllib.parse
from os.path import dirname, join

import openai
import tiktoken
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from redis import StrictRedis

from task_assistant.conversation_summary import get_comversation_summary_prompt
from task_assistant.goal_achievement_adviser import get_goal_achievement_adviser_prompt
from task_assistant.search_info import get_internal_knowledge

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Use the current user identity to authenticate with Azure OpenAI, Cognitive Search and Blob Storage (no secrets needed,
# just use 'az login' locally, and managed identity when deployed on Azure). If you need to use keys, use separate AzureKeyCredential instances with the
# keys for each service
# If you encounter a blocking error during a DefaultAzureCredntial resolution, you can exclude the problematic credential by using a parameter (ex. exclude_shared_token_cache_credential=True)
azure_credential = DefaultAzureCredential()

# Blob Storage
AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT")
AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER")
blob_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=azure_credential,
)
blob_container = blob_client.get_container_client(AZURE_STORAGE_CONTAINER)

# Redis
REDIS_NAME = os.environ["REDIS_NAME"]
REDIS_KEY = os.environ["REDIS_KEY"]
REDIS_INDEX_NAME = os.environ.get("REDIS_INDEX_NAME")
REDIS_INDEX_CATEGORY = os.environ.get("REDIS_INDEX_CATEGORY")
redis_client = StrictRedis(
    host=REDIS_NAME,
    port=10000,
    password=REDIS_KEY,
    ssl=True,
    ssl_cert_reqs=None,
    decode_responses=True,
)
redis_index_name = REDIS_INDEX_CATEGORY + "_" + REDIS_INDEX_NAME

# Azure OpenAI
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_CHAT_MODEL = os.environ.get("AZURE_OPENAI_CHAT_MODEL")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")

openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
openai.api_version = AZURE_OPENAI_API_VERSION
if AZURE_OPENAI_KEY is None:
    openai.api_type = "azure_ad"
    openai_token = azure_credential.get_token(
        "https://cognitiveservices.azure.com/.default"
    )
    openai.api_key = openai_token.token
else:
    openai.api_type = "azure"
    openai.api_key = AZURE_OPENAI_KEY

encoding = tiktoken.encoding_for_model("gpt-4")
model_max_tokens = 32768 if AZURE_OPENAI_CHAT_MODEL.find("32k") > -1 else 8192

app = Flask(__name__)


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_file(path):
    return app.send_static_file(path)


@app.route("/chat", methods=["POST"])
def chat():
    try:
        theme = request.json["theme"]
        history = request.json["history"]
        search = request.json["search"]

        messages = history
        # messages = [{"role": k, "content": v} for h in history for k, v in h.items()]

        if not messages:
            if search == 1:  # 0: No search, 1: Search Redis, 2: Search Bing
                theme = (
                    theme
                    + "\n現在の状況は、"
                    + get_internal_knowledge(
                        embedding_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                        redis_client=redis_client,
                        redis_index_name=redis_index_name,
                        question=theme,
                    )
                    + "。\n"
                )
            elif search == 2:
                print("Not Implemeted")

            messages = get_goal_achievement_adviser_prompt(theme, [])
        else:
            for m in messages:
                m["content"] = urllib.parse.unquote(m["content"])
            question = messages[len(messages) - 1]["content"]

            if "HTML" in question and "出力" in question:
                messages = get_comversation_summary_prompt(theme, messages)
            else:
                messages = get_goal_achievement_adviser_prompt(theme, messages)

        max_tokens = model_max_tokens
        input_token = encoding.encode(json.dumps(messages, ensure_ascii=False))
        token_length = len(input_token)
        if max_tokens > token_length + 1:
            max_tokens = max_tokens - (token_length + 1)

        response = openai.ChatCompletion.create(
            engine=AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.5,
            n=1,
        )

        response_text = response.choices[0]["message"]["content"]

        # HTML
        if "<html" in response_text:
            type = "html"
            blob_url = save_text_to_blob_storage(response_text)
            response_text = urllib.parse.quote(blob_url)
        # JSON
        elif re.match(r"^(\{|\[)(.|[\r\n])*?(\}|\])$", response_text):
            type = "json"
            response_text = urllib.parse.quote(
                response_text.replace("\n", "").replace("'", '"')
            )
        else:
            type = "text"
            response_text = urllib.parse.quote(response_text)

        return jsonify({"type": type, "value": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/task/<path>")
def content_file(path):
    blob = blob_container.get_blob_client(path).download_blob()
    mime_type = "text/html; charset=UTF-8"
    return (
        blob.readall(),
        200,
        {
            "Content-Type": mime_type,
        },
    )


def save_text_to_blob_storage(text):
    # ファイル名の作成
    current_datetime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"task_{current_datetime}.html"

    # テキストをBlobストレージにアップロード
    blob_client = blob_container.get_blob_client(filename)
    blob_client.upload_blob(text)

    return f"./{AZURE_STORAGE_CONTAINER}/" + filename


if __name__ == "__main__":
    PORT = os.environ.get("PORT", 5000)
    app.run(host="0.0.0.0", port=int(PORT))
