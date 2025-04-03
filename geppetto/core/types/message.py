from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from pyparsing import Enum


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """A simplified, platform-agnostic message."""

    # Core fields
    content: str
    role: MessageRole
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Optional metadata for platform-specific details
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def user(cls, content: str, id: Optional[str] = None) -> "Message":
        return cls(id=id or str(uuid.uuid4()), content=content, role=MessageRole.USER)

    @classmethod
    def assistant(cls, content: str, id: Optional[str] = None) -> "Message":
        return cls(
            id=id or str(uuid.uuid4()), content=content, role=MessageRole.ASSISTANT
        )

    @classmethod
    def system(cls, content: str, id: Optional[str] = None) -> "Message":
        return cls(id=id or str(uuid.uuid4()), content=content, role=MessageRole.SYSTEM)

    def add_metadata(self, **kwargs) -> None:
        self.metadata.update(kwargs)
