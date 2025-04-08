from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid

from geppetto.core.types.message import Message, MessageRole


# TODO: not sure if this is needed
class ConversationState(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


@dataclass
class UserInfo:
    """User information that remains consistent across platforms."""

    id: str
    name: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Simplified conversation."""

    # Core fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = field(default_factory=list)
    state: ConversationState = ConversationState.ACTIVE

    # Platform-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    @classmethod
    def create(
        cls,
        conversation_id: Optional[str] = None,
        system_message: Optional[Message] = None,
    ) -> "Conversation":
        """Create a new conversation."""
        conv = cls(id=conversation_id or str(uuid.uuid4()))
        if system_message:
            conv.add_message(system_message)
        return conv

    def set_state(self, state: ConversationState) -> None:
        self.state = state
