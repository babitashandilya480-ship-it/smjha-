# Troubleshooting

## Local application will not open
Run scripts/start.ps1 from the project root. Inspect artifacts/backend-error.log and artifacts/frontend-error.log.
If ports 8000 or 5173 are occupied, stop the prior servers. The launcher intentionally does not terminate arbitrary processes.
Use the manual two-terminal commands in README.md to see errors immediately.

## Cannot reach Ollama
Open the Ollama Windows app or run ollama serve. Check ollama list.
Visit http://127.0.0.1:11434/api/tags locally to see installed model names.
Ollama on a remote server's localhost would be that server, not this laptop. This build is deliberately a local desktop deployment.

## Model missing
Run ollama pull qwen3:4b after allowing about 2.5 GB for the weights. Restart the backend after changing backend/.env.
There is no hosted-provider fallback.

## Timeout or out of memory
Stop the separate training process or other GPU-heavy apps, close duplicate model sessions, and retry a shorter question.
Use ollama ps while a response is running; PROCESSOR reports GPU/CPU placement. Use nvidia-smi to inspect VRAM.
The configured context and output are bounded. Do not assume model file size equals runtime memory.
Use a smaller explicitly configured local model if needed; the application will never switch models silently.

## Invalid feedback / retry state
The local model sometimes returns incomplete or unsuitable structured feedback. The app repairs once, then shows a retry state and saves no successful response.
Try a shorter question. Do not repeatedly click Submit. An AI answer can still be scientifically wrong even when its JSON validates.
Numerical F=ma checks are deliberately narrow; ambiguous or unsupported questions are clarified or handled by the model.

## PDF rejected
A text PDF must contain selectable, meaningful text on every page. Image-only, blank, password-protected, damaged and partially unreadable PDFs are rejected.
Export a fresh PDF or remove blank/scanned pages in your own document editor. OCR is not installed.
Copy-and-paste extraction can reorder equations and tables. Always inspect the exact passage.
“No supporting passage found” means word-overlap retrieval did not find a relevant chunk.

## Database could not be saved
Check free disk space, file permissions and whether another tool has locked data/samjha.sqlite3.
Do not delete the database to fix an error without first exporting or backing it up.
A failed request is not counted as a successful question.

## Browser tests
Stop manually started Samjha servers before npx playwright test. Tests start their own isolated database.
The checked-in configuration uses the installed msedge channel. If Edge is unavailable, install a compatible Playwright browser explicitly and update the channel.
