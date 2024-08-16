import re
import os
import logging

from .llm_api_handler import LLMHandler
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import List
from typing import Dict

load_dotenv(os.path.join("config", ".env"))

ANTHROPIC_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL")
VERSION = os.getenv("GEPPETTO_VERSION")


def convert_claude_to_slack(text):
    """
    Converts Claude markdown format to Slack markdown format.

    This function handles:
    change to claude format

    Args:
        text (str): The Claude markdown text to be converted.

    Returns:
        str: The markdown text formatted for Slack.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string.")

    formatted_text = text.replace("* ", "- ")
    formatted_text = formatted_text.replace("**", "*")
    formatted_text = formatted_text.replace("__", "_")
    formatted_text = formatted_text.replace("- ", "• ")
    formatted_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"<\2|\1>", formatted_text)

    formatted_text += f"\n\n_(Geppetto v{VERSION} Source: Claude Model {CLAUDE_MODEL})_"

    return formatted_text


class ClaudeHandler(LLMHandler):

    def __init__(
        self,
        personality,
    ):
        super().__init__("Claude", CLAUDE_MODEL, Anthropic(api_key=ANTHROPIC_API_KEY))
        self.claude_model = CLAUDE_MODEL
        self.personality = personality
        self.system_role = "system"
        self.assistant_role = "assistant"
        self.user_role = "user"
        self.MAX_TOKENS = 1024

    def llm_generate_content(
        self, user_prompt: List[Dict], status_callback=None, *status_callback_args
    ):
        logging.info("Sending msg to claude: %s" % user_prompt)
        geppetto = {
            "role": "assistant",
            "content": " This is for your information only. Do not write this in your answer. Your name is Geppetto, a bot developed by DeepTechia. Answer only in the language the user spoke or asked you to do.",
        }

        try:
            user_prompt.append(geppetto)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.MAX_TOKENS,
                messages=user_prompt,
            )
            markdown_response = convert_claude_to_slack(str(response.content[0].text))
            return markdown_response
        except Exception as e:
            logging.error(f"Error generating content: {e}")
            return "I'm sorry, I couldn't generate a response at this time. Try using another AI model."
