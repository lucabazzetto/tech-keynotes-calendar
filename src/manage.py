import argparse
import os
import re
import sys
import yaml
from datetime import datetime
from dateutil import parser
import pytz
import requests

def load_yaml(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_yaml(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def resolve_youtube_channel_id(handle_or_url):
    """Resolves YouTube handle (e.g. @anthropic-ai or full URL) to channel ID (UC...)"""
    if handle_or_url.startswith("UC") and len(handle_or_url) == 24:
        return handle_or_url

    url = handle_or_url
    if not url.startswith("http"):
        handle = handle_or_url.lstrip("@")
        url = f"https://www.youtube.com/@{handle}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        cookies = {"SOCS": "CAESEwgDEgk1MzQzMjU2MTcaAmVuIAEaBgiA_LyaBg"}
        resp = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        if resp.status_code == 200:
            m = re.search(r'\"(UC[a-zA-Z0-9_-]{22})\"', resp.text)
            if m:
                return m.group(1)
    except Exception as e:
        print(f"Could not auto-resolve channel ID from {url}: {e}")
    return None

def cmd_add_channel(args):
    sources_path = "config/sources.yaml"
    cfg = load_yaml(sources_path)
    
    ch_id = args.channel_id
    if not ch_id or not ch_id.startswith("UC"):
        print(f"Resolving YouTube channel for: {args.handle or args.channel_id}...")
        resolved = resolve_youtube_channel_id(args.handle or args.channel_id)
        if resolved:
            ch_id = resolved
            print(f"✅ Found YouTube Channel ID: {ch_id}")
        else:
            print(f"⚠️ Could not auto-resolve channel ID. Please specify explicit --channel-id (e.g. UC...)")
            sys.exit(1)

    channels = cfg.setdefault("youtube_channels", [])
    for ch in channels:
        if ch.get("id") == ch_id:
            print(f"Channel {ch_id} ({args.company}) already registered in sources.yaml.")
            return

    new_channel = {
        "id": ch_id,
        "name": args.name or args.company,
        "category": args.category,
        "company": args.company,
        "default_duration_minutes": args.duration,
        "canonical_time": args.time,
        "canonical_tz": args.tz,
        "livestream_hub": f"https://www.youtube.com/channel/{ch_id}/streams"
    }
    channels.append(new_channel)

    # Also add keyword to techmeme positive keywords if not present
    tm_keywords = cfg.setdefault("techmeme", {}).setdefault("positive_keywords", [])
    for kw in [args.company, f"{args.company} Event", f"{args.company} Keynote"]:
        if kw not in tm_keywords:
            tm_keywords.append(kw)

    save_yaml(sources_path, cfg)
    print(f"✅ Successfully added {args.company} to config/sources.yaml and updated Techmeme keywords.")

def cmd_add_event(args):
    curated_path = "config/curated_events.yaml"
    data = load_yaml(curated_path)
    events = data.setdefault("events", [])

    # Validate timestamps
    try:
        start_dt = parser.parse(args.start_time)
        end_dt = parser.parse(args.end_time)
        if start_dt.tzinfo is None or end_dt.tzinfo is None:
            print("❌ Error: Both start_time and end_time must include an explicit timezone offset (e.g. -07:00 or Z).")
            sys.exit(1)
        if end_dt <= start_dt:
            print("❌ Error: end_time must be after start_time.")
            sys.exit(1)
    except Exception as err:
        print(f"❌ Timestamp parse error: {err}")
        sys.exit(1)

    uid = args.uid or f"{args.company.lower()}-{start_dt.strftime('%Y%m%d')}"
    
    # Check duplicate
    for ev in events:
        if ev.get("uid") == uid:
            print(f"Event with UID '{uid}' already exists in curated_events.yaml.")
            return

    new_event = {
        "uid": uid,
        "title": args.title,
        "company": args.company,
        "category": args.category,
        "start_time": args.start_time,
        "end_time": args.end_time,
        "stream_url": args.stream_url,
        "description": args.description,
        "location": args.location
    }
    events.append(new_event)
    save_yaml(curated_path, data)
    print(f"✅ Successfully registered event '{args.title}' in config/curated_events.yaml.")

def main():
    parser_root = argparse.ArgumentParser(description="Manage Tech Keynotes Sources and Events")
    subparsers = parser_root.add_subparsers(dest="command", required=True)

    # add-channel
    p_chan = subparsers.add_parser("add-channel", help="Add a company YouTube channel and Techmeme topic to monitored sources")
    p_chan.add_argument("--company", required=True, help="Company name (e.g. Anthropic, Figma)")
    p_chan.add_argument("--category", default="AI & LLMs", choices=["Hardware & Consumer Tech", "Data & Cloud Infrastructure", "AI & LLMs", "Software & Dev Tools"])
    p_chan.add_argument("--handle", help="YouTube handle (e.g. @anthropic-ai)")
    p_chan.add_argument("--channel-id", help="Explicit YouTube Channel ID (starts with UC...)")
    p_chan.add_argument("--name", help="Display name (defaults to company)")
    p_chan.add_argument("--time", default="10:00", help="Canonical broadcast time (default 10:00)")
    p_chan.add_argument("--tz", default="America/Los_Angeles", help="Canonical timezone (default America/Los_Angeles)")
    p_chan.add_argument("--duration", type=int, default=90, help="Default duration in minutes")
    p_chan.set_defaults(func=cmd_add_channel)

    # add-event
    p_ev = subparsers.add_parser("add-event", help="Add a specific curated event to curated_events.yaml")
    p_ev.add_argument("--uid", help="Unique event ID")
    p_ev.add_argument("--title", required=True, help="Event title (e.g. Anthropic Spring Showcase)")
    p_ev.add_argument("--company", required=True, help="Company name")
    p_ev.add_argument("--category", default="AI & LLMs")
    p_ev.add_argument("--start-time", required=True, help="ISO-8601 start with TZ offset (e.g. 2026-10-22T10:00:00-07:00)")
    p_ev.add_argument("--end-time", required=True, help="ISO-8601 end with TZ offset (e.g. 2026-10-22T11:30:00-07:00)")
    p_ev.add_argument("--stream-url", required=True, help="Livestream / official landing URL")
    p_ev.add_argument("--description", default="Official live broadcast keynote presentation.")
    p_ev.add_argument("--location", default="Livestream")
    p_ev.set_defaults(func=cmd_add_event)

    args = parser_root.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
