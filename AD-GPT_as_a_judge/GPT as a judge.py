import os
import json
import base64
import re
import csv
from openai import OpenAI

# --- Configuration ---
JUDGE_MODEL = "gpt-5.4"
MAPPING_FILE = "mapping.json"
DATASET_DIR = "Dataset"
RESULTS_DIR = "AD_Vision_Results"
JUDGE_OUTPUT_DIR = "judge_response"
CSV_OUTPUT_FILE = "grading_summary.csv"

client = OpenAI(api_key="")

# --- System Prompt Template ---
PROMPT_TEMPLATE = """You are a Senior Cybersecurity Auditor specializing in Active Directory (AD) security. Your task is to grade the performance of CATHARINA, an offline cybersecurity analysis tool. You will evaluate how accurately it identifies vulnerabilities in AD configuration screenshots compared to a provided Ground Truth.

Score | Label | Description
--- | --- | ---
5 | Exceptional | Correctly identifies the core flaw (e.g., LDAP Signing = None) and explicitly explains the secondary risk (e.g., NTLM Relay). Remediation is technically perfect.
4 | Good | Identifies the flaw correctly but might be slightly vague on the specific attack path or mentions only one of the remediation steps.
3 | Acceptable | Recognizes the configuration is "Vulnerable" or "Misconfigured," but the explanation of why is generic or lacks the specific technical depth found in the Ground Truth.
2 | Poor | Misses the primary flaw but identifies a minor, less critical issue, or provides remediation that is fundamentally incorrect for this specific vulnerability.
1 | Failure | Declares a "Critically Vulnerable" state as "Secure," or hallucinates a vulnerability that is clearly contradicted by the image data or if the model describes UI elements or settings that are not present in the provided image.

Ground Truth:
Short Description: {short_desc}
Description: {desc}

The models response: 
{model_response}

Instructions:
1. Provide your reasoning briefly.
2. End your response with 'SCORE: [1-5]'.
"""

def encode_image_to_base64(image_path):
    """Encodes an image to a base64 string for the Ollama API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_model_response(eval_file_path):
    """Extracts the actual LLM response from the eval text file."""
    with open(eval_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "LLM RESPONSE:" in content:
        response = content.split("LLM RESPONSE:")[1]
        response = response.replace("==================================================", "").strip()
        return response
    return None

def extract_score_from_judge(judge_output):
    """Parses the integer score from the judge's text response."""
    match = re.search(r'SCORE:\s*([1-5])', judge_output, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def get_average_time(model_dir):
    """Reads the average_time.txt file and extracts the numeric value."""
    time_file_path = os.path.join(model_dir, "average_time.txt")
    if os.path.exists(time_file_path):
        with open(time_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'[\d\.]+', content)
            if match:
                return float(match.group())
    return None

def grade_response(image_path, short_desc, desc, model_response):
    """Sends a stateless request to the OpenAI API to grade the response."""
    full_prompt = PROMPT_TEMPLATE.format(
        short_desc=short_desc,
        desc=desc,
        model_response=model_response
    )

    base64_image = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": full_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content.strip()

def main():
    # 1. Load the Ground Truth mapping
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)
    ground_truths = {os.path.basename(item["Path"]): item for item in mapping_data}
    
    summary_metrics = []

    # 2. Iterate through the tested models
    for tested_model in os.listdir(RESULTS_DIR):
        model_dir = os.path.join(RESULTS_DIR, tested_model)
        if not os.path.isdir(model_dir):
            continue
            
        print(f"\n--- Grading outputs for model: {tested_model} ---")
        
        # Setup specific output directory for this model's judge responses
        model_judge_dir = os.path.join(JUDGE_OUTPUT_DIR, tested_model)
        os.makedirs(model_judge_dir, exist_ok=True)
        
        model_scores = []
        
        # 3. Iterate through each evaluation file
        for eval_file in sorted(os.listdir(model_dir)):
            if not eval_file.endswith("_eval.txt"):
                continue
                
            img_num = eval_file.split("_eval")[0]
            img_filename = f"{img_num}.png"
            image_path = os.path.join(DATASET_DIR, img_filename)
            
            if img_filename not in ground_truths:
                continue
                
            gt_data = ground_truths[img_filename]
            eval_path = os.path.join(model_dir, eval_file)
            
            model_response = extract_model_response(eval_path)
            if not model_response:
                continue

            print(f"Evaluating {img_filename}...")
            
            # 4. API Call
            judge_output = grade_response(
                image_path=image_path,
                short_desc=gt_data["Short_Description"],
                desc=gt_data["Description"],
                model_response=model_response
            )
            
            if judge_output:
                # Save the full judge text to the new directory structure
                judge_text_filename = f"{img_num}_judge.txt"
                judge_text_path = os.path.join(model_judge_dir, judge_text_filename)
                with open(judge_text_path, "w", encoding="utf-8") as text_file:
                    text_file.write(judge_output)
                
                # Extract integer score for CSV math
                score = extract_score_from_judge(judge_output)
                if score is not None:
                    model_scores.append(score)

        # 5. Calculate Metrics for the Model
        successful_extractions = len(model_scores)
        
        if successful_extractions > 0:
            avg_score = sum(model_scores) / len(model_scores)
        else:
            avg_score = 0.0
            
        avg_time = get_average_time(model_dir)
        
        summary_metrics.append({
            "Model Name": tested_model,
            "Successful Extractions": successful_extractions,
            "Average Score": round(avg_score, 2),
            "Average Time (s)": round(avg_time, 2) if avg_time else "N/A",
        })

    # 6. Generate the CSV file
    csv_columns = ["Model Name", "Successful Extractions", "Average Score", "Average Time (s)"]
    with open(CSV_OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in summary_metrics:
            writer.writerow(data)
            
    print(f"\nGrading complete.")
    print(f"Full text responses saved to directory: {JUDGE_OUTPUT_DIR}/")
    print(f"Summary metrics saved to: {CSV_OUTPUT_FILE}")

if __name__ == "__main__":
    main()