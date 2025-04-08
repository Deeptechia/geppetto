import json
import logging
from typing import List, Optional, Dict, TypedDict, Union, Any
import functools
import openai
from openai import AsyncOpenAI

from geppetto.core.llm.base import InvalidRequestError, LLMError, LLMProvider
from geppetto.core.types.conversation import Conversation
from geppetto.core.types.images import ImageContent
from geppetto.core.types.message import Message


class OpenAIMessage(TypedDict):
    role: str
    content: Union[str, None]
    tool_calls: Optional[List[Dict[str, Any]]]


def handle_openai_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except openai.RateLimitError as e:
            raise LLMError(f"Rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            raise LLMError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error: {str(e)}")

    return wrapper


class OpenAIHandler(LLMProvider):
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "generate_image",
                "description": "Generate an image using DALL-E based on a text description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Text description of the image to generate",
                        },
                        "model": {
                            "type": "string",
                            "enum": ["dall-e-2", "dall-e-3"],
                            "description": "The DALL-E model to use",
                        },
                        "size": {
                            "type": "string",
                            "enum": ["1024x1024", "1024x1792", "1792x1024"],
                            "description": "Size of the generated image",
                        },
                        "quality": {
                            "type": "string",
                            "enum": ["standard", "hd"],
                            "description": "Quality of the generated image",
                        },
                        "style": {
                            "type": "string",
                            "enum": ["vivid", "natural"],
                            "description": "Style of the generated image",
                        },
                    },
                    "required": ["prompt"],
                },
            },
        },
    ]

    def __init__(
        self, model: str, api_key: str, organization: Optional[str] = None, **kwargs
    ):
        super().__init__(model, **kwargs)
        self.name = "OpenAI"
        self.client = AsyncOpenAI(api_key=api_key, organization=organization)

    def _convert_to_openai_messages(
        self, conversation: Conversation
    ) -> List[OpenAIMessage]:
        """Convert our Message objects to OpenAI's message format."""
        conversation_messages = conversation.messages
        user_info = conversation_messages[0].metadata
        logging.info(f"User info: {user_info}")

        return [
            {
                "role": message.role.value,
                "content": message.content,
                # "metadata": message.metadata.get("user_info", None).get("name", None),
            }
            for message in conversation.messages
        ]

    async def _handle_tool_call(
        self, tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        tool_outputs = []

        for tool_call in tool_calls:
            function = tool_call.function
            name = function.name
            args = json.loads(function.arguments)

            if name == "generate_image":
                response = await self.client.images.generate(
                    model=args.get("model", "dall-e-3"),
                    prompt=args["prompt"],
                    size=args.get("size", "1024x1024"),
                    quality=args.get("quality", "standard"),
                    style=args.get("style", "vivid"),
                    response_format="url",
                )
                tool_outputs.append(
                    {
                        "tool": name,
                        "output": response.data[0].url,
                    }
                )
            else:
                raise InvalidRequestError(f"Unknown tool: {name}")

        return tool_outputs

    @handle_openai_errors
    async def generate_response(
        self,
        conversation: Conversation,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> Message:
        if not conversation.messages:
            raise InvalidRequestError("No conversation provided")

        openai_messages = self._convert_to_openai_messages(conversation)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop_sequences,
            tools=self.TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message
        if message.tool_calls:
            tool_outputs = await self._handle_tool_call(message.tool_calls)
            image_content = ImageContent(source=tool_outputs[0]["output"], type="url")
            return Message.assistant(content=image_content)

        return Message.assistant(content=message.content)
