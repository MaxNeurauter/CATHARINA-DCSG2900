import os
from ad_vision_tester import evaluate_model_on_images

# ==========================================
# Configuration
# ==========================================
# List your vision-capable models here (e.g., llava, bakllava, llama3.2-vision)
MODELS_TO_TEST = [
    "gemma3:12b",
    "ministral-3:14b",
    "qwen3-vl:8b",
    "qwen3-vl:32b",
    "ministral-3:8b",
    "llama4:16x17b"
]

DATASET_DIRECTORY = "Dataset"
RESULTS_DIRECTORY = "AD_Vision_Results"

# ==========================================
# Main Execution Loop
# ==========================================
def main():
    print(f"{'='*50}")
    print("Starting Active Directory Vision LLM Testing Pipeline")
    print(f"{'='*50}\n")
    
    # Create the base results directory if it doesn't exist
    os.makedirs(RESULTS_DIRECTORY, exist_ok=True)
    
    for model in MODELS_TO_TEST:
        print(f"--- Initializing tests for model: {model} ---")
        evaluate_model_on_images(
            model_name=model, 
            dataset_dir=DATASET_DIRECTORY, 
            results_dir=RESULTS_DIRECTORY
        )

    print(f"All evaluations complete! Check the '{RESULTS_DIRECTORY}' folder for detailed reports.")

if __name__ == "__main__":
    main()
