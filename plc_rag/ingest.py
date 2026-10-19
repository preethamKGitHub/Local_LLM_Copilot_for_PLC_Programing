"""Ingestion: read local docs from Docs_Export -> chunks.jsonl. No network access.

  python -m plc_rag.ingest
"""
import json
import re

from bs4 import BeautifulSoup
from markdownify import markdownify

from .chunking import chunk_markdown
from .config import CHUNKS_FILE, DOCS_DIR


def html_to_markdown(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
        tag.decompose()
    title = (soup.title.string or "").strip() if soup.title else ""
    root = soup.find("main") or soup.find("article") or soup.body or soup
    md = markdownify(str(root), heading_style="ATX", code_language="iecst")
    return re.sub(r"\n{3,}", "\n\n", md).strip(), title


def _iter_docs():
    for p in sorted(DOCS_DIR.rglob("*")):
        suffix = p.suffix.lower()
        if not p.is_file() or suffix not in {".html", ".htm", ".md", ".txt"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if suffix in {".html", ".htm"}:
            md, title = html_to_markdown(text)
            yield p.as_uri(), title or p.stem, md
        else:
            yield p.as_uri(), p.stem, text


def build() -> None:
    if not DOCS_DIR.is_dir():
        raise SystemExit(f"Docs folder not found: {DOCS_DIR}")
    CHUNKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    n_docs = n_chunks = 0
    with CHUNKS_FILE.open("w", encoding="utf-8") as f:
        for url, title, md in _iter_docs():
            n_docs += 1
            for c in chunk_markdown(md, url, title):
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
                n_chunks += 1
    print(f"{n_docs} documents from {DOCS_DIR} -> {n_chunks} chunks in {CHUNKS_FILE}")


if __name__ == "__main__":
    build()
