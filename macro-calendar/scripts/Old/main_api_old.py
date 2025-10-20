from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from api.utils import load_calendar, filter_events

app = FastAPI(title="Macro Calendar API")


# ============================================================
# MODELO DE EVENTO
# ============================================================

class CalendarEvent(BaseModel):
    Id: str
    Start: str
    Name: str
    Impact: str
    Currency: str
    Type: Optional[str]
    Impact_score: Optional[float]
    MacroCateg: Optional[str]
    Release: Optional[str]
    Country: Optional[str]
    URL_ICS: Optional[str]


# ============================================================
# ROTAS
# ============================================================

@app.get("/country/{country_iso3}")
def get_country_events(country_iso3: str):
    """
    Retorna todos os eventos de um país, mais metadados úteis.
    """
    df = load_calendar(country_iso3)
    events = df.to_dict(orient="records")
    return {
        "country": country_iso3.upper(),
        "url_ics": f"https://joaoalonsocasella.github.io/Economic_Calendar/macro-calendar/data/raw/ICS/{country_iso3.upper()}.ics",
        "count": len(events),
        "events": events,
    }


@app.get("/filter", response_model=List[CalendarEvent])
def get_filtered(
    country: str,
    impact: Optional[str] = None,
    name_contains: Optional[str] = None,
    start_after: Optional[str] = None,
    start_before: Optional[str] = None,
):
    """
    Filtra eventos por impacto, nome e período.
    """
    df = load_calendar(country)
    df = filter_events(df, impact, name_contains, start_after, start_before)
    return df.to_dict(orient="records")


@app.get("/")
def root():
    return {
        "message": "Macro Calendar API is running.",
        "routes": ["/country/{country_iso3}", "/filter", "/docs"]
    }
