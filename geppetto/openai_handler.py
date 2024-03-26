from io import BytesIO
import json
from openai import OpenAI
from PIL import Image
from urllib.request import urlopen
import logging

from .exceptions import InvalidThreadFormatError
from .llm_api_handler import LLMHandler
from dotenv import load_dotenv
from typing import List, Dict
import os

load_dotenv(os.path.join("config", ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DALLE_MODEL = os.getenv("DALLE_MODEL")
CHATGPT_MODEL = os.getenv("CHATGPT_MODEL")

OPENAI_IMG_FUNCTION = "generate_image"
ROLE_FIELD = "role"


class OpenAIHandler(LLMHandler):

    def __init__(
        self,
        personality,
    ):
        super().__init__(
            'OpenAI',
            CHATGPT_MODEL,
            OpenAI(api_key=OPENAI_API_KEY)
        )
        self.dalle_model = DALLE_MODEL
        self.personality = personality
        self.system_role = "system"
        self.assistant_role = "assistant"
        self.user_role = "user"

    @staticmethod
    def download_image(url):
        img = Image.open(urlopen(url=url))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    @staticmethod
    def get_functionalities():
        return json.dumps(
            [
                "Generate an image from text",
                "Get app functionalities",
            ]
        )

    def generate_image(self, prompt, size="1024x1024"):
        logging.info("Generating image: %s with size: %s" % (prompt, size))
        try:
            response_url = self.client.images.generate(
                model=self.dalle_model,
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )
            return self.download_image(response_url.data[0].url)
        except Exception as e:
            logging.error(f"Error generating image: {e}")

    def llm_generate_content(self, user_prompt, status_callback=None, *status_callback_args):
        logging.info("Sending msg to chatgpt: %s" % user_prompt)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": OPENAI_IMG_FUNCTION,
                    "description": "Generate an image from text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "size": {
                                "type": "string",
                                "enum": [
                                    "1024x1024",
                                    "1024x1792",
                                    "1792x1024",
                                ],
                            },
                        },
                        "required": ["prompt"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_functionalities",
                    "description": "Get app functionalities",
                },
            },
        ]
        # Initial conversation message
        messages = [
            {
                "role": self.system_role,
                "content": self.personality,
            },
            *user_prompt,
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        # Handle the tool calls
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            available_functions = {
                OPENAI_IMG_FUNCTION: self.generate_image,
                "get_functionalities": self.get_functionalities,
            }
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function = available_functions[function_name]
            if function_name == OPENAI_IMG_FUNCTION and status_callback:
                status_callback(*status_callback_args, ":geppetto: I'm preparing the image, please be patient "
                                         ":lower_left_paintbrush: ...")
            response = function(**function_args)
            return response
        else:
            return response.choices[0].message.content

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
        return prompt
