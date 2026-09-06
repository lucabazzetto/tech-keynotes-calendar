# Claude Code Guidelines - Tech & Data Keynotes Calendar

Refer to `AI_CONTEXT.md` for complete architectural context and change log.

## Essential Commands
- Run pipeline locally: `.venv/bin/python -m src.main`
- Run unit tests: `.venv/bin/python -m unittest discover tests`
- Format code / inspect: `git status`

## Mandatory Commit Protocol
1. **Commit after every logical modification.** Never leave unstaged or uncommitted changes.
2. **Follow Conventional Commits 1.0.0 strictly**:
   - `feat(scope): concise imperative description`
   - `fix(scope): concise imperative description`
   - `docs(scope): concise imperative description`
   - `chore(scope): concise imperative description`
   - `ci(scope): concise imperative description`
   - `data(scope): concise imperative description`
3. Enforced by `.githooks/commit-msg` (active via `git config core.hooksPath .githooks`).
4. Update the change log table in `AI_CONTEXT.md` on significant updates.
