from io import BytesIO
import json
import openai
from PIL import Image
from urllib.request import urlopen
import logging
import os


class OpenAIHandler:
    def __init__(self, openai_api_key, dalle_model, chatgpt_model):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.dalle_model = dalle_model
        self.chatgpt_model = chatgpt_model

    def get_functionalities(self):
        # TODO: should get functionalities from config file maybe?
        return json.dumps(
            [
                "Generate an image from text",
                "Get app functionalities",
            ]
        )

    def download_image(self, url):
        img = Image.open(urlopen(url=url))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    def get_image(self, prompt, size="1024x1024"):
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
            return None

    def send_message(self, user_prompt):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "text_to_image_url",
                    "description": "Generate an image from text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "size": {"type": "string"},
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
                "role": "system",
                "content": "You are Geppetto, a general intelligence bot created by CoinFabrik.",  # TODO: get this from the config file
            },
            {"role": "user", "content": user_prompt},
        ]
        response = self.client.chat.completions.create(
            model=self.chatgpt_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        # Handle the tool calls
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            available_functions = {
                "text_to_image_url": self.get_image,
                "get_functionalities": self.get_functionalities,
            }
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function = available_functions[function_name]
            response = function(**function_args)
            return response
        else:
            return response.choices[0].message.content
