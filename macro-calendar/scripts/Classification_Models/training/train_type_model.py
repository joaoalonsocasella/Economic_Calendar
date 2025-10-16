import os
import re
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATASET_PATH = os.path.join(BASE_DIR, "data", "datasets", "ec_calend_1418_labeled.xlsx")
MODEL_DIR = os.path.join(BASE_DIR, "data", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "type_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


print(f"[INFO] Loading dataset: {DATASET_PATH}")
df = pd.read_excel(DATASET_PATH)

df = df[df["Type"] != "Other"]

required = ["Event", "Type"]
for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col} in dataset {DATASET_PATH}")

df = df.dropna(subset=required)
df["Event_clean"] = df["Event"].apply(clean_text)
print(f"[INFO] Dataset size after cleaning: {len(df)} rows")

x_train, x_test, y_train, y_test = train_test_split(
    df["Event_clean"], df["Type"],
    test_size=0.2, random_state=42,
    stratify=df["Type"]
)

print(f"[INFO] Train size: {len(x_train)}, Test size: {len(x_test)}")
print("\n[INFO] Building model pipeline (TF-IDF + Logistic Regression)")

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 3),
        min_df=2,
        max_df=0.9,
        sublinear_tf=True
    )),
    ("clf", LogisticRegression(
        C=1.5,
        max_iter=3000,
        class_weight="balanced",
        solver="lbfgs",
        n_jobs=-1,
        random_state=42
    ))
])

print("\n[INFO] Training model...")
pipeline.fit(x_train, y_train)

print(f"\n[INFO] Saving model to {MODEL_PATH}...")
joblib.dump(pipeline, MODEL_PATH)
print("[INFO] Done.")
