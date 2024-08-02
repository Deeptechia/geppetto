import os
import sys
import unittest
from unittest.mock import Mock, patch

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from geppetto.claude_handler import ClaudeHandler

TEST_PERSONALITY = "Your AI assistant"

def OF(**kw):
    class OF:
        pass

    instance = OF()
    for k, v in kw.items():
        setattr(instance, k, v)
    return instance


class TestClaude(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch("geppetto.claude_handler.Anthropic")
        cls.mock_claude = cls.patcher.start()
        cls.claude_handler = ClaudeHandler(personality=TEST_PERSONALITY)

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def test_personality(self):
        self.assertEqual(self.claude_handler.personality, TEST_PERSONALITY)


    def test_llm_generate_content(self):
        user_prompt = "Hello, Claude!"

 
        mock_response = Mock()
        mock_response.content = [Mock(text="Mocked Claude response")]
        self.claude_handler.client.messages.create = Mock(return_value=mock_response)

        response = self.claude_handler.llm_generate_content(user_prompt).split('\n\n_(Geppetto', 1)[0].strip()

        self.assertEqual(response, "Mocked Claude response")


if __name__ == "__main__":
    unittest.main()
