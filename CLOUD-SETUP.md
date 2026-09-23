# Cheaper Inference: chat and design/coding helper

The user supplied https://api.cheaperinference.com/v1. This is Cheaper Inference, not an OmniRoute deployment. Both integrations use its documented Chat Completions SSE endpoint.

## Configuration
1. Revoke the key posted in the conversation and create a replacement in the provider dashboard.
2. Set a hard spending cap on that provider key. Limit its model access and expiry as appropriate.
3. Open backend/.env.cloud locally. It is ignored by Git; never put the key in the frontend or a VITE_ variable.
4. Fill CI_API_KEY. CI_MODEL defaults to gpt-5.6-luna as an initial inexpensive catalog candidate, not a verified recommendation. Inspect the current account catalog before first inference.
5. Leave CI_ENABLED=false and CI_MAX_REQUESTS=0 until ready. To enable, set CI_ENABLED=true and a small CI_MAX_REQUESTS allowance. This is a cumulative attempted-request allowance shared by chat and the development helper, not a dollar limit.
6. Restart the app to load changed configuration.

Do not paste a key into chat or command-line arguments. No secret from the conversation was written to project files. No cloud inference was run during this increment.

## Inspect available models (read-only)
From C:\Users\admin\samjha_ai:
    .\.venv\Scripts\python.exe scripts\design_review.py --models

This requires a locally saved replacement key. The catalog request filters for streaming text and ZDR-capable availability. Review exact model, prices, pricing version, region and account permissions. The provider may change inventory; the template model is provisional.

## Use in Samjha
Start with scripts/start.ps1, then open http://127.0.0.1:5173/chat.
Create a local account. For a new conversation choose Processing → Cloud · Cheaper Inference.
The label explains that conversation messages leave this computer. Local conversations cannot be switched to cloud; create a new one. Cloud availability in the UI means configured, not live-verified.

The adapter requests zdr=true, min_discount_percent=0 and a bounded max_tokens value. Its request shape must still be smoke-tested with the selected model. A provider accepting one compatible API does not establish all feature support. No unsupported tools, automatic fallback, image input or Pro mode is requested.

## Use for design and code review
Dry run (sends nothing):
    .\.venv\Scripts\python.exe scripts\design_review.py --prompt "Review this button design for keyboard accessibility."

Explicitly selected source:
    .\.venv\Scripts\python.exe scripts\design_review.py --prompt "Review this CSS excerpt" --file frontend/samjha-frontend/src/index.css

After reviewing the prompt, selected files and spending controls, add --send. That flag sends exactly the listed content to the cloud provider and saves a model response under artifacts/design-reviews/. It does not execute tools, modify source files or validate proposed code. A human/agent must review and test any suggested patch.

The helper rejects .env files, private runtime directories, paths outside the project, oversize inputs and common secret patterns. Never rely solely on pattern detection for sensitive source. Keep total context small; select an excerpt for large files.

## Evidence and open gate
Deterministic tests cover payload shape, secret-safe errors, invalid streams, missing completion, request allowance, no retry and explicit local-only routing. Real cloud model listing and inference were not performed because a replacement key and approved spending configuration have not been supplied.

Official sources checked 22 September 2026:
- https://www.cheaperinference.com/docs
- https://www.cheaperinference.com/api-reference
- https://www.cheaperinference.com/legal/privacy
- https://www.cheaperinference.com/legal/subprocessors

Provider policy statements are provider assertions, not an independent privacy audit. Regional deployment and the exact upstream route remain unverified.
