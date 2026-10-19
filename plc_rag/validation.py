"""Advisory checks of a few documented ST patterns, never a compiler."""
import re

REFUSAL = "Not found in the provided documentation."
_LEXEME = re.compile(
    r"//[^\n]*|\(\*|\*\)|'(?:\$.|''|[^'])*'|\"(?:\$.|\"\"|[^\"])*\"|[A-Za-z_][A-Za-z0-9_]*|[(),:;]"
)


def _tokens(code: str) -> list[str]:
    tokens = []
    comment_depth = 0
    for match in _LEXEME.finditer(code):
        value = match.group()
        if value == "(*":
            comment_depth += 1
        elif value == "*)":
            comment_depth = max(0, comment_depth - 1)
        elif not comment_depth and not value.startswith(("//", "'", '"')):
            tokens.append(value.upper())
    return tokens


def validate_generation(answer: str, source_count: int | None = None) -> dict:
    result = {"status": "passed_checks", "compilation_status": "not_run", "findings": []}
    findings = result["findings"]
    blocks = []
    current = None
    fence_char = ""
    fence_length = 0
    for line in answer.splitlines():
        fence = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if fence and not fence_char:
            fence_char = fence[1][0]
            fence_length = len(fence[1])
            current = [] if fence[2].strip().lower() == "iecst" else None
        elif fence and fence[1][0] == fence_char and len(fence[1]) >= fence_length and not fence[2].strip():
            if current is not None:
                blocks.append("\n".join(current))
            current = None
            fence_char = ""
        elif current is not None:
            current.append(line)

    def warn(code: str, message: str, source: str = "") -> None:
        finding = {"code": code, "message": message, "source": source}
        if finding not in findings:
            findings.append(finding)

    if fence_char:
        warn("incomplete_fence", "An output code fence is incomplete; generation may be truncated.")
    if not blocks:
        if answer.strip() == REFUSAL:
            result["status"] = "not_applicable"
            return result
        warn("missing_code", "No complete iecst code block was returned.")

    if blocks and source_count is not None:
        citations = [int(number) for number in re.findall(r"\[DOC (\d+)\]", answer)]
        if not citations:
            warn("missing_citation", "The response does not cite its documentation excerpts as [DOC n].")
        elif any(number < 1 or number > source_count for number in citations):
            warn("invalid_citation", "The response cites a documentation number that was not included in its context.")

    for block in blocks:
        tokens = _tokens(block)
        if not tokens:
            warn("empty_code", "An iecst block contains no checkable code.")
        scopes = []
        variable_section = False
        for index, token in enumerate(tokens):
            if token in {"CLASS", "METHOD", "FUNCTION", "FUNCTION_BLOCK", "PROGRAM", "TYPE"}:
                scopes.append(token)
            elif token.startswith("END_") and token[4:] in {"CLASS", "METHOD", "FUNCTION", "FUNCTION_BLOCK", "PROGRAM", "TYPE"}:
                expected = token[4:]
                if scopes and scopes[-1] == expected:
                    scopes.pop()
                else:
                    warn("unbalanced_unit", "POU/type closing keywords appear unmatched; inspect the output.")
            if token == "VAR" or token.startswith("VAR_"):
                variable_section = True
                if scopes and scopes[-1] == "CLASS" and token in {"VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT", "VAR_TEMP", "VAR_EXTERNAL"}:
                    warn("class_section", "Class fields must use a static VAR section, not " + token + ".", "Docs_Export/ST_Language_doc.md > Class declaration")
            elif token == "END_VAR":
                variable_section = False
            if variable_section and token == ":" and tokens[index + 1:index + 2] == ["("]:
                warn("inline_enumeration", "Declare enumeration types in TYPE, not in a variable section.", "Docs_Export/ST_Language_doc.md > Enumeration")
            if token == "EXTENDS" and index + 2 < len(tokens) and tokens[index + 2] == ",":
                warn("multiple_inheritance", "A class can extend only one base class.", "Docs_Export/OOP Overview.md > Class inheritance")
        if scopes or variable_section:
            warn("incomplete_unit", "A POU/type or variable section appears unclosed; generation may be truncated.")
    if findings:
        result["status"] = "warnings"
    return result