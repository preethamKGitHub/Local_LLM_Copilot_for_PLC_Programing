import re

HEADING = re.compile(r"^(#{1,6})\s+(.*)")


def content_role(text: str) -> str:
    """Classify evidence conservatively; examples may include negative examples."""
    code = bool(re.search(r"```|^\s*(?:PROGRAM|CLASS|FUNCTION(?:_BLOCK)?|TYPE|VAR(?:_\w+)?|METHOD)\b", text, re.M))
    prose = bool(re.search(r"\b(?:must|only|not allowed|not supported|declared|defines|specifying|can declare)\b", text, re.I))
    if code and not prose:
        return "examples"
    if prose and not code:
        return "rules"
    return "mixed"


def _blocks(lines: list[str]) -> list[str]:
    """Split on blank lines, keeping fenced code blocks whole."""
    blocks, cur, in_code = [], [], False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
        if not line.strip() and not in_code:
            if cur:
                blocks.append("\n".join(cur))
                cur = []
            continue
        cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    return blocks


def chunk_markdown(md: str, url: str, title: str, max_chars: int = 1600) -> list[dict]:
    sections: list[tuple[list[str], list[str]]] = []
    path: list[str] = []
    buf: list[str] = []
    in_code = False

    for line in md.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        m = None if in_code else HEADING.match(line)
        if m:
            sections.append((list(path), buf))
            buf = []
            level = len(m.group(1))
            path = path[: level - 1] + [m.group(2).strip()]
        else:
            buf.append(line)
    sections.append((list(path), buf))

    chunks = []
    for heading_path, lines in sections:
        cur = ""
        for block in _blocks(lines):
            if cur and len(cur) + len(block) + 2 > max_chars:
                chunks.append((heading_path, cur))
                cur = ""
            cur = f"{cur}\n\n{block}" if cur else block
        if cur:
            chunks.append((heading_path, cur))

    return [
        {
            "title": title,
            "heading_path": " > ".join(hp) if hp else title,
            "url": url,
            "text": text.strip(),
            "content_role": content_role(text),
        }
        for hp, text in chunks
        if len(text.strip()) > 40
    ]
