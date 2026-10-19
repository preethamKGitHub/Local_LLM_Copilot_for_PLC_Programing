import json
from typing import Iterator

import httpx

from .config import CHAT_MODEL, EMBED_MODEL, MAX_NEW_TOKENS, NUM_CTX, OLLAMA_URL


def embed(texts: list[str]) -> list[list[float]]:
    r = httpx.post(
        f"{OLLAMA_URL}/api/embed", json={"model": EMBED_MODEL, "input": texts}, timeout=120
    )
    r.raise_for_status()
    return r.json()["embeddings"]


def chat_stream(messages: list[dict]) -> Iterator[str]:
    payload = {
        "model": CHAT_MODEL,
        "messages": messages,
        "stream": True,
        "options": {"num_ctx": NUM_CTX, "num_predict": MAX_NEW_TOKENS, "temperature": 0.2},
    }
    with httpx.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload, timeout=None) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if data.get("done"):
                return
            yield data.get("message", {}).get("content", "")


def ollama_models() -> list[str]:
    r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    r.raise_for_status()
    return [m["name"] for m in r.json().get("models", [])]
