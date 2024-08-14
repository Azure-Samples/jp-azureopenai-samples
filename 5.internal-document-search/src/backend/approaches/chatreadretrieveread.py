from text import nonewlines
from openai import AzureOpenAI

from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from approaches.approach import Approach
from approaches.chatlogging import write_chatlog, ApproachType
from core.messagebuilder import MessageBuilder
from core.modelhelper import get_gpt_model, get_max_token_from_messages

# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion 
# (answer) with that prompt.
class ChatReadRetrieveReadApproach(Approach):
    # Chat roles
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    """
    Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
    top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion
    (answer) with that prompt.
    """
    system_message_chat_conversation = """Assistant helps the customer questions. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question.
For tabular information return it as an html table. Do not return markdown format. If the question is not in English, answer in the language used in the question.
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brackets to reference the source, e.g. [info1.txt]. Don't combine sources, list each source separately, e.g. [info1.txt][info2.pdf].
"""
    query_prompt_template = """Below is a history of the conversation so far, and a new question asked by the user that needs to be answered by searching in a knowledge base.
Generate a search query based on the conversation and the new question.
Do not include cited source filenames and document names e.g info.txt or doc.pdf in the search query terms.
Do not include any text inside [] or <<>> in the search query terms.
Do not include any special characters like '+'.
The language of the search query is generated in the language of the string described in the source question.
If you cannot generate a search query, return just the number 0.

source quesion: {user_question}
"""
    query_prompt_few_shots = [
        {'role' : USER, 'content' : 'What are my health plans?' },
        {'role' : ASSISTANT, 'content' : 'Show available health plans' },
        {'role' : USER, 'content' : 'does my plan cover cardio?' },
        {'role' : ASSISTANT, 'content' : 'Health plan cardio coverage' }
    ]

    def __init__(self, search_client: SearchClient, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
    
    def run(self, openai_clients: AzureOpenAI, user_name: str, history: list[dict], overrides: dict) -> any:
        chat_model = overrides.get("gptModel")
        chat_gpt_model = get_gpt_model(chat_model)
        chat_deployment = chat_gpt_model.get("deployment")

        openai_client = openai_clients.get(chat_model)

        # STEP 1: Generate an optimized keyword search query based on the chat history and the last question
        user_q = 'Generate search query for: ' + history[-1]["user"]
        query_prompt = self.query_prompt_template.format(user_question=history[-1]["user"])
        message_builder = MessageBuilder(query_prompt)
        messages = message_builder.get_messages_from_history(
            history,
            user_q,
            self.query_prompt_few_shots
            )

        max_tokens = get_max_token_from_messages(messages, chat_model)

        # Change create type ChatCompletion.create → ChatCompletion.acreate when enabling asynchronous support.
        chat_completion = openai_client.chat.completions.create(
            model=chat_deployment,
            messages=messages,
            temperature=0.0,
            max_tokens=max_tokens,
            n=1
        )

        query_text = chat_completion.choices[0].message.content
        if query_text.strip() == "0":
            query_text = history[-1]["user"] # Use the last user input if we failed to generate a better query

        total_tokens = chat_completion.usage.total_tokens

        # STEP 2: Retrieve relevant documents from the search index with the GPT optimized query
        use_semantic_captions = True if overrides.get("semanticCaptions") else False
        top = overrides.get("top")
        exclude_category = overrides.get("excludeCategory") or None
        filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None
        semantic_ranker = overrides.get("semanticRanker")

        if semantic_ranker:
            r = self.search_client.search(query_text,
                                          filter=filter,
                                          query_type=QueryType.SEMANTIC,
                                          semantic_configuration_name="default",
                                          top=top,
                                          query_caption="extractive|highlight-false" if use_semantic_captions else None
                                          )
        else:
            r = self.search_client.search(query_text,
                                          filter=filter,
                                          top=top
                                          )
        if use_semantic_captions:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(" . ".join([c.text for c in doc['@search.captions']])) for doc in r]
        else:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field]) for doc in r]
        content = "\n".join(results)

        # STEP 3: Generate a contextual and content specific answer using the search results and chat history
        # GPT-3.5 Turbo (4k/16k)
        if "gpt-3.5-turbo" in chat_model:
            completion_model = chat_model
            # completion_model = "gpt-35-turbo-instruct" # for future use
        # GPT-4 (8k/32k)
        else:
            completion_model = chat_model

        completion_gpt_model = get_gpt_model(completion_model)
        completion_deployment = completion_gpt_model.get("deployment")

        message_builder = MessageBuilder(self.system_message_chat_conversation)
        messages = message_builder.get_messages_from_history(
            history,
            history[-1]["user"]+ "\n\nSources:\n" + content[:1024], # Model does not handle lengthy system messages well. Moving sources to latest user conversation to solve follow up questions prompt.
            )

        temperature = float(overrides.get("temperature"))
        max_tokens = get_max_token_from_messages(messages, completion_model)

        # Change create type ChatCompletion.create → ChatCompletion.acreate when enabling asynchronous support.
        response = openai_client.chat.completions.create(
            model=completion_deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=1024,
            n=1
        )

        response_text = response.choices[0].message.content
        total_tokens += response.usage.total_tokens

        # logging
        input_text = history[-1]["user"]
        write_chatlog(ApproachType.DocSearch, user_name, total_tokens, input_text, response_text, query_text)

        msg_to_display = '\n\n'.join([str(message) for message in messages])

        return {"data_points": results, "answer": response_text, "thoughts": f"Searched for:<br>{query_text}<br><br>Conversations:<br>" + msg_to_display.replace('\n', '<br>')}