"""
Thin wrapper around the Bedrock runtime client for embeddings + generation.
Isolated here so src/retriever.py, src/generator.py, and tests can all
depend on a small, mockable surface instead of talking to boto3 directly.
"""
import json

import boto3

from src.config import settings


def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=settings.aws_region)


def embed_text(client, text: str) -> list[float]:
    """Embed a single string using the configured Titan embedding model."""
    body = json.dumps({"inputText": text})
    response = client.invoke_model(
        modelId=settings.embed_model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    return payload["embedding"]


def generate(client, prompt: str, max_tokens: int | None = None) -> str:
    """Generate a response using the configured Claude-on-Bedrock model."""
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens or settings.max_generation_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
    )
    response = client.invoke_model(
        modelId=settings.gen_model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    return payload["content"][0]["text"]
