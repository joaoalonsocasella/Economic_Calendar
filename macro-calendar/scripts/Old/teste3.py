from playwright.sync_api import sync_playwright
import time, json

URL = "https://www.investing.com/economic-calendar/"

def scrape_investing_calendar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/Sao_Paulo",
            viewport={"width": 1400, "height": 800},
        )
        page = context.new_page()

        print("[INFO] Acessando calendário principal...")
        page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_selector("#datePickerToggleBtn", timeout=90000)
        print("[INFO] Página carregada. Fazendo scroll...")
        for _ in range(1):
            page.mouse.wheel(0, 200)
        print("[INFO] Scroll concluído. Página pronta para interação.")

        # Intercepta requisições da API
        captured = None
        def capture_response(response):
            nonlocal captured
            if "calendar" in response.url and "from=" in response.url:
                try:
                    captured = response.json()
                    print(f"[API DETECTADA] {response.url}")
                    print(f"[INFO] {len(captured.get('data', []))} eventos encontrados.")
                except Exception:
                    pass
        page.on("response", capture_response)

        # Abrir o calendário
        print("[INFO] Abrindo seletor de datas...")
        page.click("#datePickerToggleBtn")
        page.wait_for_selector("text=Start Date", timeout=5000)

        # Inserir datas usando JS real (para React reagir)
        print("[INFO] Inserindo datas personalizadas com eventos JS...")

        js_set_date = """
        ([selector, value]) => {
            const input = document.querySelector(selector);
            if (!input) return;
            const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeSetter.call(input, value);
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
        }
        """

        # Usa uma lista (dois parâmetros passados juntos)
        page.evaluate(js_set_date, ["input[aria-label='Start Date']", "01/01/2025"])
        time.sleep(0.5)
        page.evaluate(js_set_date, ["input[aria-label='End Date']", "10/12/2026"])
        time.sleep(0.5)

        # Clicar de volta no campo Start Date (para confirmar visualmente)
        print("[INFO] Re-focando no campo Start Date para confirmar edição...")
        page.click("input[aria-label='Start Date']")
        time.sleep(0.8)

        # Clicar em Apply
        print("[INFO] Clicando no botão Apply...")
        page.get_by_role("button", name="Apply").click()
        print("[INFO] Aguardando atualização dos dados...")

        # Esperar requisição da API
        time.sleep(10)

        if captured:
            with open("calendar_investing_2025.json", "w", encoding="utf-8") as f:
                json.dump(captured, f, ensure_ascii=False, indent=2)
            print("JSON salvo com sucesso: calendar_investing_2025.json")
        else:
            print("Nenhum dado capturado — talvez Cloudflare tenha bloqueado a requisição inicial.")

        browser.close()


if __name__ == "__main__":
    scrape_investing_calendar()
