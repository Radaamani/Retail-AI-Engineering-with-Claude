# OmniCommerceOps onboarding

Read [CODEBASE_GUIDE.md](CODEBASE_GUIDE.md), [README.md](README.md), and
[PROJECT_PROMPT.md](PROJECT_PROMPT.md) before changing this capstone.
The root [AGENTS.md](../AGENTS.md) applies too.

- Current app: two-round demand planning and promotion performance, with
  explicit supply receipts and shared stock. The old checkout is retired.
- Preserve explicit API/storage field vocabulary and the 280-row historical
  CSV exercise, which is separate from the live application seed.
- Keep `retail_math.py` pure, route handlers thin, and Streamlit behind
  `ui/http_api_client.py`.
- Public views hide the preset selected demand until a sales run; clients may
  submit decisions but not calculated outcomes or selected scenarios.
- Use `uv run pytest tests/ -q` from this directory. Counts in older session
  documents are historical, not current acceptance criteria.
- Reset with `uv run python scripts/reset_database_seed.py` only when restoring
  baseline state is part of the task.

See the detailed guide for seed stories, formulas, API paths, and the
distinction between live stock and historical CSV exercises.
