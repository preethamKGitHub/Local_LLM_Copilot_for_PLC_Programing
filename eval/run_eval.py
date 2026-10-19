"""Retrieval hit-rate: a question hits if any expected keyword appears in the top-k chunks.

  python -m eval.run_eval
"""
import json
from pathlib import Path

from plc_rag.retriever import Retriever


def main() -> None:
    r = Retriever()
    items = [json.loads(l) for l in (Path(__file__).parent / "golden.jsonl").open(encoding="utf-8")]
    hits = 0
    for it in items:
        text = " ".join(c["text"].lower() for c in r.search(it["question"]))
        ok = any(k in text for k in it["expect_any"])
        hits += ok
        print(("PASS" if ok else "FAIL"), it["question"])
    print(f"hit rate: {hits}/{len(items)}")


if __name__ == "__main__":
    main()
