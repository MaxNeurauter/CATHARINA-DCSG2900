import json
import requests
import time
from tqdm import tqdm
import re
import argparse
import sys

# Konfigurerer argumenter som sendes fra Bash
parser = argparse.ArgumentParser(description="Evaluate a local LLM on the PrimeVul dataset.")
parser.add_argument("--model", required=True, help="Name of the model to test in Ollama")
parser.add_argument("--file", required=True, help="Path to the dataset file")
parser.add_argument("--max_examples", type=int, default=20, help="Number of examples to test")
args = parser.parse_args()

# --- KONFIGURASJON ---
DATASET_PATH = args.file
MODEL = args.model
MAX_EXAMPLES = args.max_examples
OLLAMA_API_URL = "http://localhost:11434/api/generate"
RESULTS_FILE = f"results_{MODEL.replace(':', '_')}.txt"  # Safe filename

def create_prompt(code):
    return f"""Analyze the following C/C++ code.
CRITICAL INSTRUCTIONS: 
1. Do not assume the code is vulnerable. Many of these snippets are perfectly safe, secure, and production-ready.
2. Carefully analyze the code for actual security vulnerabilities (e.g., buffer overflows, use-after-free, SQLi, path traversal).
3. Write a brief analysis of your findings.
4. Finally, you MUST conclude your response by wrapping your final answer in tags like this:
   - Output <RESULT>0</RESULT> if the code is safe.
   - Output <RESULT>1</RESULT> if the code is vulnerable.

Code:
{code}

Analysis and Result:"""

def main():
    # Lese inn datasettet
    dataset = []
    try:
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                dataset.append(json.loads(line))
                if len(dataset) >= MAX_EXAMPLES:
                    break
    except FileNotFoundError:
        print(f"Error: Could not find {DATASET_PATH}")
        sys.exit(1)

    correct_answers = 0
    correct_vulnerable = 0
    correct_safe = 0
    wrong_answers = 0
    wrong_vulnerable = 0
    wrong_safe = 0
    invalid_answers = 0
    
    correct_explanations_logs = []
    incorrect_logs = []

    start_time = time.time()

    for index, row in enumerate(tqdm(dataset, desc=f"Evaluating {MODEL}")):
        
        # --- FIX: Mapped the correct keys from the dataset ---
        code = row.get("func", "") 
        label = row.get("target", -1) 
        
        prompt = create_prompt(code)
        
        # --- FIX: Included "stream": False in the payload ---
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False 
        }
        
        try:
            response = requests.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()
            response_data = response.json()
            raw_answer = response_data.get("response", "")
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            invalid_answers += 1
            incorrect_logs.append(f"  [Task {index+1}] API Error: {e}")
            continue

        # Rydder opp og trekker ut svaret
        clean_raw_answer = raw_answer.replace("\n", " ")
        match = re.search(r"<RESULT>(.*?)</RESULT>", raw_answer, re.DOTALL | re.IGNORECASE)
        
        if match:
            guessed_value = match.group(1).strip()
            try:
                guessed_int = int(guessed_value)
            except ValueError:
                guessed_int = -1
                
            if guessed_int == label:
                correct_answers += 1
                if label == 1:
                    correct_vulnerable += 1
                    correct_explanations_logs.append(f"  [Task {index+1}] Correctly identified as vulnerable. Full answer: {clean_raw_answer}")
                else:
                    correct_safe += 1
                    correct_explanations_logs.append(f"  [Task {index+1}] Correctly identified as safe.")
            else:
                wrong_answers += 1
                if label == 1:
                    wrong_vulnerable += 1
                else:
                    wrong_safe += 1
                incorrect_logs.append(f"  [Task {index+1}] Expected: {label} | Guessed: {guessed_value} | Raw: '{clean_raw_answer}'")
        else:
            invalid_answers += 1
            incorrect_logs.append(f"  [Task {index+1}] Expected: {label} | Invalid format. Raw: '{clean_raw_answer}'")

    time_spent = time.time() - start_time
    total_attempted = correct_answers + wrong_answers + invalid_answers
    acc_inc_invalids = (correct_answers / total_attempted * 100) if total_attempted > 0 else 0

    # Lagrer resultatet for denne modellen
    with open(RESULTS_FILE, "w", encoding="utf-8") as res_file:
        res_file.write(f"--- Results for {MODEL} ---\n")
        res_file.write(f"Accuracy: {acc_inc_invalids:.1f}% | Correct: {correct_answers} (Vulnerable: {correct_vulnerable} | Safe: {correct_safe}) | Wrong: {wrong_answers} (Vulnerable: {wrong_vulnerable} | Safe: {wrong_safe}) | Invalid: {invalid_answers}\n")
        res_file.write(f"Time spent: {time_spent:.1f} seconds\n\n")
        
        if correct_explanations_logs:
            res_file.write("--- Correctly Identified Tasks ---\n" + "\n".join(correct_explanations_logs) + "\n\n")
        if incorrect_logs:
            res_file.write("--- Incorrect / Invalid Tasks ---\n" + "\n".join(incorrect_logs) + "\n")
    
    print(f"\nEvaluation complete for {MODEL}! Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    main()