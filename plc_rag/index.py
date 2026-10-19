"""Embed chunks.jsonl into a persistent ChromaDB collection.

  python -m plc_rag.index
"""
import json
from typing import cast

import chromadb
from chromadb.api.types import Embedding

from .config import CHROMA_DIR, CHUNKS_FILE, COLLECTION
from .llm import embed

BATCH = 32


def main() -> None:
    chunks = [json.loads(l) for l in CHUNKS_FILE.open(encoding="utf-8")]
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine", "evidence_roles": True})

    for i in range(0, len(chunks), BATCH):
        batch = chunks[i : i + BATCH]
        docs = [f"search_document: {c['heading_path']}\n{c['text']}" for c in batch]
        col.add(
            ids=[str(i + j) for j in range(len(batch))],
            embeddings=cast(list[Embedding], embed(docs)),
            metadatas=[{
                "url": c["url"], "heading_path": c["heading_path"],
                "content_role": c.get("content_role", "mixed"),
            } for c in batch],
        )
        print(f"{min(i + BATCH, len(chunks))}/{len(chunks)}")


if __name__ == "__main__":
    main()
