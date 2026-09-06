import json
import os
from typing import List
from icalendar import Calendar
from src.models import KeynoteEvent

def generate_ics(events: List[KeynoteEvent], output_path: str = "public/tech_events.ics"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cal = Calendar()
    cal.add("prodid", "-//TechAndDataKeynotes//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", "Tech & Data Keynotes")
    cal.add("x-wr-caldesc", "Curated keynotes: Apple, Google, Samsung, OpenAI, AWS, Databricks, Snowflake, NVIDIA. Exact times & livestream links.")
    cal.add("x-wr-timezone", "UTC")
    cal.add("refresh-interval;value=duration", "PT6H")
    cal.add("x-published-ttl", "PT6H")

    for ev in events:
        cal.add_component(ev.to_ical_event())

    with open(output_path, "wb") as f:
        f.write(cal.to_ical())
    print(f"✅ Generated iCalendar feed: {output_path} ({len(events)} events)")

def generate_json(events: List[KeynoteEvent], output_path: str = "public/events.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data = [e.to_dict() for e in events]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Generated JSON API: {output_path}")

def generate_html(events: List[KeynoteEvent], output_path: str = "public/index.html"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    events_json = json.dumps([e.to_dict() for e in events])
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tech & Data Engineering Keynotes Tracker</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📡</text></svg>">
  <style>
    :root {{
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #c9d1d9;
      --heading: #f0f6fc;
      --accent: #58a6ff;
      --accent-hover: #1f6feb;
      --hardware: #f0883e;
      --data: #3fb950;
      --ai: #a371f7;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
    body {{ background-color: var(--bg); color: var(--text); padding: 2rem 1rem; line-height: 1.5; }}
    .container {{ max-width: 1000px; margin: 0 auto; }}
    header {{ text-align: center; margin-bottom: 2.5rem; }}
    h1 {{ color: var(--heading); font-size: 2.2rem; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }}
    .subtitle {{ color: #8b949e; font-size: 1.1rem; max-width: 650px; margin: 0 auto 1.5rem; }}
    
    .cta-banner {{
      background: linear-gradient(135deg, rgba(88, 166, 255, 0.1), rgba(163, 113, 247, 0.1));
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 2rem;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }}
    .cta-text h3 {{ color: var(--heading); margin-bottom: 0.25rem; font-size: 1.2rem; }}
    .cta-text p {{ color: #8b949e; font-size: 0.95rem; }}
    .cta-actions {{ display: flex; gap: 0.75rem; flex-wrap: wrap; }}
    
    .btn {{
      padding: 0.6rem 1.2rem;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.9rem;
      text-decoration: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      border: none;
      transition: all 0.2s ease;
    }}
    .btn-primary {{ background: var(--accent); color: #0d1117; }}
    .btn-primary:hover {{ background: var(--accent-hover); color: #fff; }}
    .btn-secondary {{ background: #21262d; color: var(--heading); border: 1px solid var(--border); }}
    .btn-secondary:hover {{ background: #30363d; border-color: #8b949e; }}
    
    .filters {{ display: flex; gap: 0.5rem; margin-bottom: 1.5rem; overflow-x: auto; padding-bottom: 0.5rem; }}
    .filter-btn {{
      background: #21262d;
      color: #8b949e;
      border: 1px solid var(--border);
      padding: 0.4rem 0.9rem;
      border-radius: 20px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 500;
    }}
    .filter-btn.active, .filter-btn:hover {{ background: var(--accent); color: #0d1117; border-color: var(--accent); }}
    
    .events-grid {{ display: flex; flex-direction: column; gap: 1rem; }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.25rem 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      transition: border-color 0.2s ease;
    }}
    .card:hover {{ border-color: #58a6ff66; }}
    
    .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }}
    .card-title {{ font-size: 1.25rem; font-weight: 600; color: var(--heading); }}
    .badge {{
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.2rem 0.6rem;
      border-radius: 12px;
      white-space: nowrap;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .badge-hardware {{ background: rgba(240, 136, 62, 0.15); color: var(--hardware); border: 1px solid rgba(240, 136, 62, 0.4); }}
    .badge-datacloude {{ background: rgba(63, 185, 80, 0.15); color: var(--data); border: 1px solid rgba(63, 185, 80, 0.4); }}
    .badge-ai {{ background: rgba(163, 113, 247, 0.15); color: var(--ai); border: 1px solid rgba(163, 113, 247, 0.4); }}
    
    .time-row {{ display: flex; flex-wrap: wrap; gap: 1.5rem; font-size: 0.9rem; color: #8b949e; align-items: center; }}
    .time-item {{ display: flex; align-items: center; gap: 0.4rem; }}
    .countdown {{ font-weight: 600; color: var(--accent); }}
    .card-desc {{ color: #8b949e; font-size: 0.95rem; }}
    
    .card-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 0.25rem; padding-top: 0.75rem; border-top: 1px solid #21262d; }}
    .company-tag {{ font-weight: 600; color: #f0f6fc; font-size: 0.85rem; }}
    .card-actions {{ display: flex; gap: 0.5rem; }}
    
    .toast {{
      position: fixed; bottom: 20px; right: 20px;
      background: #238636; color: #fff;
      padding: 0.75rem 1.25rem; border-radius: 8px;
      font-weight: 500; font-size: 0.9rem;
      display: none; box-shadow: 0 4px 12px rgba(0,0,0,0.4);
      z-index: 100;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>📡 Tech & Data Engineering Keynotes</h1>
      <p class="subtitle">Curated live event broadcasts from Apple, Google, Samsung, AWS, Databricks, Snowflake, NVIDIA, and OpenAI. Exact keynote hours, livestream links, zero all-day spam.</p>
    </header>

    <div class="cta-banner">
      <div class="cta-text">
        <h3>📅 Sync to your Google Calendar</h3>
        <p>Subscribe once and your calendar will automatically show upcoming showcases with direct streaming links.</p>
      </div>
      <div class="cta-actions">
        <button class="btn btn-primary" onclick="copyIcsUrl()">📋 Copy Calendar URL (.ics)</button>
        <button class="btn btn-secondary" onclick="openGCalSubscribe()">➕ Subscribe in Google Calendar</button>
      </div>
    </div>

    <div class="filters">
      <button class="filter-btn active" onclick="filterEvents('all', this)">All Keynotes</button>
      <button class="filter-btn" onclick="filterEvents('Hardware & Consumer Tech', this)">📱 Hardware & Gadgets</button>
      <button class="filter-btn" onclick="filterEvents('Data & Cloud Infrastructure', this)">☁️ Data & Cloud</button>
      <button class="filter-btn" onclick="filterEvents('AI & LLMs', this)">🧠 AI & Frontier Models</button>
    </div>

    <div id="events-container" class="events-grid"></div>
  </div>

  <div id="toast" class="toast">Copied calendar link to clipboard!</div>

  <script>
    const eventsData = {events_json};
    let currentFilter = 'all';

    function getIcsAbsoluteUrl() {{
      const loc = window.location.href.split('?')[0].split('#')[0];
      const base = loc.substring(0, loc.lastIndexOf('/') + 1);
      return base + 'tech_events.ics';
    }}

    function copyIcsUrl() {{
      const url = getIcsAbsoluteUrl();
      navigator.clipboard.writeText(url).then(() => {{
        showToast('Copied feed URL: ' + url);
      }});
    }}

    function openGCalSubscribe() {{
      const icsUrl = getIcsAbsoluteUrl();
      // Google Calendar Subscribe by URL web link
      const gcalUrl = 'https://calendar.google.com/calendar/render?cid=' + encodeURIComponent(icsUrl);
      window.open(gcalUrl, '_blank');
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      toast.innerText = msg;
      toast.style.display = 'block';
      setTimeout(() => {{ toast.style.display = 'none'; }}, 3000);
    }}

    function filterEvents(category, el) {{
      currentFilter = category;
      document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
      el.classList.add('active');
      render();
    }}

    function render() {{
      const container = document.getElementById('events-container');
      container.innerHTML = '';

      const filtered = eventsData.filter(ev => {{
        if (currentFilter === 'all') return true;
        return ev.category === currentFilter;
      }});

      if (filtered.length === 0) {{
        container.innerHTML = '<div style="text-align:center; padding: 3rem; color: #8b949e;">No upcoming keynotes found in this category.</div>';
        return;
      }}

      filtered.forEach(ev => {{
        const start = new Date(ev.start_time);
        const end = new Date(ev.end_time);

        const dateFormatted = start.toLocaleDateString(undefined, {{
          weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
        }});
        const startTimeStr = start.toLocaleTimeString(undefined, {{ hour: '2-digit', minute: '2-digit' }});
        const endTimeStr = end.toLocaleTimeString(undefined, {{ hour: '2-digit', minute: '2-digit' }});
        const tzName = Intl.DateTimeFormat().resolvedOptions().timeZone;

        // Badge class
        let badgeClass = 'badge-hardware';
        if (ev.category.includes('Data') || ev.category.includes('Cloud')) badgeClass = 'badge-datacloude';
        else if (ev.category.includes('AI')) badgeClass = 'badge-ai';

        const gcalAddUrl = 'https://calendar.google.com/calendar/render?action=TEMPLATE' +
          '&text=' + encodeURIComponent('[' + ev.company + '] ' + ev.title) +
          '&dates=' + start.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z/' +
                      end.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z' +
          '&details=' + encodeURIComponent(ev.description + '\\n\\nStream: ' + ev.stream_url) +
          '&location=' + encodeURIComponent(ev.stream_url || ev.location);

        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
          <div class="card-header">
            <div class="card-title">${{ev.title}}</div>
            <span class="badge ${{badgeClass}}">${{ev.category}}</span>
          </div>
          <div class="time-row">
            <div class="time-item">📅 ${{dateFormatted}}</div>
            <div class="time-item">⏰ ${{startTimeStr}} – ${{endTimeStr}} (${{tzName}})</div>
          </div>
          <div class="card-desc">${{ev.description}}</div>
          <div class="card-footer">
            <span class="company-tag">🏢 ${{ev.company}}</span>
            <div class="card-actions">
              ${{ev.stream_url ? `<a href="${{ev.stream_url}}" target="_blank" class="btn btn-secondary">🔴 Watch Stream</a>` : ''}}
              <a href="${{gcalAddUrl}}" target="_blank" class="btn btn-primary">➕ Add Event</a>
            </div>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    render();
  </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Generated Web UI: {output_path}")
