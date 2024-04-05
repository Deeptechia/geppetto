import os
import sys
import unittest
from unittest.mock import patch, ANY

from geppetto.llm_controller import LLMController
from tests.test_open_ai import TEST_PERSONALITY

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from geppetto.utils import load_json
from geppetto.slack_handler import SlackHandler


class TestSlack(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.patcher1 = patch("geppetto.main.OpenAIHandler")
        cls.MockOpenAIHandler = cls.patcher1.start()
        cls.patcher2 = patch("geppetto.slack_handler.App")
        cls.MockApp = cls.patcher2.start()

        SLACK_BOT_TOKEN = "slack_bot_token"
        SIGNING_SECRET = "signing_secret"
        BOT_DEFAULT_RESPONSES = load_json("default_responses.json")

        cls.slack_handler = SlackHandler(
            {"test_user_id": "Test User"},
            BOT_DEFAULT_RESPONSES,
            SLACK_BOT_TOKEN,
            SIGNING_SECRET,
            initialized_test_llm_controller(cls.MockOpenAIHandler)
        )

    @classmethod
    def tearDown(cls):
        cls.patcher1.stop()
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
            mrkdwn=True
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
            text=":geppetto: :thought_balloon: ...",
            thread_ts="1",
            mrkdwn=True
        )

    def test_handle_message(self):
        mock_open_ai_response = "Mock text response"
        self.MockOpenAIHandler().llm_generate_content.return_value = mock_open_ai_response

        channel_id = "test_channel"
        thread_id = "test_thread_id"
        message = "Test message"

        self.slack_handler.handle_message(message, channel_id, thread_id)

        self.assertIn(thread_id, self.slack_handler.thread_messages)
        self.assertIn(
            {"role": "slack_user", "content": message},
            self.slack_handler.thread_messages[thread_id]["msgs"],
        )
        self.assertIn(
            {"role": "geppetto", "content": mock_open_ai_response},
            self.slack_handler.thread_messages[thread_id]["msgs"],
        )

        self.MockApp().client.chat_postMessage.assert_called_with(
            channel=channel_id,
            text=":geppetto: :thought_balloon: ...",
            thread_ts=thread_id,
            mrkdwn=True
        )
        self.MockApp().client.chat_update.assert_called_with(
            channel=channel_id,
            text=mock_open_ai_response,
            thread_ts=thread_id,
            ts=ANY,
        )

    def test_handle_image(self):
        channel_id = "test_channel"
        thread_id = "test_thread_id"
        message = "Test message"

        mock_open_ai_text_response = "Mock text response"
        self.MockOpenAIHandler().llm_generate_content.return_value = mock_open_ai_text_response
        self.slack_handler.handle_message(message, channel_id, thread_id)
        self.MockApp().client.chat_update.assert_called_with(
            channel=channel_id,
            text=mock_open_ai_text_response,
            thread_ts=thread_id,
            ts=ANY,
        )

        mock_open_ai_byte_response = b"Mock byte response"
        self.MockOpenAIHandler().llm_generate_content.return_value = mock_open_ai_byte_response
        self.slack_handler.handle_message(message, channel_id, thread_id)
        self.MockApp().client.files_upload_v2.assert_called_with(
            channel=channel_id,
            thread_ts=thread_id,
            content=b"Mock byte response",
            title="Image",
        )

    def test_select_llm_from_msg(self):
        message_a = "#llma Test message"
        message_b = "Test #llmb# message"
        message_c = "Test message #llmc?"
        message_default_empty = "Test message"
        message_default_many = "#llmc Test #llmb message #llma"
        message_default_wrong = "Test message #zeta"

        self.assertEqual(self.slack_handler.select_llm_from_msg(
            message_a), "LlmA")

        self.assertEqual(self.slack_handler.select_llm_from_msg(
                    message_b), "LLMb")

        self.assertEqual(self.slack_handler.select_llm_from_msg(
                    message_c), "LLMC")

        self.assertEqual(self.slack_handler.select_llm_from_msg(
                    message_default_empty), "LlmA")

        self.assertEqual(self.slack_handler.select_llm_from_msg(
                            message_default_many), "LlmA")

        self.assertEqual(self.slack_handler.select_llm_from_msg(
                            message_default_wrong), "LlmA")


def initialized_test_llm_controller(mocked_handler):
    controller = LLMController(
        [
            {
                "name": "LlmA",
                "handler": mocked_handler,
                "handler_args": {
                    "personality": TEST_PERSONALITY
                }
            },
            {
                "name": "LLMb",
                "handler": mocked_handler,
                "handler_args": {
                    "personality": TEST_PERSONALITY
                }
            },
            {
                "name": "LLMC",
                "handler": mocked_handler,
                "handler_args": {
                    "personality": TEST_PERSONALITY
                }
            }
        ]
    )
    controller.init_controller()
    return controller

if __name__ == "__main__":
    unittest.main()
