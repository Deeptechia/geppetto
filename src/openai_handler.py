import openai
from PIL import Image
from urllib.request import urlopen
import logging
import os


class OpenAIHandler:
    # TODO: use a global object for OpenAI instead of redeclaring the API key every time
    def __init__(self, openai_api_key, dalle_model, chatgpt_model):
        self.openai_api_key = openai_api_key
        self.dalle_model = dalle_model
        self.chatgpt_model = chatgpt_model

    def text_to_image_url(self, prompt, size="1024x1024"):
        try:
            openai.api_key = self.openai_api_key
            response_url = openai.images.generate(
                model=self.dalle_model,
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )
            return response_url.data[0].url
        except Exception as e:
            logging.error(f"Error generating image: {e}")
            return None

    def url_to_image(self, url):
        img = Image.open(urlopen(url=url))
        # TODO: return the image instead of saving it to a file
        return img.save(os.path.join("assets", "dall-e.png"))

    def generate_chatgpt_response(self, prompt):
        try:
            openai.api_key = self.openai_api_key
            response_from_chatgpt = (
                openai.chat.completions.create(
                    model=self.chatgpt_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
                .choices[0]
                .message.content
            )
            return response_from_chatgpt
        except Exception as e:
            logging.error(f"Error generating ChatGPT response: {e}")
            return None
