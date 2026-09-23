# Architecture

React + TypeScript + Vite → same-origin /api proxy → FastAPI → local Ollama /api/chat.
FastAPI uses SQLite transactions through Python's standard sqlite3 module.

Active backend is backend/main.py → backend/samjha/api.py. The older backend/app tree is retained but is not imported by the running app.
schemas.py validates requests and feedback; physics.py performs a narrow safe arithmetic F=ma check.
inference.py supplies task-specific prompts, original chapter checklists and a JSON output schema.
A single inference lock returns a clear busy state. The backend consumes Ollama's stream but buffers it until the full structured response validates; the frontend does not display partial JSON.
Cancellation closes the local HTTP stream and avoids late UI updates. A cancelled HTTP connection is not proof that Ollama released VRAM immediately.
There is one repair attempt, bounded context/output, a total inference timeout and no hosted fallback.

db.py and schema.sql implement durable storage, foreign-key cascades, idempotent submission IDs, notebook uniqueness and derived progress.
Preferences and history survive refresh. Drafts are browser-local.
Progress is derived from successful stored operations; edits invalidate retries describing old material.
Each notebook entry retains original question, answer, category, correction, source passages, retry question, timestamps and scheduling history.

documents.py accepts PDFs only and uses a bounded parser subprocess in pdf_worker.py.
Extracted text is stored in SQLite chunks with document identity and PDF page positions. Retrieval is lexical overlap, not semantic search.
No vector database, shell tool or arbitrary file/network capability is exposed to the model.
Uploaded text is explicitly untrusted data in the prompt. That boundary is tested; semantic prompt-injection resistance is not guaranteed.

The browser renders all response text as React text nodes. Raw HTML and model Markdown are not executed.
CORS is restricted to known localhost origins, mutating requests require a custom local header, and trusted host names are restricted.
Request bodies and input fields have size limits. SQL values use parameters.
One guest profile is shared by everyone who can access this local process. There is no account isolation or authentication.

The independent training project builds a byte-level BPE tokenizer and a small randomly initialized GPT-2 architecture.
Its corpus, tokens, model weights and metrics never enter the Samjha inference path.

Final inference budget: 8192 context tokens, 750 maximum generated tokens, and a conservative 6800 UTF-8-byte cap across serialized messages and schema. Oversized requests receive a specific context-limit error. The initial live measurements used 4096 context; final configuration verification is recorded separately.
