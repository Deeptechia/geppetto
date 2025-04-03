from abc import ABC, abstractmethod
from typing import Any

from geppetto.core.types.conversation import Conversation, UserInfo


class PlatformAdapter(ABC):
    """Base interface for platform-specific adapters."""

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def get_or_create_conversation(self, platform_data: Any) -> Conversation:
        pass

    @abstractmethod
    def get_user_info(self, platform_user_id: str) -> UserInfo:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
