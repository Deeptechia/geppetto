from abc import ABC, abstractmethod
from typing import Callable, List, Dict


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

    @abstractmethod
    def get_prompt_from_thread(self, thread: List[Dict], assistant_tag: str, user_tag: str):
        pass
