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
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Simplified conversation container."""

    # Core fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = field(default_factory=list)
    state: ConversationState = ConversationState.ACTIVE
    user_info: Optional[UserInfo] = None

    # Platform-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def get_messages(
        self,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        role: Optional[MessageRole] = None,
    ) -> List[Message]:
        messages = self.messages

        if before:
            messages = [m for m in messages if m.timestamp < before]
        if after:
            messages = [m for m in messages if m.timestamp > after]
        if role:
            messages = [m for m in messages if m.role == role]

        if limit and limit > 0:
            return messages[-limit:]
        return messages

    def get_context_for_llm(self, max_messages: Optional[int] = None) -> List[Message]:
        """Get conversation context formatted for LLM consumption."""
        # By default, get recent messages up to the limit
        messages = self.get_messages(limit=max_messages)

        # Ensure system messages (if any) are included first
        system_msgs = [m for m in self.messages if m.role == MessageRole.SYSTEM]
        if system_msgs and system_msgs[0] not in messages:
            messages = [system_msgs[0]] + messages

        return messages

    @classmethod
    def create(
        cls,
        user_info: UserInfo,
        conversation_id: Optional[str] = None,
        initial_message: Optional[Message] = None,
    ) -> "Conversation":
        """Create a new conversation."""
        conv = cls(id=conversation_id or str(uuid.uuid4()), user_info=user_info)
        if initial_message:
            conv.add_message(initial_message)
        return conv

    def set_state(self, state: ConversationState) -> None:
        self.state = state
