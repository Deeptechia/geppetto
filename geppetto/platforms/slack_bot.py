import logging
import json
import os
from typing import Dict, Optional

from geppetto.adapters.slack.adapter import SlackAdapter
from geppetto.core.multiplexer import LLMMultiplexer
from geppetto.utils import load_config


def load_allowed_users(users_path: Optional[str] = None) -> Dict[str, str]:
    """Load allowed users from file."""
    allowed_users = {}

    # Default to allowing all users if no file is specified
    if not users_path:
        allowed_users = {"*": "*"}  # Wildcard to allow all users

    # Try to load from file if it exists
    elif os.path.exists(users_path):
        try:
            with open(users_path, "r") as f:
                allowed_users = json.load(f)
        except Exception as e:
            logging.error(f"Error loading allowed users: {e}")
            allowed_users = {"*": "*"}  # Fallback to wildcard

    return allowed_users


async def run_slack_bot(
    config_path: Optional[str] = None,
    users_path: Optional[str] = None,
    llm_multiplexer: Optional[LLMMultiplexer] = None,
):
    """Initialize and run the Slack bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load configuration
    slack_config = load_config(config_path)
    allowed_users = load_allowed_users(users_path)

    try:
        # Initialize Slack adapter
        logging.info("Starting Slack bot...")
        slack_adapter = SlackAdapter(
            bot_token=slack_config["SLACK_BOT_TOKEN"],
            signing_secret=slack_config["SLACK_SIGNING_SECRET"],
            app_token=slack_config["APP_TOKEN"],
            allowed_users=allowed_users,
            llm_multiplexer=llm_multiplexer,
        )

        # Start the adapter
        slack_adapter.initialize()
        await slack_adapter.start()

        logging.info("Slack bot is running. Press Ctrl+C to stop.")

    except KeyboardInterrupt:
        logging.info("Stopping Slack bot...")
        slack_adapter.stop()
        logging.info("Slack bot stopped.")

    except Exception as e:
        logging.error(f"Error running Slack bot: {e}")
