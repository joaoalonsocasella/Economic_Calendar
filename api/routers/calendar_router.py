import os
import glob
import pandas as pd
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..utils import load_calendar

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/")
def get_events(
    country: str,
    impact: Optional[str] = None,
    macrocateg: Optional[str] = None,
    release: Optional[str] = None,
    currency: Optional[str] = None,
    event_type: Optional[str] = Query(None, alias="type"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Endpoint principal — busca eventos econômicos com múltiplos filtros combináveis.
    Todos os parâmetros são opcionais, exceto 'country'.
    """
    df = load_calendar(country)

    # === Converte a coluna Start para datetime ===
    df["Start_dt"] = pd.to_datetime(df["Start"], format="%m/%d/%Y %H:%M:%S", errors="coerce")

    # === Filtros textuais ===
    if impact:
        df = df[df["Impact"].astype(str).str.upper() == impact.upper()]

    if macrocateg:
        df = df[df["MacroCateg"].astype(str).str.contains(macrocateg, case=False, na=False, regex=False)]

    if release:
        df = df[df["Name"].astype(str).str.contains(release, case=False, na=False, regex=False)]

    if currency:
        df = df[df["Currency"].astype(str).str.upper() == currency.upper()]

    if event_type:
        df = df[df["Event_Type"].astype(str).str.upper() == event_type.upper()]

    # === Filtros de data (conversão YYYY-MM-DD → datetime) ===
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            df = df[df["Start_dt"] >= start_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato inválido para start_date. Use YYYY-MM-DD.")

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            df = df[df["Start_dt"] <= end_dt]
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato inválido para end_date. Use YYYY-MM-DD.")

    # === Retorno ===
    events = df.drop(columns=["Start_dt"], errors="ignore").to_dict(orient="records")

    return {
        "country": country.upper(),
        "count": len(events),
        "filters_applied": {
            "impact": impact,
            "macrocateg": macrocateg,
            "release": release,
            "currency": currency,
            "event_type": event_type,
            "start_date": start_date,
            "end_date": end_date,
        },
        "events": events,
    }


# ============================================================
# Outros endpoints utilitários
# ============================================================

@router.get("/country/{country_iso3}")
def get_country_events(country_iso3: str):
    """
    Retorna todos os eventos de um país específico, junto com o link ICS público.
    """
    df = load_calendar(country_iso3)
    events = df.to_dict(orient="records")
    return {
        "country": country_iso3.upper(),
        "url_ics": f"https://joaoalonsocasella.github.io/Economic_Calendar/macro-calendar/data/raw/ICS/{country_iso3.upper()}.ics",
        "count": len(events),
        "events": events,
    }


@router.get("/categories")
def list_categories():
    """
    Lista todas as categorias macroeconômicas únicas encontradas nos CSVs processados.
    """
    base_dir = os.path.join(
        os.path.dirname(__file__),
        "..", "..",
        "macro-calendar",
        "data",
        "processed",
        "CSV"
    )
    files = glob.glob(os.path.join(base_dir, "*_processed.csv"))
    categories = set()
    for file in files:
        df = pd.read_csv(file)
        if "MacroCateg" in df.columns:
            categories.update(df["MacroCateg"].dropna().unique())
    return sorted(list(categories))
