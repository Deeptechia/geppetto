import logging
import os
import sys
import unittest

from geppetto.claude_handler import ClaudeHandler
from unittest.mock import Mock, patch
from tests import TestBase

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

TEST_PERSONALITY = "Your AI assistant"


class TestClaude(TestBase):
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch("geppetto.claude_handler.Anthropic")
        cls.mock_claude = cls.patcher.start()
        cls.claude_handler = ClaudeHandler(personality=TEST_PERSONALITY)
        logging.getLogger().setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def test_personality(self):
        self.assertEqual(self.claude_handler.personality, TEST_PERSONALITY)

    def test_llm_generate_content(self):
        user_prompt = [{"role": "user", "content": "Hello, Claude!"}]

        mock_response = Mock()
        mock_response.content = [Mock(text="Mocked Claude response")]
        self.claude_handler.client.messages.create = Mock(return_value=mock_response)

        response = self.claude_handler.llm_generate_content(user_prompt).split('\n\n_(Geppetto', 1)[0].strip()
        self.assertEqual(response, "Mocked Claude response")

    def test_failed_to_llm_generate_content(self):
        failed_response = "I'm sorry, I couldn't generate a response at this time. Try using another AI model."

        mock_claude = Mock()
        mock_claude.content = [Mock(text=failed_response)]
        mock_claude.return_value = mock_claude
        self.claude_handler.client.messages.create = mock_claude
        
        response = self.claude_handler.llm_generate_content("")
        self.assertEqual(response, failed_response)


if __name__ == "__main__":
    unittest.main()
