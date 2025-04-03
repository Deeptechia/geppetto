import toml
import logging
import json
import os
from typing import Dict, Any, Optional

from geppetto.core.llm.base import LLMProvider
from geppetto.core.llm.openai_handler import OpenAIHandler
from geppetto.core.llm.claude_handler import ClaudeHandler
from geppetto.core.llm.gemini_handler import GeminiHandler

with open("pyproject.toml", "r") as f:
    version = toml.load(f)["tool"]["poetry"]["version"]

GEPPETTO_VERSION = version


def append_version_to_message(message: str, source: LLMProvider) -> str:
    match source:
        case OpenAIHandler():
            return f"{message}\n\n(Geppetto v{GEPPETTO_VERSION} Source: OpenAI - {source.model})"
        case ClaudeHandler():
            return f"{message}\n\n(Geppetto v{GEPPETTO_VERSION} Source: Claude - {source.model})"
        case GeminiHandler():
            return f"{message}\n\n(Geppetto v{GEPPETTO_VERSION} Source: Gemini - {source.model})"
        case _:
            return message


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    config = {}

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Error loading config file: {e}")

    return config
