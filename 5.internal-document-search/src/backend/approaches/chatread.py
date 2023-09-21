from typing import Any

import openai
# To uncomment when enabling asynchronous support.
# from azure.cosmos.aio import ContainerProxy
from approaches.approach import Approach
from approaches.chatlogging import write_chatlog, ApproachType
from core.messagebuilder import MessageBuilder
from core.modelhelper import get_gpt_model, get_max_token_from_messages

# Simple read implementation, using the OpenAI APIs directly. It uses OpenAI to generate an completion 
# (answer) with that prompt.
class ChatReadApproach(Approach):

    def run(self, user_name: str, history: list[dict[str, str]], overrides: dict[str, Any]) -> Any:
        chat_model = overrides.get("gptModel")
        chat_gpt_model = get_gpt_model(chat_model)
        chat_deployment = chat_gpt_model.get("deployment")

        systemPrompt =  overrides.get("systemPrompt")
        temaperature = float(overrides.get("temperature"))

        user_q = history[-1]["user"]
        message_builder = MessageBuilder(systemPrompt)
        messages = message_builder.get_messages_from_history(
            history, 
            user_q
            )

        max_tokens = get_max_token_from_messages(messages, chat_model)

        # Generate a contextual and content specific answer using chat history
        # Change create type ChatCompletion.create → ChatCompletion.acreate when enabling asynchronous support.
        chat_completion = openai.ChatCompletion.create(
            engine=chat_deployment, 
            messages=messages,
            temperature=temaperature, 
            max_tokens=max_tokens,
            n=1)

        response_text = chat_completion.choices[0]["message"]["content"]
        total_tokens = chat_completion.usage.total_tokens

        # logging
        input_text = history[-1]["user"]
        write_chatlog(ApproachType.Chat, user_name, total_tokens, input_text, response_text)

        return { "answer": response_text }
    