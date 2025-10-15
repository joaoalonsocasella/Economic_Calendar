# Global Economic Calendar Feeds  
### by [João Casella](https://github.com/joaoalonsocasella)

This repository hosts a continuously updated collection of **global economic calendars** — one for each country — provided in the standard **ICS (iCalendar)** format.  

All calendars are automatically updated through **GitHub Actions** and can be easily downloaded and added to **Outlook**, **Google Calendar**, **Apple Calendar**, or any other calendar app supporting iCalendar feeds.

## About the Project

**EconomicCalendar** is an open-source project designed to aggregate and distribute global **macroeconomic event data** in a clean and machine-readable format.

All data is sourced from:  
[**MarketPulse – Economic Calendar**](https://www.marketpulse.com/tools/economic-calendar/)



## How It Works

1. Each country’s data is scraped using an individual script inside the `scripts/single_country_request/` folder.  
2. The script `Update.py` runs daily through **GitHub Actions**, updating and regenerating all `.ics` files.  
3. The script `Combine.py` merges them into a single global `.ics`.  
4. Finally, `GenerateLinks.py` updates the live HTML page and the README if needed.


## Automation

The GitHub Actions workflow (`.github/workflows/update.yml`) automatically:
- Scrapes new data from MarketPulse  
- Regenerates all `.ics` calendars  
- Commits changes to the repo  
- Keeps the hosted version up-to-date on GitHub Pages  

No manual action is needed — subscribed calendars update automatically.



## Download Calendar Page

**Access all country calendars here:**  
🔗 [https://joaoalonsocasella.github.io/Economic_Calendar/](https://joaoalonsocasella.github.io/Economic_Calendar/)

After Downloading the `.ics`, you may want to choose:

- **Static**: Import it to your own calendar by dragging and dropping;
- **Dynamic** (recommended): Add it as a subscription - Copy the URL in the table and paste it in your own calendar (designated area)


## ⚠️ Disclaimer

This project is a **non-commercial educational initiative**.  
All information originates from publicly available sources, and no proprietary or credentialed APIs are used.


**Maintained by:** João Alonso Casella  
📧 [@joaoalonsocasella](https://github.com/joaoalonsocasella)  
🌐 [https://joaocasella.github.io/Economic_Calendar/](https://joaoalonsocasella.github.io/Economic_Calendar/)
