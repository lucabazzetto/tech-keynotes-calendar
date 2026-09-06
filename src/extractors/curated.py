import yaml
from datetime import datetime
from dateutil import parser
import pytz
from typing import List
from src.models import KeynoteEvent

def load_curated_events(config_path: str = "config/curated_events.yaml") -> List[KeynoteEvent]:
    events = []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading curated events from {config_path}: {e}")
        return events

    for raw in data.get("events", []):
        try:
            start_dt = parser.parse(raw["start_time"])
            end_dt = parser.parse(raw["end_time"])
            
            # Ensure timezone awareness
            if start_dt.tzinfo is None:
                start_dt = pytz.utc.localize(start_dt)
            if end_dt.tzinfo is None:
                end_dt = pytz.utc.localize(end_dt)

            event = KeynoteEvent(
                uid=raw["uid"],
                title=raw["title"],
                company=raw["company"],
                category=raw.get("category", "General Tech"),
                start_time=start_dt,
                end_time=end_dt,
                stream_url=raw.get("stream_url", ""),
                description=raw.get("description", ""),
                location=raw.get("location", "Livestream"),
                source="curated_registry"
            )
            events.append(event)
        except Exception as err:
            print(f"Failed to parse curated event {raw.get('title', 'unknown')}: {err}")

    return events
