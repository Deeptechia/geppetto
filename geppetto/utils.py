import json
import logging
import os
from typing import List


def load_json(file_name):
    """Load information from a JSON file."""
    try:
        with open(os.path.join("config", file_name), "r") as file:
            json_file = json.load(file)
            logging.info("%s:%s" % (file_name, json_file))
            return json_file
    except FileNotFoundError:
        logging.error("%s file not found." % file_name)
    except json.JSONDecodeError:
        logging.error("Error decoding %s file." % file_name)
    return {}


def is_image_data(data):
    return isinstance(data, bytes)


def lower_string_list(list_to_process: List[str]):
    return [element.lower() for element in list_to_process]
