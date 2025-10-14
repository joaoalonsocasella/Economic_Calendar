import os, json, time
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dtparse, tz
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from playwright.sync_api import sync_playwright as pw

WIDGET_URL = "https://br.investing.com/webmaster-tools/economic-calendar"
OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
TZ_LOCAL = "America/Sao_Paulo"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
def close_popup_if_present(page):
    """Fecha o pop-up de cadastro do Investing.com, se aparecer."""
    try:
        popup_selector = ".popupCloseIcon, .largeBannerCloser, div[class*='popupOverlay'] .close"
        if page.locator(popup_selector).count() > 0:
            page.locator(popup_selector).first.click(timeout=1000)
            print("[INFO] Pop-up detectado e fechado.")
        else:
            print("[INFO] Nenhum pop-up detectado.")
    except Exception as e:
        print(f"[WARN] Falha ao tentar fechar pop-up: {e}")


def expand_iframe_url(iframe_src: str, start_date="2025-01-01", end_date="2035-12-31") -> str:
    """Adiciona parâmetros de datas ao iframe do calendário."""
    parsed = urlparse(iframe_src)
    query = parse_qs(parsed.query)

    # Adiciona/atualiza parâmetros principais
    query.update({
        "dateFrom": [start_date],
        "dateTo": [end_date],
        "calType": ["day"],      # pode trocar para 'week' ou 'month'
        "lang": ["12"],          # português
        "timeZone": ["12"],      # GMT-3
    })

    new_query = urlencode(query, doseq=True)
    new_url = urlunparse(parsed._replace(query=new_query))
    return new_url


def get_econ_cal_data():
    """Abre a página do widget e captura a URL do calendário ampliado."""
    with pw() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.route("**/*", lambda route: route.abort()
                   if any(x in route.request.url for x in ["doubleclick", "googlesyndication", "adservice"])
                   else route.continue_())

        print("[INFO] Acessando a página...")
        page.goto(WIDGET_URL, timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        close_popup_if_present(page)
        print("[INFO] Página carregada. Fazendo scroll para baixo...")

        for _ in range(5):
            page.mouse.wheel(0, 150)
        print("[INFO] Scroll concluído. Página pronta para interação.")
        time.sleep(1)

        print("[INFO] Aceitando termos e condições...")
        try:
            page.check("#termsCheckbox")
            print("[INFO] Termos e condições aceitos.")
        except Exception as e:
            print(f"[ERRO] Não foi possível clicar no checkbox: {e}")
        time.sleep(1)

        print("[INFO] Tentando extrair o iframe...")
        iframe_src = page.eval_on_selector("iframe.alignTop", "el => el.src")
        print("[INFO] URL original do calendário:", iframe_src)

        # Amplia o intervalo de datas
        iframe_expanded = expand_iframe_url(iframe_src)
        print("[INFO] URL ampliada:", iframe_expanded)

        # Salva o resultado em JSON
        ensure_dir(OUT_DIR)
        output_path = os.path.join(OUT_DIR, "calendar_iframe.json")
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "iframe_url_original": iframe_src,
            "iframe_url_ampliada": iframe_expanded,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[INFO] URLs salvas em: {output_path}")

        time.sleep(3)
        browser.close()


if __name__ == "__main__":
    get_econ_cal_data()