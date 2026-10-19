@echo off
setlocal EnableExtensions
cd /d "%~dp0"

rem Override before running, e.g.  set PLC_CHAT_MODEL=qwen2.5-coder:7b
if not defined PLC_CHAT_MODEL set "PLC_CHAT_MODEL=qwen2.5-coder:3b"
if not defined PLC_EMBED_MODEL set "PLC_EMBED_MODEL=nomic-embed-text"
set "API_URL=http://localhost:8000"
set "OLLAMA_API=http://localhost:11434"
set "PY=.venv\Scripts\python.exe"

echo ============================================================
echo  PLC ST Copilot - local RAG launcher
echo  Chat model : %PLC_CHAT_MODEL%
echo  Embed model: %PLC_EMBED_MODEL%
echo ============================================================

echo.
echo [1/7] Locating Ollama...
set "OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if not exist "%OLLAMA%" for /f "delims=" %%i in ('where ollama 2^>nul') do set "OLLAMA=%%i"
if not exist "%OLLAMA%" call :fail "Ollama not found. Install it from https://ollama.com/download" & exit /b 1
echo       %OLLAMA%

echo.
echo [2/7] Starting Ollama server...
curl.exe -s -f -o nul "%OLLAMA_API%/api/tags" && (
  echo       already running
) || (
  start "Ollama" /min "%OLLAMA%" serve
  call :wait_url "%OLLAMA_API%/api/tags" 30 || ( call :fail "Ollama did not start within 30 seconds." & exit /b 1 )
  echo       started
)

echo.
echo [3/7] Checking models...
call :ensure_model "%PLC_CHAT_MODEL%" || ( call :fail "Could not pull %PLC_CHAT_MODEL%" & exit /b 1 )
call :ensure_model "%PLC_EMBED_MODEL%" || ( call :fail "Could not pull %PLC_EMBED_MODEL%" & exit /b 1 )

echo.
echo [4/7] Preparing Python environment...
if not exist "%PY%" (
  python -m venv .venv || ( call :fail "Could not create .venv. Is Python 3.10+ installed?" & exit /b 1 )
)
"%PY%" -c "import fastapi, uvicorn, chromadb, rank_bm25, httpx, bs4, markdownify" >nul 2>&1 || (
  echo       installing dependencies, this can take several minutes...
  "%PY%" -m pip install -q -r requirements.txt || ( call :fail "pip install failed." & exit /b 1 )
)
echo       ok

echo.
echo [5/7] Building the knowledge base from Docs_Export...
"%PY%" -m plc_rag.ingest || ( call :fail "Ingest failed. Check that Docs_Export has .md, .html or .txt files." & exit /b 1 )
"%PY%" -m plc_rag.index || ( call :fail "Indexing failed." & exit /b 1 )

echo.
echo [6/7] Building the VS Code extension...
where npm >nul 2>&1 || (
  echo       npm not found, skipping. Install Node.js to use @plc in VS Code.
  goto :start_api
)
pushd vscode-ext
if not exist node_modules call npm install --no-audit --no-fund
call npm run compile
popd

:start_api
echo.
echo [7/7] Starting the RAG API...
curl.exe -s -f -o nul "%API_URL%/health" && (
  echo       API is already running on port 8000.
  echo       Close its window and re-run this file to load the rebuilt index.
  goto :ready
)
start "PLC RAG API" cmd /k "%PY% -m uvicorn plc_rag.api:app --port 8000"
call :wait_url "%API_URL%/health" 60 || ( call :fail "API did not start within 60 seconds. See the PLC RAG API window." & exit /b 1 )

echo       preloading the chat model...
curl.exe -s -o nul -X POST "%OLLAMA_API%/api/generate" -d "{\"model\":\"%PLC_CHAT_MODEL%\",\"keep_alive\":\"30m\"}"

:ready
echo.
echo ============================================================
echo  READY. The API is listening on %API_URL%
echo.
echo  Ask from the command line:
echo    %PY% demo.py "How do I declare an enumeration?"
echo    %PY% demo.py --mode generate "Write a function block with a BOOL input"
echo.
echo  Ask from VS Code: press F5 in this folder, then in Copilot Chat
echo  of the new window type:  @plc your question
echo ============================================================
echo.
pause
exit /b 0

:wait_url
rem %1 = url, %2 = max seconds
for /l %%i in (1,1,%~2) do (
  curl.exe -s -f -o nul "%~1" && exit /b 0
  ping -n 2 127.0.0.1 >nul
)
exit /b 1

:ensure_model
"%OLLAMA%" list | findstr /b /c:"%~1" >nul && (
  echo       %~1 present
  exit /b 0
)
echo       pulling %~1, this downloads the model...
"%OLLAMA%" pull %~1
exit /b %errorlevel%

:fail
echo.
echo ERROR: %~1
echo.
pause
exit /b 1
