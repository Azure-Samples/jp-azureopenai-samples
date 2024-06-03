import os
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from core.modelhelper import get_gpt_model, get_gpt_models

AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
API_MANAGEMENT_ENDPOINT = os.environ.get("API_MANAGEMENT_ENDPOINT")
ENTRA_CLIENT_ID = os.environ.get("ENTRA_CLIENT_ID")
USE_API_MANAGEMENT = True if os.environ.get("USE_API_MANAGEMENT").lower() == "true" else False

def get_openai_clients(api_key: str, azure_credential: DefaultAzureCredential) -> dict:
    openai_clients = {}
    gpt_models = get_gpt_models()
    for model in list(gpt_models.keys()):
        model_deployment = get_gpt_model(model).get("deployment")
        api_management_url = API_MANAGEMENT_ENDPOINT + f"/deployments/{model_deployment}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
        azure_endpoint = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com" if not USE_API_MANAGEMENT else api_management_url
        openai_client = AzureOpenAI(
            azure_endpoint = azure_endpoint,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key = api_key
        )
        if USE_API_MANAGEMENT:
            openai_client = set_apim_token(azure_credential, openai_client)
        openai_clients[model] = openai_client
    return openai_clients

def set_apim_token(azure_credential: DefaultAzureCredential, openai_client: AzureOpenAI) -> AzureOpenAI:
    apim_token = azure_credential.get_token(f"{ENTRA_CLIENT_ID}/.default")
    openai_client._azure_ad_token = apim_token.token
    return openai_client
