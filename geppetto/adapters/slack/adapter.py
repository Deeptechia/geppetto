from io import BytesIO
import logging
import os
from PIL import Image

from typing import Dict, Any, Optional
from urllib.request import urlopen
import certifi
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.errors import SlackApiError

from geppetto.adapters.base import PlatformAdapter
from geppetto.adapters.slack.mapper import SlackMessageMapper
from geppetto.core.multiplexer import LLMMultiplexer, LLMType
from geppetto.core.types.conversation import Conversation, UserInfo
from geppetto.core.types.images import ImageContent
from geppetto.utils import append_version_to_message


class SlackAdapter(PlatformAdapter):
    def __init__(
        self,
        bot_token: str,
        signing_secret: str,
        app_token: str,
        allowed_users: Dict[str, str],
        llm_multiplexer: LLMMultiplexer,
        default_responses: Optional[Dict[str, Any]] = None,
    ):
        # Set SSL certificate for secure requests
        os.environ["SSL_CERT_FILE"] = certifi.where()

        self.bot_token = bot_token
        self.signing_secret = signing_secret
        self.app_token = app_token
        self.allowed_users = allowed_users
        self.llm_multiplexer = llm_multiplexer
        self.llm_provider = llm_multiplexer.get_provider()
        self.default_responses = default_responses or {
            "permission_denied": "You don't have permission to interact with me.",
            "processing": ":thought_balloon:",
            "error": "There was an error processing your request.",
        }

        # Store active conversations
        self.conversations: Dict[str, Conversation] = {}

        # Initialize the Slack app
        self.app = None

    def initialize(self) -> None:
        self.app = AsyncApp(token=self.bot_token, signing_secret=self.signing_secret)

        self.app.event("message")(self._handle_event)
        self.app.event("app_mention")(self._handle_event)

        # TODO: add list of available models to platform adapters and info to platform adapters

    async def _handle_switch_model(
        self, body: Dict[str, Any], conversation: Optional[Conversation] = None
    ) -> None:
        command = body.get("command", "")
        channel_id = body.get("channel_id") or body.get("event", {}).get("channel")
        thread_ts = body.get("event", {}).get("thread_ts") or body.get("event", {}).get(
            "ts"
        )

        # Extract model from command or text
        if command.startswith("/"):
            model = command.split("/")[1]
        else:
            text = body.get("event", {}).get("text", "").lower()
            if "use claude" in text or "switch to claude" in text:
                model = "claude"
            elif "use gemini" in text or "switch to gemini" in text:
                model = "gemini"
            else:
                return

        try:
            # Switch the model
            new_provider = self.llm_multiplexer.get_provider(LLMType(model))

            # If we have a conversation, update its metadata
            if conversation:
                conversation.metadata["llm_type"] = model
                self.llm_provider = new_provider
            else:
                # This is from a slash command, update global provider
                self.llm_provider = new_provider

            await self.app.client.chat_postMessage(
                channel=channel_id,
                text=f"Switched to {model} model successfully! 🎉",
                thread_ts=thread_ts,
            )
        except Exception as e:
            logging.error(f"Error switching model: {e}")
            await self.app.client.chat_postMessage(
                channel=channel_id,
                text=f"Failed to switch to {model} model: {str(e)}",
                thread_ts=thread_ts,
            )

    async def get_or_create_conversation(
        self, platform_data: Dict[str, Any]
    ) -> Conversation:
        """Get an existing conversation or create a new one based on Slack data."""
        event = platform_data.get("event", {})

        # Get conversation identifiers
        channel_id = event.get("channel")
        thread_ts = event.get("thread_ts") or event.get("ts")
        conversation_id = f"{channel_id}:{thread_ts}"

        # Check if conversation exists
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]

        # Create new conversation
        user_id = event.get("user")
        user_info = await self.get_user_info(user_id)

        conversation = Conversation.create(
            user_info=user_info, conversation_id=conversation_id
        )

        # Add Slack-specific metadata
        conversation.metadata.update(
            {
                "channel_id": channel_id,
                "thread_ts": thread_ts,
                "team_id": event.get("team"),
            }
        )

        # Store for future reference
        self.conversations[conversation_id] = conversation

        return conversation

    async def get_user_info(self, platform_user_id: str) -> UserInfo:
        """Get or create UserInfo from a Slack user ID."""
        # If user is in allowed users, use that information
        user_name = self.allowed_users.get(platform_user_id)

        # Otherwise, fetch from Slack API
        if not user_name:
            try:
                user_info_response = await self.app.client.users_info(
                    user=platform_user_id
                )
                if user_info_response["ok"]:
                    user = user_info_response["user"]
                    user_name = user.get("real_name") or user.get("name")
                    avatar_url = user.get("profile", {}).get("image_192")
                else:
                    user_name = "Unknown User"
                    avatar_url = None
            except SlackApiError as e:
                logging.error(f"Error fetching user info: {e}")
                user_name = "Unknown User"
                avatar_url = None
        else:
            avatar_url = None

        return UserInfo(
            id=platform_user_id, name=user_name, avatar_url=avatar_url, preferences={}
        )

    async def _handle_event(self, body: Dict[str, Any]) -> None:
        """Handle incoming Slack events."""
        event = body.get("event", {})
        user_id = event.get("user")

        # Check if user is allowed
        if user_id not in self.allowed_users and "*" not in self.allowed_users.values():
            # Send permission denied message
            channel_id = event.get("channel")
            thread_ts = event.get("thread_ts") or event.get("ts")

            await self.app.client.chat_postMessage(
                channel=channel_id,
                text=append_version_to_message(
                    self.default_responses["permission_denied"], self.llm_provider
                ),
                thread_ts=thread_ts,
            )
            return

        # Get or create conversation
        conversation = await self.get_or_create_conversation(body)

        # Check if this is a model switch request
        text = event.get("text", "").lower()
        if "use " in text or "switch to " in text:
            await self._handle_switch_model(body, conversation)
            return

        # Get the appropriate LLM provider for this conversation
        if "llm_type" in conversation.metadata:
            self.llm_provider = self.llm_multiplexer.get_provider(
                LLMType(conversation.metadata["llm_type"])
            )

        # Process the message
        message = SlackMessageMapper.slack_to_core_message(event)
        conversation.add_message(message)

        # Send processing indicator
        response = await self.app.client.chat_postMessage(
            channel=conversation.metadata["channel_id"],
            text=append_version_to_message(
                self.default_responses["processing"], self.llm_provider
            ),
            thread_ts=conversation.metadata["thread_ts"],
        )

        processing_ts = response["ts"]

        # Generate response using LLM
        await self._generate_and_send_response(conversation, processing_ts)

    async def _generate_and_send_response(
        self, conversation: Conversation, processing_ts: str
    ) -> None:
        """Generate a response using the LLM and send it back to Slack."""
        try:
            # Get conversation context for LLM
            messages = conversation.get_context_for_llm()

            # Generate response
            llm_response = await self.llm_provider.generate_response(conversation)

            # Update the processing message with the actual response

            if isinstance(llm_response.content, ImageContent):
                await self.app.client.files_upload_v2(
                    channel=conversation.metadata["channel_id"],
                    thread_ts=conversation.metadata["thread_ts"],
                    content=self.download_image(llm_response.content.source),
                    title="Image",
                )
            else:
                await self.app.client.chat_update(
                    channel=conversation.metadata["channel_id"],
                    ts=processing_ts,
                    text=append_version_to_message(
                        str(llm_response.content), self.llm_provider
                    ),
                )

            # Add assistant response to conversation
            conversation.add_message(llm_response)

        except Exception as e:
            logging.error(f"Error generating response: {e}")

            # Update with error message
            await self.app.client.chat_update(
                channel=conversation.metadata["channel_id"],
                ts=processing_ts,
                text=append_version_to_message(
                    self.default_responses["error"], self.llm_provider
                ),
            )

    @staticmethod
    def download_image(url):
        img = Image.open(urlopen(url=url))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    async def start(self) -> None:
        """Start the Slack event handler."""
        if not self.app:
            self.initialize()

        try:
            # Start the app
            await AsyncSocketModeHandler(self.app, self.app_token).start_async()
            logging.info("Slack adapter started successfully")
        except Exception as e:
            logging.error(f"Error starting Slack adapter: {e}")

    def stop(self) -> None:
        """Stop the Slack event handler."""
        if self.app:
            try:
                # Stop the app
                self.app.stop()
                logging.info("Slack adapter stopped successfully")
            except Exception as e:
                logging.error(f"Error stopping Slack adapter: {e}")
