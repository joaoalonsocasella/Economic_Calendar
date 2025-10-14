# Global Economic Calendar Feeds (by João Casella)

A simple code to get the most recent economic calendar into your Google or Outlook Calendar.

**EconomicCalendar** is an open-source project that aggregates and distributes **global macroeconomic events** in standardized **ICS (iCalendar)** format — country by country — for direct integration with **Outlook**, **Google Calendar**, **Apple Calendar**, and any other iCalendar-compatible platform.

All calendars are **automatically updated** via [GitHub Actions](.github/workflows/update.yml) every day, ensuring analysts, traders, and researchers always have an up-to-date view of upcoming economic releases and events.


## Purpose

Provide a **modular, continuously updated economic calendar** where each country can be subscribed to or toggled independently within any calendar app.


## Data Source

All economic events and releases included in these calendars are collected from  
[**MarketPulse – Economic Calendar**](https://www.marketpulse.com/tools/economic-calendar/),  
a public tool provided by OANDA featuring global macroeconomic schedules and indicators.

The project’s backend scripts periodically fetch and normalize MarketPulse data into the  
iCalendar (ICS) format, ensuring consistent time zones, ISO country tags, and clean event titles.

> ⚠️ *Disclaimer:* This repository is an independent, non-commercial implementation for educational  
and analytical purposes. Data is publicly available through MarketPulse’s website and no proprietary  
APIs or credentials are used.



## How It Works

Inside the **`scripts/`** directory, you’ll find three core Python files:

| Script | Purpose |
|---------|----------|
| `Update.py` | Runs all individual country scrapers and regenerates `.ics` files |
| `Combine.py` | Merges all `.ics` files into a single global calendar |
| `GenerateLinks.py` | Creates Markdown and HTML subscription links automatically |

This modular setup was intentional — running all scrapers in a single process was prone to bugs and made debugging harder, so splitting them by country keeps the process cleaner and more reliable.

All scripts are orchestrated by **GitHub Actions**, which run automatically every day.  
Each run regenerates the `.ics` calendars, updates the subscription links, and commits them back to the repository — so your subscribed calendars always stay synchronized.


## Subscription Links

Below are the public links to subscribe directly to the economic calendars.

You can **subscribe to all countries at once**, or **select individual countries** to keep your Outlook/Google Calendar organized.

> ✅ *These are live calendars — once you subscribe, they will update automatically whenever this repository updates.*

---

### **Subscribe to All**

- **Outlook (webcal):**  
  [Add Global Calendar (Outlook)](webcal://raw.githubusercontent.com/joaocasella/econ-calendar/main/calendar.ics)
- **Google Calendar (https):**  
  [Add Global Calendar (Google)](https://raw.githubusercontent.com/joaocasella/econ-calendar/main/calendar.ics)

---

### **Subscribe Individually**
<!-- AUTO-LINKS:START -->
| Country | Outlook (webcal://) | Google (https://) |
|----------|--------------------|-------------------|
| 🇧🇷 BRA | [Add Outlook](webcal://raw.githubusercontent.com/joaocasella/econ-calendar/main/data/raw/ICS/BRA_2026.ics) | [Add Google](https://raw.githubusercontent.com/joaocasella/econ-calendar/main/data/raw/ICS/BRA_2026.ics) |
| 🇺🇸 USA | [Add Outlook](webcal://raw.githubusercontent.com/joaocasella/econ-calendar/main/data/raw/ICS/USA_2026.ics) | [Add Google](https://raw.githubusercontent.com/joaocasella/econ-calendar/main/data/raw/ICS/USA_2026.ics) |
| 🇪🇺 EUR | [Add Outlook](webcal://raw.githubusercontent.com/joaocasella/econ-calendar/main/data/raw/ICS/EUR_2026.ics) | [Add Google](https://raw.githubusercontent.com/joaocasella/econ-calendar/main/data/raw/ICS/EUR_2026.ics) |
<!-- AUTO-LINKS:END -->

*(This table is automatically updated by GitHub Actions — do not edit manually.)*



### Last Updated
*Generated automatically at:*  
`2025-10-14 09:00 UTC`



## Notes

Each `.ics` file represents a **standalone subscription**.  
When you click a `webcal://` link, Outlook (or any iCalendar client) will **subscribe** to it as a separate calendar —  
not import the events — meaning it will update automatically whenever new data is pushed by GitHub Actions.



## Automation Summary

This repository uses **GitHub Actions** to run automatically every day:

1. Execute scrapers (`Update.py`) for each country  
2. Combine all `.ics` files into `calendar.ics`  
3. Generate subscription links (`GenerateLinks.py`)  
4. Insert links into the README dynamically  
5. Commit & push all updates automatically



## Tech Stack

| Component | Description |
|------------|-------------|
| **Python 3.11** | Main scripting environment |
| **icalendar** | Library for creating and parsing `.ics` files |
| **Playwright / BeautifulSoup** | Used for scraping MarketPulse |
| **GitHub Actions** | Automates updates and publishing |
| **Raw GitHub URLs (`webcal://`)** | Enable live Outlook/Google Calendar subscriptions |



## License

This project is distributed under the **MIT License** —  
you are free to use, modify, and redistribute it with proper attribution.



## Author

**João Alonso Casella**  
• [GitHub](https://github.com/joaocasella)
