# Samjha AI workspace

Open **http://127.0.0.1:5173/chat** after running `scripts/start.ps1`.
Chat supports opt-in web research through Tavily (only the current question is sent; linked result snippets are cited), Hyper mode for deeper reasoning, and an optional second-stage review that makes three sequential review passes. Add `TAVILY_API_KEY` to `backend/.env.cloud` and restart Samjha to enable web research. The review can take longer and uses up to four model calls; cloud mode may consume additional provider allowance. Turn it off for faster replies. The supplied Model Research & Evaluation Questions PDF is included in the local document index.
The requested sidebar is available at **http://127.0.0.1:5173/home**: Home, Learn, Mistakes, Samjha, and Settings. **http://127.0.0.1:5173/samjha** opens the chatbot directly; `/chat` remains compatible. Class-specific labels and the backend's physics-only restriction have been removed.
The default experience is a general-purpose workspace for conversation, writing, coding, and document questions, with a responsive navigation rail, chat history, document library, three working modes, streaming, and per-answer timing.

Choose **Continue as guest** to chat without creating an account; guest chats and documents are shared on this local computer. You can also sign in or create a local account. Open **Document library** and choose **Add all supplied PDFs**. The bundle includes LLM Testing and Evaluation (3 pages), GPT-6 Astra - System Card Summary (4 pages), How Frontier LLMs Are Built (5 pages), Understanding LLMs & Building an Astra-Style Agent (5 pages), and Model Research & Evaluation Questions (10 pages). Select one PDF or **All documents** in the composer. Supporting passages retain the document title and original PDF page. The system-card PDF is a user-supplied independent summary; indexing it does not authenticate its claims.

Work-mode instructions apply the prompting guide's useful structure: identify the deliverable, work through the task, check assumptions, and lead with the result. The app does not claim browsing, execution, or file-writing tools it does not have. Learn now answers general questions without injecting a physics checklist.

Chat, Hyper Quick, and Work now use the installed `qwen3:4b-instruct` model. Hyper Balanced/Thorough uses `qwen3:4b` with extended reasoning. These are three modes backed by two installed model tags, not three freshly trained models. The original Qwen template begins a thinking block even when thinking output is disabled; switching direct answers to the instruct template prevents reasoning text from consuming their output budget. Model names remain configurable through `SAMJHA_MODEL_CHAT`, `SAMJHA_MODEL_WORK`, `SAMJHA_MODEL_HYPER`, and optional `SAMJHA_MODEL_HYPER_QUICK`.

PDF extraction is performed once, then locally stored passages are retrieved per question. No fine-tuning or model-weight training was performed. Quick answers are concise; cold model loading and extended reasoning still take time. Saved answers show first-text time, total time, generation rate, and significant model-load time.

See [workspace verification and limitations](docs/WORKSPACE-UPDATE.md). The app runs locally; this update does not publish a public website.

## Earlier Chat foundation

Open **http://127.0.0.1:5173/chat** after starting the app with scripts/start.ps1.
General Chat is also the default at /. The optional legacy education section remains available at /education.
General Chat adds local accounts, streamed answers and owned chat history in a separate database.
Cheaper Inference is wired for Chat and the explicit-file design/code review helper, but is disabled until a replacement key and spending controls are configured locally.

- [Fresh repository audit](docs/P0-AUDIT.md)
- [Cloud setup and design helper](docs/CLOUD-SETUP.md)
- [P1 verification and open release gates](docs/P1-VERIFICATION.md)
- [Architecture and threat model](docs/P1-ARCHITECTURE.md)
- [Operations and rollback](docs/P1-OPERATIONS.md)

The documentation below applies to the preserved guest learning experience, not the cloud Chat route.

---

# Samjha AI — local learning prototype

Samjha helps a student ask a doubt, check a written answer, save a mistake and retry it later.
The current topic is **Force and Laws of Motion**, approximately Class 9. Hindi, Hinglish and English can be requested. Language consistency and scientific accuracy are imperfect; ask a teacher to review important feedback.

This application uses the existing **Qwen3 4B** model through local Ollama. It is not a model developed or trained by us. The separate language-model training experiment in `C:\Users\admin\lm-training` is not used to answer students.

## What is installed and what was verified

The working laptop has an NVIDIA GeForce RTX 3050 Laptop GPU with 6 GB VRAM, Python 3.14.7 and Node 26.7.0.
The existing `qwen3:4b` download is present. Initial live inference used the GPU; `ollama ps` reported 100% GPU at a 4096-token context.
Backend dependencies were installed in this project's `.venv`. Frontend packages are locked in `package-lock.json`.

See [verification](docs/VERIFICATION.md) for actual test results and [model evaluation](docs/live-evaluation-baseline.json) for observed failures. Installation instructions below describe recreation; they are not claims that every possible Windows configuration was tested.

## Start on this laptop

Open PowerShell in **C:\Users\admin\samjha_ai**:

```powershell
cd C:\Users\admin\samjha_ai
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start.ps1
```

Open **http://127.0.0.1:5173**. The start script launches the two local servers without visible terminal windows and writes their logs under `artifacts`.
Keep the Ollama Windows app running. If it is not already serving, run `ollama serve` in a separate terminal.
An “address already in use” message from Ollama usually means it is already running; use `ollama list` to check.

Stop the app with:

```powershell
cd C:\Users\admin\samjha_ai
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop.ps1
```

This stops only the recorded Samjha processes. It leaves Ollama running. Use `ollama stop qwen3:4b` to unload that model, or quit the Ollama app to stop its service.
The execution-policy option applies to that process only; it does not change the machine policy.

## Install on another Windows machine

Install a supported Python (this build was tested with 3.14), Node.js (Vite 8 requires a compatible recent release; use Node 22.12+ or a compatible current release), and Ollama from their official sites.
Keep the NVIDIA driver current. An Ollama installation does not require a separate CUDA toolkit.

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-lock.txt
Copy-Item backend\.env.example backend\.env
cd frontend\samjha-frontend
npm.cmd ci
cd ..\..
```

Do not overwrite an existing `backend\.env`; edit it if needed. No API keys are required.
The backend accepts only a local Ollama URL. It never switches to a cloud response provider.

The default model is about **2.5 GB on disk**; runtime memory is higher. On a new machine, allow several additional GB of disk space for dependencies and model storage. Download only after considering that size:

```powershell
ollama pull qwen3:4b
ollama list
```

Official references: https://ollama.com/library/qwen3:4b and https://docs.ollama.com/api/chat .
The model and dependency downloads need internet. Normal app inference, database operations, fonts and assets use local resources after installation. This is not a certified fully-offline or network-isolated product.

## Manual startup, if the launcher fails

Terminal 1, project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
cd C:\Users\admin\samjha_ai\frontend\samjha-frontend
npm.cmd run dev
```

Open http://127.0.0.1:5173 . Keep both terminals open. Ctrl+C stops each server.
Never bind this prototype or Ollama to a public interface.

## Learning workflow

1. Choose a language and optional daily study time. There is one local guest profile.
2. Use Learn for a doubt, an answer check, or an experimental teach-back.
3. Read **Samjho** and **Answer likho**. “Checked with code” applies only to the narrowly supported F=ma calculation.
4. Explicitly save feedback to the mistake notebook. Saving is idempotent for the same response.
5. Start a revision session of up to three unflagged saved mistakes.
6. A retry assessed incorrect or needing clarification is due again after one day. A correct retry doubles the interval, at least two days and at most 30. Early revision is allowed.
7. Flag questionable feedback. Flagged entries are excluded from revision and improvement counts until edited.

One successful retry does not establish mastery. Progress counts recorded activity, not intelligence, confidence or predicted marks.
Model-generated correctness is an assessment that may be wrong.

## PDFs and sources

Settings accepts authorised text PDFs up to 10 MB, 100 pages and 2 million extracted characters.
Document title, edition (if known), permission statement and PDF page positions are retained. Originals are parsed in memory in a separate process; uploaded filenames are not used for filesystem paths.
Repeated page-edge headers may be removed. Tables and equations may be reordered by extraction.
Blank, scanned, encrypted, corrupt, partially unreadable or oversized files are rejected. No OCR is included.

Select a document in Learn. Retrieval uses simple word overlap and passes a small number of passages, not an entire book.
Open **Supporting sources** to inspect exact extracted text. “PDF page” means file position; a PDF page label is not a verified printed page number.
A citation is not proof that every generated claim is supported. If no passage matches, the app asks for a better query rather than fabricating evidence.
Document-supported question-bank generation is not implemented.

## Data, export and deletion

- Durable preferences, successful responses, mistakes, retries and extracted passages: `data\samjha.sqlite3`.
- Unsaved question/answer drafts and current conversation ID: browser localStorage keys beginning `samjha_v2_`.
- Logs and browser test artifacts: `artifacts\`; synthetic evaluation reports: `docs\`.
- Model weights: managed separately by Ollama (normally under the user's `.ollama` directory).

Settings → Export personal data downloads JSON. Protect that export as private data.
Delete conversation removes conversation history while retaining an explicitly saved notebook entry and its source answer.
Delete a mistake also removes its retries; progress is recalculated.
Deleting a document removes extracted chunks and document-based responses, related mistakes and retries.
Delete saved learning history clears the SQLite application records and this browser's Samjha drafts and preferences.
Exports, external original PDFs, browser backups, source backups and Ollama weights are not deleted by these actions. SSD-level forensic erasure is not claimed.

Old source files were preserved in `docs/source-backup-20260922` before changes. They are ignored by Git.
Legacy browser records can be exported separately; they are not silently imported into real progress.

## Tests

From the root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
cd frontend\samjha-frontend
npm.cmd run build
npx.cmd playwright test
```

Browser tests use installed Microsoft Edge and an isolated `artifacts/browser-test.sqlite3`. Stop normal app servers before these tests; tests refuse to reuse them.
The browser tests use code-checked questions and one explicitly mocked cancellation failure. They do not prove Qwen's answer quality.

Separate real-model evaluation (stop GPU training first):

```powershell
cd C:\Users\admin\samjha_ai
.\.venv\Scripts\python.exe scripts\live_check.py --all
```

These synthetic examples do not populate the student's history. Expectations are original and not teacher reviewed.
Cases used to adjust prompts are regression cases, not an untouched held-out benchmark.

## Integrated memory and from-scratch lab

The three supplied repositories now contribute a GPT training lab, hardware/run checks, and optional local learning observations from saved mistakes. Enable Learning memory in Settings. See [integration and commands](docs/INTEGRATION.md). The experimental GPT does not replace the local Qwen tutor.

## More documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Known limitations and verification](docs/VERIFICATION.md)
- [Public deployment checklist](docs/PUBLIC_DEPLOYMENT.md)
- [Attribution](docs/NOTICES.md)

No remote repository has been created and no service has been published.
