import json
import logging
import os

def load_allowed_users():
    """Load allowed users from a JSON file."""
    try:
        with open(os.path.join("config", "allowed-slack-ids.json"), "r") as file:
            allowed_users = json.load(file)
            logging.info("Allowed users:%s" % allowed_users)
            return allowed_users
    except FileNotFoundError:
        logging.error("Allowed users file not found.")
    except json.JSONDecodeError:
        logging.error("Error decoding allowed users file.")
    return {}

def load_bot_responses():
    """Load bot default responses from a JSON file."""
    try:
        with open(os.path.join("config", "default_responses.json"), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("default responses file not found.")
    except json.JSONDecodeError:
        logging.error("Error decoding default responses file.")
    return {}
