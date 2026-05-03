import json
import os
import glob
import argparse
import ollama
from tqdm import tqdm

# Settings
MAX_REPORTS = 20  # Limit the number of reports to process

def main():
    # Setup command-line argument parsing
    parser = argparse.ArgumentParser(description="Run Ollama Benchmark")
    parser.add_argument("--model", type=str, required=True, help="Ollama model to use")
    parser.add_argument("--outdir", type=str, required=True, help="Directory to save results")
    parser.add_argument("--dataset", type=str, required=True, help="Root dataset directory")
    args = parser.parse_args()

    model_name = args.model
    out_dir = args.outdir
    dataset_dir = args.dataset
    
    # Determine input directory dynamically based on the dataset directory
    target_dir = os.path.join(dataset_dir, "cti_sum")
    
    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)
    
    # Create a safe filename (replacing colons which might cause issues in some file systems)
    safe_model_name = model_name.replace(':', '_')
    output_file = os.path.join(out_dir, f"{safe_model_name}_results.jsonl")

    if not os.path.exists(target_dir):
        print(f"Error: Could not find directory {target_dir}. Check the dataset folder.")
        return

    # Find all JSON files in the directory
    json_files = glob.glob(os.path.join(target_dir, "*.json"))
    
    if not json_files:
        print(f"Error: No JSON files found in {target_dir}.")
        return

    print(f"Found {len(json_files)} JSON file(s) in {target_dir}.")

    # Load all entries from all JSON files
    all_data = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    all_data.extend(file_data)
                elif isinstance(file_data, dict):
                    all_data.append(file_data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    actual_run_count = min(len(all_data), MAX_REPORTS)
    print(f"Starting inference on {actual_run_count} samples using {model_name}...")

    # Clear previous results if they exist
    if os.path.exists(output_file):
        os.remove(output_file)

    # Added list slicing here to limit the run
    for entry in tqdm(all_data[:MAX_REPORTS]):
        source_text = entry.get('src', '')
        reference_text = entry.get('tgt', '')

        if not source_text:
            continue

        # Construct the prompt
        prompt = f"Summarize the following Cyber Threat Intelligence report concisely:\n\n{source_text}"

        # Call Ollama
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            options={'num_ctx': 8192} # Increased context for long CTI reports
        )
        
        generated_summary = response['message']['content'].replace('\n', ' ')

        # Save in a format ready for the evaluation scripts
        result = {
            "hyp": generated_summary,
            "ref": reference_text
        }
        
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result) + "\n")

    print(f"Inference complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()