from fastapi import FastAPI
from .routers import calendar_router

app = FastAPI(title="Macro Calendar API")

# Inclui todas as rotas definidas no módulo calendar_router.py
app.include_router(calendar_router.router)


from fastapi import FastAPI
from .routers import calendar_router

app = FastAPI(
    title="Macro Calendar API",
    description="Public economic calendar API — powered by FastAPI and daily GitHub Actions updates.",
    version="1.0.0",
)

# Inclui as rotas de eventos
app.include_router(calendar_router.router)


@app.get("/")
def root():
    """
    Endpoint raiz — mostra as instruções principais da API.
    """
    return {
        "message": "Macro Calendar API is running and ready!",
        "documentation": "Access the interactive Swagger UI at /docs",
        "usage": """
#### API Filters:

- **Country's entire economic calendar info:**
  - Add `/events?country={iso3}`
  - Example: `https://economic-calendar-api-h9hr.onrender.com/events?country=BRA`

- **Filter by Impact** (`LOW` | `MEDIUM` | `HIGH`):
  - Add `&impact={impact_level}` to the country query
  - Example: `https://economic-calendar-api-h9hr.onrender.com/events?country=BRA&impact=HIGH`

- **Filter by Macroeconomic Theme** (`Inflation` | `Growth` | `Labor Market` | `Monetary Policy` | `Confidence` | `Trade and External` | `Housing` | `Money and Credit`):
  - Add `&macrocat={categ}` to the country query
  - Example: `https://economic-calendar-api-h9hr.onrender.com/events?country=BRA&macrocat=Labor%20Market`

- **Filter by Event Name:**
  - Add `&release={event_name}` to the country query
  - Example: `https://economic-calendar-api-h9hr.onrender.com/events?country=BRA&release=PMI`

- **Filter by Event Type** (`Release` | `Speech`):
  - Add `&type=Release` to the country query
  - Example: `https://economic-calendar-api-h9hr.onrender.com/events?country=BRA&type=Release`

- **Filter by Date Range:**
  - Add `&start_date={yyyy-mm-dd}&end_date={yyyy-mm-dd}`
  - Example: `https://economic-calendar-api-h9hr.onrender.com/events?country=BRA&start_date=2025-10-01&end_date=2026-12-31`

You can **combine multiple filters** (country + impact + type + date + release, etc.)  
You can also query **different countries** by changing the ISO3 code (e.g., USA, CHN, DEU, JPN).

---

**Examples of full queries:**
- `https://economic-calendar-api-h9hr.onrender.com/events?country=USA&impact=HIGH&type=Release&release=GDP&start_date=2025-01-01&end_date=2025-12-31`
- `https://economic-calendar-api-h9hr.onrender.com/events/country/BRA`
- `https://economic-calendar-api-h9hr.onrender.com/events/categories`

---
        """,
        "routes": [
            "/events (combinable filters)",
            "/events/country/{country_iso3}",
            "/events/categories",
            "/docs (Swagger UI for interactive testing)",
        ],
    }

