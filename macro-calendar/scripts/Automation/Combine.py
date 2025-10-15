"""
Combine.py
----------
Merges all .ics files (one per country) into a single global calendar (calendar.ics),
preserving all event metadata and prefixing country tags in summaries.

Author: João Alonso Casella
Updated: 2025-10-15
"""

import os
from icalendar import Calendar
from datetime import datetime

# === Configuration ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "..", "data", "raw", "ICS")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "data","processed","calendar.ics")

def combine_calendars():
    print(f"\n[INFO] Starting calendar combination at {datetime.now():%Y-%m-%d %H:%M:%S}")
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

    total_events = 0
    for idx, file in enumerate(ics_files, start=1):
        country = os.path.splitext(file)[0].split("_")[0].upper()
        file_path = os.path.join(INPUT_DIR, file)

        print(f"[{idx}/{len(ics_files)}] Merging {file} ({country})")

        with open(file_path, "rb") as f:
            gcal = Calendar.from_ical(f.read())

        count = 0
        for component in gcal.walk("VEVENT"):
            # modify summary in place
            if "SUMMARY" in component:
                summary = component["SUMMARY"]
                if not summary.startswith(f"[{country}]"):
                    component["SUMMARY"] = f"[{country}] {summary}"
            combined.add_component(component)
            count += 1

        total_events += count
        print(f"   → Added {count} events from {country}")

    with open(OUTPUT_FILE, "wb") as f:
        f.write(combined.to_ical())

    print(f"\n[INFO] Combined {total_events} events into: {OUTPUT_FILE}")
    print(f"[INFO] Finished at {datetime.now():%Y-%m-%d %H:%M:%S}\n")

if __name__ == "__main__":
    combine_calendars()
