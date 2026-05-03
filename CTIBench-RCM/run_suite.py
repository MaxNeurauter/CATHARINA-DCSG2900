import subprocess
import sys
import os
import time
import ollama # Imported for the memory clearing step

# Only the remaining models
MODELS = [
    "gemma3:12b",
    "ministral-3:14b",
    "qwen3-vl:8b",
    "qwen3-vl:32b",
    "ministral-3:8b",
    "llama4:16x17b"
]

LIMIT = 100 
RESULTS_DIR = f"rcm_results_{LIMIT}"

for model in MODELS:
    # Check if we already have a final report for this model
    report_file = f"{RESULTS_DIR}/results_{model.replace(':', '_')}.txt"
    if os.path.exists(report_file):
        print(f"Skipping {model} - Report already exists.")
        continue

    print(f"\n{'='*40}")
    print(f"STARTING BENCHMARK: {model}")
    print(f"{'='*40}")
    
    # 1. Pull the model
    subprocess.run(["ollama", "pull", model])
    
    # 2. Run Inference (Fixed truncated syntax)
    subprocess.run([sys.executable, "run_rcm_ollama.py", "--model", model, "--limit", str(LIMIT)])
    
    # 3. Run Eval (Fixed truncated syntax)
    subprocess.run([sys.executable, "eval_rcm.py", "--model", model, "--limit", str(LIMIT)])

    # 4. Memory Clearing Step
    print(f"\nUnloading {model} to free up system VRAM...")
    try:
        # keep_alive=0 tells the Ollama background service to immediately drop the model
        ollama.generate(model=model, prompt='', keep_alive=0)
        time.sleep(3) # Give the system 3 seconds to actually flush the hardware memory
    except Exception as e:
        print(f"Warning: Could not send unload command: {e}")

print("\nAll remaining models completed!")
