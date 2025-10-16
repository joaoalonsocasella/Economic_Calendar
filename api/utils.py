import os
import pandas as pd
from fastapi import HTTPException
from datetime import datetime
from functools import lru_cache


# ============================================================
# 🔹 CONFIGURAÇÕES GERAIS
# ============================================================

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "CSV")

# Define as colunas esperadas no dataset
REQUIRED_COLUMNS = ["Id", "Start", "Name", "Impact", "Currency"]
OPTIONAL_COLUMNS = ["MacroCateg", "Release", "URL_ICS"]


# ============================================================
# 🔹 FUNÇÃO DE LEITURA DE CSV
# ============================================================

@lru_cache(maxsize=32)
def load_calendar(country_iso3: str) -> pd.DataFrame:
    """
    Lê o CSV de um país (macro-calendar/data/raw/CSV/{country}.csv)
    e garante as colunas padrão.
    """
    country_iso3 = country_iso3.upper()
    csv_path = os.path.join(DATA_PATH, f"{country_iso3}.csv")

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail=f"CSV não encontrado para {country_iso3}")

    df = pd.read_csv(csv_path)

    # Corrige colunas faltantes
    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            df[col] = None

    # Ordena as colunas para manter consistência
    df = df[[*REQUIRED_COLUMNS, *OPTIONAL_COLUMNS]]

    return df


# ============================================================
# 🔹 FILTROS / CONSULTAS
# ============================================================

def filter_events(
    df: pd.DataFrame,
    impact: str = None,
    name_contains: str = None,
    start_after: str = None,
    start_before: str = None,
):
    """
    Filtra o DataFrame com base nos parâmetros fornecidos.
    Datas devem vir no formato MM/DD/YYYY.
    """
    if impact:
        df = df[df["Impact"].str.upper() == impact.upper()]

    if name_contains:
        df = df[df["Name"].str.contains(name_contains, case=False, na=False)]

    if start_after:
        df = df[df["Start"] >= start_after]

    if start_before:
        df = df[df["Start"] <= start_before]

    return df


# ============================================================
# 🔹 FORMATAÇÃO / UTILS DE DATA
# ============================================================

def parse_datetime(dt_str: str) -> datetime:
    """
    Converte uma string no formato 'MM/DD/YYYY HH:MM:SS' para datetime.
    """
    try:
        return datetime.strptime(dt_str, "%m/%d/%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Data inválida: {dt_str}")


def format_datetime(dt: datetime) -> str:
    """Formata datetime como string padrão."""
    return dt.strftime("%m/%d/%Y %H:%M:%S")


# ============================================================
# 🔹 PREVIEW DOS DADOS (para debug ou testes)
# ============================================================

def preview_country_data(country_iso3: str, n: int = 5):
    """
    Retorna os primeiros n registros de um país, útil pra debug.
    """
    df = load_calendar(country_iso3)
    return df.head(n).to_dict(orient="records")
