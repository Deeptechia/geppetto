from abc import ABC, abstractmethod
from typing import List, Optional

from geppetto.core.types.conversation import Conversation
from geppetto.core.types.message import Message


class LLMError(Exception):
    """Base exception for LLM-related errors."""

    pass


class InvalidRequestError(LLMError):
    """Raised when the request is invalid (bad parameters, etc)."""

    pass


class LLMProvider(ABC):
    """
    Base interface for LLM providers (OpenAI, Claude, Gemini, etc.).
    This abstract class defines the contract that all LLM implementations must follow.
    """

    def __init__(self, model: str, **kwargs):
        """
        Initialize the LLM provider.

        Args:
            model: The specific model to use (e.g., 'gpt-4', 'claude-3', etc.)
            **kwargs: Additional provider-specific configuration
        """
        self.model = model
        self.config = kwargs

    @abstractmethod
    async def generate_response(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> Message:
        """
        Generate a response from the LLM based on the conversation history.

        Args:
            conversation: The conversation history
            temperature: Controls randomness in the response (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            stop_sequences: List of sequences where the LLM should stop generating

        Returns:
            Message: The LLM's response as a Message object

        Raises:
            InvalidRequestError: If the request parameters are invalid
            LLMError: For other LLM-related errors
        """
        pass
