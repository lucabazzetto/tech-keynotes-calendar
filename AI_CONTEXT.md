# AI Agent Context & Operational Handbook (AI_CONTEXT.md)

> **For LLMs & AI Coding Assistants (Gemini, Claude Code, Codex, Cursor, Antigravity):**
> Read this document first. It explains the project's purpose, architectural decisions, file structure, operational procedures, and how you should update settings and record changes.

---

## 1. Project Purpose & Philosophy

This project (`tech-keynotes-calendar`) is an automated, serverless ETL data pipeline designed for a **Senior Data Engineer & Tech Enthusiast**. It continuously aggregates, enriches, and synchronizes tier-1 technology product showcases and premier data engineering conferences into a clean, subscribable Google Calendar / iCalendar (`.ics`) feed.

### Core Non-Negotiables:
1. **Zero All-Day Clutter:** Standard feeds (like Techmeme) publish all-day events that clutter the top of the calendar. This pipeline **strictly enforces exact broadcast hours** (e.g. 10:00 AM – 12:00 PM PT, normalized to UTC with `Z` suffix in RFC 5545).
2. **Zero Financial / Earnings Spam:** Aggressive negative keyword filtering removes quarterly earnings reports, shareholder meetings, SEC calls, and generic webinars.
3. **Dual Focus:**
   - **Consumer Tech & AI Flagships:** Apple Keynotes, Google I/O & Made by Google, Samsung Galaxy Unpacked, OpenAI DevDay, Microsoft Build, Meta Connect.
   - **Data Engineering & Cloud Infrastructure:** AWS re:Invent (CEO, Data & AI, Werner Vogels Keynotes), Databricks Data + AI Summit, Snowflake Summit, Google Cloud Next, NVIDIA GTC, Confluent Current.
4. **Rich Metadata:** Direct YouTube livestream links and webcast URLs are embedded into `LOCATION`, `URL`, and `DESCRIPTION`. Each event includes a 30-minute advance `VALARM` notification.

---

## 2. Directory Structure & File Map

```text
/Users/luca/tech-keynotes-calendar/
├── config/
│   ├── sources.yaml          # Monitored YouTube channel IDs, Techmeme filter rules, canonical company hours
│   └── curated_events.yaml   # Verified annual flagship keynotes and data engineering summits
├── src/
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
├── requirements.txt          # Python dependencies (icalendar, feedparser, pyyaml, requests, pytz, etc.)
├── README.md                 # User-facing guide and calendar subscription instructions
├── AI_CONTEXT.md             # This agent instruction manual
└── CLAUDE.md                 # Link / instructions for Claude Code
```

---

## 3. Standard Procedures for AI Agents

### Running Locally
Always execute commands using the local virtual environment:
```bash
# Activate venv
source .venv/bin/activate

# Or invoke directly:
.venv/bin/python -m src.main
```

### Running Unit Tests
Before committing any changes, you must run the unit test suite:
```bash
.venv/bin/python -m unittest discover tests
```

### How to Add a New Curated Keynote Event
Edit `config/curated_events.yaml` and append an entry:
```yaml
  - uid: "company-event-name-2026"
    title: "Company Event Title"
    company: "Company Name"
    category: "Hardware & Consumer Tech" # Or "Data & Cloud Infrastructure" or "AI & LLMs"
    start_time: "2026-10-15T10:00:00-07:00" # ISO-8601 with explicit timezone offset
    end_time: "2026-10-15T12:00:00-07:00"
    stream_url: "https://www.youtube.com/watch?v=..."
    description: "Detailed description of product reveals and presentations."
    location: "Location / Livestream"
```

### How to Add a Monitored YouTube Channel
Edit `config/sources.yaml` under `youtube_channels`:
```yaml
  - id: "YOUTUBE_CHANNEL_ID"
    name: "Channel Name"
    category: "Category Name"
    company: "Company"
    default_duration_minutes: 120
    canonical_time: "10:00"
    canonical_tz: "America/Los_Angeles"
    livestream_hub: "https://www.youtube.com/@handle/streams"
```

### Critical Rules for Pipeline Modifications
* **RFC 5545 Strictness:** `DTSTART` and `DTEND` must always be formatted in UTC (e.g. `20260909T170000Z`). Never emit a `date` object without time.
* **Deduplication:** The pipeline groups events by `(company, UTC date)`. If a YouTube stream matches a curated entry, merge them by preserving the curated description while updating the exact `stream_url`.

---

## 4. AI Change Log & Settings History

> [!NOTE]
> Whenever you (Gemini, Claude, Codex, or another AI) modify configurations, extractors, or pipeline logic, log your change below with a timestamp, the tool name, and what was altered.

| Date (UTC) | Agent / Model | Action Taken | Rationale |
| :--- | :--- | :--- | :--- |
| 2026-09-06 | Antigravity (Gemini) | Initial pipeline creation | Established architecture, extractors (Techmeme, YouTube, Curated), RFC 5545 generator, GitHub Actions, and Web UI. |
| 2026-09-06 | Antigravity (Gemini) | Workspace relocation | Migrated project to `/Users/luca/tech-keynotes-calendar`, created `AI_CONTEXT.md` & `CLAUDE.md`. |
