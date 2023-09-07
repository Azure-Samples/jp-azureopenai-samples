class MessageBuilder:
    """
      A class for building and managing messages in a chat conversation.
      Attributes:
          message (list): A list of dictionaries representing chat messages.
          model (str): The name of the ChatGPT model.
          token_count (int): The total number of tokens in the conversation.
      Methods:
          __init__(self, system_content: str, chatgpt_model: str): Initializes the MessageBuilder instance.
          append_message(self, role: str, content: str, index: int = 1): Appends a new message to the conversation.
      """

    # Chat roles
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    def __init__(self, system_content: str):
        self.messages = [{'role': 'system', 'content': system_content}]

    def append_message(self, role: str, content: str, index: int = 1):
        self.messages.insert(index, {'role': role, 'content': content})

    def get_messages_from_history(self, history: list[dict[str, str]], user_conv: str, few_shots = []) -> list:
        # Add examples to show the chat what responses we want. It will try to mimic any responses and make sure they match the rules laid out in the system message.
        for shot in few_shots:
            self.append_message(shot.get('role'), shot.get('content'))

        user_content = user_conv
        append_index = len(few_shots) + 1

        self.append_message(self.USER, user_content, index=append_index)

        for h in reversed(history[:-1]):
            if bot_msg := h.get(self.ASSISTANT):
                self.append_message(self.ASSISTANT, bot_msg, index=append_index)
            if user_msg := h.get(self.USER):
                self.append_message(self.USER, user_msg, index=append_index)

        messages = self.messages
        return messages
