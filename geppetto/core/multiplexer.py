import logging
from typing import List, Dict, Optional, Type
from enum import Enum

from .llm.base import LLMProvider, LLMError
from .llm.openai_handler import OpenAIHandler
from .llm.claude_handler import ClaudeHandler
from .llm.gemini_handler import GeminiHandler


class LLMType(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"


class LLMMultiplexer:
    # Mapping of LLM types to their handler classes
    HANDLERS: Dict[LLMType, Type[LLMProvider]] = {
        LLMType.OPENAI: OpenAIHandler,
        LLMType.CLAUDE: ClaudeHandler,
        LLMType.GEMINI: GeminiHandler,
    }

    def __init__(
        self,
        api_keys: Dict[LLMType, str],
        models: Optional[Dict[LLMType, str]] = None,
        default_llm: Optional[LLMType] = None,
        **kwargs,
    ):
        self.providers: Dict[LLMType, LLMProvider] = {}
        self.default_llm = default_llm or LLMType.OPENAI

        # Initialize each provider
        for llm_type, api_key in api_keys.items():
            if llm_type not in self.HANDLERS:
                raise ValueError(f"Unsupported LLM type: {llm_type}")

            model = (models or {}).get(llm_type)
            handler_class = self.HANDLERS[llm_type]

            try:
                self.providers[llm_type] = handler_class(
                    model=model, api_key=api_key, **kwargs
                )
            except Exception as e:
                raise LLMError(f"Failed to initialize {llm_type} provider: {str(e)}")

        # Validate default LLM
        if self.default_llm not in self.providers:
            raise ValueError(f"Default LLM {self.default_llm} is not initialized")

    def get_provider(self, llm_type: Optional[LLMType] = None) -> LLMProvider:
        llm_type = llm_type or self.default_llm
        if llm_type not in self.providers:
            raise ValueError(f"LLM type {llm_type} is not initialized")
        return self.providers[llm_type]

    # TODO: add provider listing to platform adapters
    def list_available_providers(self) -> List[LLMType]:
        return list(self.providers.keys())

    # TODO: add provider info to platform adapters
    def get_provider_info(self, llm_type: Optional[LLMType] = None) -> Dict:
        if llm_type:
            provider = self.get_provider(llm_type)
            return {
                "type": llm_type,
                "model": provider.model,
                "available_tools": provider.TOOLS,
            }
        else:
            return {
                llm_type: self.get_provider_info(llm_type)
                for llm_type in self.providers
            }
