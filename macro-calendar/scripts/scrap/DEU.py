import re 
import os
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    download_dir = os.path.join(os.getcwd(), "macro-calendar/data/raw")
    os.makedirs(download_dir, exist_ok=True)

    browser = playwright.chromium.launch(headless=True, slow_mo=200)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    print("[INFO] Accessing MarketPulse...")
    page.goto("https://www.marketpulse.com/tools/economic-calendar/", timeout=60000)
    page.wait_for_load_state("domcontentloaded")

    # --- COUNTRY FILTER ---
    print("[INFO] Applying 'Germany' filter...")
    page.get_by_role("button", name="Filter").click()
    page.wait_for_selector("button:has-text('Clear')")
    page.wait_for_timeout(1200)
    page.get_by_role("button", name="Clear").click()
    page.wait_for_timeout(1200)
    page.get_by_role("checkbox", name="Germany Germany").check()
    page.wait_for_timeout(1200)
    page.get_by_role("button", name="Apply filter").click()
    page.wait_for_timeout(1200)

    # --- DEFINE DATE RANGE ---
    print("[INFO] Automatically selecting date range...")
    page.get_by_role("button", name=re.compile(r"^.* - .*$")).click()
    page.wait_for_timeout(1200)

    # Locate the year combobox and collect available options
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
    
    # Automatically select the last available date
    valid_days = page.locator("div[role='gridcell']:not([aria-disabled='true'])")
    total_days = valid_days.count()
    print(f"[INFO] Total clickable days: {total_days}")

    last_day_name = valid_days.last.text_content()
    print(f"[INFO] Last visible date: {last_day_name}")

    page.wait_for_timeout(1200)
    valid_days.last.click()
    page.wait_for_timeout(1200)
    page.get_by_role("button", name="Apply").click()
    page.wait_for_timeout(1500)

    # --- DOWNLOAD MENU ---
    print("[INFO] Opening download menu...")
    page.locator(".fxs_selectable-wrapper").click()
    page.wait_for_selector("button:has-text('ICS')")

    # --- DOWNLOAD ICS ---
    print("[INFO] Downloading .ICS file...")
    with page.expect_download() as ics_info:
        page.get_by_role("button", name="ICS").click()
    ics_download = ics_info.value
    ics_path = os.path.join(download_dir, f"ICS/DEU.ics")
    ics_download.save_as(ics_path)
    print(f"ICS saved to: {ics_path}")
    page.wait_for_timeout(1200)

    # --- DOWNLOAD CSV ---
    page.locator(".fxs_selectable-wrapper").click()
    page.wait_for_selector("button:has-text('CSV')")
    with page.expect_download() as csv_info:
        page.get_by_role("button", name="CSV").click()
    csv_download = csv_info.value
    csv_path = os.path.join(download_dir, f"CSV/DEU.csv")
    csv_download.save_as(csv_path)
    print(f"CSV saved to: {csv_path}")
    page.wait_for_timeout(1200)

    context.close()
    browser.close()
    print("Completed successfully!")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
