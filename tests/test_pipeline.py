import unittest
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar
from src.models import KeynoteEvent
from src.extractors.curated import load_curated_events
from src.generator import generate_ics

class TestKeynotePipeline(unittest.TestCase):
    def test_curated_events_loading(self):
        events = load_curated_events("config/curated_events.yaml")
        self.assertGreater(len(events), 5)
        for ev in events:
            self.assertIsNotNone(ev.start_time.tzinfo)
            self.assertIsNotNone(ev.end_time.tzinfo)
            self.assertGreater(ev.end_time, ev.start_time)
            self.assertTrue(ev.stream_url.startswith("http"))

    def test_ical_generation_and_validation(self):
        start = datetime.now(pytz.utc) + timedelta(days=1)
        end = start + timedelta(hours=2)
        ev = KeynoteEvent(
            uid="test-unit-1",
            title="Test Keynote",
            company="Apple",
            category="Hardware & Consumer Tech",
            start_time=start,
            end_time=end,
            stream_url="https://example.com/stream",
            description="Unit test description"
        )
        test_ics_path = "public/test_calendar.ics"
        generate_ics([ev], test_ics_path)

        with open(test_ics_path, "rb") as f:
            cal = Calendar.from_ical(f.read())
        
        events_found = [c for c in cal.walk() if c.name == "VEVENT"]
        self.assertEqual(len(events_found), 1)
        v = events_found[0]
        self.assertEqual(str(v.get("summary")), "[Apple] Test Keynote")
        self.assertEqual(str(v.get("url")), "https://example.com/stream")
        # Ensure DTSTART is a datetime (RFC 5545 date-time format), not date
        self.assertIsInstance(v.get("dtstart").dt, datetime)

if __name__ == "__main__":
    unittest.main()
