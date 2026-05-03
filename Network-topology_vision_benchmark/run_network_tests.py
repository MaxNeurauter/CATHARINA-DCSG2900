import os
from network_vision_tester import evaluate_model_on_topologies

# ==========================================
# Configuration
# ==========================================
MODELS_TO_TEST = [
    "gemma3:12b",
    "ministral-3:14b",
    "qwen3-vl:8b",
    "qwen3-vl:32b",
    "ministral-3:8b",
    "llama4:16x17b"
]

# Path folder name
DATASET_DIRECTORY = "nettverksdatasett" 
RESULTS_DIRECTORY = "Topology_Analysis_Results"

def main():
    print(f"{'='*50}")
    print("Network Topology Vision LLM Testing Pipeline")
    print(f"{'='*50}\n")
    
    os.makedirs(RESULTS_DIRECTORY, exist_ok=True)
    
    for model in MODELS_TO_TEST:
        print(f"--- Initializing tests for model: {model} ---")
        evaluate_model_on_topologies(
            model_name=model, 
            dataset_dir=DATASET_DIRECTORY, 
            results_dir=RESULTS_DIRECTORY
        )

    print(f"All evaluations complete! Check '{RESULTS_DIRECTORY}' for reports.")

if __name__ == "__main__":
    main()
