# TODO:CosmosDB化
import os
import json
import jwt
import logging
import traceback
from flask import request
from opencensus.ext.azure.log_exporter import AzureLogHandler
from enum import Enum
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

# CosmosDB
endpoint = os.environ.get("AZURE_COSMOSDB_ENDPOINT")
key = os.environ.get("AZURE_COSMOSDB_KEY")
database_name = os.environ.get("AZURE_COSMOSDB_DATABASE")
container_name = os.environ.get("AZURE_COSMOSDB_CONTAINER")
# CosmosDB Initialization
credential = DefaultAzureCredential() # for production
# credential = key # for local
database = CosmosClient(endpoint, credential).get_database_client(database_name)
container = database.get_container_client(container_name)

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string=os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")))
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

class ApproachType(Enum):
    Chat = "chat"
    DocSearch = "docsearch"
    Ask = "ask"

def get_user_name(req: request):
    user_name = ""

    try:
        token = req.headers["X-MS-TOKEN-AAD-ID-TOKEN"]
        claim = jwt.decode(jwt=token, options={"verify_signature": False})
        user_name = claim["preferred_username"]
        write_chatlog(ApproachType.Chat, user_name, 0, "claim", json.dumps(claim))
    except Exception:
        user_name = "anonymous"

    return user_name

def write_chatlog(approach: ApproachType, user_name: str, total_tokens: int, input: str, response: str, query: str=""):
    properties = {
        "approach" : approach.value,
        "user" : user_name, 
        "tokens" : total_tokens,
        "input" : input,  
        "response" : response
    }

    if query != "":
        properties["query"] = query
    container.create_item(body=properties, enable_automatic_id_generation=True)
    

def write_error(category: str, user_name: str, error: str):
    properties = {
        "category" : category, # "chat", "docsearch", "content"
        "user" : user_name,
        "error" : error
    }

    log_data = json.dumps(properties).encode('utf-8').decode('unicode-escape')
    traceback.print_exc()
    logger.error(log_data)
