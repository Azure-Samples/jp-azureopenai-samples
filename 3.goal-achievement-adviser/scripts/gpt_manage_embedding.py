import json
import uuid
import numpy as np
import pandas as pd
import os
from os.path import join, dirname
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

# from redis import Redis
from redis import StrictRedis
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import VectorField, TextField

import openai
import tiktoken

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Azure Open AI
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_VERSION = os.environ.get("AZURE_OPENAI_VERSION")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")

openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
openai.api_version = AZURE_OPENAI_VERSION

azure_credential = DefaultAzureCredential()

if AZURE_OPENAI_KEY is None:
    openai.api_type = "azure_ad"
    openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
    openai.api_key = openai_token.token
else:
    openai.api_type = "azure"
    openai.api_key = os.environ.get("AZURE_OPENAI_KEY")

# encoding for tokenization
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

# GPT Embedding tonen limit
# https://learn.microsoft.com/azure/cognitive-services/openai/concepts/models
#max_token = 2046 # V1
max_token = 8191 # V2

# Redis
redis_name = os.environ.get("REDIS_NAME")
redis_key  = os.environ.get("REDIS_KEY")
redis_index_name = os.environ.get("REDIS_INDEX_CATEGORY") + "_" + os.environ.get("REDIS_INDEX_NAME")
redis_conn = StrictRedis(host=redis_name, port=10000, password=redis_key, ssl=True, ssl_cert_reqs=None, decode_responses=True)
category = os.environ.get("REDIS_INDEX_CATEGORY")

# Clear Redis Cache
def clear_cache():
    print("Redis: clear cache")
    print()

    keys = redis_conn.keys(category + ':*')
    if len(keys) > 0:
        print("Redis: remove", len(keys), "items.")

        redis_conn.delete(*keys)
    else:
        print("Redis: no items.")

# Register Redis Index
def register_cache_index(category):
    text = TextField(name="text")
    embeddings = VectorField("embeddings",
                "HNSW", {
                    "TYPE": "FLOAT32",
                    "DIM": 1536,
                    "DISTANCE_METRIC": "COSINE",
                    "INITIAL_CAP": 3155
                })

    print("Redis: drop index", redis_index_name)
    print()
    try:
        redis_conn.ft(redis_index_name).dropindex() 
    except:
        print(f"Redis: index {redis_index_name} does not exist.")

    print("Redis: create index", redis_index_name)
    print()
    redis_conn.ft(redis_index_name).create_index(
        fields = [text, embeddings],
        definition = IndexDefinition(prefix=[category], index_type=IndexType.HASH))

# Get GPT Embedding from text
def get_gpt_embedding(text):
    text = text.replace("\n", " ")
    response = openai.Embedding.create(engine=AZURE_OPENAI_EMBEDDING_DEPLOYMENT, input=text)
    return response["data"][0]["embedding"]

# Calculate GPT Embedding token count
def get_gpt_token_count(text):
    return len(encoding.encode(text))

# Add Redis Cache Item
def register_embedding_cache(category, data):

    text = data["name"] + " : " + data["text"]

    tokens = get_gpt_token_count(text)

    if (tokens < max_token):
        print("Redis: register ", text)

        embedding = get_gpt_embedding(text)

        id = f"{category}:{uuid.uuid4().hex}"

        redis_conn.hset(
            id,
            mapping={
                "text": text,
                "embeddings": np.array(embedding).astype(dtype=np.float32).tobytes()
            }
        )
        item = { "id": id, "text": text }
    else:
        item = { "id": "Error", "text": "The text is too long: " + tokens }

    return item

def register_topics(filename):
    datafile_path = join(dirname(__file__), filename)

    with open(datafile_path, 'r', encoding='utf-8') as f:
        for text in f:
            data = json.loads(text)
            register_embedding_cache(category, data)

# Query Redis Cache
def query_all_cache():
    base_query = '*'
    query = Query(base_query)\
        .return_fields("text")\
        .dialect(2)

    redis_ret = redis_conn.ft(redis_index_name).search(query)

    df_ret = pd.DataFrame(list(map(lambda x: {'id' : x.id, 'text': x.text}, redis_ret.docs)))

    return df_ret

# Retrieve all Redis Cache
def query_cache(text, n=6):
    base_query = f'*=>[KNN {n} @embeddings $vec_param AS vector_score]'
    query = Query(base_query)\
        .sort_by("vector_score")\
        .paging(0, n)\
        .return_fields("text", "vector_score")\
        .dialect(2)

    embedding = get_gpt_embedding(text)
    query_params = {"vec_param": np.array(embedding).astype(np.float32).tobytes()}
    redis_ret = redis_conn.ft(redis_index_name).search(query, query_params=query_params)
    df_ret = pd.DataFrame(list(map(lambda x: {'id' : x.id, 'vector_score': x.vector_score, 'text': x.text}, redis_ret.docs)))

    return df_ret

clear_cache()
register_cache_index(category)

register_topics("topics.jsonl")
        
df = query_all_cache()
print(df)
print()

df = query_cache("コントソの強み弱み")
print(df)
print()
