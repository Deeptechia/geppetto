import logging
from typing import List, Optional, Dict, Any
import functools
import anthropic
from anthropic import AsyncAnthropic

from geppetto.core.types.message import MessageRole
from geppetto.core.types.conversation import Conversation

from .base import (
    LLMProvider,
    Message,
    InvalidRequestError,
    LLMError,
)


def handle_claude_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except anthropic.RateLimitError as e:
            raise LLMError(f"Rate limit exceeded: {str(e)}")
        except anthropic.APIError as e:
            raise LLMError(f"Claude API error: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error: {str(e)}")

    return wrapper


class ClaudeHandler(LLMProvider):
    def __init__(self, model: str, api_key: str, **kwargs):
        super().__init__(model, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key)
        self.name = "Claude"

    def _convert_to_claude_messages(
        self, messages: List[Message]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "role": (
                    "assistant"
                    if message.role.value == "assistant"
                    else message.role.value
                ),
                "content": (
                    message.content
                    if isinstance(message.content, str)
                    else str(message.content)
                ),
            }
            for message in messages
        ]

    @handle_claude_errors
    async def generate_response(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1024,
    ) -> Message:
        if not conversation.messages:
            raise InvalidRequestError("No conversation provided")

        claude_messages = self._convert_to_claude_messages(conversation.messages)

        response = await self.client.messages.create(
            model=self.model,
            messages=claude_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Return the response
        return Message.assistant(content=response.content[0].text)
