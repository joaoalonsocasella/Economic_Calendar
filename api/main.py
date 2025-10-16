from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from .utils import load_calendar, filter_events

app = FastAPI(title="Macro Calendar API")

class CalendarEvent(BaseModel):
    URL_ICS: Optional[str]
    Id: str
    Start: str
    Name: str
    Impact: str
    Currency: str
    MacroCateg: Optional[str]
    Release: Optional[str]


@app.get("/country/{country_iso3}", response_model=List[CalendarEvent])
def get_country_events(country_iso3: str):
    df = load_calendar(country_iso3)
    return df.to_dict(orient="records")


@app.get("/filter", response_model=List[CalendarEvent])
def get_filtered(
    country: str,
    impact: Optional[str] = None,
    name_contains: Optional[str] = None,
    start_after: Optional[str] = None,
    start_before: Optional[str] = None,
):
    df = load_calendar(country)
    df = filter_events(df, impact, name_contains, start_after, start_before)
    return df.to_dict(orient="records")
