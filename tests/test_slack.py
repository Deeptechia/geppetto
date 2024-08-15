import os
import sys
import unittest

from unittest.mock import patch, ANY
from geppetto.llm_controller import LLMController
from tests import TestBase
from tests.test_open_ai import TEST_PERSONALITY
from geppetto.slack_handler import SlackHandler
from geppetto.utils import load_json

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

MOCK_GENERIC_LLM_RESPONSE = "Mock text response"
MOCK_GENERIC_LLM_RESPONSE_B = MOCK_GENERIC_LLM_RESPONSE + " B"
MOCK_GENERIC_LLM_RESPONSE_C = MOCK_GENERIC_LLM_RESPONSE + " C"
MOCK_ANY_RESPONSE = "a response"

CHANNEL_ID = "test_channel"
THREAD_ID = "test_thread_id"


class TestSlack(TestBase):
    def setUp(self):
        super(TestBase, self).setUp()
        self.patcherA = patch("tests.test_controller.HandlerMockA")
        self.patcherB = patch("tests.test_controller.HandlerMockB")
        self.patcherC = patch("tests.test_controller.HandlerMockC")
        self.MockLLMHandlerA = self.patcherA.start()
        self.MockLLMHandlerB = self.patcherB.start()
        self.MockLLMHandlerC = self.patcherC.start()
        self.patcher1 = patch("geppetto.slack_handler.App")
        self.MockApp = self.patcher1.start()

        SLACK_BOT_TOKEN = "slack_bot_token"
        SIGNING_SECRET = "signing_secret"
        BOT_DEFAULT_RESPONSES = load_json("default_responses.json")

        self.slack_handler = SlackHandler({"test_user_id": "Test User"},
                                          BOT_DEFAULT_RESPONSES,
                                          SLACK_BOT_TOKEN,
                                          SIGNING_SECRET,
                                          initialized_test_llm_controller(self.MockLLMHandlerA,
                                                                          self.MockLLMHandlerB,
                                                                          self.MockLLMHandlerC))

    def tearDown(self):
        self.patcher1.stop()
        self.patcherA.stop()
        self.patcherB.stop()
        self.patcherC.stop()

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
            mrkdwn=True)

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
            text=":thought_balloon:",
            thread_ts="1",
            mrkdwn=True
        )

    def test_handle_message(self):
        self.MockLLMHandlerA().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE

        message = "Test message"

        self.slack_handler.handle_message(message, CHANNEL_ID, THREAD_ID)

        self.assertIn(THREAD_ID, self.slack_handler.thread_messages)
        self.assertIn(
            {"role": "slack_user", "content": message},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )
        self.assertIn(
            {"role": "geppetto", "content": MOCK_GENERIC_LLM_RESPONSE},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )

        self.MockApp().client.chat_postMessage.assert_called_with(
            channel=CHANNEL_ID,
            text=":thought_balloon:",
            thread_ts=THREAD_ID,
            mrkdwn=True
        )
        self.MockApp().client.chat_update.assert_called_with(
            channel=CHANNEL_ID,
            text=MOCK_GENERIC_LLM_RESPONSE,
            thread_ts=THREAD_ID,
            ts=ANY,
        )

    def test_handle_message_switch_simple(self):

        # Case A: DEFAULT LLM A
        self.MockLLMHandlerA().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE
        message_a = "Test message"
        self.slack_handler.handle_message(message_a, CHANNEL_ID, THREAD_ID)
        self.assertIn(
            {"role": "slack_user", "content": message_a},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )
        self.assertIn(
            {"role": "geppetto", "content": MOCK_GENERIC_LLM_RESPONSE},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )

        # Case B: LLM B
        self.MockLLMHandlerB().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE_B
        message_b = "Test message llm_llmb"
        self.slack_handler.handle_message(message_b, CHANNEL_ID, THREAD_ID)
        self.assertIn(
            {"role": "slack_user", "content": message_b},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )
        self.assertIn(
            {"role": "geppetto", "content": MOCK_GENERIC_LLM_RESPONSE_B},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )

    def test_handle_message_switch_same_thread_continue_non_default(self):
        # Case C: LLM C
        self.MockLLMHandlerC().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE_C
        message_c = "Test message llm_llmc"
        self.slack_handler.handle_message(message_c, CHANNEL_ID, THREAD_ID)
        self.assertIn(
            {"role": "slack_user", "content": message_c},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )
        self.assertIn(
            {"role": "geppetto", "content": MOCK_GENERIC_LLM_RESPONSE_C},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )

        # DON'T switch to DEFAULT in started NON DEFAULT conversations
        self.MockLLMHandlerA().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE
        non_labeled_msg = "Second message"
        self.slack_handler.handle_message(
            non_labeled_msg, CHANNEL_ID, THREAD_ID)
        self.assertIn(
            {"role": "slack_user", "content": non_labeled_msg},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )
        self.assertIn(
            {"role": "geppetto", "content": MOCK_GENERIC_LLM_RESPONSE_C},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )

    def test_handle_message_switch_same_thread_reset_on_switch(self):
        # Case A: LLM A
        self.MockLLMHandlerA().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE
        message_a = "Test message llm_llma"
        self.slack_handler.handle_message(message_a, CHANNEL_ID, THREAD_ID)
        user_msg_a = {"role": "slack_user", "content": message_a}
        geppetto_msg_a = {
            "role": "geppetto",
            "content": MOCK_GENERIC_LLM_RESPONSE}
        self.assertEqual(
            self.slack_handler.thread_messages[THREAD_ID]["msgs"].count(user_msg_a), 1)

        self.assertEqual(
            self.slack_handler.thread_messages[THREAD_ID]["msgs"].count(geppetto_msg_a), 1)

        # Continue conversation with LLM A
        for _ in range(3):
            self.slack_handler.handle_message(message_a, CHANNEL_ID, THREAD_ID)
        self.assertEqual(
            self.slack_handler.thread_messages[THREAD_ID]["msgs"].count(user_msg_a), 4)
        self.assertEqual(
            self.slack_handler.thread_messages[THREAD_ID]["msgs"].count(geppetto_msg_a), 4)

        # SWITCH TO LLM C in an ongoing conversation
        self.MockLLMHandlerC().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE_C
        message_c = "Test message llm_llmc"
        user_msg_c = {"role": "slack_user", "content": message_c}
        geppetto_msg_c = {"role": "geppetto", "content": MOCK_GENERIC_LLM_RESPONSE_C}
        self.slack_handler.handle_message(message_c, CHANNEL_ID, THREAD_ID)

        # the first user message is kept but the rest is dumped
        self.assertEqual(self.slack_handler.thread_messages[THREAD_ID]["msgs"].count(user_msg_a), 1)
        
        # the previous llm responses are dumped
        self.assertEqual(self.slack_handler.thread_messages[THREAD_ID]["msgs"].count(geppetto_msg_a), 0)

        # the message that triggered the switch is kept to give context
        self.assertEqual(self.slack_handler.thread_messages[THREAD_ID]["msgs"].count(user_msg_c), 1)

        # the answer of the new selected llm
        self.assertEqual(self.slack_handler.thread_messages[THREAD_ID]["msgs"].count(geppetto_msg_c), 1)

    def test_handle_message_switch_different_thread(self):
        thread_id_i = "test_thread_id_i"
        thread_id_ii = "test_thread_id_ii"
        non_labeled_msg = "Second message"
        user_msg_generic = {"role": "slack_user", "content": non_labeled_msg}

        # --- LLM B on thread I ---
        self.MockLLMHandlerB().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE
        message_b = "Test message llm_llmb"
        self.slack_handler.handle_message(message_b, CHANNEL_ID, thread_id_i)
        user_msg_b = {"role": "slack_user", "content": message_b}
        geppetto_msg_b = {
            "role": "geppetto",
            "content": MOCK_GENERIC_LLM_RESPONSE}

        # --- LLM C on thread II ---
        self.MockLLMHandlerC().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE
        message_c = "Test message llm_llmc"
        self.slack_handler.handle_message(message_c, CHANNEL_ID, thread_id_ii)
        user_msg_c = {"role": "slack_user", "content": message_c}
        geppetto_msg_c = {
            "role": "geppetto",
            "content": MOCK_GENERIC_LLM_RESPONSE}

        # --- Return to LLM B on thread I ---
        # check
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_i]["msgs"].count(user_msg_b), 1)
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_i]["msgs"].count(
                geppetto_msg_b),
            1)
        # Continue conversation with LLM B without label
        for _ in range(3):
            self.slack_handler.handle_message(
                non_labeled_msg, CHANNEL_ID, thread_id_i)

        # --- Return to LLM C on thread II ---
        # check
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_ii]["msgs"].count(user_msg_c), 1)
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_ii]["msgs"].count(
                geppetto_msg_c),
            1)
        # Continue conversation with LLM C without label
        for _ in range(9):
            self.slack_handler.handle_message(
                non_labeled_msg, CHANNEL_ID, thread_id_ii)

        # --- Return to LLM B on thread I ---
        # check
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_i]["msgs"].count(user_msg_b), 1)
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_i]["msgs"].count(
                user_msg_generic),
            3)
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_i]["msgs"].count(
                geppetto_msg_b),
            4)

        # --- Return to LLM C on thread II ---
        # check
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_ii]["msgs"].count(user_msg_c), 1)
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_ii]["msgs"].count(
                user_msg_generic),
            9)
        self.assertEqual(
            self.slack_handler.thread_messages[thread_id_ii]["msgs"].count(
                geppetto_msg_c),
            10)

    def test_handle_image(self):
        message = "Test message"

        self.MockLLMHandlerA().llm_generate_content.return_value = MOCK_GENERIC_LLM_RESPONSE
        self.slack_handler.handle_message(message, CHANNEL_ID, THREAD_ID)
        self.MockApp().client.chat_update.assert_called_with(
            channel=CHANNEL_ID,
            text=MOCK_GENERIC_LLM_RESPONSE,
            thread_ts=THREAD_ID,
            ts=ANY,
        )

        mock_open_ai_byte_response = b"Mock byte response"
        self.MockLLMHandlerA().llm_generate_content.return_value = mock_open_ai_byte_response
        self.slack_handler.handle_message(message, CHANNEL_ID, THREAD_ID)
        self.MockApp().client.files_upload_v2.assert_called_with(
            channel=CHANNEL_ID,
            thread_ts=THREAD_ID,
            content=b"Mock byte response",
            title="Image",
        )

    def test_select_llm_from_msg(self):
        message_a = "llm_llma Test message"
        message_b = "Test llm_llmb message"
        message_c = "Test message llm_llmc?"
        message_default_empty = "Test message"
        message_default_many = "llm_llmc Test llm_llmb message llm_llma"
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

    def test_handle_command(self):
        mock_list_llms_response = ["Here are the available AI models!"]
        assistants = self.slack_handler.llm_ctrl.list_llms()

        for assistant in assistants:
            mock_list_llms_response.append(
                f"* {assistant} -> llm_{assistant.lower()}")

        reminder = "Example: Using 'llm_gemini' at the start of your message to Geppetto switches to gemini model."
        mock_list_llms_response.append(reminder)
        mock_list_llms_response = '\n'.join(mock_list_llms_response)

        self.MockLLMHandlerA().llm_generate_content.return_value = mock_list_llms_response
        # message with blank spaces
        message = "   llms   "
        self.slack_handler.handle_message(message, CHANNEL_ID, THREAD_ID)

        self.assertIn(
            {"role": "slack_user", "content": message.strip()},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )
        self.assertIn(
            {"role": "geppetto", "content": mock_list_llms_response},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )
        self.MockApp().client.chat_update.assert_called_with(
            channel=CHANNEL_ID,
            text=mock_list_llms_response,
            thread_ts=THREAD_ID,
            ts=ANY,
        )

    def test_command_not_written_properly(self):
        mock_list_llms_response = ["Here are the available AI models!"]
        assistants = self.slack_handler.llm_ctrl.list_llms()

        for assistant in assistants:
            mock_list_llms_response.append(
                f"* {assistant} -> llm_{assistant.lower()}")

        reminder = "Example: Using 'llm_gemini' at the start of your message to Geppetto switches to gemini model."
        mock_list_llms_response.append(reminder)
        mock_list_llms_response = '\n'.join(mock_list_llms_response)

        self.MockLLMHandlerA().llm_generate_content.return_value = MOCK_ANY_RESPONSE

        message = "llms is the command"
        self.slack_handler.handle_message(message, CHANNEL_ID, THREAD_ID)

        self.assertIn(
            {"role": "slack_user", "content": message},
            self.slack_handler.thread_messages[THREAD_ID]["msgs"],
        )
        self.assertNotIn({"role": "geppetto", "content": mock_list_llms_response},
                         self.slack_handler.thread_messages[THREAD_ID]["msgs"],)
        self.MockApp().client.chat_update.assert_called_with(
            channel=CHANNEL_ID,
            text=MOCK_ANY_RESPONSE,
            thread_ts=THREAD_ID,
            ts=ANY,
        )


def initialized_test_llm_controller(mocked_handler_a,
                                    mocked_handler_b,
                                    mocked_handler_c):
    controller = LLMController([
        {"name": "LlmA",
         "handler": mocked_handler_a,
         "handler_args": {"personality": TEST_PERSONALITY}},
        {"name": "LLMb",
         "handler": mocked_handler_b,
         "handler_args": {"personality": TEST_PERSONALITY}},
        {"name": "LLMC",
         "handler": mocked_handler_c,
         "handler_args": {"personality": TEST_PERSONALITY}}])
    controller.init_controller()
    return controller


if __name__ == "__main__":
    unittest.main()
