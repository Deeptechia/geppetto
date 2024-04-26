from abc import ABC, abstractmethod
from typing import List, Dict, Callable
from .exceptions import InvalidThreadFormatError

ROLE_FIELD = "role"

class LLMHandler(ABC):
    def __init__(self, name, model, client):
        self.name = name
        self.model = model
        self.client = client

    def get_info(self):
        return f"Name: {self.name} - Model: {self.model}"

    @abstractmethod
    def llm_generate_content(self, prompt: str, callback: Callable, *callback_args):
        pass

    def get_prompt_from_thread(self, thread: List[Dict], assistant_tag: str, user_tag: str):
        prompt = []
        for msg in thread:
            formatted_msg = dict(msg)
            if ROLE_FIELD in formatted_msg:
                formatted_msg[ROLE_FIELD] = formatted_msg[ROLE_FIELD].replace(assistant_tag, self.assistant_role)
                formatted_msg[ROLE_FIELD] = formatted_msg[ROLE_FIELD].replace(user_tag, self.user_role)
                prompt.append(formatted_msg)
            else:
                raise InvalidThreadFormatError("The input thread doesn't have the field %s" % ROLE_FIELD)
        return prompt
    
    def split_message(self, message):
        """
        Split a message into parts if it exceeds 4000 characters.
        
        Args:
            message (str): The message to split.
        
        Returns:
            List[str]: A list of message parts.
        """
        max_length = 4000
        return [message[i:i+max_length] for i in range(0, len(message), max_length)]
