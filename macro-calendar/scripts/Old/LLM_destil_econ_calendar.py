import os
import json
import re
import time
import pandas as pd
from openai import OpenAI
import toml

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


def extract_json(text):
    """Safely extract the first JSON list from a GPT response."""
    try:
        match = re.search(r'\[.*\]', text, re.S)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"JSON parsing failed: {e}")
    return None


def classify_batch(event_list, retries=3):
    joined_events = "\n".join([f"{i+1}. {name}" for i, name in enumerate(event_list)])
    prompt = f"""
You are a macroeconomist. Classify each event below into 2 fields:
1. MacroCateg: Inflation, Growth, Labor Market, Monetary Policy, Confidence, Trade and External, Housing, Money and Credit, Other
2. Type: Release or Speech.

Respond ONLY in raw JSON list (no explanation). Format exactly:
[
  {{"Event": "event1", "MacroCateg": "Inflation", "Type": "Release"}},
  {{"Event": "event2", "MacroCateg": "Growth", "Type": "Speech"}}
]

Events:
{joined_events}
"""

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content.strip()
            data = extract_json(text)
            if isinstance(data, list):
                return data
            else:
                print("Invalid JSON, raw output below:")
                print(text)
        except Exception as e:
            print(f"Retry {attempt+1}/{retries} ({e})")
            time.sleep(3)
    return [{"Event": e, "MacroCateg": "Other", "Type": "Release"} for e in event_list]


if __name__ == "__main__":
    input_path = r"C:\Github_commits\Economic_Calendar\macro-calendar\data\datasets\econ_calendar_2014_2018.xlsx"
    output_path = r"C:\Github_commits\Economic_Calendar\macro-calendar\data\datasets\econ_calendar_2014_2018_labeled.xlsx"

    df = pd.read_excel(input_path)
    if "Event" not in df.columns:
        raise ValueError("Missing 'Event' column")

    if os.path.exists(output_path):
        labeled = pd.read_excel(output_path)
        done = labeled["MacroCateg"].ne("").sum()
        print(f"Resuming from checkpoint ({done} events done)")
    else:
        labeled = df.copy()
        labeled["MacroCateg"] = ""
        labeled["Type"] = ""
        done = 0

    total = len(df)
    batch_size = 15

    print(f"[INFO] Starting classification for {total} events...")

    for start in range(done, total, batch_size):
        end = min(start + batch_size, total)
        batch = df["Event"].iloc[start:end].astype(str).tolist()

        print(f"\n Batch {start} → {end}")
        results = classify_batch(batch)

        for i, result in enumerate(results, start=start):
            labeled.at[i, "MacroCateg"] = result.get("MacroCateg", "Other")
            labeled.at[i, "Type"] = result.get("Type", "Release")

        labeled.to_excel(output_path, index=False)
        print(f" Saved checkpoint ({end}/{total})")
        time.sleep(2)

    print("\n All events classified successfully!")
    print(f"[INFO] Output saved to: {output_path}")
