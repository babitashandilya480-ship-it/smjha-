# P1 increment verification — 22 September 2026

Scope: local authenticated chat beta plus disabled-by-default Cheaper Inference wiring for chat and design/code reviews. This is not the full master specification and is not production ready.

## Executed
| Check | Result |
|---|---|
| Baseline backend suite before changes | 51 passed |
| Full backend suite including foundation/provider boundary tests | 73 passed, 2 dependency deprecation warnings |
| Frontend TypeScript + Vite build | Passed |
| New chat browser journeys, Edge, synthetic provider | 3 passed |
| Preserved learning browser journeys, Edge | 4 passed |
| Real local Qwen chat smoke | 2 completed responses, persisted user + assistant history |
| Design helper dry run | Passed; no network request |
| Desktop and mobile screenshot review | Performed; small sidebar account layout adjusted |
| Horizontal overflow at 320, 360, 768, 1280 and 1920 CSS px | No overflow in browser checks |

Real local model: qwen3:4b, Q4_K_M, digest 359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7.
Synthetic smoke requests: sunrise caption and Hinglish recursion explanation. Full request completion times: 12.74 s and 6.65 s. These are not first-token latency benchmarks or SLO evidence.
See artifacts/p1-live-smoke.json for synthetic prompts, actual outputs, model metadata and run records.

Backend coverage includes authentication/logout, cross-user conversation/run/event/cancel/export rejection, replay cursors, idempotency conflicts, final-message persistence, incomplete streams, cancellation, context rejection, unsupported modes, disabled cloud, local-only policy, CSRF/origin/body limits, account deletion, restart interruption handling, provider errors, cloud allowance and helper path/secret rejection.

UI tests cover sign-in, streamed fixture text, reload and history, original prompt preservation through "Reuse as draft", logout, Stop, provider failure, responsive layout, skip link and inert HTML rendering. The fixture output is visibly labeled. These tests do not prove model quality.

## Not verified / not implemented
- Cloud account catalog or live inference: no replacement key or spending configuration provided; no paid request made.
- Development/design model review: dry-run verified only; no external model output obtained.
- 300 reviewed benchmark tasks and untouched final holdout; human language/safety review.
- Automated accessibility scanner, manual screen-reader/200% text-zoom validation and full WCAG 2.2 AA audit.
- Hyper evidence pipeline, Work projects/artifacts, code sandbox, multimodal, new-chat uploads, opt-in memory, branch editing and durable distributed orchestration.
- OIDC, workspaces/membership, PostgreSQL/RLS, HTTPS deployment, staging, canary, load test, encrypted backup/restore drills, legal/age review and operational ownership.
- Exact cloud pricing/retention/region and billed-dollar reconciliation. Local request allowance is not a financial hard cap.
- Full Markdown/math rendering; current output is safely rendered text and fenced code.

## Release decision
Suitable for review as a local development increment. Keep cloud disabled until its setup gate passes. Do not enable public sign-up or expose legacy guest APIs. The broader P0/P1 release gates and all later phases remain open.

Next dependency: locally configure a rotated Cheaper Inference key with a provider-side spending cap, inspect its catalog, then authorize and record one small live cloud smoke request before using it for design reviews or user chats.
