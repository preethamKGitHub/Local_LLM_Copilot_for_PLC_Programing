"""Local retrieval evaluation and opt-in generation observations, not correctness proof.

  python -m eval.run_eval
    python -m eval.run_eval --generate --limit 2
"""
import argparse
import json
from pathlib import Path
from time import perf_counter

from plc_rag.llm import chat_stream
from plc_rag.prompt import build_messages
from plc_rag.retriever import Retriever
from plc_rag.validation import REFUSAL, validate_generation


def evaluate_generation(retriever: Retriever, item: dict) -> dict:
        started = perf_counter()
        hits = retriever.search_generation(item["question"])
        messages, used = build_messages(item["question"], hits, mode="generate")
        answer = "".join(chat_stream(messages)) if used else REFUSAL
        validation = validate_generation(answer, source_count=len(used))
        headings = [hit["heading_path"] for hit in used]
        required = item.get("expect_headings", [])
        evidence_ok = all(any(heading.lower() in actual.lower() for actual in headings) for heading in required)
        refused = answer.strip() == REFUSAL
        return {
                "question": item["question"], "answer": answer,
                "sources": [{"heading": hit["heading_path"], "url": hit["url"]} for hit in used],
                "evidence_coverage": evidence_ok if required else None,
                "refused": refused, "expected_refusal": item.get("expect_refusal", False),
                "refusal_matched": refused == item.get("expect_refusal", False),
                "validation": validation, "latency_seconds": round(perf_counter() - started, 3),
                "expert_review_required": True,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true", help="Run opt-in local generation cases instead of retrieval baseline")
    parser.add_argument("--limit", type=int, help="Maximum number of cases")
    parser.add_argument("--case", default="", help="Only questions containing this text (case insensitive)")
    parser.add_argument("--output", type=Path, help="Write detailed JSONL observations, including generated answers")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    items = [json.loads(l) for l in (Path(__file__).parent / "golden.jsonl").open(encoding="utf-8")]
    items = [item for item in items if (item.get("mode") == "generate") == args.generate and args.case.lower() in item["question"].lower()]
    if args.limit:
        items = items[:args.limit]
    if not items:
        parser.error("No matching evaluation cases")
    r = Retriever()
    if args.generate:
        results = []
        for item in items:
            try:
                result = evaluate_generation(r, item)
                print(json.dumps(result, ensure_ascii=False))
            except Exception as exc:
                result = {"question": item["question"], "error": str(exc), "compilation_status": "not_run"}
                print(json.dumps(result))
            results.append(result)
        if args.output:
            args.output.write_text("".join(json.dumps(result, ensure_ascii=False) + "\n" for result in results), encoding="utf-8")
        print(f"generation observations: {len(results)}; errors: {sum('error' in result for result in results)}; compilation: not_run")
        print("Static checks and retrieval coverage do not establish functional correctness. Engineer review required.")
        return
    hits = 0
    for it in items:
        text = " ".join(c["text"].lower() for c in r.search(it["question"]))
        ok = any(k in text for k in it["expect_any"])
        hits += ok
        print(("PASS" if ok else "FAIL"), it["question"])
    print(f"hit rate: {hits}/{len(items)}")


if __name__ == "__main__":
    main()
