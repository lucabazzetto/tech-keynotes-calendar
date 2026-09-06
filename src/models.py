from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pytz
from typing import Optional
from icalendar import Event, Alarm

@dataclass
class KeynoteEvent:
    uid: str
    title: str
    company: str
    category: str
    start_time: datetime
    end_time: datetime
    stream_url: str
    description: str
    location: str = "Livestream"
    source: str = "curated"

    def to_dict(self):
        return {
            "uid": self.uid,
            "title": self.title,
            "company": self.company,
            "category": self.category,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "stream_url": self.stream_url,
            "description": self.description,
            "location": self.location,
            "source": self.source,
        }

    def to_ical_event(self) -> Event:
        event = Event()
        event.add("uid", self.uid)
        event.add("summary", f"[{self.company}] {self.title}")
        
        # Ensure UTC timezone for DTSTART and DTEND (strictly time-bound, no all-day DATE)
        start_utc = self.start_time.astimezone(pytz.utc)
        end_utc = self.end_time.astimezone(pytz.utc)
        
        event.add("dtstart", start_utc)
        event.add("dtend", end_utc)
        event.add("dtstamp", datetime.now(pytz.utc))
        
        # Livestream location & URL
        full_location = f"{self.location} - {self.stream_url}" if self.stream_url else self.location
        event.add("location", full_location)
        if self.stream_url:
            event.add("url", self.stream_url)
        
        # Rich description with direct watch link
        full_desc = (
            f"{self.description}\n\n"
            f"🔴 Watch Live Stream: {self.stream_url}\n"
            f"🏢 Company: {self.company}\n"
            f"🏷️ Category: {self.category}\n"
            f"📡 Pipeline Source: {self.source}"
        )
        event.add("description", full_desc)
        event.add("categories", [self.category, self.company, "Tech Keynote"])
        event.add("status", "CONFIRMED")
        
        # Alarm: 30 minutes before keynote
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", f"Keynote Starting Soon: [{self.company}] {self.title}")
        alarm.add("trigger", timedelta(minutes=-30))
        event.add_component(alarm)
        
        return event
