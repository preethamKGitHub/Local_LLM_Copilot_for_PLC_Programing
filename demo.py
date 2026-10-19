"""Console client for the RAG API.

  python demo.py "How do I declare a function block?"
  python demo.py --mode generate "Write a function block that counts rising edges"
"""
import argparse
import json

import httpx

ap = argparse.ArgumentParser()
ap.add_argument("question")
ap.add_argument("--mode", default="ask", choices=["ask", "generate", "explain"])
ap.add_argument("--url", default="http://localhost:8000")
args = ap.parse_args()

with httpx.stream(
    "POST", f"{args.url}/chat", json={"question": args.question, "mode": args.mode}, timeout=None
) as r:
    r.raise_for_status()
    for line in r.iter_lines():
        if not line.startswith("data: "):
            continue
        m = json.loads(line[6:])
        if m["type"] == "sources":
            print("Sources:", *[f"\n  [DOC {s['n']}] {s['heading']}" for s in m["sources"]])
            print("\nAnswer:")
        elif m["type"] == "token":
            print(m["text"], end="", flush=True)
        elif m["type"] == "error":
            print("\nERROR:", m["message"])
        elif m["type"] == "validation":
            labels = {
                "not_applicable": "No code generated",
                "warnings": "Static warnings",
                "passed_checks": "No issues found by limited static checks",
            }
            print(f"\n\n{labels[m['status']]}. Compilation not run.")
            for finding in m["findings"]:
                print(f"- {finding['message']} ({finding['source'] or 'Output format'})")
print()
