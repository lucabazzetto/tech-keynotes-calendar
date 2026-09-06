from datetime import datetime, timedelta
import pytz
from typing import List
from src.models import KeynoteEvent
from src.extractors.curated import load_curated_events
from src.extractors.techmeme import load_techmeme_events
from src.extractors.youtube import check_youtube_streams

def merge_and_deduplicate(all_events: List[KeynoteEvent]) -> List[KeynoteEvent]:
    # Group by company and date (YYYY-MM-DD in UTC)
    buckets = {}
    for ev in all_events:
        utc_date = ev.start_time.astimezone(pytz.utc).strftime("%Y-%m-%d")
        key = (ev.company.lower(), utc_date)
        if key not in buckets:
            buckets[key] = []
        buckets[key].append(ev)

    deduped = []
    for key, ev_list in buckets.items():
        if len(ev_list) == 1:
            deduped.append(ev_list[0])
            continue

        # Multiple events for same company on same date: merge intelligently
        # Preference order for base info: curated > techmeme > youtube
        base_event = next((e for e in ev_list if e.source == "curated_registry"), None)
        if not base_event:
            base_event = next((e for e in ev_list if e.source == "techmeme_feed"), ev_list[0])

        # If any event in the bucket has a direct YouTube stream URL, inject it
        yt_event = next((e for e in ev_list if "youtube.com" in e.stream_url), None)
        if yt_event and yt_event.stream_url:
            base_event.stream_url = yt_event.stream_url
            base_event.location = f"YouTube Live - {yt_event.stream_url}"

        deduped.append(base_event)

    # Sort chronologically
    deduped.sort(key=lambda x: x.start_time)
    return deduped

def run_pipeline() -> List[KeynoteEvent]:
    print("▶ Fetching curated keynotes registry...")
    curated = load_curated_events()
    print(f"  Loaded {len(curated)} curated events.")

    print("▶ Fetching Techmeme newsy events feed (filtered)...")
    tm_events = load_techmeme_events()
    print(f"  Loaded {len(tm_events)} filtered Techmeme events.")

    print("▶ Checking official YouTube live feeds for tech & data channels...")
    yt_events = check_youtube_streams()
    print(f"  Loaded {len(yt_events)} YouTube live events.")

    combined = curated + tm_events + yt_events
    print(f"Total raw events gathered: {len(combined)}")

    # Deduplicate and enrich
    final_events = merge_and_deduplicate(combined)
    print(f"Final deduplicated events: {len(final_events)}")
    return final_events
