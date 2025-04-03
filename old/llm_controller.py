from typing import List, Type, TypedDict, Dict
from .llm_api_handler import LLMHandler


class LLMCfgRec(TypedDict):
    name: str
    handler: Type[LLMHandler]
    handler_args: Dict


LLMCfgs = List[LLMCfgRec]


class LLMController:

    def __init__(self, llm_cfgs: LLMCfgs):
        self.llm_cfgs = llm_cfgs
        self.handlers = {}

    def init_controller(self):
        for llm in self.llm_cfgs:
            name = llm["name"]
            self.handlers[name] = self.get_handler(name)

    def list_llms(self):
        return [x["name"] for x in self.llm_cfgs]

    def get_llm_cfg(self, name):
        for llm in self.llm_cfgs:
            if llm["name"] == name:
                return llm
        raise ValueError("LLM configuration not found for name: %s" % name)

    def get_handler(self, name):
        llm_cfg = self.get_llm_cfg(name)
        return llm_cfg["handler"](**llm_cfg["handler_args"])
