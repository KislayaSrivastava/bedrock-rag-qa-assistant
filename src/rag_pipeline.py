"""
Orchestrates retrieval + generation into a single call, and is the
one class both the API layer and the Streamlit demo depend on.
"""
import time

from src.bedrock_client import get_bedrock_client
from src.generator import generate_answer
from src.retriever import Retriever


class RAGPipeline:
    def __init__(self):
        self._retriever = Retriever()
        self._bedrock = get_bedrock_client()

    def is_ready(self) -> bool:
        return self._retriever.count() > 0

    def chunk_count(self) -> int:
        return self._retriever.count()

    def answer(self, question: str, top_k: int | None = None) -> dict:
        start = time.perf_counter()

        chunks = self._retriever.retrieve(self._bedrock, question, top_k)
        answer_text = generate_answer(self._bedrock, question, chunks)

        latency_ms = int((time.perf_counter() - start) * 1000)

        return {
            "answer": answer_text,
            "sources": [
                {
                    "chunk_id": c.chunk_id,
                    "source_file": c.source_file,
                    "score": c.score,
                    "text_preview": c.text[:200],
                }
                for c in chunks
            ],
            "latency_ms": latency_ms,
        }
