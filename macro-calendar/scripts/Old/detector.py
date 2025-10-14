import requests
import json
from datetime import date

def fetch_investing_calendar(start_date="2025-01-01", end_date="2025-12-31"):
    url = "https://api.investing.com/api/financialdata/calendar/economic"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.investing.com/economic-calendar/",
        "Origin": "https://www.investing.com",
    }
    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "timeZone": 12,               # GMT-3
        "lang": "pt",
        "importance": [1, 2, 3],
        "countries": [29, 5, 17, 72, 14, 35],  # EUA, Brasil, Reino Unido, China, etc.
        "limit": 10000,
    }

    print(f"[INFO] Consultando {url}")
    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code == 200:
        data = response.json()
        events = data.get("data", [])
        print(f"Retornou {len(events)} eventos.")
        with open("calendar_public.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data
    else:
        print(f"[ERRO {response.status_code}] {response.text}")
        return None


if __name__ == "__main__":
    fetch_investing_calendar()
