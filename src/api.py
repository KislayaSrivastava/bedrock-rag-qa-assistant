"""
FastAPI app exposing the RAG pipeline. Used both for local dev
(uvicorn src.api:app) and, wrapped by Mangum, for Lambda (lambda/handler.py).
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.rag_pipeline import RAGPipeline

app = FastAPI(
    title="Bedrock RAG QA Assistant",
    description="Retrieval-Augmented Generation Q&A API built on Amazon Bedrock.",
    version="0.1.0",
)

_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to answer")
    top_k: int = Field(default=4, ge=1, le=20, description="Number of chunks to retrieve")


class SourceChunk(BaseModel):
    chunk_id: str
    source_file: str
    score: float
    text_preview: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    latency_ms: int


class HealthResponse(BaseModel):
    status: str
    vector_store_ready: bool
    chunk_count: int


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    pipeline = get_pipeline()
    return HealthResponse(
        status="ok",
        vector_store_ready=pipeline.is_ready(),
        chunk_count=pipeline.chunk_count(),
    )


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    pipeline = get_pipeline()
    try:
        result = pipeline.answer(request.question, request.top_k)
    except Exception as exc:  # broad on purpose -- surfaced to the client as a 500
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return QueryResponse(**result)
