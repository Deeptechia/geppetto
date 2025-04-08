from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class SlackMessage:
    """Representation of a Slack message with all Slack-specific attributes."""
    text: str
    user_id: Optional[str] = None
    ts: Optional[str] = None
    channel_id: Optional[str] = None
    thread_ts: Optional[str] = None
    team_id: Optional[str] = None
    subtype: Optional[str] = None
    event_ts: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    files: List[Dict[str, Any]] = field(default_factory=list)
    blocks: List[Dict[str, Any]] = field(default_factory=list)
    mrkdwn: bool = True

    @classmethod
    def from_event(cls, event: Dict[str, Any]) -> "SlackMessage":
        """Create a SlackMessage from a Slack event."""
        return cls(
            text=event.get("text", ""),
            user_id=event.get("user"),
            ts=event.get("ts"),
            channel_id=event.get("channel"),
            thread_ts=event.get("thread_ts"),
            team_id=event.get("team"),
            subtype=event.get("subtype"),
            event_ts=event.get("event_ts"),
            attachments=event.get("attachments", []),
            files=event.get("files", [])
        )

    def to_slack_payload(self) -> Dict[str, Any]:
        """Convert to a payload for Slack API."""
        payload = {
            "text": self.text,
            "mrkdwn": self.mrkdwn
        }

        if self.channel_id:
            payload["channel"] = self.channel_id

        if self.thread_ts:
            payload["thread_ts"] = self.thread_ts

        if self.ts:
            payload["ts"] = self.ts

        if self.blocks:
            payload["blocks"] = self.blocks

        return payload