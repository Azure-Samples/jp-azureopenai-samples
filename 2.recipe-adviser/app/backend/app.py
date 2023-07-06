import os
import sys
import time
import json
import jwt
import openai
from flask import Flask, request, jsonify, render_template, send_from_directory
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from dotenv import load_dotenv

# Food Menu
from food_menu.food_receipe import get_food_receipe
from food_menu.food_advisory import get_food_advisory
from food_menu.food_image import get_food_image

# Davinci, ChatGPT
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_GPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")

# DALL-E
AZURE_OPENAI_DALLE_API_VERSION = os.environ.get("AZURE_OPENAI_DALLE_API_VERSION")

# load .env file if exists
load_dotenv()

# Use the current user identity to authenticate with Azure OpenAI, Cognitive Search and Blob Storage (no secrets needed, 
# just use 'az login' locally, and managed identity when deployed on Azure). If you need to use keys, use separate AzureKeyCredential instances with the 
# keys for each service
# If you encounter a blocking error during a DefaultAzureCredntial resolution, you can exclude the problematic credential by using a parameter (ex. exclude_shared_token_cache_credential=True)
# azure_credential = DefaultAzureCredential()

# Used by the OpenAI SDK
openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
openai.api_version = AZURE_OPENAI_API_VERSION

# Comment these two lines out if using keys, set your API key in the AZURE_OPENAI_API_KEY environment variable instead
openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY

# openai.api_type = "azure_ad"
# azure_credential = DefaultAzureCredential()
# openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
# openai.api_key = openai_token.token

app = Flask(__name__)

def get_user_name(req: request):
    user_name = ""

    try:
        token = req.headers["X-MS-TOKEN-AAD-ID-TOKEN"]
        claim = jwt.decode(jwt=token, algorithms=["HS256"], options={"verify_signature": False})
        user_name = claim["preferred_username"]
        user_name = user_name.split("@")[0]
    except Exception as e:
        user_name = ""

    return user_name

@app.route("/")
def index():
    user_name = get_user_name(request)
    return render_template("food_menu.html", user_name=user_name)

@app.route("/food_receipe", methods=["POST"])
def food_receipe():
    try:
        print(openai.api_base, flush=True)
        # ensure_openai_token()
        family_profile = request.json["family_profile"]
        ingredients_have = request.json["ingredients_have"]
        user_menu_request = request.json["user_menu_request"]

        response = get_food_receipe(AZURE_OPENAI_GPT_DEPLOYMENT, family_profile, ingredients_have, user_menu_request)
        response_text = response.choices[0].text
        response_text = response_text[response_text.find('{'):]

        return jsonify(json.loads(response_text))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/food_advisory", methods=["POST"])
def food_advisory():
    try:
        family_profile = request.json["family_profile"]
        missing_nutrient = request.json["missing_nutrient"]

        response = get_food_advisory(AZURE_OPENAI_GPT_DEPLOYMENT, family_profile, missing_nutrient)
        response_text = response.choices[0].text
        response_text = response_text[response_text.find('{'):]

        return jsonify(json.loads(response_text))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/food_image", methods=["POST"])
def food_image():
    try:
        food_name = request.json["food_name"]

        image_url = get_food_image(AZURE_OPENAI_SERVICE, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DALLE_API_VERSION, AZURE_OPENAI_GPT_DEPLOYMENT, food_name)

        return jsonify(image_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/<path:path>")
def static_file(path):
    return app.send_static_file(path)

# def get_cognitive_service_api_key():
#     credential = DefaultAzureCredential()
#     secret_client = SecretClient(vault_url="https://kv-aoai-recipe-adviser.vault.azure.net/", credential=credential)
#     secret = secret_client.get_secret("aoai-secret")
#     return secret.value

# def ensure_openai_token():
#     global openai_token
#     # if ENV == "local":
#     #     return
#     if openai_token or openai_token.expires_on < int(time.time()) - 60:
#         openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
#     openai.api_key = openai_token.token
#     print(openai.api_key)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico',mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
