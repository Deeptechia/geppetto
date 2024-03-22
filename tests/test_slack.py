import os
import sys
import unittest
from unittest.mock import patch, ANY

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from geppetto.utils import load_json
from geppetto.slack_handler import SlackHandler


class TestSlack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # cls.patcher1 = patch("geppetto.slack_handler.OpenAIHandler")
        cls.patcher2 = patch("geppetto.slack_handler.App")
        cls.controller_patcher = patch("geppetto.llm_controller.LLMController")
        # cls.MockOpenAIHandler = cls.patcher1.start()
        cls.MockApp = cls.patcher2.start()

        SLACK_BOT_TOKEN = "slack_bot_token"
        SIGNING_SECRET = "signing_secret"
        BOT_DEFAULT_RESPONSES = load_json("default_responses.json")

        cls.slack_handler = SlackHandler(
            {"test_user_id": "Test User"},
            BOT_DEFAULT_RESPONSES,
            SLACK_BOT_TOKEN,
            SIGNING_SECRET,
            cls.controller_patcher.start()
        )

    @classmethod
    def tearDownClass(cls):
        # cls.patcher1.stop()
        cls.patcher2.stop()

    def test_permission_check(self):
        body = {
            "event": {
                "text": "Test message",
                "channel": "test_channel",
                "ts": "1",
                "user": "disallowed_user_id",
            }
        }

        self.slack_handler.handle_event(body)

        self.MockApp().client.chat_postMessage.assert_called_with(
            channel="test_channel",
            text=self.slack_handler.bot_default_responses["user"]["permission_denied"],
            thread_ts="1",
        )

    def test_random_user_allowed_with_wildcard_permission(self):
        body = {
            "event": {
                "text": "Test message",
                "channel": "test_channel",
                "ts": "1",
                "user": "random_user_id",
            }
        }

        self.slack_handler.allowed_users = {"random_users": "*"}
        self.slack_handler.handle_event(body)

        self.MockApp().client.chat_postMessage.assert_called_with(
            channel="test_channel",
            text=":geppetto: ... :thought_balloon: ...",
            thread_ts="1",
        )

    @unittest.skip("WIP: TBD with Controller")
    def test_handle_message(self):
        mock_open_ai_response = "Mock text response"
        self.MockOpenAIHandler().send_message.return_value = mock_open_ai_response

        channel_id = "test_channel"
        thread_id = "test_thread_id"
        message = "Test message"

        self.slack_handler.handle_message(message, channel_id, thread_id)

        self.assertIn(thread_id, self.slack_handler.thread_messages)
        self.assertIn(
            {"role": "user", "content": message},
            self.slack_handler.thread_messages[thread_id],
        )
        self.assertIn(
            {"role": "assistant", "content": mock_open_ai_response},
            self.slack_handler.thread_messages[thread_id],
        )

        self.MockApp().client.chat_postMessage.assert_called_with(
            channel=channel_id,
            text=":geppetto: ... :thought_balloon: ...",
            thread_ts=thread_id,
        )
        self.MockApp().client.chat_update.assert_called_with(
            channel=channel_id,
            text=mock_open_ai_response,
            thread_ts=thread_id,
            ts=ANY,
        )

    @unittest.skip("WIP: TBD with Controller")
    def test_handle_image(self):
        channel_id = "test_channel"
        thread_id = "test_thread_id"
        message = "Test message"

        mock_open_ai_text_response = "Mock text response"
        self.MockOpenAIHandler().send_message.return_value = mock_open_ai_text_response
        self.slack_handler.handle_message(message, channel_id, thread_id)
        self.MockApp().client.chat_update.assert_called_with(
            channel=channel_id,
            text=mock_open_ai_text_response,
            thread_ts=thread_id,
            ts=ANY,
        )

        mock_open_ai_byte_response = b"Mock byte response"
        self.MockOpenAIHandler().send_message.return_value = mock_open_ai_byte_response
        self.slack_handler.handle_message(message, channel_id, thread_id)
        self.MockApp().client.files_upload_v2.assert_called_with(
            channel=channel_id,
            thread_ts=thread_id,
            username="Dall-E",
            content=b"Mock byte response",
            title="Image",
        )


if __name__ == "__main__":
    unittest.main()
