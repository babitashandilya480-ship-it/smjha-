# P0 repository audit — restarted implementation
Date: 22 September 2026. Scope: the actual local repository at C:\Users\admin\samjha_ai.

## Evidence and baseline
The supplied master brief's "no actual application identified" described other inspected archives. This workspace contains a real application.
- backend/main.py imports samjha.api. backend/samjha/api.py implements a local FastAPI learning API.
- backend/samjha/inference.py calls local Ollama and constrains the old system prompt to Class 9 Force and Laws of Motion.
- backend/samjha/schema.sql and db.py implement SQLite guest preferences, interactions, mistakes, revisions, retries, documents and chunks. There is no tenant owner column in those legacy tables.
- frontend/samjha-frontend/src/App.tsx provides Home, Learn, Mistakes, Progress and Settings. Its package-lock.json locks the existing React/Vite toolchain.
- backend/requirements.txt pins direct Python packages. The README referenced a missing requirements-lock.txt; an installed-environment snapshot is now provided. This is not a hash-verified supply-chain lock.
- tests/test_core.py, test_boundaries.py and test_memory.py provide 51 baseline passing backend tests (executed during this audit).
- scripts/start.ps1 and stop.ps1 manage loopback app processes. There is no production deployment, hosted identity provider, PostgreSQL service, durable distributed worker, or staging environment established here.
- training/ and third_party/ contain separate educational integrations. They were preserved and are not used as the new chat model.
- data/samjha.sqlite3 existed (73,728 bytes at inspection). Its private contents were not copied into prompts or new accounts.
- git status reported no Git repository. No branch, commit or remote publication was performed.
- No project AGENTS.md was found in the inspected source trees. The user-supplied RTK.md requires rtk-prefixed shell commands.

## Disposition
| Area | Baseline | This increment |
|---|---|---|
| Learning / PDF notes / notebook | Implemented for one shared local guest | Preserved; four legacy browser journeys pass |
| General chat | Missing | Beta at /chat |
| Auth and owned chat history | Missing | Local accounts and a separate chat database |
| Streaming to browser | Learning response buffered | Persisted sequenced SSE for new chat |
| Model gateway | Ollama only | Local adapter plus explicit Cheaper Inference adapter |
| Hyper research / citations | Missing | Planned; not presented as available |
| Work / artifacts / sandbox | Missing | Planned; no tools execute in Chat |
| Durable memory | Optional legacy learning observations | Off / unavailable in new Chat |
| Cloud live behavior | Unverifiable | Contract fixtures pass; replacement key and budget needed |
| Deployment / human evaluation | Missing | Release blockers documented |

## Migration decision
Preserve the learning API, routes and all legacy records. Add a separate data/samjha-chat.sqlite3 by default; do not guess ownership of guest records. New accounts cannot read each other's new-chat records. The old guest area is still a shared loopback-only app and is explicitly labeled as such: this is not a multi-tenant deployment of the whole product.

The new SQL migration is backend/samjha/foundation_schema.sql. It creates only the new database's tables, version marker, constraints and indexes. Existing guest data has no migration or destructive rewrite. Source originals and a patch are in artifacts/p1-backup-20260922-214057.

## Decisions and unresolved gates
1. Reuse the existing React / TypeScript / FastAPI stack. No new runtime dependency was required.
2. SQLite is a reversible local-beta choice, not the specified production PostgreSQL architecture. Accounts currently own conversations directly; workspaces, memberships and project sharing remain unimplemented.
3. One ASGI worker shares the existing inference gate with the learning flow. Events survive reconnects. Interrupted runs fail honestly at startup; there is no automatic replay or distributed recovery.
4. Local is the default and cannot silently switch to cloud. Processing is fixed when creating a conversation.
5. Cloud requests are disabled until configured. A lifetime request allowance is enforced locally. A monetary hard cap must be set on the provider key; app-side billed-cost reconciliation is not implemented.
6. General chat uses no files, search, tools, inferred memory or model training.
7. Password recovery, production identity, HTTPS deployment, encrypted-at-rest storage, comprehensive accessibility review, and the 300-task reviewed benchmark are not complete.
8. English and Hinglish smoke examples are original development inputs, not a human-reviewed capability benchmark.

This audit is P0 engineering evidence, not completion of every P0 exit criterion or a production-readiness assertion.
