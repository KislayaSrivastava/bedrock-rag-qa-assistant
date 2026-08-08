"""
Prompt assembly + generation. Kept deliberately simple and inspectable --
the prompt template is the thing worth iterating on, so it isn't buried
inside a framework abstraction.
"""
from src.bedrock_client import generate
from src.retriever import RetrievedChunk

SYSTEM_INSTRUCTIONS = """You are a precise assistant answering questions using ONLY the context provided below.

Rules:
- Answer using only information present in the context.
- If the context does not contain enough information to answer, say so explicitly -- do not guess or use outside knowledge.
- Keep answers concise and directly responsive to the question.
- Do not mention "the context" or "the provided text" in your answer -- just answer naturally, as if you know the material.
"""


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n---\n\n".join(f"[{c.source_file}]\n{c.text}" for c in chunks)
    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )


def generate_answer(bedrock_client, question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "I don't have enough information in the provided context to answer that."

    prompt = build_prompt(question, chunks)
    return generate(bedrock_client, prompt)
