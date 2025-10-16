import os
import subprocess
from datetime import datetime

# Caminho para a pasta contendo os scripts individuais
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, "scrap")

def run_scripts():
    print(f"\n[INFO] Starting batch execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[INFO] Searching for Python scripts in: {TARGET_DIR}\n")

    scripts = sorted([f for f in os.listdir(TARGET_DIR) if f.endswith(".py") and f != "Update.py"])

    if not scripts:
        print("[WARN] No Python scripts found in scrap folder.")
        return

    for idx, script in enumerate(scripts, start=1):
        script_path = os.path.join(TARGET_DIR, script)
        print(f"\n[{idx}/{len(scripts)}] ▶ Running {script}...")
        try:
            subprocess.run(["python", script_path], check=True)
            print(f" Finished {script} successfully.\n")
        except subprocess.CalledProcessError as e:
            print(f" Error while running {script}: {e}")
            # Se quiser parar na primeira falha, descomente a linha abaixo:
            # break
            continue

    print(f"\n All scripts executed. Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_scripts()
