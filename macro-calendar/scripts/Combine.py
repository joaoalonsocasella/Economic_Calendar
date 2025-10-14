"""
Combine.py
----------
This script merges all individual .ics files (one per country)
into a single global calendar called 'calendar.ics'.

It automatically adds country tags to each event title
(e.g., [BRA] GDP YoY), preserving all original metadata.

Author: João Alonso Casella
Updated: 2025-10-14
"""

import os
from icalendar import Calendar, Event
from datetime import datetime

# === Configuration ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "..", "data", "raw", "ICS")
OUTPUT_FILE = os.path.join(BASE_DIR, "..","data","combined", "calendar.ics")

def combine_calendars():
    print(f"\n[INFO] Starting calendar combination at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[INFO] Reading ICS files from: {INPUT_DIR}\n")

    combined = Calendar()
    combined.add('prodid', '-//EconCalendar//joaocasella//')
    combined.add('version', '2.0')
    combined.add('X-WR-CALNAME', 'Global Economic Calendar')
    combined.add('X-WR-TIMEZONE', 'UTC')

    ics_files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(".ics")])

    if not ics_files:
        print("[WARN] No .ics files found to combine.")
        return

    for idx, file in enumerate(ics_files, start=1):
        country = os.path.splitext(file)[0].upper()
        file_path = os.path.join(INPUT_DIR, file)

        print(f"[{idx}/{len(ics_files)}] Merging {file} ({country})")

        with open(file_path, "r", encoding="utf-8") as f:
            gcal = Calendar.from_ical(f.read())

        count = 0
        for component in gcal.walk():
            if component.name == "VEVENT":
                event = Event()
                # Copy all standard properties
                for key in component.keys():
                    event.add(key, component.get(key))
                # Prefix country tag to title
                summary = component.get('summary')
                event['summary'] = f"[{country}] {summary}"
                combined.add_component(event)
                count += 1

        print(f"   → Added {count} events from {country}")

    with open(OUTPUT_FILE, "wb") as f:
        f.write(combined.to_ical())

    print(f"\n Combined calendar successfully written to: {OUTPUT_FILE}")
    print(f"[INFO] Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    combine_calendars()
