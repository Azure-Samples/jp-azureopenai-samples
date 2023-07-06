# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import os
import time
import json
import jwt
import openai
from flask import Flask, request, jsonify, render_template
from azure.identity import DefaultAzureCredential
from redis import StrictRedis
import inspect
import traceback

# Company
from company_research.company import CompanyResearch

# Davinci, ChatGPT
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_COMPLETION_DEPLOYMENT = os.environ.get("AZURE_OPENAI_COMPLETION_DEPLOYMENT")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

# Redis
# TODO: This part used to be "REDIS_NAME = os.environ["REDIS_NAME"]" check why
REDIS_NAME = os.environ.get("REDIS_NAME")
REDIS_KEY  = os.environ.get("REDIS_KEY")

REDIS_INDEX_NAME = os.environ.get("REDIS_INDEX_NAME")
REDIS_CATEGORY_COMMON = os.environ.get("REDIS_CATEGORY_COMMON")
REDIS_CATEGORY_TOPICS = os.environ.get("REDIS_CATEGORY_TOPICS")

redis_client = StrictRedis(host=REDIS_NAME, port=10000, password=REDIS_KEY, ssl=True, ssl_cert_reqs=None, decode_responses=True)

# Use the current user identity to authenticate with Azure OpenAI, Cognitive Search and Blob Storage (no secrets needed, 
# just use 'az login' locally, and managed identity when deployed on Azure). If you need to use keys, use separate AzureKeyCredential instances with the 
# keys for each service
# If you encounter a blocking error during a DefaultAzureCredntial resolution, you can exclude the problematic credential by using a parameter (ex. exclude_shared_token_cache_credential=True)
azure_credential = DefaultAzureCredential()

# Used by the OpenAI SDK
openai.api_type = "azure"
openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
openai.api_version = AZURE_OPENAI_API_VERSION

# Comment these two lines out if using keys, set your API key in the OPENAI_API_KEY environment variable instead
openai.api_type = "azure_ad"
openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
openai.api_key = openai_token.token

# Redis Index Name
def get_redis_index_name(category):
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    return str(category) + "_" + REDIS_INDEX_NAME

company_research = CompanyResearch(
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT, 
    AZURE_OPENAI_CHAT_DEPLOYMENT, 
    AZURE_OPENAI_COMPLETION_DEPLOYMENT, 
    redis_client, 
    get_redis_index_name(REDIS_CATEGORY_COMMON), 
    get_redis_index_name(REDIS_CATEGORY_TOPICS))

app = Flask(__name__)

def get_user_name(req: request):
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    user_name = ""

    try:
        token = req.headers["X-MS-TOKEN-AAD-ID-TOKEN"]
        claim = jwt.decode(jwt=token, options={"verify_signature": False})
        user_name = claim["preferred_username"]
        user_name = user_name.split("@")[0]
    except Exception as e:
        print(f"An error occurred in {inspect.currentframe().f_code.co_name}: {e}")
        traceback.print_exc()
        user_name = ""

    return user_name

# Web Page
@app.route("/")
@app.route("/company_chat")
def index():
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    user_name = get_user_name(request)
    return render_template("company_chat.html", user_name=user_name)

# Added this because because otherise it was causing an error. TODO: check if needed later
@app.route('/favicon.ico')
def favicon():
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    return {}, 404

@app.route("/<page>")
def company_info(page):
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    user_name = get_user_name(request)
    return render_template("{page}.html".format(page=page), user_name=user_name)

# Web API
@app.route("/search_company", methods=["POST"])
def search_company():
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    try:
        company_name = request.json["company_name"]
        df = company_research.search_embedded_company_common(company_name)

        response_items = []
        for _, row in df.iterrows():
            response_items.append(json.loads(row.data))

        print(jsonify(response_items))
        return jsonify(response_items)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route("/company_chat", methods=["POST"])
def company_chat():
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    try:
        ensure_openai_token()
        locale = request.json["locale"]
        company_name = request.json["company_name"]
        company_info = request.json["company_info"]
        messages = request.json["messages"]
        n = request.json["n"]

        response = company_research.get_company_chat(locale, company_name, company_info, messages, n)

        return jsonify(response)
    except Exception as e:
        print(f"An error occurred in {inspect.currentframe().f_code.co_name}: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/company_completion", methods=["POST"])
def company_completion():
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    try:
        ensure_openai_token()
        locale = request.json["locale"]
        company_name = request.json["company_name"]
        company_info = request.json["company_info"]
        question = request.json["question"]
        n = request.json["n"]

        response = company_research.get_company_completion(locale, company_name, company_info, question, n)

        return response.choices[0].text.replace("\n", "")
    except Exception as e:
        print(f"An error occurred in {inspect.currentframe().f_code.co_name}: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/analysis_feedback", methods=["POST"])
def analysis_feedback():
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    try:
        ensure_openai_token()
        locale = request.json["locale"]
        company_name = request.json["company_name"]
        company_info = request.json["company_info"]
        question = request.json["question"]
        n = request.json["n"]
        source = request.json["source"]
        feedback = request.json["feedback"]

        response = company_research.get_analysis_feedback(locale, company_name, company_info, question, source, feedback, n)

        return response.choices[0].text
    except Exception as e:
        print(f"An error occurred in {inspect.currentframe().f_code.co_name}: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/<path:path>")
def static_file(path):
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    return app.send_static_file(path)

def ensure_openai_token():
    print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
    global openai_token
    if openai_token or openai_token.expires_on < int(time.time()) - 60:
        openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
        openai.api_key = openai_token.token
    
if __name__ == "__main__":
    app.run()
