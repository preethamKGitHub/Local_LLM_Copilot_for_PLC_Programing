# PLC ST Copilot (local RAG)

RAG assistant for SIMATIC AX Structured Text. Ollama + Python API run in WSL; a VS Code chat participant (`@plc`) is the front end.

Documentation comes only from the local `Docs_Export/` folder (`.md`, `.html`, `.txt`). Nothing is fetched online.

The research paper informs the architecture, not the ST dialect or generation corpus. Generation stays grounded in the exported language/OOP documentation; Mitsubishi/GX Works3 label rules and instructions are not imported.

## 1. WSL setup

```bash
ollama pull qwen2.5-coder:7b      # or :3b on low RAM (set PLC_CHAT_MODEL)
ollama pull nomic-embed-text
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Ingest and index

```bash
python -m plc_rag.ingest          # Docs_Export/ -> data/chunks.jsonl
python -m plc_rag.index           # embed into data/chroma
python -m eval.run_eval           # retrieval hit rate
```

Re-run both commands whenever `Docs_Export/` changes. Override the folder with `PLC_DOCS_DIR`.

Rebuild both after upgrading to role-aware retrieval. Chunks carry `rules`, `examples`, or `mixed` metadata. Generation adds at most one focused retrieval pass for documented POU/type/OOP topics, merges relevant rules/examples with hybrid results, and keeps the existing top-k limit. Ambiguous/legacy chunks are treated as mixed. Example classification does not certify that an example is correct: excerpts can contain explicitly wrong examples.

Indexing replaces the configured Chroma collection. Test rebuilds using a separate `PLC_RAG_DATA` folder first, and restart the API after rebuilding because its retriever is cached. The existing index remains readable without rebuilding, but lacks indexed role filters.

## 3. Run the API

```bash
uvicorn plc_rag.api:app --host 0.0.0.0 --port 8000
curl localhost:8000/health
```

Env vars: `PLC_DOCS_DIR`, `PLC_CHAT_MODEL`, `PLC_EMBED_MODEL`, `PLC_NUM_CTX` (default 4096), `PLC_MAX_NEW_TOKENS`, `PLC_TOP_K`, `OLLAMA_URL`.

## 4. VS Code extension

```bash
cd vscode-ext && npm install && npm run compile
```

Press F5 to launch an Extension Development Host, then use `@plc`, `@plc /generate`, `@plc /explain` (uses the editor selection). Setting `plcRag.apiUrl` defaults to `http://localhost:8000`, which WSL2 forwards to Windows.

## 5. Command-line examples

With the API running (Windows PowerShell, from the project root):

```powershell
.\.venv\Scripts\python demo.py "How do I declare a if statement?"
.\.venv\Scripts\python demo.py --mode generate "Write a function block that debounces a BOOL input"
.\.venv\Scripts\python demo.py --mode explain "paste your ST code here"
```

Modes: `ask` (default) answers from the docs, `generate` writes ST code, `explain` explains the code you pass in. If the docs lack the topic, the answer is "Not found in the provided documentation."

## 6. Static feedback and limits

Generation streams code as before, followed by an additive `validation` SSE event shown in chat and the CLI. Its `status` is `passed_checks`, `warnings`, or `not_applicable`; `compilation_status` is always `not_run`. Findings contain a code, message, and documentation heading where applicable.

The lightweight checker examines all complete `iecst` blocks for a few documented restrictions: class-level variable sections (distinct from method inputs), inline enumeration declarations in variable sections, and comma-separated multiple inheritance. It also warns about missing/empty code fences, apparently incomplete units, and missing/out-of-range `[DOC n]` citations. Citation checks only validate presence and numbering, not semantic support. These checks are advisory, not a complete ST parser, symbol/type checker, compiler, or functional verifier. A definition-only function block does not need an instance or call to pass these checks.

No compiler is configured and no automatic repairs run. Integrating a real SIMATIC AX compiler requires its verified invocation/service, version, license, and project/dependency setup. Future repair must be bounded to three total compilation attempts and stop on timeout/unavailability. Generated code requires qualified engineering review and simulation/vendor testing before deployment; passing checks never means safe to deploy.

Oversized requests/selected code return HTTP 422 rather than silently overflowing the context budget. Model token-limit termination and interrupted streams return an error without a passing validation event.

## 7. Verification

```bash
python -m unittest discover -s tests
python -m eval.run_eval                       # original ten retrieval fixtures
python -m eval.run_eval --generate --limit 2  # opt-in local generation observations
python -m eval.run_eval --generate --case RTRIG_P --output observations.jsonl
```

Unit tests mock model/vector calls and require no Ollama service or existing index. Live evaluations require an indexed corpus and configured Ollama models. Generation observations include actual used source headings, expected refusal outcomes, static findings, latency, and answers for expert review. They do not measure compilation or prove correct control logic. Keep detailed reports local because they contain generated code and source paths.

Ollama chat and embeddings remain the only inference path; there is no cloud provider or new runtime dependency. Fully local operation assumes `OLLAMA_URL` points to a local/on-premises service, and models/dependencies are already installed. Nothing is executed or downloaded to a PLC.
