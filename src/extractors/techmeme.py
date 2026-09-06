import hashlib
from datetime import datetime, date, time, timedelta
import pytz
import requests
import yaml
from icalendar import Calendar
from typing import List
from src.models import KeynoteEvent

def get_company_category(company: str) -> str:
    company_lower = company.lower()
    if any(k in company_lower for k in ["aws", "databricks", "snowflake", "cloud", "kafka", "confluent"]):
        return "Data & Cloud Infrastructure"
    elif any(k in company_lower for k in ["openai", "nvidia", "meta"]):
        return "AI & LLMs"
    return "Hardware & Consumer Tech"

def load_techmeme_events(config_path: str = "config/sources.yaml") -> List[KeynoteEvent]:
    events = []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {config_path}: {e}")
        return events

    tm_cfg = cfg.get("techmeme", {})
    if not tm_cfg.get("enabled", True):
        return events

    feed_url = tm_cfg.get("feed_url", "https://techmeme.com/newsy_events.ics")
    positive_keywords = [k.lower() for k in tm_cfg.get("positive_keywords", [])]
    negative_keywords = [k.lower() for k in tm_cfg.get("negative_keywords", [])]

    # Map companies to their canonical launch hours (defaulting to 10:00 AM PT)
    canonical_hours = {
        "apple": (10, 0, "America/Los_Angeles", 120),
        "google": (10, 0, "America/Los_Angeles", 120),
        "samsung": (10, 0, "America/New_York", 90),
        "aws": (8, 30, "America/Los_Angeles", 120),
        "databricks": (9, 0, "America/Los_Angeles", 120),
        "snowflake": (9, 0, "America/Los_Angeles", 120),
        "openai": (10, 0, "America/Los_Angeles", 60),
        "microsoft": (9, 0, "America/Los_Angeles", 120),
        "nvidia": (11, 0, "America/Los_Angeles", 120),
        "meta": (10, 0, "America/Los_Angeles", 120),
        "anthropic": (10, 0, "America/Los_Angeles", 90),
        "claude": (10, 0, "America/Los_Angeles", 90),
        "github": (9, 0, "America/Los_Angeles", 120),
        "oracle": (9, 0, "America/Los_Angeles", 120),
        "airflow": (9, 0, "America/Los_Angeles", 90),
        "copilot": (9, 0, "America/Los_Angeles", 90),
    }

    try:
        headers = {"User-Agent": "Mozilla/5.0 (TechKeynoteCalendar/1.0)"}
        resp = requests.get(feed_url, headers=headers, timeout=12)
        if resp.status_code != 200:
            print(f"Failed to fetch Techmeme feed (status {resp.status_code})")
            return events
        cal = Calendar.from_ical(resp.content)
    except Exception as err:
        print(f"Could not retrieve or parse Techmeme ICS feed: {err}")
        return events

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        summary = str(component.get("summary", "")).strip()
        summary_lower = summary.lower()

        # Check negative keywords first
        if any(neg in summary_lower for neg in negative_keywords):
            continue

        # Check positive match
        matched_keyword = next((pos for pos in positive_keywords if pos in summary_lower), None)
        if not matched_keyword:
            continue

        # Identify company
        company = "Tech Event"
        for comp_key in canonical_hours.keys():
            if comp_key in summary_lower:
                company = comp_key.capitalize()
                if comp_key == "aws":
                    company = "AWS"
                elif comp_key == "openai":
                    company = "OpenAI"
                elif comp_key == "nvidia":
                    company = "NVIDIA"
                break

        # Handle all-day vs hourly timestamp
        raw_dtstart = component.get("dtstart").dt
        hour, minute, tz_str, duration_mins = canonical_hours.get(company.lower(), (10, 0, "America/Los_Angeles", 120))
        target_tz = pytz.timezone(tz_str)

        if isinstance(raw_dtstart, datetime):
            # It's already a datetime
            if raw_dtstart.tzinfo is None:
                start_dt = target_tz.localize(raw_dtstart)
            else:
                start_dt = raw_dtstart
            end_dt = start_dt + timedelta(minutes=duration_mins)
        elif isinstance(raw_dtstart, date):
            # Techmeme all-day event! Convert to canonical keynote time window
            naive_dt = datetime.combine(raw_dtstart, time(hour, minute))
            start_dt = target_tz.localize(naive_dt)
            end_dt = start_dt + timedelta(minutes=duration_mins)
        else:
            continue

        url = str(component.get("url", "")).strip()
        description = str(component.get("description", "")).strip() or f"{summary} keynote presentation."
        location = str(component.get("location", "Livestream")).strip() or "Livestream"

        # Unique ID hash based on summary and date to prevent duplicates
        date_str = start_dt.strftime("%Y%m%d")
        uid_seed = f"techmeme-{company.lower()}-{date_str}"
        uid = f"tm-{hashlib.md5(uid_seed.encode('utf-8')).hexdigest()[:12]}"

        events.append(KeynoteEvent(
            uid=uid,
            title=summary,
            company=company,
            category=get_company_category(company),
            start_time=start_dt,
            end_time=end_dt,
            stream_url=url,
            description=description,
            location=location,
            source="techmeme_feed"
        ))

    return events
