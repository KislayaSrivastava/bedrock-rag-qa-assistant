from unittest.mock import MagicMock

from src.bedrock_client import generate


def test_generate_parses_converse_response():
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {"message": {"content": [{"text": "Hello from the model."}]}}
    }

    result = generate(mock_client, "Say hi")

    assert result == "Hello from the model."
    mock_client.converse.assert_called_once()
    call_kwargs = mock_client.converse.call_args.kwargs
    assert call_kwargs["messages"] == [{"role": "user", "content": [{"text": "Say hi"}]}]