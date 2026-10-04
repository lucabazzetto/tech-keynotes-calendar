import yaml
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from typing import List
from src.models import KeynoteEvent

# Used only when the organizer publishes a start time but no end time.
UNPUBLISHED_END_MINUTES = 60


def load_curated_config(config_path: str = "config/curated_events.yaml") -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error loading curated events from {config_path}: {e}")
        return {}


def load_curated_events(config_path: str = "config/curated_events.yaml", now: datetime = None) -> List[KeynoteEvent]:
    now = now or datetime.now(pytz.utc)
    events = []

    for raw in load_curated_config(config_path).get("events", []) or []:
        title = raw.get("title", "unknown")
        try:
            if not raw.get("source_url"):
                print(f"  ✗ Rejected curated event '{title}': missing source_url (official confirmation required)")
                continue

            start_dt = parser.parse(raw["start_time"])
            if start_dt.tzinfo is None:
                print(f"  ✗ Rejected curated event '{title}': start_time has no timezone offset")
                continue

            description = raw.get("description", "")
            if raw.get("end_time"):
                end_dt = parser.parse(raw["end_time"])
                if end_dt.tzinfo is None:
                    print(f"  ✗ Rejected curated event '{title}': end_time has no timezone offset")
                    continue
            else:
                end_dt = start_dt + timedelta(minutes=UNPUBLISHED_END_MINUTES)
                description = f"{description}\n(Official start time; end time not published by the organizer.)".strip()

            if end_dt <= now:
                continue

            events.append(KeynoteEvent(
                uid=raw["uid"],
                title=title,
                company=raw["company"],
                category=raw.get("category", "General Tech"),
                start_time=start_dt,
                end_time=end_dt,
                stream_url=raw.get("stream_url", ""),
                description=description,
                location=raw.get("location", "Livestream"),
                source="curated_registry",
                source_url=raw["source_url"],
            ))
        except Exception as err:
            print(f"Failed to parse curated event {title}: {err}")

    return events


def load_watchlist(config_path: str = "config/curated_events.yaml") -> List[dict]:
    return load_curated_config(config_path).get("watchlist", []) or []
