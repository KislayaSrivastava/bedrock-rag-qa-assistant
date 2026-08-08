from unittest.mock import MagicMock, patch

from src.rag_pipeline import RAGPipeline
from src.retriever import RetrievedChunk


@patch("src.rag_pipeline.get_bedrock_client")
@patch("src.rag_pipeline.Retriever")
def test_answer_returns_expected_shape(mock_retriever_cls, mock_get_client):
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [
        RetrievedChunk(chunk_id="doc.md::chunk-0", text="Some context.", source_file="doc.md", score=0.87)
    ]
    mock_retriever_cls.return_value = mock_retriever
    mock_get_client.return_value = MagicMock()

    with patch("src.rag_pipeline.generate_answer", return_value="A grounded answer."):
        pipeline = RAGPipeline()
        result = pipeline.answer("What is this about?", top_k=3)

    assert result["answer"] == "A grounded answer."
    assert result["sources"][0]["source_file"] == "doc.md"
    assert isinstance(result["latency_ms"], int)
    mock_retriever.retrieve.assert_called_once()
