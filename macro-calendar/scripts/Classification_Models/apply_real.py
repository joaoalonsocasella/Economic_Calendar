import os
import pandas as pd
import joblib
from tqdm import tqdm

# ============================================================
# Paths
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw", "CSV")
OUT_DIR = os.path.join(BASE_DIR, "data", "processed", "CSV")

os.makedirs(OUT_DIR, exist_ok=True)

MACRO_MODEL_PATH = os.path.join(BASE_DIR, "data", "models", "macro_model.pkl")
TYPE_MODEL_PATH = os.path.join(BASE_DIR, "data", "models", "type_model.pkl")

# ============================================================
# Load models
# ============================================================
print("[INFO] Loading models...")
macro_model = joblib.load(MACRO_MODEL_PATH)
type_model = joblib.load(TYPE_MODEL_PATH)
print("[INFO] Models successfully loaded.")

# ============================================================
# Process all CSVs
# ============================================================
for file in tqdm(os.listdir(RAW_DIR), desc="Processing CSV files"):
    if not file.endswith(".csv"):
        continue

    input_path = os.path.join(RAW_DIR, file)
    df = pd.read_csv(input_path)

    if "Name" not in df.columns:
        print(f"[WARN] Column 'Name' not found in {file}. Skipping...")
        continue

    df["Name"] = df["Name"].astype(str)

    print(f"[INFO] Classifying events from {file}...")

    # --- Apply MacroCateg model ---
    df["MacroCateg"] = macro_model.predict(df["Name"])

    # --- Apply Type model ---
    df["Type"] = type_model.predict(df["Name"])

    # --- Save processed CSV ---
    file_name, _ = os.path.splitext(file)
    output_path = os.path.join(OUT_DIR, f"{file_name}_processed.csv")

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[OK] {file} → {output_path}")

print("\n[INFO] All files processed and saved successfully.")
