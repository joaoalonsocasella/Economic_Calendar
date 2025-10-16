import os
import pandas as pd
from tqdm import tqdm

# ============================================================
# Paths
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "data", "processed", "CSV")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed", "CSV")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# Weights
# ============================================================

# --- Macro Category relevance ---
macro_weights = {
    "Monetary Policy": 1.00,
    "Inflation": 0.95,
    "Labor Market": 0.90,
    "Growth": 0.85,
    "Confidence": 0.70,
    "Trade and External": 0.55,
    "Money and Credit": 0.45,
    "Housing": 0.35,
}

# --- Country relevance (importance for Brazilian economy) ---
country_weights = {
    "BRA": 1.00, "USA": 0.90, "EUR": 0.85, "CHN": 0.80, "ARG": 0.75,
    "MEX": 0.70, "JPN": 0.65, "GBR": 0.60, "CAN": 0.55, "DEU": 0.55,
    "FRA": 0.50, "ITA": 0.50, "ESP": 0.50, "KOR": 0.45, "IND": 0.45,
    "ZAF": 0.45, "AUS": 0.40, "CHL": 0.40, "COL": 0.40, "TUR": 0.35,
    "RUS": 0.35, "CHE": 0.30, "NLD": 0.30, "BEL": 0.30, "PRT": 0.30,
    "SWE": 0.30, "NOR": 0.30, "POL": 0.30, "FIN": 0.30, "AUT": 0.30,
    "IRL": 0.30, "ISL": 0.30, "GRC": 0.25, "CZE": 0.25, "HUN": 0.25,
    "ROU": 0.25, "SVK": 0.25, "SGP": 0.25, "IDN": 0.25, "THA": 0.25,
    "VNM": 0.25, "NZL": 0.25, "ARE": 0.20, "SAU": 0.20, "QAT": 0.20,
    "KWT": 0.20, "ISR": 0.20, "HKG": 0.20, "EGY": 0.20, "UKR": 0.20,
}

# --- Type relevance ---
type_weights = {
    "Release": 1.00,
    "Speech": 0.65,  # menor peso, pois são menos diretamente econômicos
}

# --- Default weights ---
DEFAULT_MACRO_WEIGHT = 0.3
DEFAULT_COUNTRY_WEIGHT = 0.2
DEFAULT_TYPE_WEIGHT = 0.7

# ============================================================
# Impact Scoring
# ============================================================

def compute_impact_score(row):
    """Compute continuous impact score."""
    macro = row.get("MacroCateg", "")
    currency = row.get("Currency", "")
    event_type = row.get("Type", "")

    macro_score = macro_weights.get(macro, DEFAULT_MACRO_WEIGHT)
    country_score = country_weights.get(currency, DEFAULT_COUNTRY_WEIGHT)
    type_score = type_weights.get(event_type, DEFAULT_TYPE_WEIGHT)

    return round(macro_score * country_score * type_score, 3)


def categorize_impact(score):
    """Assign LOW / MEDIUM / HIGH based on fixed global ranges."""
    if score > 0.15:
        return "HIGH"
    elif score >= 0.10:
        return "MEDIUM"
    else:
        return "LOW"

# ============================================================
# Execution
# ============================================================

print("[INFO] Starting proprietary impact scoring (fixed global thresholds)...")

files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".csv")]

for file in tqdm(files, desc="Applying Impact Model"):
    path = os.path.join(INPUT_DIR, file)
    df = pd.read_csv(path)

    if not all(col in df.columns for col in ["MacroCateg", "Currency", "Type"]):
        print(f"[WARN] Skipping {file}: missing required columns.")
        continue

    # Compute impact score & category
    df["Impact_score"] = df.apply(compute_impact_score, axis=1)
    df["Impact"] = df["Impact_score"].apply(categorize_impact)

    # Move MacroCateg to the end for clarity
    cols = [c for c in df.columns if c != "MacroCateg"]
    cols.append("MacroCateg")
    df = df[cols]

    # Save file
    output_path = os.path.join(OUTPUT_DIR, file)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"[OK] {file} updated with fixed-threshold Impact model.")

print("\n All CSVs successfully updated with simplified global thresholds (0.10 / 0.15).")
