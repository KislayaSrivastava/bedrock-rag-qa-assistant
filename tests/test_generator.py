from unittest.mock import MagicMock, patch

from src.generator import build_prompt, generate_answer
from src.retriever import RetrievedChunk


def make_chunk(text="AWS Lambda is a serverless compute service.", source="doc.md"):
    return RetrievedChunk(chunk_id=f"{source}::chunk-0", text=text, source_file=source, score=0.9)


def test_build_prompt_includes_question_and_context():
    chunks = [make_chunk()]
    prompt = build_prompt("What is Lambda?", chunks)

    assert "What is Lambda?" in prompt
    assert "AWS Lambda is a serverless compute service." in prompt
    assert "doc.md" in prompt


def test_generate_answer_with_no_chunks_short_circuits():
    result = generate_answer(bedrock_client=MagicMock(), question="anything", chunks=[])
    assert "don't have enough information" in result.lower()


@patch("src.generator.generate")
def test_generate_answer_calls_bedrock_when_chunks_present(mock_generate):
    mock_generate.return_value = "Lambda is a serverless compute service."

    result = generate_answer(bedrock_client=MagicMock(), question="What is Lambda?", chunks=[make_chunk()])

    assert result == "Lambda is a serverless compute service."
    mock_generate.assert_called_once()
