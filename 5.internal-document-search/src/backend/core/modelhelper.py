from __future__ import annotations

import os
import json
import tiktoken

AZURE_OPENAI_GPT_35_TURBO_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_35_TURBO_DEPLOYMENT")
AZURE_OPENAI_GPT_35_TURBO_16K_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_35_TURBO_16K_DEPLOYMENT")
AZURE_OPENAI_GPT_4_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_4_DEPLOYMENT")
AZURE_OPENAI_GPT_4_32K_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_4_32K_DEPLOYMENT")

gpt_models = {
    "gpt-3.5-turbo": {
        "deployment": AZURE_OPENAI_GPT_35_TURBO_DEPLOYMENT,
        "max_tokens": 4096,
        "encoding": tiktoken.encoding_for_model("gpt-3.5-turbo")
    },
    "gpt-3.5-turbo-16k": {
        "deployment": AZURE_OPENAI_GPT_35_TURBO_16K_DEPLOYMENT,
        "max_tokens": 16384,
        "encoding": tiktoken.encoding_for_model("gpt-3.5-turbo")
    },
    "gpt-4": {
        "deployment": AZURE_OPENAI_GPT_4_DEPLOYMENT,
        "max_tokens": 8192,
        "encoding": tiktoken.encoding_for_model("gpt-4")
    },
    "gpt-4-32k": {
        "deployment": AZURE_OPENAI_GPT_4_32K_DEPLOYMENT,
        "max_tokens": 32768,
        "encoding": tiktoken.encoding_for_model("gpt-4-32k")
    }
}

# MODELS_2_TOKEN_LIMITS = {
#     "gpt-35-turbo": 4000,
#     "gpt-3.5-turbo": 4000,
#     "gpt-35-turbo-16k": 16000,
#     "gpt-3.5-turbo-16k": 16000,
#     "gpt-4": 8100,
#     "gpt-4-32k": 32000
# }

# AOAI_2_OAI = {
#     "gpt-35-turbo": "gpt-3.5-turbo",
#     "gpt-35-turbo-16k": "gpt-3.5-turbo-16k"
# }


# def get_token_limit(model_id: str) -> int:
#     if model_id not in MODELS_2_TOKEN_LIMITS:
#         raise ValueError("Expected model gpt-35-turbo and above")
#     return MODELS_2_TOKEN_LIMITS[model_id]


# def num_tokens_from_messages(message: dict[str, str], model: str) -> int:
#     """
#     Calculate the number of tokens required to encode a message.
#     Args:
#         message (dict): The message to encode, represented as a dictionary.
#         model (str): The name of the model to use for encoding.
#     Returns:
#         int: The total number of tokens required to encode the message.
#     Example:
#         message = {'role': 'user', 'content': 'Hello, how are you?'}
#         model = 'gpt-3.5-turbo'
#         num_tokens_from_messages(message, model)
#         output: 11
#     """
#     encoding = tiktoken.encoding_for_model(get_oai_chatmodel_tiktok(model))
#     num_tokens = 2  # For "role" and "content" keys
#     for key, value in message.items():
#         num_tokens += len(encoding.encode(value))
#     return num_tokens


# def get_oai_chatmodel_tiktok(aoaimodel: str) -> str:
#     message = "Expected Azure OpenAI ChatGPT model name"
#     if aoaimodel == "" or aoaimodel is None:
#         raise ValueError(message)
#     if aoaimodel not in AOAI_2_OAI and aoaimodel not in MODELS_2_TOKEN_LIMITS:
#         raise ValueError(message)
#     return AOAI_2_OAI.get(aoaimodel) or aoaimodel

def get_gpt_model(model_name: str) -> dict:
    return gpt_models.get(model_name)

def get_gpt_models() -> dict:
    return gpt_models

def get_max_token_from_messages(messages: dict[str, str], model: str) -> int:
    gpt_model = get_gpt_model(model)
    encoding = gpt_model.get("encoding")
    max_tokens = gpt_model.get("max_tokens")

    # input tokens + output tokens < max tokens of the model
    input_token = encoding.encode(json.dumps(messages, ensure_ascii=False))
    token_length = len(input_token)
    if max_tokens > token_length + 1:
        max_tokens = max_tokens - (token_length + 1)

    return max_tokens