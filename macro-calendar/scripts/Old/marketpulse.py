import re
import os
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    download_dir = os.path.join(os.getcwd(), "data/marketpulse")
    os.makedirs(download_dir, exist_ok=True)

    browser = playwright.chromium.launch(headless=False, slow_mo=200)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    print("[INFO] Acessando MarketPulse...")
    page.goto("https://www.marketpulse.com/tools/economic-calendar/", timeout=60000)
    page.wait_for_load_state("domcontentloaded")

    # --- FILTRO POR PAÍS ---
    print("[INFO] Aplicando filtro 'Brazil'...")
    page.get_by_role("button", name="Filter").click()
    page.wait_for_selector("button:has-text('Clear')")
    page.get_by_role("button", name="Clear").click()
    page.get_by_role("checkbox", name="Brazil Brazil").check()
    page.get_by_role("button", name="Apply filter").click()
    page.wait_for_timeout(2000)

    # --- DEFINIR PERÍODO ---
    print("[INFO] Selecionando intervalo de datas...")
    page.get_by_role("button", name=re.compile(r"^.* - .*$")).click()
    page.get_by_role("combobox").nth(3).select_option("2026")
    page.get_by_role("gridcell", name="Sat Oct 31").click()
    page.get_by_role("button", name="Apply").click()
    page.wait_for_timeout(4000)
    # --- ABRIR MENU DE DOWNLOAD ---
    print("[INFO] Abrindo menu de download...")
    page.locator(".fxs_selectable-wrapper").click()
    page.wait_for_selector("button:has-text('ICS')")

    # --- DOWNLOAD ICS ---
    print("[INFO] Baixando arquivo .ICS...")
    with page.expect_download() as ics_info:
        page.get_by_role("button", name="ICS").click()
    ics_download = ics_info.value
    ics_path = os.path.join(download_dir, "calendar_brazil.ics")
    ics_download.save_as(ics_path)
    print(f"ICS salvo em: {ics_path}")

    # --- ABRIR MENU DE DOWNLOAD NOVAMENTE ---
    page.locator(".fxs_selectable-wrapper").click()
    page.wait_for_selector("button:has-text('CSV')")

    # --- DOWNLOAD CSV ---
    print("[INFO] Baixando arquivo .CSV...")
    with page.expect_download() as csv_info:
        page.get_by_role("button", name="CSV").click()
    csv_download = csv_info.value
    csv_path = os.path.join(download_dir, "calendar_brazil.csv")
    csv_download.save_as(csv_path)
    print(f"CSV salvo em: {csv_path}")

    context.close()
    browser.close()
    print("Concluído com sucesso!")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
