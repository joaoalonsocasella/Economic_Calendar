import os
import subprocess
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, "scrap")

def run_single_script(script_path):
    """Executa um único script Python e retorna o nome e status."""
    script_name = os.path.basename(script_path)
    try:
        subprocess.run(["python", script_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return (script_name, True, None)
    except subprocess.CalledProcessError as e:
        return (script_name, False, e)

def run_scripts_parallel(max_workers=4):
    print(f"\n[INFO] Starting parallel batch execution at {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"[INFO] Searching for Python scripts in: {TARGET_DIR}\n")

    scripts = sorted(
        [os.path.join(TARGET_DIR, f) for f in os.listdir(TARGET_DIR)
         if f.endswith(".py") and f != "Update.py"]
    )

    if not scripts:
        print("[WARN] No Python scripts found in scrap folder.")
        return

    print(f"[INFO] Running {len(scripts)} scripts using {max_workers} workers...\n")

    start_time = datetime.now()
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_single_script, s): s for s in scripts}
        for future in as_completed(futures):
            script_name = os.path.basename(futures[future])
            try:
                name, success, error = future.result()
                if success:
                    print(f"[OK] {name} finished successfully.")
                else:
                    print(f"[ERROR] {name} failed: {error}")
                results.append((name, success))
            except Exception as e:
                print(f"[CRITICAL] {script_name} crashed: {e}")
                results.append((script_name, False))

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n[INFO] All scripts completed in {elapsed:.1f} seconds.")
    print(f"[SUMMARY] Successful: {sum(s for _, s in results)} / {len(results)} total.")

if __name__ == "__main__":
    run_scripts_parallel(max_workers=4)
