"""
Ingestion entrypoint: reads documents, chunks them, embeds each chunk via
Bedrock, and persists everything to a local ChromaDB collection.

Run directly:  python -m src.ingest
"""
import glob
import os

import chromadb

from src.bedrock_client import embed_text, get_bedrock_client
from src.chunking import chunk_text
from src.config import settings


def load_documents(data_dir: str) -> dict[str, str]:
    docs = {}
    for path in glob.glob(os.path.join(data_dir, "**", "*.*"), recursive=True):
        if path.endswith((".md", ".txt")):
            with open(path, encoding="utf-8") as f:
                docs[os.path.basename(path)] = f.read()
    return docs


def run_ingest() -> int:
    docs = load_documents(settings.data_dir)
    if not docs:
        print(f"No .md/.txt documents found under {settings.data_dir}")
        return 0

    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection(settings.chroma_collection_name)

    bedrock = get_bedrock_client()

    total_chunks = 0
    for filename, text in docs.items():
        chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
        print(f"{filename}: {len(chunks)} chunks")

        ids, embeddings, documents, metadatas = [], [], [], []
        for c in chunks:
            embedding = embed_text(bedrock, c.text)
            ids.append(f"{filename}::chunk-{c.index}")
            embeddings.append(embedding)
            documents.append(c.text)
            metadatas.append({"source_file": filename, "chunk_index": c.index})

        collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        total_chunks += len(chunks)

    print(f"\nIngested {total_chunks} chunks from {len(docs)} document(s) into "
          f"'{settings.chroma_collection_name}' at {settings.chroma_persist_dir}")
    return total_chunks


if __name__ == "__main__":
    run_ingest()
