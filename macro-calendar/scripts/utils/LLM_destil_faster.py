import os
import json
import re
import time
import asyncio
import pandas as pd
import toml
from openai import AsyncOpenAI
from datetime import datetime

# ================================================================
# Load key
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
client = AsyncOpenAI(api_key=api_key)


# ================================================================
# Helpers
# ================================================================
def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.S)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"JSON parsing failed: {e}")
    return None


async def classify_batch(event_list, batch_id):
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

    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content.strip()
            data = extract_json(text)
            if isinstance(data, list):
                return data
            else:
                print(f"[Batch {batch_id}] Invalid JSON — retrying...")
        except Exception as e:
            print(f"[Batch {batch_id}] Retry {attempt+1}/3 — {e}")
            await asyncio.sleep(3)
    return [{"Event": e, "MacroCateg": "Other", "Type": "Release"} for e in event_list]


# ================================================================
# Async orchestrator
# ================================================================
async def main():
    input_path = r"C:\Github_commits\Economic_Calendar\macro-calendar\data\datasets\ec_calend_1418.xlsx"
    output_path = r"C:\Github_commits\Economic_Calendar\macro-calendar\data\datasets\ec_calend_1418_labeled.xlsx"

    df = pd.read_excel(input_path)
    if "Event" not in df.columns:
        raise ValueError("Missing 'Event' column")

    # checkpoint resume
    if os.path.exists(output_path):
        labeled = pd.read_excel(output_path)
        done = labeled["MacroCateg"].ne("").sum()
        print(f"Resuming from checkpoint ({done} done)")
    else:
        labeled = df.copy()
        labeled["MacroCateg"] = ""
        labeled["Type"] = ""
        done = 0

    total = len(df)
    batch_size = 15
    concurrency = 10  # number of parallel API calls

    print(f"[INFO] Starting classification for {total} events...")

    semaphore = asyncio.Semaphore(concurrency)
    tasks = []

    async def process_batch(start, end):
        async with semaphore:
            batch = df["Event"].iloc[start:end].astype(str).tolist()
            results = await classify_batch(batch, start)
            for i, result in enumerate(results, start=start):
                labeled.at[i, "MacroCateg"] = result.get("MacroCateg", "Other")
                labeled.at[i, "Type"] = result.get("Type", "Release")
            print(f"[Batch {start} → {end}] done")
            return end

    for start in range(done, total, batch_size):
        end = min(start + batch_size, total)
        tasks.append(process_batch(start, end))

        # Controla checkpoint a cada ~20 batches
        if len(tasks) >= 20:
            results = await asyncio.gather(*tasks)
            labeled.to_excel(output_path, index=False)
            print(f"[Checkpoint] Saved up to {max(results)}/{total} ({datetime.now().strftime('%H:%M:%S')})")
            tasks = []

    if tasks:
        await asyncio.gather(*tasks)
        labeled.to_excel(output_path, index=False)
        print(f"[Final] Saved all ({datetime.now().strftime('%H:%M:%S')})")


if __name__ == "__main__":
    asyncio.run(main())
