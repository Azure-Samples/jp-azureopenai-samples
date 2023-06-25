# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import openai
import json
import pandas as pd
import numpy as np
import inspect

from redis import StrictRedis
from redis.commands.search.query import Query


class CompanyResearch():

    def __init__(self, embedding_deployment: str, chat_deployment: str, completion_deployment: str, redis_client: StrictRedis, redis_index_name_common: str, redis_index_name_topics: str):
        self.embedding_deployment = embedding_deployment
        self.chat_deployment = chat_deployment
        self.completion_deployment = completion_deployment
        self.redis_client = redis_client
        self.redis_index_name_common = redis_index_name_common
        self.redis_index_name_topics = redis_index_name_topics

    # query company cache to RediSearch
    def search_embedded_company(self, redis_index_name, q, n):
        print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
        # query caches with cosine similarity
        base_query = f'*=>[KNN {n} @embeddings $vec_param AS vector_score]'

        # get fields
        query = Query(base_query)\
            .sort_by("vector_score")\
            .paging(0, n)\
            .return_fields("name", "data", "tokens", "vector_score")\
            .dialect(2)

        # Get the embedding from RediSearch with company name and text
        embedding = self.get_gpt_embedding(q)
        query_params = {"vec_param": np.array(embedding).astype(np.float32).tobytes()}
        redis_ret = self.redis_client.ft(redis_index_name).search(query, query_params=query_params)

        # Convert to Pandas Dataframe
        df_ret = pd.DataFrame(list(map(lambda x: {'id' : x.id, 'name' : x.name, 'data': x.data, 'tokens': x.tokens, 'vector_score': x.vector_score}, redis_ret.docs)))

        return df_ret

    def search_embedded_company_common(self, company_name):
        return self.search_embedded_company(self.redis_index_name_common, company_name, 1)

    def get_gpt_embedding(self, text):
        response = openai.Embedding.create(engine=self.embedding_deployment, input=text)
        return response["data"][0]["embedding"]

    system_prompt_en_us = """
You are an assistant supporting the sales department. Please use the following company information proactively, and if you cannot get an answer, please answer based on the information you know. Please also answer in the same way as previously asked. Do not answer questions other than those related to banking and corporate analysis.
company name: {company_name}
company information: {company_info}, {company_topics}
"""
    system_prompt_ja_jp = """
あなたは営業部門をサポートするアシスタントです。次に与える企業情報を積極的に使い回答が得られない場合はあなたが知っている情報から回答してください。以前聞かれたことも同じように答えてください。
企業名: {company_name}
企業情報: {company_info}, {company_topics}
"""
    def get_chat_system_prompt(self, locale, company_name, company_info, company_topics_text):
        print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
        if locale == "en-us":
            prompt_template = self.system_prompt_en_us
        else:
            prompt_template = self.system_prompt_ja_jp

        system_prompt = prompt_template.format(company_name=company_name, company_info=company_info, company_topics=company_topics_text)

        return { "role": "system", "content" : system_prompt }

    def get_company_chat(self,  locale, company_name, company_info, messages, n):
        print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
        q = company_name + ":" + messages[-1]["content"]
        data_source = []
        company_topics_text = self.get_company_topics_text(company_name, q, n, data_source)
        messages.insert(0, self.get_chat_system_prompt(locale, company_name, company_info, company_topics_text))

        print(f"I'm in function: {inspect.currentframe().f_code.co_name}, before calling ChatCompletion.create()")

        result = openai.ChatCompletion.create(
            engine=self.chat_deployment,
            messages=messages,
            temperature=0.9,
            max_tokens=1000,
            n=1)

        print(f"I'm in function: {inspect.currentframe().f_code.co_name}, after calling ChatCompletion.create()")
        
        content = result.choices[0]["message"]["content"]

        response = {
            "content": content,
            "data_source": data_source
        }

        return response
    
    prompt_template_report_en_us = """
answer the questions based on company information.
company name: {company_name}
question: {question}
company information: {company_info}, {company_topics}
"""
    prompt_template_report_ja_jp = """
企業情報に基づいて質問に回答してください。企業情報に記載された内容だけで回答してください。回答以外の文章は返さないでください。
企業名: {company_name}
質問: {question}
企業情報: {company_info}, {company_topics}
"""
    def get_company_completion(self, locale, company_name, company_info, question, n):
        q = company_name + ":" + question
        company_topics_text = self.get_company_topics_text(company_name, q, n)

        if locale == "en-us":
            prompt_template_report = self.prompt_template_report_en_us
        else:
            prompt_template_report = self.prompt_template_report_ja_jp

        prompt = prompt_template_report.format(company_name=company_name, company_info=company_info, question=question, company_topics=company_topics_text)

        print(f"I'm in function: {inspect.currentframe().f_code.co_name}")

        return openai.Completion.create(
            engine=self.completion_deployment, 
            prompt=prompt, 
            temperature=0.5, 
            max_tokens=1000, 
            n=1)

    prompt_template_feedback_en_us = """
The following sentence is generated from company information. 
source sentence: {source}

Keep the content of the original sentence and regenerate the sentence reflecting the feedback.
feedback: {feedback}
company name: {company_name}
company information: {company_info}, {company_topics}
"""
    prompt_template_feedback_ja_jp = """
次の文章は企業情報から生成されたものです。
文章: {source}

文章の内容は保持してフィードバックを反映した文章を生成し直してください。
フィードバック: {feedback}
企業名: {company_name}
企業情報: {company_info}, {company_topics}
"""
    def get_analysis_feedback(self, locale, company_name, company_info, question, source, feedback, n):
        q = company_name + ":" + question
        company_topics_text = self.get_company_topics_text(company_name, q, n)

        if locale == "en-us":
            prompt_template_feedback = self.prompt_template_feedback_en_us
        else:
            prompt_template_feedback = self.prompt_template_feedback_ja_jp

        prompt = prompt_template_feedback.format(company_name=company_name, company_info=company_info, source=source, feedback=feedback, company_topics=company_topics_text)

        print(f"I'm in function: {inspect.currentframe().f_code.co_name}")

        return openai.Completion.create(
            engine=self.completion_deployment, 
            prompt=prompt, 
            temperature=0.5, 
            max_tokens=1000, 
            n=1)

    def get_company_topics_text(self, company_name, question, n, data_source=None):
        print(f"I'm in function: {inspect.currentframe().f_code.co_name}")
        q = company_name + ":" + question
        print(f"self.redis_index_name_topics={self.redis_index_name_topics}")
        df = self.search_embedded_company(self.redis_index_name_topics, q, n)

        company_topics_text = ""
        for _, row in df.iterrows():
            json_data = json.loads(row.data)
            company_topics_text += json_data["label"] + " : " + json_data["text"] + ","

            if data_source is not None:
                data_source.append({
                    "label": json_data["label"],
                    "source": json_data["source"]
                })
        print(f"company_topics_text={company_topics_text}")
        return company_topics_text

