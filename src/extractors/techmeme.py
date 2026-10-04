from datetime import date, datetime, timedelta
import requests
import yaml
from icalendar import Calendar
from typing import List


def load_techmeme_leads(config_path: str = "config/sources.yaml") -> List[dict]:
    """Return keyword-matched Techmeme events as *leads* for manual verification.

    Techmeme publishes date-only entries (no keynote time) and its dates have been seen
    off by a day versus the organizers' official pages, so these are never published.
    """
    leads = []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {config_path}: {e}")
        return leads

    tm_cfg = cfg.get("techmeme", {})
    if not tm_cfg.get("enabled", True):
        return leads

    feed_url = tm_cfg.get("feed_url", "https://techmeme.com/newsy_events.ics")
    positive_keywords = [k.lower() for k in tm_cfg.get("positive_keywords", [])]
    negative_keywords = [k.lower() for k in tm_cfg.get("negative_keywords", [])]

    try:
        headers = {"User-Agent": "Mozilla/5.0 (TechKeynoteCalendar/1.0)"}
        resp = requests.get(feed_url, headers=headers, timeout=12)
        if resp.status_code != 200:
            print(f"Failed to fetch Techmeme feed (status {resp.status_code})")
            return leads
        cal = Calendar.from_ical(resp.content)
    except Exception as err:
        print(f"Could not retrieve or parse Techmeme ICS feed: {err}")
        return leads

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        summary = str(component.get("summary", "")).strip()
        summary_lower = summary.lower()
        if any(neg in summary_lower for neg in negative_keywords):
            continue
        if not any(pos in summary_lower for pos in positive_keywords):
            continue

        start = component.get("dtstart").dt
        end = component.get("dtend").dt if component.get("dtend") else start
        start_date = start.date() if isinstance(start, datetime) else start
        end_date = end.date() if isinstance(end, datetime) else end
        if isinstance(start, date) and not isinstance(start, datetime) and end_date > start_date:
            end_date -= timedelta(days=1)  # DTEND is exclusive for all-day events

        leads.append({
            "title": summary,
            "start_date": start_date,
            "end_date": end_date,
            "url": str(component.get("url", "")).strip(),
        })

    return leads
