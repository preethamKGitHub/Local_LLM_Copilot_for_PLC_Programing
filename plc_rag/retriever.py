import json
import re
from typing import cast

import chromadb
from chromadb.api.types import Embedding
from rank_bm25 import BM25Okapi

from .config import CHROMA_DIR, CHUNKS_FILE, COLLECTION, TOP_K
from .llm import embed

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+")
_TOPICS = (
    (r"\b(function[ _]block|fb)\b", "Function block declaration"),
    (r"\b(enum\w*|enumeration)\b", "Enumeration"),
    (r"\b(inherit\w*|extends)\b", "Class inheritance"),
    (r"\b(overrid\w*|override)\b", "Method overriding"),
    (r"\bclass\b", "Class declaration"),
    (r"\bmethod\b", "Method declaration"),
    (r"\bfunction\b", "Function declaration"),
    (r"\bprogram\b", "Program declaration"),
)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text)]


class Retriever:
    """Hybrid BM25 + vector search fused with reciprocal rank fusion."""

    def __init__(self) -> None:
        self.chunks = [json.loads(l) for l in CHUNKS_FILE.open(encoding="utf-8")]
        self.bm25 = BM25Okapi([tokenize(c["heading_path"] + " " + c["text"]) for c in self.chunks])
        self.col = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(COLLECTION)

    def search(
        self, query: str, k: int = TOP_K, pool: int = 20,
        roles: tuple[str, ...] | None = None,
    ) -> list[dict]:
        eligible = {
            idx for idx, chunk in enumerate(self.chunks)
            if roles is None or chunk.get("content_role", "mixed") in roles
        }
        if not eligible or k <= 0 or pool <= 0:
            return []
        scores = self.bm25.get_scores(tokenize(query))
        bm_rank = [idx for idx in sorted(eligible, key=lambda idx: -scores[idx]) if scores[idx] > 0][:pool]
        kwargs = {}
        indexed_roles = (self.col.metadata or {}).get("evidence_roles", False)
        if roles is not None and indexed_roles:
            kwargs["where"] = {"content_role": {"$in": list(roles)}}
        count = min(len(eligible), pool) if roles is None or indexed_roles else len(self.chunks)
        res = self.col.query(
            query_embeddings=cast(list[Embedding], embed([f"search_query: {query}"])), n_results=count, **kwargs
        )
        vec_rank = [int(idx) for idx in res["ids"][0] if int(idx) in eligible][:pool]

        fused: dict[int, float] = {}
        for ranking in (bm_rank, vec_rank):
            for rank, idx in enumerate(ranking):
                fused[idx] = fused.get(idx, 0.0) + 1.0 / (60 + rank)
        top = sorted(fused, key=lambda idx: fused[idx], reverse=True)[:k]
        return [self.chunks[i] for i in top]

    def search_generation(self, query: str, k: int = TOP_K) -> list[dict]:
        """Reserve evidence slots for the requested construct, not generic ST patterns."""
        ordinary = self.search(query, k=k)
        topic = next((heading for pattern, heading in _TOPICS if re.search(pattern, query, re.I)), None)
        if topic is None or k <= 0:
            return ordinary
        focused = self.search(
            f"{query}\n{topic} syntax rules example", k=k, roles=("rules", "mixed", "examples")
        )
        candidates = [hit for hit in focused if topic.lower() in hit["heading_path"].lower()]
        rules = next((hit for hit in candidates if hit.get("content_role", "mixed") != "examples"), None)
        example = next((hit for hit in candidates if hit.get("content_role") == "examples"), None)
        if example is None:
            example = next((hit for hit in candidates if hit is not rules and hit.get("content_role", "mixed") == "mixed"), None)
        selected = []
        seen = set()
        for hit in [rules, example, *ordinary, *focused]:
            if hit is None:
                continue
            identity = (hit["url"], hit["heading_path"], hit["text"])
            if identity not in seen:
                selected.append(hit)
                seen.add(identity)
        return selected[:k]
