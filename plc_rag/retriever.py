import json
import re

import chromadb
from rank_bm25 import BM25Okapi

from .config import CHROMA_DIR, CHUNKS_FILE, COLLECTION, TOP_K
from .llm import embed

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text)]


class Retriever:
    """Hybrid BM25 + vector search fused with reciprocal rank fusion."""

    def __init__(self) -> None:
        self.chunks = [json.loads(l) for l in CHUNKS_FILE.open(encoding="utf-8")]
        self.bm25 = BM25Okapi([tokenize(c["heading_path"] + " " + c["text"]) for c in self.chunks])
        self.col = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(COLLECTION)

    def search(self, query: str, k: int = TOP_K, pool: int = 20) -> list[dict]:
        scores = self.bm25.get_scores(tokenize(query))
        bm_rank = [i for i in sorted(range(len(scores)), key=lambda i: -scores[i])[:pool] if scores[i] > 0]
        res = self.col.query(query_embeddings=embed([f"search_query: {query}"]), n_results=pool)
        vec_rank = [int(i) for i in res["ids"][0]]

        fused: dict[int, float] = {}
        for ranking in (bm_rank, vec_rank):
            for rank, idx in enumerate(ranking):
                fused[idx] = fused.get(idx, 0.0) + 1.0 / (60 + rank)
        top = sorted(fused, key=fused.get, reverse=True)[:k]
        return [self.chunks[i] for i in top]
