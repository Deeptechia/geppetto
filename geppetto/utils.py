import json
import logging
import os

def load_json(json_name):
    """Load information from a JSON file."""
    try:
        with open(os.path.join("config", "%s.json" %json_name), "r") as file:
            json_file = json.load(file)
            logging.info("%s:%s" % (json_name, json_file))
            return json_file
    except FileNotFoundError:
        logging.error("%s file not found." % json_name)
    except json.JSONDecodeError:
        logging.error("Error decoding %s file." % json_name)
    return {}