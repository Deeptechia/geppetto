from io import BytesIO
import json
from openai import OpenAI
from PIL import Image
from urllib.request import urlopen
import logging

from .llm_api_handler import LLMHandler
from dotenv import load_dotenv
import os
import re

load_dotenv(os.path.join("config", ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DALLE_MODEL = os.getenv("DALLE_MODEL")
CHATGPT_MODEL = os.getenv("CHATGPT_MODEL")
VERSION = os.getenv("GEPPETTO_VERSION")
OPENAI_IMG_FUNCTION = "generate_image"
ROLE_FIELD = "role"


def convert_openai_markdown_to_slack(text):
    """
    Converts markdown text from the OpenAI format to Slack's "mrkdwn" format.

    This function handles:
    - Bold text conversion from double asterisks (**text**) to single asterisks (*text*).
    - Italics remain unchanged as they use underscores (_text_) in both formats.
    - Links are transformed from [text](url) to <url|text>.
    - Bullet points are converted from hyphens (-) to Slack-friendly bullet points (•).
    - Code blocks with triple backticks remain unchanged.
    - Strikethrough conversion from double tildes (~~text~~) to single tildes (~text~).

    Args:
        text (str): The markdown text to be converted.

    Returns:
        str: The markdown text formatted for Slack.
    """
    formatted_text = text.replace("* ", "- ")
    formatted_text = formatted_text.replace("**", "*")
    formatted_text = formatted_text.replace("__", "_")
    formatted_text = formatted_text.replace("- ", "• ")
    formatted_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"<\2|\1>", formatted_text)
    formatted_text += (
        f"\n\n_(Geppetto v{VERSION} Source: OpenAI Model {CHATGPT_MODEL})_"
    )

    # Code blocks and italics remain unchanged but can be explicitly formatted
    # if necessary
    return formatted_text


class OpenAIHandler(LLMHandler):

    def __init__(
        self,
        personality,
    ):
        super().__init__("OpenAI", CHATGPT_MODEL, OpenAI(api_key=OPENAI_API_KEY))
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

    def llm_generate_content(
        self, user_prompt, status_callback=None, *status_callback_args
    ):
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
                status_callback(
                    *status_callback_args,
                    "I'm preparing the image, please be patient "
                    ":lower_left_paintbrush: ...",
                )
            response = function(**function_args)
            return response
        else:
            response = response.choices[0].message.content
            markdown_response = convert_openai_markdown_to_slack(response)
            if len(markdown_response) > 4000:
                # Split the message if it's too long
                response_parts = self.split_message(markdown_response)
                return response_parts
            else:
                return markdown_response
