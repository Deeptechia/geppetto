from abc import ABC, abstractmethod


class LLMHandler(ABC):
    def __init__(self, name, models_dict, client):
        self.name = name
        self.models = models_dict
        self.client = client

    def get_info(self):
        return "Name:\t{name}\nModel:\t{model}\nClient\t{client}"

    @abstractmethod
    def llm_generate_content(self, prompt: str):
        pass

    @abstractmethod
    def thread_history_append(self, thread_history: dict, msg: str, role: str):
        pass

    @abstractmethod
    def is_image_data(self, response_from_llm_api):
        pass
