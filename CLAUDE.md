# Claude Code Guidelines - Tech & Data Keynotes Calendar

Refer to `AI_CONTEXT.md` for complete architectural context, change log, and the Scenario C protocol.

## Essential Commands
- Run pipeline locally: `.venv/bin/python -m src.main`
- Run unit tests: `.venv/bin/python -m unittest discover tests`
- Add a monitored channel: `.venv/bin/python -m src.manage add-channel --company "<Name>" --handle "@handle" --category "<Category>"`
- Add a curated event: `.venv/bin/python -m src.manage add-event --title "..." --company "..." --start-time "..." --end-time "..." --stream-url "..."`

## Mandatory Commit Protocol
1. **Commit after every modification.** Never leave uncommitted changes.
2. **Follow Conventional Commits 1.0.0 strictly** (`feat:`, `fix:`, `docs:`, `chore:`, `ci:`, `data:`).
3. Validated by `.githooks/commit-msg`.
