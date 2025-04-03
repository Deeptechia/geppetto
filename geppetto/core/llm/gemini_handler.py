from typing import List, Optional
import functools
import google.generativeai as genai
from google.generativeai.types import content_types
from google.generativeai.types.generation_types import GenerateContentResponse

from geppetto.core.llm.base import InvalidRequestError, LLMError, LLMProvider
from geppetto.core.types.conversation import Conversation
from geppetto.core.types.images import ImageContent
from geppetto.core.types.message import Message


def handle_gemini_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            raise LLMError(f"Gemini API error: {str(e)}")

    return wrapper


class GeminiHandler(LLMProvider):
    def __init__(self, model: str, api_key: str, **kwargs):
        super().__init__(model, **kwargs)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model_name=model)
        self.name = "Gemini"

    def _convert_to_gemini_messages(
        self, messages: List[Message]
    ) -> List[content_types.ContentType]:
        gemini_messages = []

        for message in messages:
            role = message.role.value
            content = message.content

            # Handle different content types
            if isinstance(content, str):
                if role == "system":
                    # Gemini doesn't have a system role, so we'll make it a user message
                    gemini_messages.append({"role": "user", "parts": [content]})
                else:
                    gemini_messages.append(
                        {
                            "role": "user" if role == "user" else "model",
                            "parts": [content],
                        }
                    )
            elif isinstance(content, ImageContent):
                # If we need to handle image inputs in the future
                # TODO: Implement image handling when needed
                raise NotImplementedError("Image content not yet supported for Gemini")
            else:
                # Convert any other content type to string
                gemini_messages.append(
                    {
                        "role": "user" if role == "user" else "model",
                        "parts": [str(content)],
                    }
                )

        return gemini_messages

    def _process_gemini_response(self, response: GenerateContentResponse) -> str:
        if not response.text:
            raise LLMError("Empty response from Gemini")
        return response.text

    @handle_gemini_errors
    async def generate_response(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> Message:
        if not conversation.messages:
            raise InvalidRequestError("No conversation provided")

        gemini_messages = self._convert_to_gemini_messages(conversation.messages)

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens if max_tokens else None,
            "stop_sequences": stop_sequences if stop_sequences else None,
        }

        generation_config = {
            k: v for k, v in generation_config.items() if v is not None
        }

        response = self.client.generate_content(
            gemini_messages, generation_config=generation_config
        )

        response_text = self._process_gemini_response(response)
        return Message.assistant(content=response_text)
