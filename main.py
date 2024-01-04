import os
import sys
import logging
import json
from dotenv import load_dotenv
from srcs.openai_handler import OpenAIHandler
from srcs.slack_handler import SlackHandler
from slack_bolt import App
from slack_sdk import WebClient
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv("config/.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DALLE_MODEL = os.getenv("DALLE_MODEL")
CHATGPT_MODEL = os.getenv("CHATGPT_MODEL")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN_TEST")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN_TEST")
SIGNING_SECRET = os.getenv("SIGNING_SECRET_TEST")

# Initialize logging
logging.basicConfig(level=logging.INFO)

allowed_users = {}


def load_allowed_users():
    """Load allowed users from a JSON file."""
    global allowed_users
    try:
        with open("./config/allowed-slack-ids.json", "r") as file:
            allowed_users = json.load(file)
            logging.info("Allowed users:%s" % allowed_users)
    except FileNotFoundError:
        logging.error("Allowed users file not found.")
    except json.JSONDecodeError:
        logging.error("Error decoding allowed users file.")


# Start the Slack app
if __name__ == "__main__":
    load_allowed_users()
    Slack_Handler = SlackHandler(
        allowed_users,
        SLACK_BOT_TOKEN,
        SLACK_APP_TOKEN,
        SIGNING_SECRET,
        OPENAI_API_KEY,
        DALLE_MODEL,
        CHATGPT_MODEL,
    )
    SocketModeHandler(Slack_Handler.app, Slack_Handler.SLACK_APP_TOKEN).start()
