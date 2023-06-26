# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import json
import uuid
import numpy as np
import pandas as pd
import os
import time
from os.path import join, dirname
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from redis import StrictRedis
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import VectorField, NumericField, TextField

import openai
import tiktoken

from gpt_locale import get_company_description

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Azure Open AI
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_VERSION = os.environ.get("AZURE_OPENAI_VERSION")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")


openai.api_type = "azure_ad"
openai.api_base = AZURE_OPENAI_SERVICE
openai.api_version = AZURE_OPENAI_VERSION
azure_credential = DefaultAzureCredential()
openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
openai.api_key = openai_token.token

max_token = 2000

# Redis Search
REDIS_NAME = os.environ.get("REDIS_NAME")
REDIS_KEY  = os.environ.get("REDIS_KEY")

REDIS_INDEX_NAME = os.environ.get("REDIS_INDEX_NAME")
REDIS_CATEGORY_COMMON = os.environ.get("REDIS_CATEGORY_COMMON")
REDIS_CATEGORY_TOPICS = os.environ.get("REDIS_CATEGORY_TOPICS")

redis_conn = StrictRedis(host=REDIS_NAME, port=10000, password=REDIS_KEY, ssl=True, ssl_cert_reqs=None, decode_responses=True)

# encoding for tokenization
encodeing = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Redis Index Name
def get_redis_index_name(category):
    return category + "_" + REDIS_INDEX_NAME

# Clear Redis Cache
def clear_cache(category):
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
    name = TextField(name="name")
    data = TextField(name="data")
    tokens = NumericField(name="tokens")
    embeddings = VectorField("embeddings",
                "HNSW", {
                    "TYPE": "FLOAT32",
                    "DIM": 1536,
                    "DISTANCE_METRIC": "COSINE",
                    "INITIAL_CAP": 3155
                })
    
    index_name = get_redis_index_name(category)

    print("Redis: drop index", index_name)
    print()
    try:
        redis_conn.ft(index_name).dropindex() 
    except:
        print(f"Redis: index {index_name} does not exist.")

    print("Redis: create index", index_name)
    print()
    redis_conn.ft(index_name).create_index(
        fields = [name, data, tokens, embeddings],
        definition = IndexDefinition(prefix=[category], index_type=IndexType.HASH))

# Get GPT Embedding from text
def get_gpt_embedding(text):
    text = text.replace("\n", " ")
    return openai.Embedding.create(engine=AZURE_OPENAI_EMBEDDING_DEPLOYMENT, input=text)["data"][0]["embedding"]

# Calculate GPT Embedding token count
def get_gpt_token_count(text):
    return len(encodeing.encode(text))

# Add Redis Cache Item
def register_embedding_cache(category, data, keyword=None):

    if keyword is not None:
        text_for_embedding = data["name"] + " : " + data["text"] +  " : " + keyword
    else:
        text_for_embedding = data["name"] + " : " + data["text"]

    tokens = get_gpt_token_count(text_for_embedding)

    if (tokens < max_token):
        print("Redis: register ", "name", data["name"], "text", data["text"][:20], "...", "tokens", tokens)

        embedding = get_gpt_embedding(text_for_embedding)

        id = f"{category}:{uuid.uuid4().hex}"

        redis_conn.hset(
            id,
            mapping={
                "name": data["name"],
                "data": json.dumps(data),
                "tokens": tokens,
                "embeddings": np.array(embedding).astype(dtype=np.float32).tobytes()
            }
        )
        item = { "id": id, "name" : data["name"], "data": data }
    else:
        item = { "id": "Error", "data": "The text is too long: " + tokens }

    return item

# Calculate Operating Profit Margin
def get_operating_profit_margin(revenue, operating_profit):
    return round((operating_profit / revenue * 100), 1)

# Add company data to Redis Cache
def register_company(category, data):
    years = []

    # Calculate Operating Profit Margin
    operating_profit_margin = []
    for i, r in enumerate(data["revenue"]):
        keys = list(r.keys())
        for key in keys:
            revenue_value = r[key]
            operating_profit_value = data["operating_profit"][i][key]
            operating_profit_margin.append( { key : get_operating_profit_margin(revenue_value, operating_profit_value) } )
        years.append(keys[0])
    data["operating_profit_margin"] = operating_profit_margin

    revenues = [data["revenue"][i][years[i]] for i in range(0, len(years))]
    operating_profits = [data["operating_profit"][i][years[i]] for i in range(0, len(years))]
    operating_profit_margins = [data["operating_profit_margin"][i][years[i]] for i in range(0, len(years))]
    total_assets = [data["total_assets"][i][years[i]] for i in range(0, len(years))]
    equity_ratios = [data["equity_ratio"][i][years[i]] for i in range(0, len(years))]

    data["text"] = get_company_description(data["locale"], data, years, revenues, operating_profits, operating_profit_margins, total_assets, equity_ratios)

    register_embedding_cache(category, data)

# Add all companies from json data
def register_companies(category, filename):
    with open(filename, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    for company in companies:
        register_company(category, company)
        time.sleep(60)

def register_company_topics(category, filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            print(line)
            data = json.loads(line)

            azure_credential = DefaultAzureCredential()
            openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
            openai.api_key = openai_token.token

            register_embedding_cache(category, data, data["keyword"])
            time.sleep(60)

# Query Redis Cache
def query_all_cache(category):
    base_query = f'*'
    query = Query(base_query)\
        .return_fields("name", "data", "tokens")\
        .dialect(2)
    
    index_name = get_redis_index_name(category)
    redis_ret = redis_conn.ft(index_name).search(query)

    df_ret = pd.DataFrame(list(map(lambda x: {'id' : x.id, 'name' : x.name, 'data': x.data, 'tokens': x.tokens}, redis_ret.docs)))

    return df_ret

# Retrieve all Redis Cache
def query_cache(category, text, n=5):
    base_query = f'*=>[KNN {n} @embeddings $vec_param AS vector_score]'
    query = Query(base_query)\
        .sort_by("vector_score")\
        .paging(0, n)\
        .return_fields("name", "data", "tokens", "vector_score")\
        .dialect(2)

    embedding = get_gpt_embedding(text)
    query_params = {"vec_param": np.array(embedding).astype(np.float32).tobytes()}

    index_name = get_redis_index_name(category)
    redis_ret = redis_conn.ft(index_name).search(query, query_params=query_params)

    df_ret = pd.DataFrame(list(map(lambda x: {'id' : x.id, 'name' : x.name, 'data': x.data, 'tokens': x.tokens, 'vector_score': x.vector_score}, redis_ret.docs)))

    return df_ret

# main
def main():
    # Common
    clear_cache(REDIS_CATEGORY_COMMON)
    register_cache_index(REDIS_CATEGORY_COMMON)
    register_companies(REDIS_CATEGORY_COMMON, "company_common.json")

    df = query_all_cache(REDIS_CATEGORY_COMMON)
    print(df)
    print()

    df = query_cache(REDIS_CATEGORY_COMMON, "コントソ", n=1)
    print(df)
    print()

    # Topics
    clear_cache(REDIS_CATEGORY_TOPICS)
    register_cache_index(REDIS_CATEGORY_TOPICS)

    register_company_topics(REDIS_CATEGORY_TOPICS, "company_topics_ja.jsonl")
    # register_company_topics(REDIS_CATEGORY_TOPICS, "company_topics_en.jsonl")

    df = query_all_cache(REDIS_CATEGORY_TOPICS)
    print(df)
    print()

    df = query_cache(REDIS_CATEGORY_TOPICS, "コントソ 経営者", n=3)
    print(df)
    print()

if __name__ == '__main__':
    main()
