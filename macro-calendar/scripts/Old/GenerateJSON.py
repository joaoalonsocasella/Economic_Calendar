import os
import json
import argparse
import pandas as pd
import joblib
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "CSV")
OUT_PATH = os.path.join(BASE_DIR, "data", "processed", "JSON")
MODELS_PATH = os.path.join(BASE_DIR, "data", "models")

MACRO_MODEL_PATH = os.path.join(MODELS_PATH, "macro_model.pkl")
TYPE_MODEL_PATH  = os.path.join(MODELS_PATH, "type_model.pkl")

REQUIRED_COLS = ["Id", "Start", "Name", "Impact", "Currency"]

def load_models():
    if not (os.path.exists(MACRO_MODEL_PATH) and os.path.exists(TYPE_MODEL_PATH)):
        raise FileNotFoundError("Modelos .pkl não encontrados em data/models/")
    macro_model = joblib.load(MACRO_MODEL_PATH)
    type_model  = joblib.load(TYPE_MODEL_PATH)
    return macro_model, type_model

def list_csvs(country_only=None):
    if country_only:
        path = os.path.join(RAW_PATH, f"{country_only.upper()}.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV de {country_only} não encontrado em {RAW_PATH}")
        return [path]
    return [os.path.join(RAW_PATH, f) for f in os.listdir(RAW_PATH) if f.lower().endswith(".csv")]

def ensure_cols(df):
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV faltando colunas obrigatórias: {missing}")

def predict_with_conf(model, X_series):
    # model é um Pipeline sklearn com vectorizer + classifier
    y_pred = model.predict(X_series)
    conf = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_series)
        conf = proba.max(axis=1)
    else:
        # fallback: sem probas
        conf = pd.Series([None] * len(X_series))
    return pd.Series(y_pred), pd.Series(conf)

def process_csv(csv_path, macro_model, type_model, min_conf_macro=0.0, min_conf_type=0.0):
    iso3 = os.path.basename(csv_path).replace(".csv", "").upper()
    df = pd.read_csv(csv_path)
    ensure_cols(df)

    # Predição baseada em 'Name' (pode enriquecer com Impact/Currency se seus modelos aceitarem)
    X = df["Name"].astype(str)

    # MacroCateg
    macro_pred, macro_conf = predict_with_conf(macro_model, X)
    # Type
    type_pred, type_conf = predict_with_conf(type_model, X)

    # Aplicar thresholds opcionais
    macro_pred_final = macro_pred.where(macro_conf.fillna(1.0) >= min_conf_macro, other="Other")
    type_pred_final  = type_pred.where(type_conf.fillna(1.0)  >= min_conf_type,  other="Release")

    out = df.copy()
    out["MacroCateg"]     = macro_pred_final
    out["Release"]        = type_pred_final      # mapeia Type -> Release
    out["MacroCateg_conf"]= macro_conf
    out["Release_conf"]   = type_conf
    out["URL_ICS"]        = f"https://macro-calendar.example/ics/{iso3}.ics"

    # Ordena e garante colunas finais
    final_cols = ["URL_ICS", "Id", "Start", "Name", "Impact", "Currency", "MacroCateg", "Release",
                  "MacroCateg_conf", "Release_conf"]
    out = out[final_cols]

    os.makedirs(OUT_PATH, exist_ok=True)
    json_path = os.path.join(OUT_PATH, f"{iso3}.json")
    out.to_json(json_path, orient="records", indent=2, force_ascii=False)
    return iso3, json_path, len(out)

def main():
    parser = argparse.ArgumentParser(description="Gera JSONs preditos por país a partir dos CSVs.")
    parser.add_argument("--country", "-c", help="ISO3 do país (ex: ARE). Se ausente, processa todos.")
    parser.add_argument("--min-conf-macro", type=float, default=0.0, help="Threshold para MacroCateg (0..1)")
    parser.add_argument("--min-conf-type",  type=float, default=0.0, help="Threshold para Type/Release (0..1)")
    args = parser.parse_args()

    macro_model, type_model = load_models()
    csvs = list_csvs(args.country)

    print(f"[INFO] Gerando JSON(s) em: {OUT_PATH}")
    for path in tqdm(csvs, desc="Países"):
        iso3, out_path, n = process_csv(
            path, macro_model, type_model,
            min_conf_macro=args.min_conf_macro,
            min_conf_type=args.min_conf_type
        )
        print(f"  - {iso3}: {n} eventos → {out_path}")

    print("Pronto!")

if __name__ == "__main__":
    main()
