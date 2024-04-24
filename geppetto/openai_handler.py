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
import re

load_dotenv(os.path.join("config", ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DALLE_MODEL = os.getenv("DALLE_MODEL")
CHATGPT_MODEL = os.getenv("CHATGPT_MODEL")
GEPPETTO_VERSION = os.getenv("GEPPETTO_VERSION", "0.2.2")

OPENAI_IMG_FUNCTION = "generate_image"
ROLE_FIELD = "role"

def add_footnote(text):
    if type(text) is str:
        text=text.encode() 
    #print(text)
    footnote = f"\n\n_(Geppetto v{GEPPETTO_VERSION} Source: OpenAI Model {CHATGPT_MODEL})_"
    text = text + footnote.encode() 
    return text

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
    #formatted_text += f"\n\n_(Geppetto v0.2.1 Source: OpenAI Model {CHATGPT_MODEL})_"
    
    # Code blocks and italics remain unchanged but can be explicitly formatted if necessary
    return formatted_text


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
            # Extract the function name to identify which function to call.
            function_name = tool_call.function.name
            # Deserialize the JSON arguments needed for the function call.
            function_args = json.loads(tool_call.function.arguments)
            # Retrieve the function to call from the available functions dictionary using the function name.
            function = available_functions[function_name]
            # Special case: if the function is related to image generation and a status callback is provided,
            # notify the user that the image is being prepared.
            if function_name == OPENAI_IMG_FUNCTION and status_callback:
                status_callback(*status_callback_args, "I'm preparing the image, please be patient "
                                         ":lower_left_paintbrush: ...")
            # Call the function with its appropriate arguments.
            response = function(**function_args)
  
        else:
            # If there are no tool calls, process the content response from the first choice.
            response = response.choices[0].message.content
            # Convert the response from markdown to a specific format (e.g., for Slack).
            response = convert_openai_markdown_to_slack(response)

        response = add_footnote( response )
        return response

        
