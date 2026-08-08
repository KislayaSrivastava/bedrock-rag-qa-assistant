"""
Lightweight, dependency-free text chunker.

Splits on paragraph boundaries first, then sentence boundaries, falling
back to a fixed-width split only when a single sentence exceeds chunk_size.
Kept dependency-free and readable on purpose -- this is the piece most
worth understanding (and swapping out) rather than importing as a black box.
"""
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    index: int


def _split_sentences(paragraph: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+", paragraph.strip())


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> list[Chunk]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        # Paragraph alone is too big to add to the current chunk.
        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) <= chunk_size:
            current = paragraph
            continue

        # Even a single paragraph exceeds chunk_size -- split by sentence.
        sentence_buffer = ""
        for sentence in _split_sentences(paragraph):
            candidate_sentence = f"{sentence_buffer} {sentence}".strip() if sentence_buffer else sentence
            if len(candidate_sentence) <= chunk_size:
                sentence_buffer = candidate_sentence
            else:
                if sentence_buffer:
                    chunks.append(sentence_buffer)
                # Fixed-width fallback for a single oversized sentence.
                if len(sentence) > chunk_size:
                    for i in range(0, len(sentence), chunk_size - chunk_overlap):
                        chunks.append(sentence[i : i + chunk_size])
                    sentence_buffer = ""
                else:
                    sentence_buffer = sentence
        if sentence_buffer:
            current = sentence_buffer

    if current:
        chunks.append(current)

    # Apply overlap by prepending a tail of the previous chunk.
    overlapped: list[str] = []
    for i, c in enumerate(chunks):
        if i == 0 or chunk_overlap == 0:
            overlapped.append(c)
        else:
            tail = chunks[i - 1][-chunk_overlap:]
            overlapped.append(f"{tail} {c}")

    return [Chunk(text=c, index=i) for i, c in enumerate(overlapped)]
