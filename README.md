# PLC ST Copilot (local RAG)

RAG assistant for SIMATIC AX Structured Text. Ollama + Python API run in WSL; a VS Code chat participant (`@plc`) is the front end.

Documentation comes only from the local `Docs_Export/` folder (`.md`, `.html`, `.txt`). Nothing is fetched online.

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
