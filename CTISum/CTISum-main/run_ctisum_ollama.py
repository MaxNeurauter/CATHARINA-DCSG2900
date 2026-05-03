import os
import json
import ollama
import time
from tqdm import tqdm

# Configuration
TASK = "general-summary"
MODEL = "ministral-3:8b"
SRC_DIR = f"dataset/{TASK}/src"
TGT_DIR = f"dataset/{TASK}/tgt"
OUTPUT_FILE = f"{MODEL}_{TASK}_results.jsonl"
LOG_FILE = f"error_log_{MODEL}_{TASK}.txt"
MAX_REPORTS = 10  # Limit the number of reports to process

def main():
    src_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.txt')]
    valid_pairs = [f for f in src_files if os.path.exists(os.path.join(TGT_DIR, f))]
    
    print(f"Found {len(valid_pairs)} total reports. Starting tmux-safe run for up to {MAX_REPORTS} reports...")

    # List slicing to limit the run
    for filename in tqdm(valid_pairs[:MAX_REPORTS]):
        try:
            with open(os.path.join(SRC_DIR, filename), 'r', encoding='utf-8') as f:
                source_text = f.read()
            with open(os.path.join(TGT_DIR, filename), 'r', encoding='utf-8') as f:
                reference_text = f.read()

            prompt = f"Summarize this Cyber Threat Intelligence report. Focus on Actors and TTPs:\n\n{source_text}"

            response = ollama.chat(
                model=MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                options={'num_ctx': 8192} 
            )
            
            gen_sum = response['message']['content'].strip().replace('\n', ' ')

            with open(OUTPUT_FILE, 'a', encoding='utf-8') as out:
                out.write(json.dumps({
                    "filename": filename,
                    "hyp": gen_sum, 
                    "ref": reference_text.replace('\n', ' ')
                }) + "\n")
                
        except Exception as e:
            with open(LOG_FILE, 'a') as log:
                log.write(f"Error on {filename}: {str(e)}\n")

    print(f"\nBenchmark finished. Results in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()