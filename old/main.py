import os
import logging
from dotenv import load_dotenv

from .llm_controller import LLMController
from .slack_handler import SlackHandler
from .openai_handler import OpenAIHandler
from .gemini_handler import GeminiHandler
from .claude_handler import ClaudeHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from .utils import load_json

load_dotenv(os.path.join("config", ".env"))


SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN_TEST")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN_TEST")
SIGNING_SECRET = os.getenv("SIGNING_SECRET_TEST")

DEFAULT_RESPONSES = load_json("default_responses.json")

# Initialize logging
# TODO: log to a file
logging.basicConfig(level=logging.INFO)


def initialized_llm_controller():
    controller = LLMController(
        [
            {
                "name": "OpenAI",
                "handler": OpenAIHandler,
                "handler_args": {
                    "personality": DEFAULT_RESPONSES["features"]["personality"]
                },
            },
            {
                "name": "Gemini",
                "handler": GeminiHandler,
                "handler_args": {
                    "personality": DEFAULT_RESPONSES["features"]["personality"]
                },
            },
            {
                "name": "Claude",
                "handler": ClaudeHandler,
                "handler_args": {
                    "personality": DEFAULT_RESPONSES["features"]["personality"]
                },
            },
        ]
    )
    controller.init_controller()
    return controller


def main():
    Slack_Handler = SlackHandler(
        load_json("allowed-slack-ids.json"),
        DEFAULT_RESPONSES,
        SLACK_BOT_TOKEN,
        SIGNING_SECRET,
        initialized_llm_controller(),
    )
    SocketModeHandler(Slack_Handler.app, SLACK_APP_TOKEN).start()


if __name__ == "__main__":
    main()
