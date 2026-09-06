# Claude Code Guidelines - Tech & Data Keynotes Calendar

Refer to `AI_CONTEXT.md` for complete architectural context and change log.

## Essential Commands
- Run pipeline locally: `.venv/bin/python -m src.main`
- Run unit tests: `.venv/bin/python -m unittest discover tests`
- Format code / inspect: `git status`

## Architecture Highlights
- `config/sources.yaml`: Monitored channels, Techmeme filters, canonical keynote hours.
- `config/curated_events.yaml`: Fixed annual keynotes (Apple, AWS re:Invent, Databricks, etc.).
- `src/extractors/`: Modular parsers for Curated, Techmeme, and YouTube feeds.
- `src/generator.py`: RFC 5545 iCalendar builder (`public/tech_events.ics`), JSON, and HTML dashboard.
- Output: strictly exact broadcast hours in UTC (no all-day events), livestream links in location & description.
