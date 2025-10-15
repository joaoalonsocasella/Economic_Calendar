"""
I use GPT to do an initial classification of the economic events into macro categories.
Then I use my own logistic regression model to independently classify the events, no costs attached,
which results in a model that uses GPT as a teacher to distill knowledge into a smaller cost-free model.

Teacher Model: GPT-4
Student Model: Logistic Regression (sklearn)
Dataset: https://www.kaggle.com/datasets/crtatu/economic-calendar-20142018
Path in the project: macro-calendar/data/datasets/econ_calendar_2014_2018.xlsx
"""

import os
import json
import time
import pandas as pd
import openai
from openai import OpenAI
import toml

# ================================================================
#  Load secrets safely
# ================================================================

def load_openai_key():
    """Loads OPENAI_API_KEY from secrets.toml or environment."""
    secrets_path = os.path.join(os.path.dirname(__file__), "..", "..", "secrets", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            secrets = toml.load(secrets_path)
            api_key = secrets.get("OPENAI_API_KEY")
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
                return api_key
        except Exception as e:
            print(f"Erro ao ler secrets.toml: {e}")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found. Please configure it in secrets.toml or as environment variable.")
    return api_key


# ================================================================
#  Initialize OpenAI client
# ================================================================
api_key = load_openai_key()
client = OpenAI(api_key=api_key)

# ================================================================
#  Example use: classify economic events
# ================================================================

def classify_event(event_name: str):
    """Uses GPT to classify a single economic event."""
    prompt = f"""
You are an economist specialized in macroeconomic data releases.
Classify the event below according to two labels:

1. MacroCateg:
   - Inflation
   - Growth
   - Labor Market
   - Monetary Policy
   - Confidence
   - Trade and External
   - Housing
   - Money and Credit
   - Other

2. Type:
   - Release (economic data releases)
   - Speech (public speeches, statements, or minutes)

Return ONLY valid JSON:
{{"Event": "{event_name}", "MacroCateg": "...", "Type": "..."}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except:
        print("Raw output:", text)
        return {"Event": event_name, "MacroCateg": "Other", "Type": "Release"}


# Example: test one event
if __name__ == "__main__":
    example = classify_event("Consumer Price Index (YoY)")
    print(example)
