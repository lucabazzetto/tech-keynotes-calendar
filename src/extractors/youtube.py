from datetime import datetime, timedelta
from dateutil import parser
import feedparser
import json
import pytz
import re
import requests
import yaml
from typing import List, Optional
from src.models import KeynoteEvent

KEYNOTE_KEYWORDS = [
    "keynote", "event", "unpacked", "special event", "livestream",
    "live:", "live :", "announcement", "launch", "devday", "summit", "reinvent", "gtc"
]

# Recaps and replays are uploaded videos, not scheduled broadcasts.
EXCLUDE_KEYWORDS = ["highlights", "recap", "replay", "in under", "in 10 minutes", "supercut"]

LIVE_DETAILS_RE = re.compile(r'"liveBroadcastDetails":(\{[^{}]*\})')


def parse_live_details(watch_html: str) -> Optional[dict]:
    """Extract YouTube's liveBroadcastDetails (official scheduled start) from a watch page."""
    m = LIVE_DETAILS_RE.search(watch_html)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def fetch_live_details(url: str) -> Optional[dict]:
    headers = {"User-Agent": "Mozilla/5.0 (TechKeynoteCalendar/1.0)", "Accept-Language": "en"}
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        return None
    return parse_live_details(resp.text)


def check_youtube_streams(config_path: str = "config/sources.yaml", now: datetime = None) -> List[KeynoteEvent]:
    """Return only upcoming or in-progress scheduled live streams, timed by YouTube's own schedule."""
    now = now or datetime.now(pytz.utc)
    events = []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {config_path}: {e}")
        return events

    for ch in cfg.get("youtube_channels", []):
        ch_id = ch.get("id")
        ch_name = ch.get("name")
        company = ch.get("company", ch_name)
        category = ch.get("category", "General Tech")
        duration_mins = ch.get("default_duration_minutes", 120)

        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch_id}"
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.title
                title_lower = title.lower()
                if not any(k in title_lower for k in KEYNOTE_KEYWORDS):
                    continue
                if any(k in title_lower for k in EXCLUDE_KEYWORDS):
                    continue

                details = fetch_live_details(entry.link)
                if not details or not details.get("startTimestamp"):
                    continue  # regular upload, not a scheduled broadcast
                if details.get("endTimestamp") and not details.get("isLiveNow"):
                    continue  # broadcast already finished

                start_dt = parser.parse(details["startTimestamp"])
                if start_dt.tzinfo is None:
                    start_dt = pytz.utc.localize(start_dt)
                end_dt = start_dt + timedelta(minutes=duration_mins)
                if end_dt <= now and not details.get("isLiveNow"):
                    continue

                vid_id = getattr(entry, "yt_videoid", entry.link.split("v=")[-1])
                events.append(KeynoteEvent(
                    uid=f"yt-{vid_id}",
                    title=f"{company}: {title}",
                    company=company,
                    category=category,
                    start_time=start_dt,
                    end_time=end_dt,
                    stream_url=entry.link,
                    description=(
                        f"Scheduled live broadcast on the official {company} YouTube channel.\n"
                        f"(Start time from YouTube's schedule; end time not published.)\n"
                        f"Watch live at {entry.link}"
                    ),
                    location=f"YouTube Live - {entry.link}",
                    source="youtube_live",
                    source_url=entry.link,
                ))
        except Exception as err:
            print(f"Could not check YouTube channel {ch_name}: {err}")

    return events
