import json
import logging
import os


def load_bot_default_responses():
    """Load bot default responses from a JSON file."""
    try:
        with open(os.path.join("config", "default_responses.json"), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("default responses file not found.")
    except json.JSONDecodeError:
        logging.error("Error decoding default responses file.")
    return {}
