"""
Central configuration, loaded from environment variables (.env in local dev).
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")

    # Bedrock model IDs -- check the Bedrock console for what's enabled
    # in your account/region before running. These defaults are a
    # reasonable starting point, not a guarantee of availability.
    embed_model_id: str = os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
    gen_model_id: str = os.getenv("BEDROCK_GEN_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")

    # Ingestion
    data_dir: str = os.getenv("DATA_DIR", "data/sample_docs")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))

    # Vector store
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "rag_documents")

    # Retrieval / generation
    default_top_k: int = int(os.getenv("TOP_K", "4"))
    max_generation_tokens: int = int(os.getenv("MAX_GENERATION_TOKENS", "1024"))


settings = Settings()
