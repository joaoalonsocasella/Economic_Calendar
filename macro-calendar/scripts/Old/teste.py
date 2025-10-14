from playwright.sync_api import sync_playwright
import time

IFRAME_URL = "https://sslecal2.investing.com/?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&features=datepicker,timezone&countries=110,17,29,25,32,6,37,26,5,22,39,14,48,10,35,7,43,38,4,36,12,72&calType=week&timeZone=12&lang=12"

def simulate_calendar_fixed_path():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        page = browser.new_page()
        page.goto(IFRAME_URL, timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        print("[INFO] Página carregada. Aguardando calendário...")
        time.sleep(4)

        
        page.wait_for_selector("#datePickerIconWrap", timeout=10000)

        # Abrir o calendário
        print("[INFO] Clicando no ícone do calendário...")
        page.click("#datePickerIconWrap")
        page.wait_for_selector("div.datepicker", timeout=10000)
        print("[INFO] Calendário aberto.")
        time.sleep(4)

        # Selecionar o primeiro dia (canto superior esquerdo visível)
        print("[INFO] Selecionando o primeiro dia visível (início)...")
        first_day = "table.datepickerViewDays tr:nth-child(3) td:nth-child(2) a span"
        page.click(first_day)
        time.sleep(4)

        # Clicar no título "Mês, Ano" para ir para visão de meses
        print("[INFO] Entrando na seleção de mês/ano...")
        page.click("a.datepickerMonth")
        time.sleep(4)

        # Ir para o ano seguinte
        print("[INFO] Avançando para o ano seguinte...")
        page.click("a.datepickerGoNext")
        time.sleep(4)

        # Selecionar "Dez."
        print("[INFO] Selecionando o mês de Dezembro...")
        page.locator("a span:text('Dez.')").click()
        time.sleep(4)

        # Selecionar o último dia (canto inferior direito)
        print("[INFO] Selecionando o último dia visível (fim)...")
        last_day = "table.datepickerViewDays tr:last-child td:nth-last-child(2) a span"
        page.click(last_day)
        time.sleep(4)

        # Aplicar
        print("[INFO] Aplicando intervalo selecionado...")
        page.click("#datePickerApplyButton a")

        # Capturar a requisição XHR da API
        def capture_response(response):
            if "calendar" in response.url and "from=" in response.url:
                print("\n[API DETECTADA] ", response.url)
        page.on("response", capture_response)
        time.sleep(4)

        # Esperar as requisições carregarem
        print("[INFO] Aguardando respostas da API...")
        page.wait_for_timeout(8000)
        browser.close()
        print("Finalizado com sucesso!")

if __name__ == "__main__":
    simulate_calendar_fixed_path()
