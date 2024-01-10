import os
import sys
import unittest
from unittest.mock import patch, ANY

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from utils.load_bot_responses import load_bot_responses
from src.slack_handler import SlackHandler, thread_messages


class TestSlack(unittest.TestCase):
    def setup(self):
        SLACK_BOT_TOKEN = "slack_bot_token"
        SIGNING_SECRET = "signing_secret"
        OPENAI_API_KEY = "openai_key"
        DALLE_MODEL = "dall-e-3"
        CHATGPT_MODEL = "gpt-4"
        BOT_DEFAULT_RESPONSES = load_bot_responses()

        return SlackHandler(
            {"test_user_id": "Test User"},
            BOT_DEFAULT_RESPONSES,
            SLACK_BOT_TOKEN,
            SIGNING_SECRET,
            OPENAI_API_KEY,
            DALLE_MODEL,
            CHATGPT_MODEL,
        )

    @patch("src.slack_handler.App")
    def test_permission_check(self, MockApp):
        slack_handler = self.setup()

        body = {
            "event": {
                "text": "Test message",
                "channel": "test_channel",
                "ts": "1",
                "user": "disallowed_user_id",
            }
        }

        slack_handler.handle_event(body)

        MockApp().client.chat_postMessage.assert_called_with(
            channel="test_channel",
            text=slack_handler.bot_default_responses["user"]["permission_denied"],
            thread_ts="1",
        )

    @patch("src.slack_handler.OpenAIHandler")
    @patch("src.slack_handler.App")
    def test_handle_message(self, MockApp, MockOpenAIHandler):
        mock_open_ai_response = "Mock text response"
        MockOpenAIHandler().send_message.return_value = mock_open_ai_response

        slack_handler = self.setup()

        channel_id = "test_channel"
        thread_id = "test_thread_id"
        message = "Test message"

        slack_handler.handle_message(message, channel_id, thread_id)

        self.assertIn(thread_id, thread_messages)
        self.assertIn({"role": "user", "content": message}, thread_messages[thread_id])
        self.assertIn(
            {"role": "assistant", "content": mock_open_ai_response},
            thread_messages[thread_id],
        )

        MockApp().client.chat_postMessage.assert_called_with(
            channel=channel_id,
            text=":geppetto: ... :thought_balloon: ...",
            thread_ts=thread_id,
        )
        MockApp().client.chat_update.assert_called_with(
            channel=channel_id,
            text=mock_open_ai_response,
            thread_ts=thread_id,
            ts=ANY,
        )

    @patch("src.slack_handler.OpenAIHandler")
    @patch("src.slack_handler.App")
    def test_handle_image(self, MockApp, MockOpenAIHandler):
        slack_handler = self.setup()

        channel_id = "test_channel"
        thread_id = "test_thread_id"
        message = "Test message"

        mock_open_ai_text_response = "Mock text response"
        MockOpenAIHandler().send_message.return_value = mock_open_ai_text_response
        slack_handler.handle_message(message, channel_id, thread_id)
        MockApp().client.chat_update.assert_called_with(
            channel=channel_id,
            text=mock_open_ai_text_response,
            thread_ts=thread_id,
            ts=ANY,
        )

        mock_open_ai_byte_response = b"Mock byte response"
        MockOpenAIHandler().send_message.return_value = mock_open_ai_byte_response
        slack_handler.handle_message(message, channel_id, thread_id)
        MockApp().client.files_upload_v2.assert_called_with(
            channel=channel_id,
            thread_ts=thread_id,
            username="Dall-E",
            content=b"Mock byte response",
            title="Image",
        )


if __name__ == "__main__":
    unittest.main()
