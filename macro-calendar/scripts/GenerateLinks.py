"""
GenerateLinks.py
----------------
Creates Markdown and HTML pages listing all public ICS subscription links.

Works with a repository structure like:
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
Last updated: 2025-10-14
"""

import os
from datetime import datetime

# === Configuration ===
BASE_URL = "https://raw.githubusercontent.com/joaocasella/econ-calendar/main/data/raw/ICS"
WEB_URL  = "webcal://raw.githubusercontent.com/joaocasella/econ-calendar/main/data/raw/ICS"
GLOBAL_URL = "https://raw.githubusercontent.com/joaocasella/econ-calendar/main/calendar.ics"
WEB_GLOBAL_URL = "webcal://raw.githubusercontent.com/joaocasella/econ-calendar/main/calendar.ics"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "..", "data", "raw", "ICS")
OUTPUT_MD = os.path.join(BASE_DIR, "..", "CALENDAR_LINKS.md")
OUTPUT_HTML = os.path.join(BASE_DIR, "..", "calendar_links.html")

# ISO3 flags (you can extend this dictionary)
FLAGS = {
    "ARE": "🇦🇪", "ARG": "🇦🇷", "AUS": "🇦🇺", "AUT": "🇦🇹", "BEL": "🇧🇪", "BRA": "🇧🇷", "CAN": "🇨🇦",
    "CHE": "🇨🇭", "CHL": "🇨🇱", "CHN": "🇨🇳", "COL": "🇨🇴", "CZE": "🇨🇿", "DEU": "🇩🇪", "EGY": "🇪🇬",
    "ESP": "🇪🇸", "EUR": "🇪🇺", "FIN": "🇫🇮", "FRA": "🇫🇷", "GBR": "🇬🇧", "GRC": "🇬🇷", "HKG": "🇭🇰",
    "HUN": "🇭🇺", "IDN": "🇮🇩", "IND": "🇮🇳", "IRL": "🇮🇪", "ISL": "🇮🇸", "ISR": "🇮🇱", "ITA": "🇮🇹",
    "JPN": "🇯🇵", "KOR": "🇰🇷", "MEX": "🇲🇽", "NLD": "🇳🇱", "NOR": "🇳🇴", "NZL": "🇳🇿", "POL": "🇵🇱",
    "PRT": "🇵🇹", "RUS": "🇷🇺", "SGP": "🇸🇬", "SWE": "🇸🇪", "TUR": "🇹🇷", "UKR": "🇺🇦", "USA": "🇺🇸"
}


def generate_links():
    print(f"\n[INFO] Generating calendar link list at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ics_files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(".ics")])
    if not ics_files:
        print("[WARN] No .ics files found in input directory.")
        return

    # --- Markdown table ---
    md_lines = [
        "# 🌎 Economic Calendar Feeds",
        "",
        "Below are the public subscription links for each country's economic calendar.",
        "",
        "| Country | Outlook (webcal://) | Google (https://) |",
        "|----------|--------------------|-------------------|"
    ]

    for f in ics_files:
        country = os.path.splitext(f)[0].split("_")[0].upper()  # Extract "BRA" from "BRA_2026.ics"
        flag = FLAGS.get(country, "🌍")
        web_link = f"{WEB_URL}/{f}"
        raw_link = f"{BASE_URL}/{f}"
        md_lines.append(f"| {flag} {country} | `{web_link}` | `{raw_link}` |")

    md_lines.append("")
    md_lines.append(f"**🌍 Global calendar:** `{WEB_GLOBAL_URL}`")
    md_lines.append("")
    md_lines.append(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    with open(OUTPUT_MD, "w", encoding="utf-8") as md:
        md.write("\n".join(md_lines))

    print(f" Markdown links written to: {OUTPUT_MD}")

    # --- HTML version ---
    html_header = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Economic Calendar Feeds</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; background: #fafafa; }
table { border-collapse: collapse; width: 100%; max-width: 900px; }
th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
th { background: #f0f0f0; }
a { text-decoration: none; color: #0056b3; }
</style>
</head>
<body>
<h1>🌎 Economic Calendar Feeds</h1>
<p>Click to subscribe directly to <b>Outlook</b> or <b>Google Calendar</b>.</p>
<table>
<tr><th>Country</th><th>Outlook (webcal)</th><th>Google (https)</th></tr>
"""

    html_rows = ""
    for f in ics_files:
        country = os.path.splitext(f)[0].split("_")[0].upper()
        flag = FLAGS.get(country, "🌍")
        web_link = f"{WEB_URL}/{f}"
        raw_link = f"{BASE_URL}/{f}"
        html_rows += f"<tr><td>{flag} {country}</td><td><a href='{web_link}'>Add to Outlook</a></td><td><a href='{raw_link}'>Add to Google Calendar</a></td></tr>\n"

    html_footer = f"""
<tr><td>🌍 Global</td><td><a href='{WEB_GLOBAL_URL}'>Add to Outlook</a></td><td><a href='{GLOBAL_URL}'>Add to Google Calendar</a></td></tr>
</table>
<p><em>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
</body></html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as html:
        html.write(html_header + html_rows + html_footer)

    print(f" HTML link page written to: {OUTPUT_HTML}\n")


if __name__ == "__main__":
    generate_links()
