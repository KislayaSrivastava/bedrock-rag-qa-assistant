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
    """Generate a response using the Bedrock Converse API.

    Converse is a unified interface across model families (Anthropic Claude,
    Amazon Nova, Meta Llama, etc.) -- unlike invoke_model, which expects a
    different request/response JSON shape per provider. That means changing
    BEDROCK_GEN_MODEL_ID in .env is enough to switch providers; this function
    doesn't need to change.
    """
    response = client.converse(
        modelId=settings.gen_model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens or settings.max_generation_tokens},
    )
    return response["output"]["message"]["content"][0]["text"]