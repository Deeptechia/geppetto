import os
import sys
import unittest
from unittest.mock import Mock, patch, ANY

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from src.slack_handler import SlackHandler, SlackMethods, thread_messages


class TestSlackMethods(unittest.TestCase):
    @patch("src.slack_handler.WebClient")
    @patch("src.slack_handler.App")
    def test_permission_check(self, MockApp, MockWebClient):
        # Mock OpenAIHandler
        mock_open_ai_handler = Mock()

        # Mock the chat_postMessage method of the WebClient instance
        mock_web_client_instance = MockWebClient.return_value
        mock_web_client_instance.chat_postMessage = Mock()

        # Make sure App.client returns the mocked WebClient instance
        MockApp.return_value.client = mock_web_client_instance

        slack_methods = SlackMethods(
            app=MockApp(),
            client=MockWebClient(),
            allowed_users={"allowed_user_id": "User Name"},
            open_ai=mock_open_ai_handler,
        )

        body = {
            "event": {
                "text": "Test message",
                "channel": "test_channel",
                "ts": "1",
                "user": "disallowed_user_id",
            }
        }

        slack_methods.handle_event(body)

        mock_web_client_instance.chat_postMessage.assert_called_with(
            channel="test_channel",
            text="El usuario solicitante no pertenece a la lista de usuarios permitidos. Solicite permiso para utilizar la aplicación",
            thread_ts="1",
        )

    @patch("src.slack_handler.WebClient")
    @patch("src.slack_handler.App")
    def test_handle_default(self, MockApp, MockWebClient):
        # Mock OpenAIHandler
        mock_open_ai_handler = Mock()
        mock_open_ai_response = "Mock response from OpenAI"
        mock_open_ai_handler.send_message.return_value = mock_open_ai_response

        # Mock WebClient instance methods
        mock_web_client_instance = MockWebClient.return_value
        mock_web_client_instance.chat_postMessage.return_value = {
            "ok": True,
            "message": {"ts": "test_timestamp"},
        }
        mock_web_client_instance.chat_update = Mock()

        # Make sure App.client returns the mocked WebClient instance
        MockApp.return_value.client = mock_web_client_instance

        slack_methods = SlackMethods(
            app=MockApp(),
            client=MockWebClient(),
            allowed_users={"test_user_id": "Test User"},
            open_ai=mock_open_ai_handler,
        )

        channel_id = "test_channel"
        thread_id = "test_thread_id"
        message = "Test message"

        slack_methods.handle_default(message, channel_id, thread_id)

        self.assertIn(thread_id, thread_messages)
        self.assertIn({"role": "user", "content": message}, thread_messages[thread_id])
        self.assertIn(
            {"role": "assistant", "content": mock_open_ai_response},
            thread_messages[thread_id],
        )

        mock_web_client_instance.chat_postMessage.assert_called_with(
            channel=channel_id,
            text=":geppetto: ... :thought_balloon: ...",
            thread_ts=thread_id,
        )
        mock_web_client_instance.chat_update.assert_called_with(
            channel=channel_id,
            text=mock_open_ai_response,
            thread_ts=thread_id,
            ts=ANY,
        )

    @patch("src.slack_handler.WebClient")
    @patch("src.slack_handler.App")
    def test_openai_response_handling(self, MockApp, MockWebClient):
        # Mock OpenAIHandler
        mock_open_ai_handler = Mock()

        # Mock WebClient instance methods
        mock_web_client_instance = MockWebClient.return_value
        mock_web_client_instance.chat_postMessage.return_value = {
            "ok": True,
            "message": {"ts": "test_timestamp"},
        }
        mock_web_client_instance.chat_update = Mock()
        mock_web_client_instance.files_upload_v2 = Mock()

        # Make sure App.client returns the mocked WebClient instance
        MockApp.return_value.client = mock_web_client_instance

        slack_methods = SlackMethods(
            app=MockApp(),
            client=mock_web_client_instance,
            allowed_users={"test_user_id": "Test User"},
            open_ai=mock_open_ai_handler,
        )

        channel_id = "test_channel"
        thread_id = "test_thread_id"
        message = "Test message"

        mock_open_ai_handler.send_message.return_value = "Mock text response"
        slack_methods.handle_default(message, channel_id, thread_id)
        mock_web_client_instance.chat_update.assert_called_with(
            channel=channel_id,
            text="Mock text response",
            thread_ts=thread_id,
            ts=ANY,
        )

        mock_open_ai_handler.send_message.return_value = b"Mock byte response"
        slack_methods.handle_default(message, channel_id, thread_id)
        mock_web_client_instance.files_upload_v2.assert_called_with(
            channel=channel_id,
            thread_ts=thread_id,
            username="Dall-E",
            content=b"Mock byte response",
            title="Image",
        )

    @patch("src.slack_handler.SlackMethods")
    @patch("src.slack_handler.OpenAIHandler")
    @patch("src.slack_handler.WebClient")
    @patch("src.slack_handler.App")
    def test_event_handling(
        self, MockApp, MockWebClient, MockOpenAIHandler, MockSlackMethods
    ):
        # Mock data
        SLACK_BOT_TOKEN = "test_slack_bot_token"
        SIGNING_SECRET = "test_signing_secret"
        OPENAI_API_KEY = "test_openai_api_key"
        DALLE_MODEL = "test_dalle_model"
        CHATGPT_MODEL = "test_chatgpt_model"

        # Mock SlackMethods' handle_event
        mock_slack_methods_instance = MockSlackMethods.return_value
        mock_slack_methods_instance.handle_event = Mock()

        slack_handler = SlackHandler(
            {"test_user_id": "Test User"},
            SLACK_BOT_TOKEN,
            SIGNING_SECRET,
            OPENAI_API_KEY,
            DALLE_MODEL,
            CHATGPT_MODEL,
        )

        direct_message_event = {
            "event": {
                "type": "message",
                "user": "test_user_id",
                "text": "Test direct message",
                "channel": "test_channel",
                "ts": "test_timestamp",
            }
        }
        slack_handler.slack.handle_event(direct_message_event)

        mock_slack_methods_instance.handle_event.assert_called_with(
            direct_message_event
        )

        app_mention_event = {
            "event": {
                "type": "app_mention",
                "user": "test_user_id",
                "text": "Test app mention",
                "channel": "test_channel",
                "ts": "test_timestamp",
            }
        }
        slack_handler.slack.handle_event(app_mention_event)

        mock_slack_methods_instance.handle_event.assert_called_with(app_mention_event)


if __name__ == "__main__":
    unittest.main()
