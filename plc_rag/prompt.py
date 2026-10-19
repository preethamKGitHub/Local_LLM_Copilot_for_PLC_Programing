from .config import MAX_NEW_TOKENS, NUM_CTX

SYSTEM = """You are a coding assistant for SIMATIC AX Structured Text (IEC 61131-3 ST).
Rules:
- Use ONLY the documentation excerpts provided in [DOC n] blocks. Do not invent syntax, keywords or library functions.
- If the excerpts do not contain the answer, say "Not found in the provided documentation." and stop.
- When an excerpt contains a matching example, copy its structure exactly and only change names, types and values.
- Put all ST code in ```iecst fenced blocks. Declare every variable in a VAR..END_VAR section.
- Use only the VAR sections the task needs. Never add VAR_EXTERNAL unless asked.
- Cite the excerpts you used as [DOC n]. Be concise.

SIMATIC AX ST skeletons (valid syntax; each unit closes with its own END_ keyword; format code one declaration or statement per line, indented):
PROGRAM Name ... END_PROGRAM
FUNCTION Name : INT ... END_FUNCTION
FUNCTION_BLOCK Name
    VAR_INPUT a : BOOL; END_VAR
    VAR_OUTPUT q : INT; END_VAR
    VAR s : INT; END_VAR
    <statements>
END_FUNCTION_BLOCK
CLASS Name
    VAR PRIVATE x : BOOL; END_VAR
    METHOD PUBLIC Start
        <statements>
    END_METHOD
END_CLASS
TYPE Colors : (Red, Green, Blue); END_TYPE   (enumerations are declared in TYPE, never in VAR; no ENUM keyword)
Variables and statements live inside a unit; there is no FUNC keyword. Statements end with ';' and IF closes with END_IF;"""

MODE_HINT = {
    "ask": "Answer the question.",
    "generate": "Write the requested Structured Text code, then give a 1-2 line explanation.",
    "explain": "Explain what the given code does, step by step, and point out any issues.",
}


def est_tokens(text: str) -> int:
    # Conservative: code and identifiers tokenize at roughly 3 chars/token.
    return len(text) // 3 + 1


def build_messages(
    question: str,
    hits: list[dict],
    mode: str = "ask",
    history: list[dict] | None = None,
    code_context: str = "",
) -> tuple[list[dict], list[dict]]:
    """Return (messages, hits_actually_used), fitted to the context window."""
    user_tail = f"{MODE_HINT.get(mode, MODE_HINT['ask'])}\n\n"
    if code_context:
        user_tail += f"Code provided by the user:\n```iecst\n{code_context}\n```\n\n"
    user_tail += f"Request: {question}"

    budget = NUM_CTX - MAX_NEW_TOKENS - est_tokens(SYSTEM) - est_tokens(user_tail) - 50

    kept_history: list[dict] = []
    for m in reversed(history or []):
        cost = est_tokens(m["content"])
        if cost > budget // 4:
            break
        budget -= cost
        kept_history.insert(0, m)

    used, blocks = [], []
    for n, h in enumerate(hits, 1):
        block = f"[DOC {n}] {h['heading_path']}\n{h['text']}"
        cost = est_tokens(block)
        if cost > budget:
            break
        budget -= cost
        used.append(h)
        blocks.append(block)

    docs = "\n\n".join(blocks) if blocks else "(no documentation found)"
    messages = [{"role": "system", "content": SYSTEM}, *kept_history]
    messages.append({"role": "user", "content": f"Documentation:\n{docs}\n\n{user_tail}"})
    return messages, used
