from playwright.sync_api import sync_playwright
import json
import time

def sniff_investing_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1400, "height": 800},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
        )

        page = context.new_page()
        page.goto("https://www.investing.com/economic-calendar/", timeout=60000)
        print("[INFO] Aguardando a página carregar...")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        # 🔍 Interceptar as respostas AJAX da página
        captured_url = None
        captured_json = None

        def capture_response(response):
            nonlocal captured_url, captured_json
            url = response.url
            if "calendar" in url and "from=" in url:
                try:
                    json_data = response.json()
                    captured_json = json_data
                    captured_url = url
                    print(f"\n[API DETECTADA]\n{url}\n")
                    print(f"[INFO] {len(json_data.get('data', []))} eventos coletados.")
                except:
                    pass

        page.on("response", capture_response)

        print("[INFO] Y Agora use o calendário na página manualmente.")
        print("   - Clique no ícone de datas")
        print("   - Escolha um intervalo amplo (ex: 01/01/2020 a 31/12/2030)")
        print("   - Clique em 'Aplicar'")
        print("O script vai capturar a chamada e salvar o JSON da API.\n")

        time.sleep(45)  # tempo para você interagir

        if captured_json:
            with open("calendar_data.json", "w", encoding="utf-8") as f:
                json.dump(captured_json, f, ensure_ascii=False, indent=2)
            print("[Y] JSON salvo em calendar_data.json")
        else:
            print("[X] Nenhuma resposta detectada — tente interagir novamente.")

        browser.close()

if __name__ == "__main__":
    sniff_investing_api()
