import re
from typing import Dict, Any, List, Optional

from geppetto.core.types.message import Message, MessageRole
from geppetto.core.types.conversation import UserInfo


class SlackMessageMapper:
    """Handles complex mapping between Slack messages and core message models."""

    @staticmethod
    def slack_to_core_message(
        slack_event: Dict[str, Any], bot_id: Optional[str] = None
    ) -> Message:
        # Extract basic message content
        content = slack_event.get("text", "")
        user_id = slack_event.get("user")

        # Clean up message content - remove mentions
        content = SlackMessageMapper._clean_mentions(content)

        # Determine message role // IS THIS NEEDED?
        role = MessageRole.ASSISTANT if user_id == bot_id else MessageRole.USER

        # Create message with basic info
        message = Message(content=content, role=role)

        # Add Slack-specific metadata
        message.add_metadata(
            slack_ts=slack_event.get("ts"),
            channel_id=slack_event.get("channel"),
            thread_ts=slack_event.get("thread_ts"),
            user_id=user_id,
            team_id=slack_event.get("team"),
            subtype=slack_event.get("subtype"),
            event_ts=slack_event.get("event_ts"),
        )

        # Handle attachments if present
        attachments = slack_event.get("attachments", [])
        if attachments:
            SlackMessageMapper._add_attachment_metadata(message, attachments)

        # Handle files if present
        files = slack_event.get("files", [])
        if files:
            SlackMessageMapper._add_file_metadata(message, files)

        return message

    @staticmethod
    def core_to_slack_message(message: Message) -> Dict[str, Any]:
        # Basic message payload
        slack_message = {"text": message.content, "mrkdwn": True}

        # Add channel and thread if available in metadata
        if "channel_id" in message.metadata:
            slack_message["channel"] = message.metadata["channel_id"]

        if "thread_ts" in message.metadata:
            slack_message["thread_ts"] = message.metadata["thread_ts"]

        # Handle blocks/attachments if needed
        if "blocks" in message.metadata:
            slack_message["blocks"] = message.metadata["blocks"]

        return slack_message

    @staticmethod
    def get_conversation_key(slack_event: Dict[str, Any]) -> str:
        """
        Generate a unique conversation key from a Slack event.

        Args:
            slack_event: Slack event data

        Returns:
            str: Unique conversation identifier
        """
        channel_id = slack_event.get("channel")
        thread_ts = slack_event.get("thread_ts") or slack_event.get("ts")
        return f"{channel_id}:{thread_ts}"

    @staticmethod
    def extract_user_info(slack_user_data: Dict[str, Any]) -> UserInfo:
        """
        Extract UserInfo from Slack user data.

        Args:
            slack_user_data: User data from Slack API

        Returns:
            UserInfo: Core user information
        """
        user = slack_user_data.get("user", {})
        user_id = user.get("id")
        profile = user.get("profile", {})

        return UserInfo(
            id=user_id,
            name=profile.get("real_name") or user.get("name", "Unknown"),
            avatar_url=profile.get("image_192"),
            preferences={
                "timezone": user.get("tz"),
                "locale": user.get("locale"),
                "is_admin": user.get("is_admin", False),
                "is_owner": user.get("is_owner", False),
            },
        )

    @staticmethod
    def _clean_mentions(text: str) -> str:
        """Remove Slack user/channel mentions from text."""
        # Remove user mentions like <@U12345>
        text = re.sub(r"<@[A-Z0-9]+>", "", text)
        # Remove channel mentions like <#C12345>
        text = re.sub(r"<#[A-Z0-9]+\|([^>]+)>", r"#\1", text)
        # Clean up remaining Slack formatting
        text = re.sub(r"<([^|]+)\|([^>]+)>", r"\2", text)
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _add_attachment_metadata(
        message: Message, attachments: List[Dict[str, Any]]
    ) -> None:
        """Add attachment information to message metadata."""
        attachment_data = []

        for attachment in attachments:
            attachment_item = {
                "fallback": attachment.get("fallback"),
                "title": attachment.get("title"),
                "text": attachment.get("text"),
                "image_url": attachment.get("image_url"),
                "thumb_url": attachment.get("thumb_url"),
            }
            attachment_data.append(attachment_item)

        message.add_metadata(attachments=attachment_data)

        # If message has image attachments, note this in content
        has_images = any(a.get("image_url") for a in attachments)
        if has_images and not message.content:
            message.content = "[Shared an image]"

    @staticmethod
    def _add_file_metadata(message: Message, files: List[Dict[str, Any]]) -> None:
        """Add file information to message metadata."""
        file_data = []

        for file in files:
            file_item = {
                "id": file.get("id"),
                "name": file.get("name"),
                "filetype": file.get("filetype"),
                "url_private": file.get("url_private"),
                "thumb_url": file.get("thumb_url"),
                "is_image": file.get("mimetype", "").startswith("image/"),
            }
            file_data.append(file_item)

        message.add_metadata(files=file_data)

        # If message has file attachments but no content, add descriptive text
        if files and not message.content:
            file_types = set(f.get("filetype", "").upper() for f in files)
            file_desc = ", ".join(file_types)
            message.content = f"[Shared {len(files)} file(s): {file_desc}]"
