import pandas as pd
import ollama
from tqdm import tqdm
import os
import argparse
import time

def get_cwe_mapping(model, prompt_text):
    response = ollama.generate(model=model, prompt=prompt_text, options={'temperature': 0})
    return response['response'].strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Ollama model name")
    parser.add_argument("--limit", type=int, default=20, help="Number of questions")
    args = parser.parse_args()

    INPUT_FILE = "data/cti-rcm.tsv"
    # Individual response file for each model
    output_filename = f"evaluation/responses/rcm_{args.model.replace(':', '_')}.tsv"
    
    df = pd.read_csv(INPUT_FILE, sep='\t').head(args.limit)
    
    # Track time
    start_time = time.time()
    
    # Clear existing file for clean run
    if os.path.exists(output_filename): os.remove(output_filename)

    for i in tqdm(range(len(df)), desc=f"Running {args.model}"):
        row = df.iloc[i]
        prediction = get_cwe_mapping(args.model, row['Prompt'])
        
        result_row = pd.DataFrame([{
            'Description': row['Description'],
            'ground_truth': row['GT'],
            'model_response': prediction
        }])
        result_row.to_csv(output_filename, sep='\t', mode='a', index=False, header=not os.path.exists(output_filename))

    total_duration = time.time() - start_time
    print(f"Completed {args.model} in {total_duration:.2f}s")
    
    # Save the time to a temp file for the eval script to read
    with open(".last_run_time", "w") as f:
        f.write(str(total_duration))

if __name__ == "__main__":
    main()
