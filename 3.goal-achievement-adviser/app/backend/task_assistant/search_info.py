import numpy as np
import openai
import pandas as pd

# Redis
from redis import StrictRedis
from redis.commands.search.query import Query


def get_gpt_embedding(embedding_deployment: str, text: str):
    response = openai.Embedding.create(engine=embedding_deployment, input=text)
    return response["data"][0]["embedding"]


def query_cache(
    embedding_deployment: str,
    redis_client: StrictRedis,
    redis_index_name: str,
    text: str,
    n: int,
):
    base_query = f"*=>[KNN {n} @embeddings $vec_param AS vector_score]"
    query = (
        Query(base_query)
        .sort_by("vector_score")
        .paging(0, n)
        .return_fields("text", "vector_score")
        .dialect(2)
    )

    embedding = get_gpt_embedding(embedding_deployment, text)
    query_params = {"vec_param": np.array(embedding).astype(np.float32).tobytes()}
    redis_ret = redis_client.ft(redis_index_name).search(
        query, query_params=query_params
    )
    df = pd.DataFrame(
        [
            {"id": x.id, "text": x.text, "vector_score": x.vector_score}
            for x in redis_ret.docs
        ]
    )

    return df["text"].str.cat(sep=" ")


def get_internal_knowledge(
    embedding_deployment: str,
    redis_client: StrictRedis,
    redis_index_name: str,
    question: str,
):
    return query_cache(
        embedding_deployment=embedding_deployment,
        redis_client=redis_client,
        redis_index_name=redis_index_name,
        text=question,
        n=3,
    )
