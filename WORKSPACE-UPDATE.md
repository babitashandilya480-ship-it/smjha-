# Workspace update - 23 September 2026

## Latest sidebar and fourth-PDF update

- Added consistent Home, Learn, Mistakes, Samjha, Settings navigation and the `/samjha` chat route; `/home`, `/education`, and `/chat` remain accessible.
- Removed class/subject restrictions from the served Home, Learn, Mistakes, Settings, and chat interfaces. Removed the learning system prompt's physics-only rejection and unrelated demonstration checklist injection. New saved mistakes use general metadata; progress shows actual attempted questions.
- Added `LLMs_and_GPT6_Astra_Agent_Prompting.pdf` to the supplied reference index. Its blank second page has no text or images and is retained in numbering, so the five-part framework is cited as PDF page 3.
- Applied result-first, task-completion, assumption-checking guidance to Work mode within its actual text-only capabilities.
- Verification: 80 backend tests and 6 browser tests passed; TypeScript/production build passed. A real local Learn request explained Python dictionaries, and a real Work request returned all five framework labels from the new PDF with a page-3 citation. See `artifacts/general-workspace-live-check.json`.
- Use Home > Samjha > Document library > Add all 4 supplied PDFs. Existing imported documents are reused; the new guide is added to the signed-in account.

The sections below record the preceding three-PDF redesign and speed investigation.

## Delivered

- General-purpose workspace and split-panel sign-in, responsive at 320 through 1920 pixels.
- Chat, Hyper, and Work modes, streamed responses, owned history, cancellation, copy/reuse, and saved timing.
- All three supplied PDFs indexed once with page attribution. Library import is idempotent. A user can choose one document or ask across the library.
- Wider overlapping passages preserve short lists. A real test caught a missing third stage in the training explainer; passage expansion fixed the observed answer.
- Prompt instructions require attribution, page citations, and explicit handling of missing evidence. Sources remain inspectable after reloading.
- Quick replies use the installed instruct model. Hyper Balanced/Thorough retains the reasoning model. Small output tokens are coalesced into database events, with the first answer persisted immediately.

## Actual model mapping

| Mode | Quick | Balanced / Thorough |
| --- | --- | --- |
| Chat | qwen3:4b-instruct | qwen3:4b-instruct |
| Hyper | qwen3:4b-instruct | qwen3:4b, thinking enabled |
| Work | qwen3:4b-instruct | qwen3:4b-instruct |

The two tags were already installed. No model downloads, provider-key changes, paid cloud calls, fine-tuning, or weight training were performed. The PDFs are reference sources, not trained weights. The application cannot acquire a frontier model's capability from its system-card summary.

## Speed investigation

The installed `qwen3:4b` Go template unconditionally ends with an open `<think>` block. With `think:false`, a baseline Chat/Work request emitted reasoning as answer text and used all 256 output tokens before completing the answer. The installed instruct template returned the requested answer directly.

Same simple question (18/20 as a percentage), Quick, one local sample per mode:

| Mode | Before, total seconds | After, total seconds | After, first text seconds |
| --- | ---: | ---: | ---: |
| Chat | 11.736 | 3.048 | 1.697 |
| Hyper | 10.999 | 0.746 | 0.456 |
| Work | 6.309 | 0.676 | 0.400 |

These are smoke measurements, not a controlled benchmark. The first baseline model was cold, cache state differs, and response lengths changed. Long prompts, GPU contention, switching model tags, and extended reasoning can be slower. Raw reports are in `artifacts/latency-before.json` and `artifacts/latency-after.json`.

API controls and timing fields were checked against [Ollama chat API](https://docs.ollama.com/api/chat) and [thinking controls](https://docs.ollama.com/capabilities/thinking).

## Verification

- `python -m pytest tests -q`: 80 passed. Includes cross-account PDF access, cross-document evidence, mode routing, streamed text preservation, and timing persistence. Two dependency deprecation warnings remain.
- `npm run build`: passed TypeScript and production build.
- `npx playwright test --config playwright.foundation.config.ts`: 5 passed. Covers authenticated streaming, reload, cancellation/failure, safe rendering, keyboard send, document import, and mobile/desktop reflow. Uses clearly labeled synthetic model output and isolated databases.
- `python scripts/verify_supplied_pdf_chat.py`: actual local model answers using each reference, a Hyper reasoning calculation, and a cross-document summary. Report: `artifacts/supplied-pdf-live-check.json`. Sources, generated answers, model names, and timings are retained for review.
- Desktop sign-in, welcome, model page, conversation, and mobile document layouts visually inspected from browser screenshots under `artifacts/workspace-*.png`.

All five live cases completed and included page references present in the supplied evidence. The test accepts equivalent bracketed/parenthesized citations; this verifies page references, not every claim's entailment. Final single-document Quick cases took 2.8-3.7 seconds. Extended Hyper reasoning took 46.1 seconds, including 5.0 seconds loading the model. The all-document Quick summary took 10.2 seconds, including 5.1 seconds switching back to the instruct model. These limits are visible in the saved per-answer timings.

## Use and limits

Run `scripts/start.ps1`, open `/chat`, sign in, and select Document library > Add all 3 supplied PDFs. In Conversations choose the reference and mode, then send a question. Choose Quick for low latency. Each answer exposes supporting passages and timing; the first request may load the model.

Retrieval is local lexical matching with bounded excerpts, not semantic embedding search. It may miss relevant passages or context; citations do not guarantee correctness. Some source PDFs contain missing subscript glyphs in formulas; no reconstructed formula is represented as verbatim source text. Cross-document summaries use selected excerpts, not a full-document read. Cloud routing remains optional and subject to the existing disabled-by-default configuration. Public multi-user deployment, external actions, new model training, and a production security audit are outside this update.
