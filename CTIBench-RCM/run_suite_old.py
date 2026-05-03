import subprocess
import sys

# Define the models you want to test
MODELS = [
    "gemma3:12b",
    "ministral-3:14b",
    "qwen3-vl:8b",
    "qwen3-vl:32b",
    "ministral-3:8b",
    "llama4:16x17b"
]

LIMIT = 100

for model in MODELS:
    print(f"\n{'='*40}")
    print(f"STARTING BENCHMARK: {model}")
    print(f"{'='*40}")
    
    # 1. Pull the model
    subprocess.run(["ollama", "pull", model])
    
    # 2. Run Inference using the current environment's Python
    subprocess.run([sys.executable, "run_rcm_ollama.py", "--model", model, "--limit", str(LIMIT)])
    
    # 3. Run Eval using the current environment's Python
    subprocess.run([sys.executable, "eval_rcm.py", "--model", model, "--limit", str(LIMIT)])

print("\nAll models completed!")
