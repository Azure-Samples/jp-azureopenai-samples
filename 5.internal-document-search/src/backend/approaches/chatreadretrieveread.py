import json
import sys
from text import nonewlines
import openai
import urllib.parse
from approaches.approach import Approach
from approaches.chatlogging import write_chatlog, ApproachType
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType

# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion 
# (answer) with that prompt.
class ChatReadRetrieveReadApproach(Approach):
    prompt_prefix_davinci = """<|im_start|>system
{system_prompt}

Sources:
{sources}

<|im_end|>
{chat_history}
"""

    prompt_prefix_gpt_4 = """
{system_prompt}

Sources:
{sources}
"""

    system_prompt = """
Assistant helps the questions. Be brief in your answers.
generate the answer in the same language as the language of the Sources.
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question.
For tabular information return it as an html table. Do not return markdown format.
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brakets to reference the source, e.g. [info1.txt]. Don't combine sources, list each source separately, e.g. [info1.txt][info2.pdf].
"""


    query_prompt_template = """Below is a history of the conversation so far, and a new question asked by the user that needs to be answered by searching in a knowledge base about financial documents.
Generate a search query based on the conversation and the new question. 
Do not include cited source filenames and document names e.g info.txt or doc.pdf in the search query terms.
Do not include any text inside [] or <<>> in the search query terms.
generate the search query in the same language as the language of the question.

Chat History:
{chat_history}

Question:
{question}

Search query:
"""

    def __init__(self, search_client: SearchClient, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field

    def run(self, selected_model_name, gpt_chat_model, gpt_completion_model, user_name: str, history: list[dict], overrides: dict) -> any:
        # STEP 1: Generate an optimized keyword search query based on the chat history and the last question
        chat_deployment = gpt_chat_model.get("deployment")
        max_tokens = gpt_chat_model.get("max_tokens")
        encoding = gpt_chat_model.get("encoding")
        prompt = self.query_prompt_template.format(chat_history=self.get_chat_history_as_text(history, include_last_turn=False), question=history[-1]["user"])
        token_length = len(encoding.encode(prompt))
        if max_tokens > token_length + 1:
            max_tokens = max_tokens - (token_length + 1)
        completion = openai.Completion.create(
            engine=chat_deployment, 
            prompt=prompt, 
            temperature=0.0, # Temperature is set to 0.0 because query keyword should be more stable.
            max_tokens=max_tokens,
            n=1, 
            stop=["\n"])
        q = completion.choices[0].text

        total_tokens = completion.usage.total_tokens

        # STEP 2: Retrieve relevant documents from the search index with the GPT optimized query
        use_semantic_captions = True if overrides.get("semanticCaptions") else False
        top = overrides.get("top")
        exclude_category = overrides.get("excludeCategory") or None
        filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None
        semantic_ranker = overrides.get("semanticRanker")
        if semantic_ranker:
            r = self.search_client.search(q, 
                                          filter=filter,
                                          query_type=QueryType.SEMANTIC,
                                          query_language="en-US", 
                                          query_speller="lexicon", 
                                          semantic_configuration_name="default", 
                                          top=top, 
                                          query_caption="extractive|highlight-false" if use_semantic_captions else None)
        else:
            r = self.search_client.search(q, filter=filter, top=top)
        if use_semantic_captions:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(" . ".join([c.text for c in doc['@search.captions']])) for doc in r]
        else:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field]) for doc in r]
        content = "\n".join(results)

        # STEP 3: Generate a contextual and content specific answer using the search results and chat history
        completion_deployment = gpt_completion_model.get("deployment")
        max_tokens = gpt_completion_model.get("max_tokens")
        encoding = gpt_completion_model.get("encoding")
        temaperature = float(overrides.get("temperature"))

        if (selected_model_name == "text-davinci-003"):   # davinci
            prompt = self.prompt_prefix_davinci.format(system_prompt=self.system_prompt, sources=content, chat_history=self.get_chat_history_as_text(history))

            # input tokens + output tokens < max tokens of the model
            token_length = len(encoding.encode(prompt))
            if max_tokens > token_length + 1:
                max_tokens = max_tokens - (token_length + 1)

            completion = openai.Completion.create(
                engine=completion_deployment, 
                prompt=prompt, 
                temperature=temaperature, 
                max_tokens=max_tokens, 
                n=1, 
                stop=["<|im_end|>", "<|im_start|>"])
            
            response_text = completion.choices[0].text

            total_tokens += completion.usage.total_tokens

            response = {"data_points": results, "answer": response_text, "thoughts": f"Searched for:<br>{q}<br><br>Prompt:<br>" + prompt.replace('\n', '<br>')}
        else:   # gpt-4 / gpt-4-32k
            messages = [{"role": k, "content": v} for i in history for k, v in i.items()]
            prompt = self.prompt_prefix_gpt_4.format(system_prompt=self.system_prompt, sources=content)
            messages.insert(0, {"role": "system", "content": prompt})

            token_length = len(json.dumps(messages, ensure_ascii=False))
            if max_tokens > token_length + 1:
                max_tokens = max_tokens - (token_length + 1)

            response = openai.ChatCompletion.create(
                engine=completion_deployment, 
                messages=messages,
                max_tokens=max_tokens,
                temperature=temaperature, 
                n=1)

            response_text = response.choices[0]["message"]["content"]
            total_tokens += response.usage.total_tokens

            response = {"data_points": results, "answer": response_text, "thoughts": f"Searched for:<br>{q}<br><br>Prompt:<br>" + json.dumps(messages, ensure_ascii=False).replace('\n', '<br>')}

        input_text = history[-1]["user"]

        # logging
        write_chatlog(ApproachType.DocSearch, user_name, total_tokens, input_text, response_text, q)

        return response
    
    def get_chat_history_as_text(self, history, include_last_turn=True, approx_max_tokens=1000) -> str:
        history_text = ""
        for h in reversed(history if include_last_turn else history[:-1]):
            history_text = """<|im_start|>user""" +"\n" + h["user"] + "\n" + """<|im_end|>""" + "\n" + """<|im_start|>assistant""" + "\n" + (h.get("bot") + """<|im_end|>""" if h.get("bot") else "") + "\n" + history_text
            if len(history_text) > approx_max_tokens*4:
                break    
        return history_text