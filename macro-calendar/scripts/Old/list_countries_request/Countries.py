import re
import os
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    download_dir = os.path.join(os.getcwd(), "macro-calendar/data/raw")
    os.makedirs(os.path.join(download_dir, "ICS"), exist_ok=True)
    os.makedirs(os.path.join(download_dir, "CSV"), exist_ok=True)

    # --- ISO3 country mapping ---
    country_iso3 = {
        "United Arab Emirates": "ARE",
        "Argentina": "ARG",
        "Australia": "AUS",
        "Austria": "AUT",
        "Belgium": "BEL",
        "Brazil": "BRA",
        "Canada": "CAN",
        "Switzerland": "CHE",
        "Chile": "CHL",
        "China": "CHN",
        "Colombia": "COL",
        "Czech Republic": "CZE",
        "Germany": "DEU",
        "Egypt": "EGY",
        "Spain": "ESP",
        "Eurozone": "EUR",
        "Finland": "FIN",
        "France": "FRA",
        "United Kingdom": "GBR",
        "Greece": "GRC",
        "Hong Kong SAR": "HKG",
        "Hungary": "HUN",
        "Indonesia": "IDN",
        "India": "IND",
        "Ireland": "IRL",
        "Iceland": "ISL",
        "Israel": "ISR",
        "Italy": "ITA",
        "Japan": "JPN",
        "South Korea": "KOR",
        "Kuwait": "KWT",
        "Mexico": "MEX",
        "Netherlands, The": "NLD",
        "Norway": "NOR",
        "New Zealand": "NZL",
        "Poland": "POL",
        "Portugal": "PRT",
        "Qatar": "QAT",
        "Romania": "ROU",
        "Russia": "RUS",
        "Saudi Arabia": "SAU",
        "Singapore": "SGP",
        "Slovakia": "SVK",
        "Sweden": "SWE",
        "Thailand": "THA",
        "Türkiye": "TUR",
        "Ukraine": "UKR",
        "United States": "USA",
        "Vietnam": "VNM",
        "South Africa": "ZAF"
    }

    countries = list(country_iso3.keys())

    browser = playwright.chromium.launch(headless=False, slow_mo=200)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    print("[INFO] Accessing MarketPulse...")
    page.goto("https://www.marketpulse.com/tools/economic-calendar/", timeout=90000)
    page.wait_for_load_state("domcontentloaded")

    for idx, country in enumerate(countries, start=1):
        try:
            iso_code = country_iso3[country]
            print(f"\n [{idx}/{len(countries)}] Processing: {country} ({iso_code})")

            # Open filter menu
            page.get_by_role("button", name="Filter").click()
            page.wait_for_selector("button:has-text('Clear')")
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="Clear").click()
            page.wait_for_timeout(1000)

            checkbox_name = f"{country} {country}"
            page.get_by_role("checkbox", name=checkbox_name).check()
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="Apply filter").click()
            page.wait_for_timeout(2000)

            # --- Reset possible date selection issues ---
            try:
                # Click outside to close overlays
                page.mouse.click(10, 10)
                page.wait_for_timeout(500)
                # Sometimes helps to reload part of the DOM
                page.wait_for_selector(".fxs_table", timeout=20000)
            except:
                pass

            # Select maximum available date range
            print("[INFO] Selecting date range...")
            page.get_by_role("button", name=re.compile(r"^.* - .*$")).click()
            page.wait_for_timeout(1500)

            select_year = page.get_by_role("combobox").nth(3)
            page.wait_for_selector("select[name='year']", state="attached")
            available_years = select_year.locator("option").evaluate_all(
                "opts => opts.map(o => o.value.trim()).filter(v => v)"
            )
            last_year = available_years[-1]
            print(f"[INFO] Available years: {available_years}")
            print(f"[INFO] Latest available year: {last_year}")
            select_year.select_option(last_year)
            page.wait_for_timeout(1200)

            valid_days = page.locator("div[role='gridcell']:not([aria-disabled='true'])")
            total_days = valid_days.count()
            print(f"[INFO] Total clickable days: {total_days}")
            last_day_name = valid_days.last.text_content()
            print(f"[INFO] Last visible date: {last_day_name}")
            valid_days.last.click()
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="Apply").click()
            page.wait_for_timeout(4000)

            # --- Download section ---
            print("[INFO] Downloading files...")
            page.locator(".fxs_selectable-wrapper").click()
            page.wait_for_selector("button:has-text('ICS')")

            # Download ICS
            with page.expect_download() as ics_info:
                page.get_by_role("button", name="ICS").click()
            ics_download = ics_info.value
            ics_path = os.path.join(download_dir, "ICS", f"{iso_code}_{last_year}.ics")
            ics_download.save_as(ics_path)
            print(f" ICS saved: {ics_path}")

            # Download CSV
            page.locator(".fxs_selectable-wrapper").click()
            page.wait_for_selector("button:has-text('CSV')")
            with page.expect_download() as csv_info:
                page.get_by_role("button", name="CSV").click()
            csv_download = csv_info.value
            csv_path = os.path.join(download_dir, "CSV", f"{iso_code}_{last_year}.csv")
            csv_download.save_as(csv_path)
            print(f" CSV saved: {csv_path}")

            # Wait and clear before next iteration
            page.wait_for_timeout(3000)

        except Exception as e:
            print(f"Failed to process {country}: {e}")
            # Ensure overlay is closed before next iteration
            page.mouse.click(10, 10)
            page.wait_for_timeout(3000)
            continue

    context.close()
    browser.close()
    print("\n Data collection completed successfully!")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
