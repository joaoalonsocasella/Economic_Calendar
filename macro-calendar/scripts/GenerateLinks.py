"""
GenerateLinks.py
----------------
Creates a simple HTML index page listing download links for each country's .ICS file.

Repository structure:
macro-calendar/
 ├── data/
 │   └── raw/
 │       └── ICS/
 │           ├── BRA_2026.ics
 │           ├── USA_2026.ics
 │           ├── ...
 ├── calendar.ics
 └── scripts/GenerateLinks.py

Author: João Alonso Casella
Last updated: 2025-10-15
"""

import os
from datetime import datetime

# === Configuration ===
BASE_URL = "https://joaocasella.github.io/Economic_Calendar/macro-calendar/data/raw/ICS"
GLOBAL_URL = "https://joaocasella.github.io/Economic_Calendar/macro-calendar/calendar.ics"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "..", "data", "raw", "ICS")
OUTPUT_HTML = os.path.join(BASE_DIR, "..", "..", "index.html")

def generate_links():
    print(f"\n[INFO] Generating calendar download page at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    ics_files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(".ics")])
    if not ics_files:
        print("[WARN] No .ics files found in input directory.")
        return

    html_header = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Economic Calendar ICS Downloads</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; background: #fafafa; color: #222; }
h1 { margin-bottom: 10px; }
p  { margin-bottom: 30px; }
table { border-collapse: collapse; width: 100%; max-width: 800px; background: #fff; }
th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
th { background: #f0f0f0; }
a { color: #0056b3; text-decoration: none; }
a:hover { text-decoration: underline; }
footer { margin-top: 40px; font-size: 0.9em; color: #555; }
</style>
</head>
<body>
<h1>Global Economic Calendar Data</h1>
<p>Below are direct download links for each country's <code>.ics</code> file. These calendars are updated automatically via GitHub Actions.</p>

<table>
<tr><th>Country</th><th>Download Link</th></tr>
"""

    html_rows = ""
    for f in ics_files:
        country = os.path.splitext(f)[0].split("_")[0].upper()
        country_name = country  # No flags or fancy formatting
        file_link = f"{BASE_URL}/{f}"
        html_rows += f"<tr><td>{country_name}</td><td><a href='{file_link}' download>Download {f}</a></td></tr>\n"

    html_footer = f"""
<tr><td><strong>GLOBAL</strong></td><td><a href='{GLOBAL_URL}' download>Download calendar.ics</a></td></tr>
</table>

<footer>
<p>Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.</p>
<p>Maintained by João Alonso Casella — Economic Calendar Project.</p>
</footer>
</body></html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as html:
        html.write(html_header + html_rows + html_footer)

    print(f"[INFO] HTML download page written to: {OUTPUT_HTML}\n")


if __name__ == "__main__":
    generate_links()
