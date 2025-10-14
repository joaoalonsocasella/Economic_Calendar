from playwright.sync_api import sync_playwright
import time

IFRAME_URL = (
    "https://sslecal2.investing.com/?columns=exc_flags,exc_currency,exc_importance,"
    "exc_actual,exc_forecast,exc_previous&features=datepicker,timezone&countries="
    "110,17,29,25,32,6,37,26,5,22,39,14,48,10,35,7,43,38,4,36,12,72&calType=week&"
    "timeZone=12&lang=12"
)

def simulate_calendar_fixed_path():
    with sync_playwright() as p:
        # ⚙️ 1. Configuração anti-detecção
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        context_args = {
            "user_agent": user_agent,
            "viewport": {"width": 1366, "height": 768},
            "locale": "pt-BR",
            "timezone_id": "America/Sao_Paulo",
        }

        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-extensions",
                "--disable-gpu",
            ],
            slow_mo=150,
        )

        context = browser.new_context(**context_args)

        # 2. Limpar rastros de automação
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
        """)

        page = context.new_page()

        # 3. Acessar a página do calendário
        page.goto(IFRAME_URL, timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        print("[INFO] Página carregada. Aguardando calendário...")
        time.sleep(3)

        # 4. Abrir o calendário
        print("[INFO] Clicando no ícone do calendário...")
        page.click("#datePickerIconWrap")
        page.wait_for_selector("div.datepicker", timeout=10000)
        print("[INFO] Calendário aberto.")
        time.sleep(2)

        # Selecionar o primeiro dia visível
        print("[INFO] Selecionando o primeiro dia (início)...")
        first_day = "table.datepickerViewDays tr:nth-child(3) td:nth-child(2) a span"
        page.click(first_day)
        time.sleep(2)

        # Entrar na seleção de mês/ano
        print("[INFO] Entrando na seleção de mês/ano...")
        page.click("a.datepickerMonth")
        time.sleep(2)

        # Avançar para o ano seguinte
        print("[INFO] Avançando para o ano seguinte...")
        page.click("a.datepickerGoNext")
        time.sleep(2)

        # Selecionar "Dez."
        print("[INFO] Selecionando o mês de Dezembro...")
        page.locator("a span:text('Dez.')").click()
        time.sleep(2)

        # Selecionar o último dia visível
        print("[INFO] Selecionando o último dia (fim)...")
        last_day = "table.datepickerViewDays tr:last-child td:nth-last-child(2) a span"
        page.click(last_day)
        time.sleep(2)

        # Aplicar (clique físico via coordenadas)
        print("[INFO] Aplicando intervalo selecionado (clique físico)...")
        btn = page.locator("#datePickerApplyButton a")
        box = btn.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            print(f"[INFO] Movendo mouse para ({x:.0f}, {y:.0f}) e clicando fisicamente...")
            page.mouse.move(x, y)
            time.sleep(0.3)
            page.mouse.down()
            time.sleep(0.15)
            page.mouse.up()
            print("[INFO] Clique físico executado com sucesso.")
        else:
            print("[ERRO] Não foi possível obter coordenadas do botão 'Aplicar'.")

        # ⏳ 5. Capturar a requisição AJAX de atualização
        def capture_response(response):
            if "calendar" in response.url and "from=" in response.url:
                print("\n[API DETECTADA] ", response.url)

        page.on("response", capture_response)

        print("[INFO] Aguardando respostas da API...")
        page.wait_for_timeout(8000)

        browser.close()
        print("Finalizado com sucesso!")

if __name__ == "__main__":
    simulate_calendar_fixed_path()
