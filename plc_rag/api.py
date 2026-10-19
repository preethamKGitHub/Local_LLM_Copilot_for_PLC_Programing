"""  uvicorn plc_rag.api:app --host 0.0.0.0 --port 8000"""
import json
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .config import CHAT_MODEL, EMBED_MODEL, NUM_CTX
from .llm import chat_stream, ollama_models
from .prompt import build_messages
from .retriever import Retriever

app = FastAPI(title="PLC ST RAG")
_retriever: Retriever | None = None


def retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    question: str
    mode: Literal["ask", "generate", "explain"] = "ask"
    history: list[Turn] = []
    code: str = ""


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


@app.get("/health")
def health():
    try:
        models = ollama_models()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    return {
        "ok": True,
        "chat_model": CHAT_MODEL,
        "embed_model": EMBED_MODEL,
        "num_ctx": NUM_CTX,
        "models_present": [m for m in models if m.split(":")[0] in (CHAT_MODEL.split(":")[0], EMBED_MODEL)],
    }


@app.post("/chat")
def chat(req: ChatRequest):
    # Plain def: FastAPI runs it in a threadpool, so blocking HTTP calls don't stall the loop.
    query = f"{req.question}\n{req.code[:500]}" if req.code else req.question
    hits = retriever().search(query)
    messages, used = build_messages(
        req.question, hits, req.mode, [t.model_dump() for t in req.history], req.code
    )

    def events():
        yield _sse({"type": "sources", "model": CHAT_MODEL, "sources": [
            {"n": i, "heading": h["heading_path"], "url": h["url"]} for i, h in enumerate(used, 1)
        ]})
        try:
            for tok in chat_stream(messages):
                yield _sse({"type": "token", "text": tok})
        except Exception as exc:
            yield _sse({"type": "error", "message": str(exc)})
        yield _sse({"type": "done"})

    return StreamingResponse(events(), media_type="text/event-stream")
