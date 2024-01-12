import os
import logging
from dotenv import load_dotenv
from slack_handler import SlackHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from utils.load_bot_responses import load_bot_responses
from utils.load_allowed_users import load_allowed_users

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


def main():
    Slack_Handler = SlackHandler(
        load_allowed_users(),
        load_bot_responses(),
        SLACK_BOT_TOKEN,
        SIGNING_SECRET,
        OPENAI_API_KEY,
        DALLE_MODEL,
        CHATGPT_MODEL,
    )
    SocketModeHandler(Slack_Handler.app, SLACK_APP_TOKEN).start()


if __name__ == "__main__":
    main()
