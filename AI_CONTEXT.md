# AI Agent Context & Operational Handbook (AI_CONTEXT.md)

> **For LLMs & AI Coding Assistants (Gemini, Claude Code, Codex, Cursor, Antigravity):**
> Read this document first. It defines the project's architecture, philosophy, operational procedures, and **the Scenario C Auto-Ingestion Protocol** for adding new topics/companies based on historical event patterns.

---

## 1. Project Purpose & Philosophy

This project (`tech-keynotes-calendar`) is an automated, serverless ETL data pipeline designed for a **Senior Data Engineer & Tech Enthusiast**. It continuously aggregates, enriches, and synchronizes tier-1 technology product showcases and premier data engineering conferences into a clean, subscribable Google Calendar / iCalendar (`.ics`) feed.

### Core Non-Negotiables:
1. **Zero All-Day Clutter:** Standard feeds (like Techmeme) publish all-day events that clutter the top of the calendar. This pipeline **strictly enforces exact broadcast hours** (e.g. 10:00 AM – 12:00 PM PT, normalized to UTC with `Z` suffix in RFC 5545).
2. **Zero Financial / Earnings Spam:** Aggressive negative keyword filtering removes quarterly earnings reports, shareholder meetings, SEC calls, and generic webinars.
3. **Dual Focus:**
   - **Consumer Tech & AI Flagships:** Apple Keynotes, Google I/O & Made by Google, Samsung Galaxy Unpacked, OpenAI DevDay, Microsoft Build, Meta Connect, Anthropic.
   - **Data Engineering & Cloud Infrastructure:** AWS re:Invent (CEO, Data & AI, Werner Vogels Keynotes), Databricks Data + AI Summit, Snowflake Summit, Google Cloud Next, NVIDIA GTC, Confluent Current.
4. **Rich Metadata:** Direct YouTube livestream links and webcast URLs are embedded into `LOCATION`, `URL`, and `DESCRIPTION`. Each event includes a 30-minute advance `VALARM` notification.

---

## 2. Scenario C: How AI Agents Must Add New Topics & Companies

When the user asks you to add a new company, event, or topic (e.g. *"Add Anthropic showcases"*, *"Add Figma Config"*, or *"Add Kafka Summit"*), you must execute the following 4-step protocol:

```text
User Request ("Add X")
       │
       ▼
[Step 1: Historical Research] ──► Search previous event months, time of day (PT/ET), and official YouTube handle
       │
       ▼
[Step 2: Schema Classification] ─► Map to category: "Hardware & Consumer Tech" | "Data & Cloud Infrastructure" | "AI & LLMs"
       │
       ▼
[Step 3: CLI Registration] ─────► Run `python -m src.manage add-channel` (auto-resolves YouTube channel ID & keywords)
       │                         and optionally `python -m src.manage add-event` for known future dates
       ▼
[Step 4: Verify & Deploy] ──────► Run test suite ──► Run pipeline ──► Commit (Conventional Commits) ──► Git Push
```

### Step 1: Historical Event Research
1. Search previous editions of the company's events over the past 2–3 years:
   - What month(s) do they usually broadcast? (e.g., Apple iPhone is always September; AWS re:Invent is late November; Figma Config is June).
   - What time of day? (Default to `10:00` PT for West Coast tech; `09:00` ET for East Coast).
   - What is their official YouTube handle? (e.g., `@anthropic-ai`, `@Figma`, `@OpenAI`).

### Step 2: Auto-Registration via CLI Tool
Do NOT edit YAML manually when possible; use the built-in management CLI:

```bash
# 1. Register the company / channel for continuous monitoring
.venv/bin/python -m src.manage add-channel \
  --company "Anthropic" \
  --handle "@anthropic-ai" \
  --category "AI & LLMs" \
  --time "10:00" \
  --tz "America/Los_Angeles"

# 2. If a specific upcoming flagship keynote date is announced or anticipated:
.venv/bin/python -m src.manage add-event \
  --title "Anthropic: Frontier Showcase" \
  --company "Anthropic" \
  --category "AI & LLMs" \
  --start-time "2026-10-22T10:00:00-07:00" \
  --end-time "2026-10-22T11:30:00-07:00" \
  --stream-url "https://www.youtube.com/@anthropic-ai/streams" \
  --description "Official live keynote revealing next-generation Claude models and developer APIs."
```

### Step 3: Verification & Atomic Push
```bash
# 1. Verify tests pass
.venv/bin/python -m unittest discover tests

# 2. Run pipeline to refresh public feeds
.venv/bin/python -m src.main

# 3. Commit with Conventional Commits
git add config/ public/
git commit -m "feat(sources): add Anthropic live monitoring and keynote tracking"

# 4. Push to remote
git push origin main
```

---

## 3. Mandatory Git Commit Standards (State-of-the-Art)

1. **Commit on Every Modification:** Never leave unstaged or uncommitted code after finishing a task.
2. **Conventional Commits 1.0.0 Specification:**
   `<type>(<optional-scope>): <imperative summary>`
   - `feat:` New features or extractors
   - `fix:` Bug fixes (e.g. timezone offsets, parsing edge cases)
   - `docs:` Documentation updates
   - `chore:` Routine maintenance or dependency bumps
   - `ci:` CI/CD & GitHub Actions workflows
   - `data:` Keynote registry updates
3. **Git Hook Verification:** A client-side hook in `.githooks/commit-msg` automatically validates every commit.

---

## 4. Directory Structure & File Map

```text
/Users/luca/tech-keynotes-calendar/
├── .githooks/
│   └── commit-msg            # Client-side hook enforcing Conventional Commits
├── config/
│   ├── sources.yaml          # Monitored YouTube channel IDs, Techmeme filter rules, canonical company hours
│   └── curated_events.yaml   # Verified annual flagship keynotes and data engineering summits
├── src/
│   ├── manage.py             # CLI for adding channels, auto-resolving YouTube IDs, and adding events
│   ├── models.py             # KeynoteEvent dataclass & RFC 5545 iCalendar component builder
│   ├── extractors/
│   │   ├── curated.py        # Parses config/curated_events.yaml
│   │   ├── techmeme.py       # Ingests & filters Techmeme ICS, mapping dates to canonical broadcast hours
│   │   └── youtube.py        # Checks YouTube Atom/RSS feeds for scheduled live streams
│   ├── pipeline.py           # Ingestion, deduplication, stream enrichment, and chronological sorting
│   ├── generator.py          # Generates public/tech_events.ics, public/events.json, and public/index.html
│   └── main.py               # Main CLI entrypoint
├── tests/
│   └── test_pipeline.py      # Unit tests (parsing, timezone awareness, RFC 5545 compliance)
├── public/                   # Generated artifacts (served via GitHub Pages)
│   ├── tech_events.ics       # Subscribable WebCal iCalendar feed
│   ├── events.json           # JSON API output
│   └── index.html            # Dark-mode responsive dashboard with 1-click GCal add buttons
├── .github/workflows/
│   └── sync_calendar.yml     # GitHub Actions workflow (runs every 6h and deploys to gh-pages)
├── requirements.txt          # Python dependencies
├── README.md                 # User-facing guide and calendar subscription instructions
├── AI_CONTEXT.md             # This agent instruction manual
└── CLAUDE.md                 # Quick commands & guidelines for Claude Code
```

---

## 5. AI Change Log & Settings History

| Date (UTC) | Agent / Model | Action Taken | Rationale |
| :--- | :--- | :--- | :--- |
| 2026-09-06 | Antigravity (Gemini) | Initial pipeline creation | Established architecture, extractors (Techmeme, YouTube, Curated), RFC 5545 generator, GitHub Actions, and Web UI. |
| 2026-09-06 | Antigravity (Gemini) | Workspace relocation | Migrated project to `/Users/luca/tech-keynotes-calendar`, created `AI_CONTEXT.md` & `CLAUDE.md`. |
| 2026-09-06 | Antigravity (Gemini) | Conventional Commits enforcement | Added `.githooks/commit-msg`, upgraded `.github/workflows/sync_calendar.yml` with dynamic meaningful commit generation. |
| 2026-09-06 | Antigravity (Gemini) | Scenario C Management CLI | Created `src/manage.py` with automatic YouTube channel ID resolution and documented historical pattern inference recipe. |

| 2026-09-06 | Antigravity (Gemini) | Add Anthropic & Claude tracking | Registered Anthropic YouTube channel ID, added Claude keywords to Techmeme filter, and registered Autumn 2026 and Spring 2027 keynotes. |
