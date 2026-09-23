# P1 architecture and threat model

## Data and execution
The legacy application remains in samjha.api. The optional frontend /chat route calls /api/v1. foundation_api.py validates accounts and ownership, foundation_store.py owns a separate SQLite database, and foundation_provider.py / cloud_provider.py implement model adapters.

The schema has users, hashed sessions, conversations, runs, messages, events and a migration version. Cloud calls have a separate metadata-only allowance ledger. Session tokens are random, stored as SHA-256 hashes, and carried in HttpOnly SameSite=Strict cookies scoped to /api/v1. Passwords use salted scrypt. Sessions expire after 12 hours.

SQL ownership checks precede conversation, run, stream, cancel, export and delete operations. Foreign keys prevent messages referencing another conversation's run. IDs are not authorization. There are no administrator conversation-reading endpoints.

POST submission uses a request UUID plus content hash. Reusing the same request returns the same run; changed content conflicts. An inference has a 60-second ceiling, a bounded input byte budget, 256/640/1024 output-token defaults, 24 KB response ceiling, 60 user requests/hour and one shared model slot. No automatic model-call retries occur.

An async task emits monotonic, schema-versioned events into SQLite. SSE reads persisted events and honors Last-Event-ID. Streaming connections recheck session validity. Completion inserts the final assistant message and terminal event in one transaction. Failure preserves the submitted prompt and partial event text. Only completed turns become context for later model calls. Input is rejected when context is full rather than silently truncated.

Cancellation first persists a terminal state then cancels the provider task. A task completion callback releases the model slot even when cancellation occurs before task entry. Upstream cancellation and billing cannot be guaranteed by disconnecting.

## Security boundaries
- Loopback only, one ASGI worker. Do not deploy this beta to a network interface.
- The legacy guest APIs remain shared. New account isolation is not retroactively applied to them.
- Existing origin/host checks and required custom mutation header protect browser requests. Responses under /api/v1 are no-store.
- Cookie Secure is not used on this HTTP loopback beta. HTTPS + Secure cookies, stronger session lifecycle and production identity are predeployment requirements.
- New prompts never load the guest notebook, uploaded files or automatic memories.
- Model output renders as React text with simple fenced-code formatting; raw HTML does not execute.
- The cloud base URL is fixed to the user-authorized HTTPS endpoint. HTTP redirects and environment proxies are disabled. Keys stay in the backend; provider response bodies are not exposed in errors.
- Local endpoint policy accepts only loopback HTTP. There is no local-to-cloud fallback.
- The coding/design helper sends a supplied prompt and explicitly listed source files only. It rejects common secret patterns and sensitive paths; this is defense in depth, not proof of perfect secret detection. It saves advice as untrusted Markdown and never applies a patch or runs model-proposed commands.
- Deleting a chat account cascades through its sessions, conversations, messages, runs and event records. It does not erase previously exported files, provider records, backups or the separate guest learning database.
- Cloud usage records contain model/timing/usage metadata without user text. Provider-side retention, region, pricing and subprocessor policy still need account-specific review.

## Versioned API
All following paths are under /api/v1:
POST /auth/register, /auth/login, /auth/logout
GET /auth/me, /capabilities
GET/POST /conversations
GET /conversations/{id}
POST /conversations/{id}/messages
GET /runs/{id}, /runs/{id}/events
POST /runs/{id}/cancel
GET /export
DELETE /account

Events: run.started, text.delta, run.completed, run.failed, run.cancelled.
Each event includes schema_version=1, run_id, seq, type, timestamp and data.
Planned resume, branching, projects, uploads, sources, artifacts, memory and approval routes are not implemented. Hyper/Work cannot be submitted to this API.

## Known limits
No PostgreSQL row policies or workspace membership yet. No durable queue or worker lease: use a single worker; a restart marks interrupted runs failed exactly once. No external execution, uploads or research in Chat. The local request allowance is not a monetary billing guarantee; use a provider key hard spending cap before enabling cloud. No model quality or accessibility certification is claimed.
