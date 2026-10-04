import os
import unittest
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar
from src.models import KeynoteEvent
from src.extractors.curated import load_curated_events
from src.extractors.youtube import parse_live_details
from src.pipeline import merge_and_deduplicate
from src.generator import generate_ics

class TestKeynotePipeline(unittest.TestCase):
    def test_curated_events_loading(self):
        # Load as of a fixed past date so the registry's events aren't filtered as already past.
        events = load_curated_events("config/curated_events.yaml", now=datetime(2026, 1, 1, tzinfo=pytz.utc))
        self.assertGreater(len(events), 0)
        for ev in events:
            self.assertIsNotNone(ev.start_time.tzinfo)
            self.assertIsNotNone(ev.end_time.tzinfo)
            self.assertGreater(ev.end_time, ev.start_time)
            self.assertTrue(ev.stream_url.startswith("http"))
            self.assertTrue(ev.source_url.startswith("http"))

    def test_curated_rejects_unconfirmed_and_past_events(self):
        path = "public/test_curated.yaml"
        with open(path, "w") as f:
            f.write(
                "events:\n"
                "- {uid: a, title: No Source, company: X, start_time: '2030-01-01T10:00:00-08:00', stream_url: 'https://x'}\n"
                "- {uid: b, title: Past, company: X, start_time: '2020-01-01T10:00:00-08:00', stream_url: 'https://x', source_url: 'https://x'}\n"
                "- {uid: c, title: Good, company: X, start_time: '2030-01-01T10:00:00-08:00', stream_url: 'https://x', source_url: 'https://x'}\n"
            )
        events = load_curated_events(path)
        os.remove(path)
        self.assertEqual([e.uid for e in events], ["c"])
        self.assertEqual(events[0].end_time - events[0].start_time, timedelta(minutes=60))

    def test_youtube_live_details_parsing(self):
        html = 'x"liveBroadcastDetails":{"isLiveNow":false,"startTimestamp":"2026-10-28T16:00:00+00:00"},"y"'
        self.assertEqual(parse_live_details(html)["startTimestamp"], "2026-10-28T16:00:00+00:00")
        self.assertIsNone(parse_live_details("<html>regular upload</html>"))

    def _event(self, uid, source, start, url="https://example.com"):
        return KeynoteEvent(uid=uid, title=uid, company="GitHub", category="c", start_time=start,
                            end_time=start + timedelta(hours=1), stream_url=url, description="", source=source)

    def test_merge_keeps_distinct_days_and_merges_same_stream(self):
        day1 = datetime(2026, 10, 28, 16, 0, tzinfo=pytz.utc)
        curated = self._event("cur", "curated_registry", day1)
        yt_same = self._event("yt1", "youtube_live", day1, "https://www.youtube.com/watch?v=abc")
        yt_other = self._event("yt2", "youtube_live", day1 + timedelta(days=1))
        merged = merge_and_deduplicate([curated, yt_same, yt_other])
        self.assertEqual([e.uid for e in merged], ["cur", "yt2"])
        self.assertEqual(merged[0].stream_url, "https://www.youtube.com/watch?v=abc")

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
