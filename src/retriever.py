"""
Query-time retrieval: embed the question, run similarity search against
the persisted ChromaDB collection, return ranked chunks with metadata.
"""
from dataclasses import dataclass

import chromadb

from src.bedrock_client import embed_text
from src.config import settings


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    source_file: str
    score: float


class Retriever:
    def __init__(self):
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._collection = self._client.get_or_create_collection(settings.chroma_collection_name)

    def count(self) -> int:
        return self._collection.count()

    def retrieve(self, bedrock_client, question: str, top_k: int | None = None) -> list[RetrievedChunk]:
        top_k = top_k or settings.default_top_k
        query_embedding = embed_text(bedrock_client, question)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        chunks: list[RetrievedChunk] = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for chunk_id, text, meta, distance in zip(ids, documents, metadatas, distances):
            # Chroma returns a distance (lower = more similar) -- convert to
            # a 0-1 "similarity-ish" score for a more intuitive API response.
            score = 1.0 / (1.0 + distance)
            chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=text,
                    source_file=meta.get("source_file", "unknown"),
                    score=round(score, 4),
                )
            )
        return chunks
