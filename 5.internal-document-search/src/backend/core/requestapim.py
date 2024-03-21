import os
import json
import requests

class RequestAPIM:
    """
    This class is responsible for making requests to the API Management (APIM) endpoint to request chat completion.
    """

    apim_config = {
        'endpoint': os.environ.get("API_MANAGEMENT_ENDPOINT"),
        'headers' : {
            'Content-Type': 'application/json'
        }
    }

    def post_chat_completion(self, body: dict, jwt: str):
        endpoint = self.apim_config['endpoint'] + "/deployments/gpt-35-turbo-deploy/chat/completions?api-version=2023-05-15"
        headers = self.apim_config['headers']
        headers['Authorization'] = jwt
        response = requests.post(endpoint, headers=headers, data=json.dumps(body))
        if response.status_code != 200:
            raise Exception(f'Failed to get chat completion: {json.loads(response.content.decode())["message"]}')
        decoded_response = response.content.decode()
        json_response = json.loads(decoded_response)
        chat_completion = ChatCompletion(json_response)
        return chat_completion


class ChatCompletion:
    def __init__(self, data):
        self.id = data['id']
        self.object = data['object']
        self.created = data['created']
        self.model = data['model']
        self.choices = [Choice(choice) for choice in data['choices']]
        self.usage = Usage(data['usage'])

class Choice:
    def __init__(self, data):
        self.finish_reason = data['finish_reason']
        self.index = data['index']
        self.message = Message(data['message'])

class Message:
    def __init__(self, data):
        self.role = data['role']
        self.content = data['content']

class Usage:
    def __init__(self, data):
        self.prompt_tokens = data['prompt_tokens']
        self.completion_tokens = data['completion_tokens']
        self.total_tokens = data['total_tokens']
