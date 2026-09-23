# Local beta operations and rollback

## Start and use
From the project root:
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start.ps1

General Chat: http://127.0.0.1:5173/chat
Preserved guest learning: http://127.0.0.1:5173/
Stop: scripts/stop.ps1

Do not use scripts/p1_browser_app.py for real usage: it is an explicitly synthetic test service. Do not run multiple ASGI workers. Keep the production backend entrypoint backend/main.py.

## Files
Guest history: data/samjha.sqlite3 (unchanged).
New chat accounts/history: data/samjha-chat.sqlite3 by default.
Cloud secret: backend/.env.cloud.
Backups and tests: artifacts/.
SAMJHA_CHAT_DB can override the new DB path; keep it separate from SAMJHA_DB.

Passwords cannot currently be recovered. Export important chats from Settings & capabilities. Exports contain private text; protect them.

## Verification commands
    .\.venv\Scripts\python.exe -m pytest tests -q
    .\.venv\Scripts\python.exe scripts/p1_live_smoke.py
    cd frontend/samjha-frontend
    npm.cmd run build
    npx.cmd playwright test
    npx.cmd playwright test --config playwright.foundation.config.ts

Browser suites use isolated databases and refuse to reuse an existing server. Stop normal app servers first. The foundation browser suite is synthetic; p1_live_smoke.py tests real local Ollama with temporary accounts and original test prompts. Neither sends cloud requests.

requirements-lock.txt snapshots the installed backend environment. Recreating it on other operating systems has not been verified.

## Failure handling
- Local model unavailable: open Ollama; confirm the configured qwen3:4b exists. Chat fails clearly and never falls back to cloud.
- Cloud unavailable: check the replacement key, model permissions, balance, cap and request allowance locally. Do not post the key in logs or support messages.
- Interrupted stream: EventSource reconnects with the event cursor; reconnecting does not create a new inference.
- Restarted backend: unfinished runs become failed with retained partial events. Retry intentionally with a new request.
- Busy: stop the active model request or let its timeout expire. Learning and general chat share one model slot.
- Disk/database failure: stop app, preserve the database, check disk space, and restore a verified copy if required. Do not delete data to clear an error.
- Leaked key: revoke with the provider, replace local configuration and restart. Inspect provider usage separately.
- Cost risk: disable CI_ENABLED immediately, stop active cloud requests, and enforce the provider key cap. Local allowance counts uncertain attempts conservatively; it is not a monetary ledger.
- Account deletion: stop active requests then delete via Settings. Cascades remove new-chat content; guest history, exports, external provider records and backups remain.

## Backups and rollback
Original changed files from the installation are in artifacts/p1-backup-20260922-214057 with changes.patch and manifest.json. That initial patch predates test-driven refinements; use the final patch in artifacts/p1-final.patch for review.

To temporarily hide the new UI, set VITE_CHAT_FOUNDATION=false in the frontend environment and restart Vite/rebuild. The original routes remain accessible.
For code rollback: stop servers; restore original api.py, main.tsx, App.tsx and .gitignore from the backup; restore any additional reviewed changes as needed. Leave both databases intact. Newly added modules may remain unused.
The new database is separate; no destructive guest migration needs reversing.

Back up SQLite using sqlite3's backup API or while the app is stopped. Backup encryption, periodic scheduling, expiry, restoration drill, production RPO/RTO and incident ownership remain release gates. A source-code backup is not a tested database backup strategy.
