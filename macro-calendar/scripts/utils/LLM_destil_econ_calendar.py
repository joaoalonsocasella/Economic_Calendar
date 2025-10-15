"""
Batch-safe GPT labeling for economic calendar events.
Processes in chunks, handles retries, and checkpoints safely.
"""

import os
import json
import time
import pandas as pd
from openai import OpenAI
import toml

# ================================================================
#  Load OpenAI key
# ================================================================
def load_openai_key():
    secrets_path = os.path.join(os.path.dirname(__file__), "..", "..", "secrets", "secrets.toml")
    if os.path.exists(secrets_path):
        secrets = toml.load(secrets_path)
        api_key = secrets.get("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            return api_key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found.")
    return api_key


api_key = load_openai_key()
client = OpenAI(api_key=api_key)


# ================================================================
#  GPT Classifier
# ================================================================
def classify_event(event_name: str, retries=3):
    """Uses GPT to classify one event, with retry logic."""
    prompt = f"""
Classify this economic event into two categories:
1. MacroCateg: Inflation, Growth, Labor Market, Monetary Policy, Confidence, Trade and External, Housing, Money and Credit, Other
2. Type: Release (data) or Speech (public remarks)

Return JSON only:
{{"Event": "{event_name}", "MacroCateg": "...", "Type": "..."}}
"""

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content.strip()
            return json.loads(text)
        except Exception as e:
            print(f"Retry {attempt+1}/{retries} for: {event_name} ({e})")
            time.sleep(2)
    return {"Event": event_name, "MacroCateg": "Other", "Type": "Release"}


# ================================================================
#  Batch processing
# ================================================================
if __name__ == "__main__":
    input_path = r"C:\Github_commits\Economic_Calendar-1\macro-calendar\data\datasets\econ_calendar_2014_2018.xlsx"
    output_path = r"C:\Github_commits\Economic_Calendar-1\macro-calendar\data\datasets\econ_calendar_2014_2018_labeled.xlsx"

    df = pd.read_excel(input_path)
    if "Name" not in df.columns:
        raise ValueError("Missing column 'Name' in dataset")

    # Resume if partial file exists
    if os.path.exists(output_path):
        labeled = pd.read_excel(output_path)
        done = len(labeled)
        print(f"Resuming from checkpoint ({done} events done)")
    else:
        labeled = df.copy()
        labeled["MacroCateg"] = ""
        labeled["Type"] = ""
        done = 0

    total = len(df)
    batch_size = 500

    print(f"[INFO] Starting classification for {total} events...\n")

    for start in range(done, total, batch_size):
        end = min(start + batch_size, total)
        print(f"\n Processing batch {start} → {end}")
        batch = df.iloc[start:end]

        for i, event in enumerate(batch["Name"].astype(str), start=start):
            result = classify_event(event)
            labeled.at[i, "MacroCateg"] = result["MacroCateg"]
            labeled.at[i, "Type"] = result["Type"]
            if (i + 1) % 50 == 0:
                print(f"  {i + 1}/{total} done...")
            time.sleep(0.3)

        labeled.to_excel(output_path, index=False)
        print(f" Checkpoint saved ({end}/{total})")

    print("\n All events classified successfully!")
    print(f"[INFO] Final labeled dataset saved to: {output_path}")
