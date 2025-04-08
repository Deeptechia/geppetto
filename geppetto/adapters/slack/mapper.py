import logging
import re
from typing import Dict, Any, List, Optional

from geppetto.adapters.slack.types import SlackMessage
from geppetto.core.types.message import Message, MessageRole
from geppetto.core.types.conversation import UserInfo


class SlackMessageMapper:
    """Handles complex mapping between Slack messages and core message models."""

    @staticmethod
    def slack_to_core_message(
        slack_message: SlackMessage,
        bot_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        # Determine message role
        role = (
            MessageRole.ASSISTANT
            if slack_message.user_id == bot_id
            else MessageRole.USER
        )

        # Clean up message content
        content = SlackMessageMapper._clean_mentions(slack_message.text)

        # Create the core message
        return Message(content=content, role=role, metadata=metadata)

    @staticmethod
    def core_to_slack_message(
        message: Message, conversation_metadata: Dict[str, Any]
    ) -> SlackMessage:
        # Create SlackMessage with only the content from the core message
        slack_message = SlackMessage(
            text=message.content,
            channel_id=conversation_metadata.get("channel_id"),
            thread_ts=conversation_metadata.get("thread_ts"),
        )

        # Add any special blocks if needed
        if "blocks" in message.metadata:
            slack_message.blocks = message.metadata["blocks"]

        return slack_message

    @staticmethod
    def extract_user_info(slack_user_data: Dict[str, Any]) -> UserInfo:
        user = slack_user_data.get("user", {})
        user_id = user.get("id")
        profile = user.get("profile", {})

        return UserInfo(
            id=user_id,
            name=profile.get("real_name") or user.get("name", "Unknown"),
            preferences={
                "timezone": user.get("tz"),
                "locale": user.get("locale"),
                "is_admin": user.get("is_admin", False),
                "is_owner": user.get("is_owner", False),
            },
        )

    @staticmethod
    def _clean_mentions(text: str) -> str:
        # Remove user mentions like <@U12345>
        text = re.sub(r"<@[A-Z0-9]+>", "", text)
        # Remove channel mentions like <#C12345>
        text = re.sub(r"<#[A-Z0-9]+\|([^>]+)>", r"#\1", text)
        # Clean up remaining Slack formatting
        text = re.sub(r"<([^|]+)\|([^>]+)>", r"\2", text)
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text
