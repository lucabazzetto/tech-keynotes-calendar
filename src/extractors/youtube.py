from datetime import datetime, timedelta
from dateutil import parser
import feedparser
import pytz
import re
import requests
import yaml
from typing import List, Dict
from src.models import KeynoteEvent

KEYNOTE_KEYWORDS = [
    "keynote", "event", "unpacked", "special event", "livestream", 
    "live:", "live :", "announcement", "launch", "devday", "summit", "reinvent", "gtc"
]

def check_youtube_streams(config_path: str = "config/sources.yaml") -> List[KeynoteEvent]:
    events = []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {config_path}: {e}")
        return events

    channels = cfg.get("youtube_channels", [])

    for ch in channels:
        ch_id = ch.get("id")
        ch_name = ch.get("name")
        company = ch.get("company", ch_name)
        category = ch.get("category", "General Tech")
        tz_name = ch.get("canonical_tz", "America/Los_Angeles")
        duration_mins = ch.get("default_duration_minutes", 120)
        canonical_tz = pytz.timezone(tz_name)

        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch_id}"
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]: # inspect the latest 10 uploads/scheduled items
                title = entry.title
                title_lower = title.lower()
                
                # Check if title indicates a live broadcast or keynote showcase
                is_keynote = any(k in title_lower for k in KEYNOTE_KEYWORDS)
                if not is_keynote:
                    continue

                link = entry.link
                published_str = getattr(entry, "published", None)
                if not published_str:
                    continue

                pub_dt = parser.parse(published_str)
                if pub_dt.tzinfo is None:
                    pub_dt = pytz.utc.localize(pub_dt)
                
                # If published within recent 7 days or in future
                now = datetime.now(pytz.utc)
                if pub_dt < now - timedelta(days=7):
                    continue

                start_dt = pub_dt
                end_dt = start_dt + timedelta(minutes=duration_mins)
                vid_id = getattr(entry, "yt_videoid", link.split("v=")[-1])

                event = KeynoteEvent(
                    uid=f"yt-{vid_id}",
                    title=f"{company}: {title}",
                    company=company,
                    category=category,
                    start_time=start_dt,
                    end_time=end_dt,
                    stream_url=link,
                    description=f"Official live broadcast stream on YouTube for {company}.\nWatch live at {link}",
                    location=f"YouTube Live - {link}",
                    source="youtube_live"
                )
                events.append(event)
        except Exception as err:
            print(f"Could not check YouTube channel {ch_name}: {err}")

    return events
