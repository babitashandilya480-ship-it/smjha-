# Attribution and dependency notices

Samjha application source retains the existing MIT licence in LICENSE.
Qwen3 is developed by the Qwen team, not by Samjha. The Ollama qwen3:4b model page lists Apache 2.0 and a roughly 2.5 GB Q4_K_M download:
https://ollama.com/library/qwen3:4b
Ollama is an independent local inference project: https://github.com/ollama/ollama .

Main application dependencies: React (MIT), TypeScript (Apache 2.0), Vite (MIT), React Router (MIT), FastAPI (MIT), Pydantic (MIT), HTTPX (BSD), Uvicorn (BSD), python-dotenv (BSD), python-multipart (Apache 2.0), pypdf (BSD), pytest (MIT), Playwright (Apache 2.0).
Consult the installed packages' own licence files for authoritative full terms and transitive dependencies.
No external font or stock-image service is used in the active UI.

The independent training corpus is wikimedia/wikipedia, 20231101.en.
The dataset card labels CC BY-SA 3.0 and GFDL: https://huggingface.co/datasets/wikimedia/wikipedia .
The local manifest records the dataset revision, and each raw article records its title and source URL for attribution.
This is licensed Wikipedia text, not public-domain text. Review reuse obligations before redistribution.
The trained tiny GPT-2 experiment is not the Qwen model and is not a dependable student chatbot.

Original chapter checklists, practice questions and evaluation expectations are demonstration material, not teacher-reviewed curriculum.
No supplied textbook edition, board alignment, endorsement or guaranteed exam performance is claimed.


## Supplied archive integration

GPT model code is adapted from Sebastian Raschka (2023-2026), Apache 2.0. Training workflow draws on Hector Hernandez (2026), MIT. Local bounded memory design draws on Intertwine Systems (2026), MIT. Full licenses and selected originals are in `third_party/`; exact source hashes in `third_party/manifest.json`. See `docs/INTEGRATION.md` for the distinction between reused code and adapted design.
