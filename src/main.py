import sys
import os
from src.pipeline import run_pipeline
from src.generator import generate_ics, generate_json, generate_html

def main():
    print("==================================================")
    print("🚀 Tech & Data Engineering Keynote Pipeline Starting")
    print("==================================================")
    
    events = run_pipeline()
    
    if not events:
        print("⚠️ Warning: No events retrieved from pipeline.")
        sys.exit(0)

    # Output directory
    dist_dir = "public"
    os.makedirs(dist_dir, exist_ok=True)

    ics_path = os.path.join(dist_dir, "tech_events.ics")
    json_path = os.path.join(dist_dir, "events.json")
    html_path = os.path.join(dist_dir, "index.html")

    generate_ics(events, ics_path)
    generate_json(events, json_path)
    generate_html(events, html_path)

    print("==================================================")
    print(f"✨ Pipeline completed successfully! {len(events)} events ready.")
    print("==================================================")

if __name__ == "__main__":
    main()
