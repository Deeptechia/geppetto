import os
import sys
import unittest
from unittest.mock import Mock, patch

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from geppetto.exceptions import InvalidThreadFormatError
from geppetto.gemini_handler import GeminiHandler

def OF(**kw):
    class OF:
        pass
    instance = OF()
    for k, v in kw.items():
        setattr(instance, k, v)
    return instance

class TestGemini(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch("geppetto.gemini_handler.genai")
        cls.mock_genai = cls.patcher.start()
        cls.gemini_handler = GeminiHandler(personality="Your AI personality")

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def test_personality(self):
        self.assertEqual(self.gemini_handler.personality, "Your AI personality")

    @patch("geppetto.gemini_handler.convert_gemini_to_slack")
    def test_llm_generate_content(self, mock_to_markdown):
        user_prompt = [
        {"role": "user", "parts": ["Hello"]},
        {"role": "user", "parts": ["How are you?"]}
        ]
        mock_response = Mock()
        mock_response.text = "Mocked Gemini response"
        self.gemini_handler.client.generate_content.return_value = mock_response
        mock_to_markdown.return_value = Mock(data="Mocked Markdown data")

        response = self.gemini_handler.llm_generate_content(user_prompt)

        self.assertEqual(response.data, "Mocked Markdown data")
        mock_to_markdown.assert_called_once_with("Mocked Gemini response")

    def test_get_prompt_from_thread(self):
        thread = [
            {"role": "slack_user", "content": "Message 1"},
            {"role": "geppetto", "content": "Message 2"}
        ]
    
        ROLE_FIELD = "role"
        MSG_FIELD = "parts"

        prompt = self.gemini_handler.get_prompt_from_thread(
            thread, assistant_tag="geppetto", user_tag="slack_user"
        )
    
        self.assertIsInstance(prompt, list)
    
        for msg in prompt:
            self.assertIsInstance(msg, dict)
            self.assertIn(ROLE_FIELD, msg)
            self.assertIn(MSG_FIELD, msg)
            self.assertIsInstance(msg[MSG_FIELD], list)
            self.assertTrue(msg[MSG_FIELD])

        with self.assertRaises(InvalidThreadFormatError):
            incomplete_thread = [{"role": "geppetto"}]
            self.gemini_handler.get_prompt_from_thread(
                incomplete_thread, assistant_tag="geppetto", user_tag="slack_user"
            )

    def test_llm_generate_content_user_repetition(self):
        user_prompt = [
            {"role": "user", "parts": ["Hello"]},
            {"role": "user", "parts": ["How are you?"]},
            {"role": "geppetto", "parts": ["I'm fine."]}
        ]

        with patch.object(self.gemini_handler.client, "generate_content") as mock_generate_content:
            mock_response = Mock()
            mock_response.text = "Mocked Gemini response"
            mock_generate_content.return_value = mock_response

            self.gemini_handler.llm_generate_content(user_prompt)

            mock_generate_content.assert_called_once_with(
                [{"role": "user", "parts": ["Hello", "How are you?"]}, {"role": "geppetto", "parts": ["I'm fine."]}]
            )

if __name__ == "__main__":
    unittest.main()