import os
import logging
import json
from dotenv import load_dotenv
from src.slack_handler import SlackHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv(os.path.join("config", ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DALLE_MODEL = os.getenv("DALLE_MODEL")
CHATGPT_MODEL = os.getenv("CHATGPT_MODEL")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN_TEST")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN_TEST")
SIGNING_SECRET = os.getenv("SIGNING_SECRET_TEST")

# Initialize logging
# TODO: log to a file
logging.basicConfig(level=logging.INFO)

allowed_users = {}


def load_allowed_users():
    """Load allowed users from a JSON file."""
    global allowed_users
    try:
        with open(os.path.join("config", "allowed-slack-ids.json"), "r") as file:
            allowed_users = json.load(file)
            logging.info("Allowed users:%s" % allowed_users)
    except FileNotFoundError:
        logging.error("Allowed users file not found.")
    except json.JSONDecodeError:
        logging.error("Error decoding allowed users file.")


def load_bot_default_responses():
    """Load bot default responses from a JSON file."""
    global bot_default_responses
    try:
        with open(os.path.join("config", "default_responses.json"), "r") as file:
            bot_default_responses = json.load(file)
    except FileNotFoundError:
        logging.error("default responses file not found.")
    except json.JSONDecodeError:
        logging.error("Error decoding default responses file.")


def main():
    load_allowed_users()
    load_bot_default_responses()
    Slack_Handler = SlackHandler(
        allowed_users,
        bot_default_responses,
        SLACK_BOT_TOKEN,
        SIGNING_SECRET,
        OPENAI_API_KEY,
        DALLE_MODEL,
        CHATGPT_MODEL,
    )

    SocketModeHandler(Slack_Handler.app, SLACK_APP_TOKEN).start()


# Start the Slack app
if __name__ == "__main__":
    main()
