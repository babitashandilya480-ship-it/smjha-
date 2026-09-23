# Samjha integration, 2026-09-22

The three supplied archives are combined by responsibility:

| Source | Use in Samjha |
|---|---|
| Sebastian Raschka, LLMs-from-scratch | GPT architecture in `training/model.py`, with original source and Apache license retained. |
| Hector Hernandez, llm-training-from-scratch | Real backward hardware checks and dated run records adapted as a smaller native Windows lab. Original diagnostic scripts and MIT notices retained for reference. |
| Intertwine Systems, grok-observational-memory | Bounded, inspectable local context pattern adapted to Samjha's notebook. Original docs and MIT license retained. No Grok hooks or external OM service installed. |

The Grok archive describes itself as unmaintained legacy software and contains a wrapper, not the core memory engine. The training curriculum is a notebook, not another pretrained model. Combining these repositories does not merge trained weights or establish better answer accuracy.

## Tutor and learning memory

Supported arithmetic uses the existing deterministic checker. Other teaching requests use the configured local Qwen model; selected PDFs supply retrieved evidence. Experimental GPT weights never answer students.

Enable Learning memory under Settings and save preferences. `/api/memory` shows observations and source notebook IDs. Memory groups the latest 30 unflagged saved mistakes by category and reflects only the most recent retry per item. It supplies category counts, never raw notebook text, to non-document model prompts. Current question, current language and rubric take precedence. Optional memory is omitted when prompt space is tight. PDF questions do not use cross-topic memory.

Memory starts off for existing and new profiles. It has no duplicate persistent store: edits, flags, deletions and document cascades update observations on the next read. Export already contains all underlying preferences, mistakes and retries. Turning memory off stops use but retains the notebook. Clearing learning history removes all source records. Saved notebook entries still survive conversation deletion as documented before.

This is deterministic observation/reflection over practice records, not an LLM observer, semantic search or an assessment of mastery. It reads no Grok, Codex or other agent histories.

## Training lab

From `C:\Users\admin\samjha_ai` use the existing training environment:

```powershell
rtk proxy C:\Users\admin\lm-training\.venv\Scripts\python.exe -m training.lab --device cpu --steps 30
rtk proxy C:\Users\admin\lm-training\.venv\Scripts\python.exe -m unittest training.test_lab -v
```

This trains the adapted Raschka GPT from random weights on a small original demonstration corpus with UTF-8 byte tokens. Defaults: two layers, width 64, context 32, CPU. `--device cuda` explicitly chooses the GPU. No dependency, corpus or weight download occurs. Training dependencies stay outside the web backend environment. PyTorch is required; use a build suitable for the machine when recreating the environment.

Use `--train path --validation path --steps N --out new-directory` for another explicitly prepared text corpus. Exact duplicate lines across splits are rejected; this does not detect semantic leakage. Output directories are never overwritten. Reports include data hashes, seed, hardware, losses and checkpoint reload verification. `artifacts/training-runs.jsonl` records dated runs. Checkpoints are inference snapshots, not optimizer/RNG resume checkpoints. The existing larger `lm-training` experiment remains separately resumable with its original commands.

The demo is an engineering smoke test, not a useful trained tutor or a claim of Hindi proficiency. Synthetic model output is labelled unvalidated. No private student database is used for training.

## Verification commands

```powershell
rtk proxy .\.venv\Scripts\python.exe -m pytest tests -q
cd frontend\samjha-frontend
rtk proxy npm.cmd run build
rtk proxy npx.cmd playwright test
```

Browser tests require the normal Samjha servers to be stopped and use an isolated test database. Tests cover preference persistence, memory provenance, latest-retry reflection, flag/edit/delete invalidation, prompt handling, deterministic routing, causal attention, tokenization, real backward execution, loss decrease and checkpoint reload. Automated memory tests mock Qwen and do not measure its teaching quality.

See `third_party/manifest.json` for selected archive file hashes and retained licenses. Files changed by this integration are backed up under `artifacts/integration-backup-*`.

## Observed results

On 2026-09-22: 51 backend tests, 8 training tests and 4 Edge browser tests passed. The final frontend production build passed. Mobile Settings screenshot was inspected. Restarted app returned HTTP 200; Qwen health reported ready. All 9 selected original archive files match their SHA-256 manifest.

A 30-step CPU run trained 134,528 parameters from random weights: training loss 5.6566 to 2.3174, validation loss 5.6820 to 3.0857. Checkpoint reload reproduced logits exactly. See `artifacts/scratch-20260922-165110-715457/report.json`. These tiny-corpus results are engineering validation only.

Live synthetic inference with memory context and exact output are recorded in `docs/integration-verification.json`. The automated suite emitted two pre-existing dependency deprecation warnings.
