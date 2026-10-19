import * as vscode from "vscode";

type Mode = "ask" | "generate" | "explain";

interface Source {
  n: number;
  heading: string;
  url: string;
}

export function activate(context: vscode.ExtensionContext) {
  const participant = vscode.chat.createChatParticipant(
    "plc-st-copilot.plc",
    async (request, chatContext, stream, token) => {
      const apiUrl = vscode.workspace.getConfiguration("plcRag").get<string>("apiUrl", "http://localhost:8000");
      const mode: Mode = request.command === "generate" ? "generate" : request.command === "explain" ? "explain" : "ask";

      const editor = vscode.window.activeTextEditor;
      const code = editor && !editor.selection.isEmpty ? editor.document.getText(editor.selection) : "";

      const history = chatContext.history.flatMap((turn) => {
        if (turn instanceof vscode.ChatRequestTurn) {
          return [{ role: "user", content: turn.prompt }];
        }
        const text = (turn as vscode.ChatResponseTurn).response
          .filter((p): p is vscode.ChatResponseMarkdownPart => p instanceof vscode.ChatResponseMarkdownPart)
          .map((p) => p.value.value)
          .join("");
        return text ? [{ role: "assistant", content: text }] : [];
      });

      const abort = new AbortController();
      token.onCancellationRequested(() => abort.abort());

      let res: Response;
      try {
        res = await fetch(`${apiUrl}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: request.prompt, mode, history: history.slice(-4), code }),
          signal: abort.signal,
        });
      } catch (err) {
        stream.markdown(`Cannot reach the RAG service at ${apiUrl}. Is it running in WSL?\n\n${err}`);
        return;
      }
      if (!res.ok || !res.body) {
        stream.markdown(`RAG service error: HTTP ${res.status}`);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let sources: Source[] = [];
      let model = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";
        for (const ev of events) {
          if (!ev.startsWith("data: ")) {
            continue;
          }
          const msg = JSON.parse(ev.slice(6));
          if (msg.type === "sources") {
            sources = msg.sources;
            model = msg.model;
          } else if (msg.type === "token") {
            stream.markdown(msg.text);
          } else if (msg.type === "error") {
            stream.markdown(`\n\nError: ${msg.message}`);
          } else if (msg.type === "validation") {
            const summary = msg.status === "not_applicable" ? "No code generated" :
              msg.status === "warnings" ? "Static warnings" : "No issues found by limited static checks";
            stream.markdown(`\n\n**${summary}. Compilation not run.**\n`);
            for (const finding of msg.findings ?? []) {
              stream.markdown(`- ${finding.message}${finding.source ? ` (${finding.source})` : ""}\n`);
            }
          }
        }
      }

      stream.markdown(`\n\n_Answered locally by Ollama model \`${model}\`_\n`);
      if (sources.length) {
        stream.markdown("\n---\n**Sources**\n");
        for (const s of sources) {
          stream.markdown(`- [DOC ${s.n}] [${s.heading}](${s.url})\n`);
        }
      }
    }
  );
  context.subscriptions.push(participant);
}

export function deactivate() {}
