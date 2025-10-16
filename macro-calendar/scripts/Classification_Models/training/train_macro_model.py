import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data","datasets","ec_calend_1418_labeled.xlsx")
MODEL_DIR = os.path.join(BASE_DIR,"data","models")
MODEL_PATH = os.path.join(MODEL_DIR, "macro_model.pkl")


os.makedirs(MODEL_DIR, exist_ok=True)

def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s]","",text)
    text = re.sub(r"\s+"," ",text).strip()
    return text

print(f"[INFO] Loading dataset: {DATASET_PATH}")
df = pd.read_excel(DATASET_PATH)

def merge_categories(df):
    mapping = {
        "Consumption": "Growth"
        #"Confidence": "Growth"
    }
    df["MacroCateg"] = df["MacroCateg"].replace(mapping)
    return df
df = df[df["MacroCateg"] != "Other"]
df = merge_categories(df)


required = ["Event", "MacroCateg"]
for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col} in dataset {DATASET_PATH}")
    
df = df.dropna(subset=required)
df["Event_clean"] = df["Event"].apply(clean_text)
print(f"[INFO] Dataset size after cleaning: {len(df)} rows")

print("[INFO] Splitting training and testing...")

x_train, x_test, y_train, y_test = train_test_split(
    df["Event_clean"], df["MacroCateg"],
    test_size=0.2,random_state=42,
    stratify=df["MacroCateg"]
)

print(f"[INFO] Training size: {len(x_train)}, Testing size: {len(x_test)}")
print("[INFO] Training model: TF-IDF + Logistic Regression")
print("Remeber that TF-IDF is idf(t,d) = tf(t) * (log(n/df(t)) + 1), which represents the importance of term t in document d.")
print("tf(t) is the term frequency and idf(t) is the rarity of the term across all documents.")

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1,3),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True)),
        ("clf", LogisticRegression(
            C=2,
            max_iter=2000,
            class_weight="balanced",
            n_jobs=-1,
            solver="lbfgs",
            multi_class="auto"
    ))
])

print("[INFO] Training the model...")
pipeline.fit(x_train, y_train)

print("[INFO] Evaluating the model...")
y_pred = pipeline.predict(x_test)
print(f"[INFO] Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred))


print(f"[INFO] Saving model to {MODEL_PATH}...")
joblib.dump(pipeline, MODEL_PATH)
print("[INFO] Done.")




