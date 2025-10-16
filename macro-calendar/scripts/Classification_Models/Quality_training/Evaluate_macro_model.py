import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import(
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score
)
import joblib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "datasets", "ec_calend_1418_labeled.xlsx")
MODEL_PATH = os.path.join(BASE_DIR, "data", "models", "macro_model.pkl")
OUTPUT_DIR = os.path.join(BASE_DIR, "scripts", "Classification_Models", "Quality_training")

PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

df = pd.read_excel(DATA_PATH)
def merge_categories(df):
    mapping = {
        "Consumption": "Growth"
        #"Confidence": "Growth"
    }
    df["MacroCateg"] = df["MacroCateg"].replace(mapping)
    return df
df = df[df["MacroCateg"] != "Other"]
df = merge_categories(df)


model = joblib.load(MODEL_PATH)
X = df["Event"]
y_true = df["MacroCateg"]
mask = y_true.notna() & (y_true.astype(str).str.strip() != "")
X = X[mask]
y_true = y_true[mask]
y_pred = model.predict(X)
y_pred = pd.Series(y_pred).astype(str)
y_true = y_true.astype(str)

report = classification_report(y_true, y_pred, output_dict=True)
accuracy = accuracy_score(y_true, y_pred)
report_text = classification_report(y_true, y_pred)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

report_path = os.path.join(REPORTS_DIR, f"classification_report_{timestamp}.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write(f"[INFO] Accuracy: {accuracy:.4f}\n\n")
    f.write(report_text)

json_path = os.path.join(REPORTS_DIR, f"summary_metrics_{timestamp}.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump({"accuracy": accuracy, "report": report}, f, indent=4)


cm = confusion_matrix(y_true, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot(xticks_rotation=45, cmap="Blues", values_format="d")
plt.title(f"Confusion Matrix (Accuracy: {accuracy:.2f})")
plt.tight_layout()

conf_matrix_path = os.path.join(PLOTS_DIR, f"confusion_matrix_{timestamp}.png")
plt.savefig(conf_matrix_path, dpi=300)
plt.close()


plt.figure(figsize=(10, 5))
df["MacroCateg"].value_counts().plot(kind="bar")
plt.title("Distribuição de Classes (Dataset)")
plt.xlabel("MacroCateg")
plt.ylabel("Número de amostras")
plt.tight_layout()

class_dist_path = os.path.join(PLOTS_DIR, f"class_distribution_{timestamp}.png")
plt.savefig(class_dist_path, dpi=300)
plt.close()


import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "datasets", "ec_calend_1418_labeled.xlsx")
OUTPUT_DIR = os.path.join(BASE_DIR, "scripts", "Classification_Models", "Quality_training")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

df = pd.read_excel(DATA_PATH)
def merge_categories(df):
    mapping = {
        "Consumption": "Growth"
        #"Confidence": "Growth"
    }
    df["MacroCateg"] = df["MacroCateg"].replace(mapping)
    return df
df = df[df["MacroCateg"] != "Other"]
df = merge_categories(df)


df = df[df["MacroCateg"].notna() & (df["MacroCateg"].astype(str).str.strip() != "")]
df["Event"] = df["Event"].astype(str)

X = df["Event"]
y = df["MacroCateg"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

param_grid = {
    "tfidf__ngram_range": [(1, 1), (1, 2), (1, 3)],
    "tfidf__min_df": [1, 2, 3],
    "tfidf__max_df": [0.9, 0.95],
    "clf__C": [0.3, 1, 3],
}

from itertools import product

results = []

for ngram, min_df, max_df, C in tqdm(
    product(param_grid["tfidf__ngram_range"],
            param_grid["tfidf__min_df"],
            param_grid["tfidf__max_df"],
            param_grid["clf__C"]),
    desc="Testing parameter combinations"
):
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=ngram,
            min_df=min_df,
            max_df=max_df,
            sublinear_tf=True,
            stop_words="english"
        )),
        ("clf", LogisticRegression(
            C=C,
            class_weight="balanced",
            solver="lbfgs",
            max_iter=2000
        ))
    ])

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")
    f1_weighted = f1_score(y_test, y_pred, average="weighted")

    results.append({
        "ngram_range": ngram,
        "min_df": min_df,
        "max_df": max_df,
        "C": C,
        "accuracy": acc,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted
    })

results_df = pd.DataFrame(results)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

csv_path = os.path.join(REPORTS_DIR, f"sensitivity_results_{timestamp}.csv")
results_df.to_csv(csv_path, index=False)
print(f"Resultados salvos em: {csv_path}")


plt.figure(figsize=(10, 6))
for ngram in results_df["ngram_range"].unique():
    subset = results_df[results_df["ngram_range"] == ngram]
    plt.plot(subset["C"], subset["accuracy"], marker="o", label=f"ngram={ngram}")
plt.title("Sensibilidade de Acurácia vs C (por ngram_range)")
plt.xlabel("C (regularização da regressão logística)")
plt.ylabel("Accuracy")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, f"sensitivity_accuracy_{timestamp}.png"), dpi=300)
plt.close()

plt.figure(figsize=(10, 6))
for ngram in results_df["ngram_range"].unique():
    subset = results_df[results_df["ngram_range"] == ngram]
    plt.plot(subset["C"], subset["f1_macro"], marker="o", label=f"ngram={ngram}")
plt.title("Sensibilidade do F1 Macro vs C (por ngram_range)")
plt.xlabel("C (regularização)")
plt.ylabel("F1 Macro")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, f"sensitivity_f1_{timestamp}.png"), dpi=300)
plt.close()

print("Gráficos de sensibilidade gerados com sucesso!")
