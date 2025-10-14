# Global Economic Calendar Feeds (by João Casella)

A simple code to get the most recent economic calendar into your google agenda/outlook calendar

**EconomicCalendar** is an open-source project that aggregates and distributes **global macroeconomic events** in standardized **ICS (iCalendar)** format — country by country — for direct integration with **Outlook**, **Google Calendar**, **Apple Calendar**, and any other iCalendar-compatible platform.

All calendars are **automatically updated** via [GitHub Actions](.github/workflows/update.yml) every 6 hours, ensuring analysts, traders, and researchers always have an up-to-date view of upcoming economic releases and events.

---

## Purpose

Provide a **modular, continuously updated economic calendar** where each country can be subscribed to or toggled independently within any calendar app.

---

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

Inside the **`scripts/`** directory, you’ll find a subfolder named **`scrap/`**, which contains one web-scraping script per country.  
This modular setup was intentional — running all scrapers in a single loop was prone to bugs and made debugging harder, so splitting them by country keeps the process cleaner and more reliable.

Also within **`scripts/`**, there’s a central file called **`Update.py`**, which is executed automatically by **GitHub Actions**.  
This script regenerates and updates all `.ics` calendar files on a fixed schedule, ensuring that the public links below always reflect the latest data.

There are two subscription options available:
- **Subscribe to All:** imports a unified `.ics` containing all countries.
- **Subscribe Individually:** allows you to follow specific countries separately.

Once you click any subscription link, the calendar will be added directly to your **Outlook** (or any iCalendar-compatible app).  
You won’t need to click it again — it will automatically stay up to date through GitHub’s scheduled updates.





