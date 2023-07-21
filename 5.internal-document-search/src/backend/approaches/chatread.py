import openai
import json
import tiktoken
from approaches.approach import Approach
from approaches.chatlogging import write_chatlog, ApproachType

# Simple read implementation, using the OpenAI APIs directly. It uses OpenAI to generate an completion 
# (answer) with that prompt.
class ChatReadApproach(Approach):
    def run(self, gpt_model, user_name: str, history: list[dict], overrides: dict) -> any:
        deployment = gpt_model.get("deployment")
        max_tokens = gpt_model.get("max_tokens")
        temaperature = float(overrides.get("temperature"))
        systemPrompt =  overrides.get("systemPrompt")
        messages = [{"role": k, "content": v} for i in history for k, v in i.items()]

        if systemPrompt != "":
            messages.insert(0, {"role": "system", "content": systemPrompt})

        # input tokens + output tokens < max tokens of the model
        encoding = gpt_model.get("encoding")
        input_token = encoding.encode(json.dumps(messages, ensure_ascii=False))
        token_length = len(input_token)
        if max_tokens > token_length + 1:
            max_tokens = max_tokens - (token_length + 1)

        # Generate a contextual and content specific answer using chat history
        response = openai.ChatCompletion.create(
            engine=deployment, 
            messages=messages,
            max_tokens=max_tokens,
            temperature=temaperature, 
            n=1)

        response_text = response.choices[0]["message"]["content"]
        total_tokens = response.usage.total_tokens
        input_text = history[-1]["user"]

        write_chatlog(ApproachType.Chat, user_name, total_tokens, input_text, response_text)

        return { "answer": response_text }
