import json
import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

import openai


script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from src.openai_handler import OpenAIHandler


class MockOpenAIChatCompletionResponse:
    def __init__(self):
        self.message = {"content": "Mocked ChatGPT Response", "tool_calls": []}


class TestOpenAI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch("src.openai_handler.OpenAI")
        cls.mock_openai = cls.patcher.start()

        # Mocking the ChatCompletion response as a dictionary

        object_with_attributes_choice = MockOpenAIChatCompletionResponse()


        cls.openai_handler = OpenAIHandler(
            "openai_api_key",
            "dall-e-3",
            "gpt-4",
            {"features": {"personality": "_"}},
        )

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def test_send_text_message(self):
        user_prompt = [{"role": "user", "content": "Hello"}]
        response = self.openai_handler.send_message(user_prompt)
        self.assertEqual(response, "Mocked ChatGPT Response")

    def test_send_image_message(self):
        # Mock tool_call for image generation
        mock_tool_call = Mock()
        mock_tool_call.function.name = "generate_image"
        mock_tool_call.function.arguments = json.dumps(
            {"prompt": "Generate an image of a mountain", "size": "1024x1024"}
        )

        mock_chat_completion_response = Mock()
        mock_chat_completion_response.choices = [
            {"message": {"content": "", "tool_calls": [mock_tool_call]}}
        ]
        self.mock_openai.return_value.chat.completions.create.return_value = (
            mock_chat_completion_response
        )

        user_prompt = [{"role": "user", "content": "Generate an image of a mountain"}]
        response = self.openai_handler.send_message(user_prompt)

        # Assuming download_image returns bytes
        self.assertIsInstance(response, bytes)


if __name__ == "__main__":
    unittest.main()
