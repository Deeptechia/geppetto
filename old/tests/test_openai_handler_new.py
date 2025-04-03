import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import openai

from geppetto.core.llm.base import Message, MessageRole, InvalidRequestError, LLMError
from geppetto.core.llm.openai_handler import OpenAIHandler


@pytest.fixture
def openai_handler():
    return OpenAIHandler(model="gpt-4", api_key="test-key", organization="test-org")


@pytest.fixture
def mock_openai_response():
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content="Test response"))]
    return response


@pytest.fixture
def mock_openai_stream():
    chunks = [
        MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
        MagicMock(choices=[MagicMock(delta=MagicMock(content=" world"))]),
    ]
    return chunks


@pytest.mark.asyncio
async def test_generate_response_success(openai_handler, mock_openai_response):
    # Arrange
    messages = [Message.user(content="Hello"), Message.assistant(content="Hi there!")]

    with patch.object(
        openai_handler.client.chat.completions,
        "create",
        AsyncMock(return_value=mock_openai_response),
    ):
        # Act
        response = await openai_handler.generate_response(messages)

        # Assert
        assert isinstance(response, Message)
        assert response.role == MessageRole.ASSISTANT
        assert response.content == "Test response"

        # Verify API call
        openai_handler.client.chat.completions.create.assert_called_once()
        call_args = openai_handler.client.chat.completions.create.call_args[1]
        assert call_args["model"] == "gpt-4"
        assert len(call_args["messages"]) == 2
        assert call_args["temperature"] == 0.7


@pytest.mark.asyncio
async def test_generate_response_empty_messages(openai_handler):
    # Act & Assert
    with pytest.raises(InvalidRequestError, match="No messages provided"):
        await openai_handler.generate_response([])


@pytest.mark.asyncio
async def test_generate_response_api_error(openai_handler):
    messages = [Message.user(content="Hello")]

    with patch.object(
        openai_handler.client.chat.completions,
        "create",
        AsyncMock(side_effect=openai.APIError("API Error")),
    ):
        # Act & Assert
        with pytest.raises(LLMError, match="OpenAI API error: API Error"):
            await openai_handler.generate_response(messages)


@pytest.mark.asyncio
async def test_stream_response_success(openai_handler, mock_openai_stream):
    messages = [Message.user(content="Hello")]

    with patch.object(
        openai_handler.client.chat.completions,
        "create",
        AsyncMock(return_value=mock_openai_stream),
    ):
        # Act
        responses = []
        async for response in openai_handler.stream_response(messages):
            responses.append(response)

        # Assert
        assert len(responses) == 2
        assert all(isinstance(r, Message) for r in responses)
        assert all(r.role == MessageRole.ASSISTANT for r in responses)
        assert responses[0].content == "Hello"
        assert responses[1].content == " world"


@pytest.mark.asyncio
async def test_stream_response_empty_messages(openai_handler):
    # Act & Assert
    with pytest.raises(InvalidRequestError, match="No messages provided"):
        async for _ in openai_handler.stream_response([]):
            pass


@pytest.mark.asyncio
async def test_stream_response_rate_limit_error(openai_handler):
    messages = [Message.user(content="Hello")]

    with patch.object(
        openai_handler.client.chat.completions,
        "create",
        AsyncMock(side_effect=openai.RateLimitError("Rate limit exceeded")),
    ):
        # Act & Assert
        with pytest.raises(LLMError, match="Rate limit exceeded"):
            async for _ in openai_handler.stream_response(messages):
                pass
