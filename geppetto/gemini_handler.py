from io import BytesIO
import json
from PIL import Image
from urllib.request import urlopen
import logging

from .exceptions import InvalidThreadFormatError
from .llm_api_handler import LLMHandler
from dotenv import load_dotenv
from typing import List, Dict
import os

import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown

load_dotenv(os.path.join("config", ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_IMG_FUNCTION = "generate_image"
GEMINI_MODEL=os.getenv("GEMINI_MODEL")
ROLE_FIELD = "role"
MSG_FIELD = "parts"
MSG_INPUT_FIELD = "content"

class GeminiHandler(LLMHandler):

    def __init__(
        self,
        personality,
    ):
        super().__init__(
            'Gemini',
            GEMINI_MODEL,
            genai.GenerativeModel(GEMINI_MODEL),
        )
        self.personality = personality
        self.system_role = "system"
        self.assistant_role = "model"
        self.user_role = "user"
        genai.configure(api_key=GOOGLE_API_KEY)

    @staticmethod
    def download_image(url):
        pass

    @staticmethod
    def get_functionalities():
        pass

    def generate_image(self, prompt, size="1024x1024"): 
        pass

    def llm_generate_content(self, user_prompt, status_callback=None, *status_callback_args):
        logging.info("Sending msg to gemini: %s" % user_prompt)
        response= self.client.generate_content(user_prompt)
        return str(response.text)

    def get_prompt_from_thread(self, thread: List[Dict], assistant_tag: str, user_tag: str):
        prompt = []
        for msg in thread:
            formatted_msg = dict(msg)
            if ROLE_FIELD in formatted_msg:
                formatted_msg[ROLE_FIELD] = formatted_msg[ROLE_FIELD].replace(assistant_tag, self.assistant_role)
                formatted_msg[ROLE_FIELD] = formatted_msg[ROLE_FIELD].replace(user_tag, self.user_role)
                prompt.append(formatted_msg)
            else:
                raise InvalidThreadFormatError("The input thread doesn't have the field %s" % ROLE_FIELD)
            
            if MSG_INPUT_FIELD in formatted_msg:
                formatted_msg[MSG_FIELD] = [formatted_msg.pop(MSG_INPUT_FIELD)]
            else:
                raise InvalidThreadFormatError("The input thread doesn't have the field %s" % MSG_INPUT_FIELD)
        return prompt
