# 📡 Tech & Data Engineering Keynotes Calendar

An automated data pipeline that continuously curates, enriches, and synchronizes tier-1 technology showcases and data engineering summits directly into your Google Calendar (or Apple Calendar / Outlook).

---

## 🎯 Why This Exists

Generic calendars (like Techmeme or tech news aggregators) create two frustrating problems:
1. **Calendar Spam:** They dump hundreds of quarterly earnings calls, financial filings, and sponsor webinars.
2. **All-Day Event Clutter:** They publish events as all-day blocks, clogging the top bar of your calendar without exact hours or direct livestream links.

This pipeline solves that by:
* **Filtering Strictly:** Only tier-1 consumer tech announcements (Apple, Google, Samsung, OpenAI) and major data engineering / cloud summits (AWS re:Invent, Databricks Data + AI, Snowflake Summit, Google Cloud Next, NVIDIA GTC).
* **Exact Broadcast Times:** Replaces all-day blocks with precise keynote hours (e.g., 10:00 AM – 12:00 PM PT / normalized in UTC).
* **Direct Livestream Links:** Embedded YouTube / official webcast URLs in the location and description.
* **Pre-Keynote Reminders:** 30-minute advance alarm built into the calendar.

---

## 📅 How to Subscribe in Google Calendar

Once your repository is published to GitHub and GitHub Pages is enabled:

1. Copy your feed URL:
   ```text
   webcal://<your-username>.github.io/<repo-name>/tech_events.ics
   ```
   *(or the `https://` version)*
2. Open **[Google Calendar](https://calendar.google.com)** on your computer.
3. On the left sidebar, next to **Other calendars**, click the **`+`** icon $\rightarrow$ **From URL**.
4. Paste the URL and click **Add calendar**.
5. *(Recommended)* Rename the new calendar to **"Tech Keynotes & Showcases"** and assign it a distinct color. You can toggle it on/off whenever you want!

---

## 🏗️ Architecture & Pipeline Flow

```text
               ┌──────────────────────────────────────────────┐
               │                Data Sources                  │
               │  • YouTube Scheduled Live Streams (Atom/RSS) │
               │  • Techmeme Newsy Feed (Filtered)            │
               │  • Curated Keynote Registry (YAML)           │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │          ETL & Deduplication Engine          │
               │  • Filter out earnings / financial calls     │
               │  • Convert all-day dates to keynote hours    │
               │  • Merge YouTube livestream URLs             │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │               Published Feeds                │
               │  • public/tech_events.ics (RFC 5545 WebCal)  │
               │  • public/events.json                        │
               │  • public/index.html (Interactive Web UI)    │
               └──────────────────────────────────────────────┘
```

---

## 🛠️ Monitored Showcases

### Consumer Tech & AI
* **Apple:** Fall iPhone Event, WWDC, Spring Showcases
* **Google:** Google I/O, Made by Google (Pixel / Android)
* **Samsung:** Galaxy Unpacked (Winter & Summer)
* **OpenAI:** DevDay, Spring / Autumn Feature Launches
* **Microsoft:** Microsoft Build, Surface / Copilot Events
* **Meta:** Meta Connect Keynote

### Data Engineering & Cloud Infrastructure
* **AWS:** re:Invent (CEO Keynote, Swami Sivasubramanian Data & AI Keynote, Werner Vogels Keynote)
* **Databricks:** Data + AI Summit (Matei Zaharia & Ali Ghodsi Keynote)
* **Snowflake:** Snowflake Summit Keynote
* **Google Cloud:** Google Cloud Next Keynote
* **NVIDIA:** GTC Global Keynote (Jensen Huang)

---

## 🚀 Local Development

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run pipeline
python -m src.main

# 4. Run tests
python -m unittest discover tests

# 5. Preview Web Dashboard locally
open public/index.html
```

---

## ⚙️ Configuration

* **`config/sources.yaml`**: Add/remove YouTube channel IDs, configure positive/negative keyword filters for Techmeme.
* **`config/curated_events.yaml`**: Add known dates and times for upcoming flagship summits.
