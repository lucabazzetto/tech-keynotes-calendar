from datetime import date, datetime, timedelta
from dateutil import parser
import pytz
from typing import List
from src.models import KeynoteEvent
from src.extractors.curated import load_curated_events, load_watchlist
from src.extractors.techmeme import load_techmeme_leads
from src.extractors.youtube import check_youtube_streams

# A curated keynote and a YouTube stream of the same company starting this close are one event.
SAME_EVENT_WINDOW = timedelta(hours=2)


def merge_and_deduplicate(all_events: List[KeynoteEvent]) -> List[KeynoteEvent]:
    curated = [e for e in all_events if e.source == "curated_registry"]
    others = [e for e in all_events if e.source != "curated_registry"]

    deduped = list(curated)
    for ev in others:
        match = next((
            c for c in deduped
            if c.company.lower() == ev.company.lower()
            and abs(c.start_time - ev.start_time) <= SAME_EVENT_WINDOW
        ), None)
        if match is None:
            deduped.append(ev)
        elif "youtube.com/watch" in ev.stream_url and "youtube.com/watch" not in match.stream_url:
            match.stream_url = ev.stream_url

    deduped.sort(key=lambda x: x.start_time)
    return deduped


def _as_date(value) -> date:
    return value if isinstance(value, date) else parser.parse(str(value)).date()


def report_unverified_leads(leads: List[dict], events: List[KeynoteEvent], watchlist: List[dict]):
    """Print Techmeme leads that no confirmed event or watchlist entry covers yet."""
    known = [(e.company.lower(), e.start_time.date(), e.end_time.date()) for e in events]
    known += [(w["company"].lower(), _as_date(w["start_date"]), _as_date(w["end_date"])) for w in watchlist]
    slack = timedelta(days=2)

    uncovered = [
        lead for lead in leads
        if lead["end_date"] >= datetime.now(pytz.utc).date()
        and not any(
            company in lead["title"].lower()
            and lead["start_date"] <= end + slack and lead["end_date"] >= start - slack
            for company, start, end in known
        )
    ]
    if uncovered:
        print("ℹ Techmeme leads needing official verification (not published):")
        for lead in uncovered:
            print(f"    - {lead['start_date']} → {lead['end_date']}  {lead['title']}  {lead['url']}")


def run_pipeline() -> List[KeynoteEvent]:
    print("▶ Fetching curated keynotes registry (official sources only)...")
    curated = load_curated_events()
    print(f"  Loaded {len(curated)} upcoming confirmed events.")

    print("▶ Checking official YouTube channels for scheduled live streams...")
    yt_events = check_youtube_streams()
    print(f"  Loaded {len(yt_events)} scheduled YouTube broadcasts.")

    final_events = merge_and_deduplicate(curated + yt_events)
    print(f"Final deduplicated events: {len(final_events)}")

    print("▶ Checking Techmeme for leads...")
    report_unverified_leads(load_techmeme_leads(), final_events, load_watchlist())
    return final_events
