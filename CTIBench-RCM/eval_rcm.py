import pandas as pd
import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--limit", type=int, required=True)
    args = parser.parse_args()

    # Setup paths
    folder_name = f"rcm_results_{args.limit}"
    os.makedirs(folder_name, exist_ok=True)
    
    input_file = f"evaluation/responses/rcm_{args.model.replace(':', '_')}.tsv"
    report_file = f"{folder_name}/results_{args.model.replace(':', '_')}.txt"
    
    # Load data and timing
    df = pd.read_csv(input_file, sep='\t')
    try:
        with open(".last_run_time", "r") as f:
            total_time = float(f.read())
    except: total_time = 0

    correct_count = 0
    wrong_answers = []

    for _, row in df.iterrows():
        gt = str(row['ground_truth']).strip().lower()
        pred = str(row['model_response']).strip().lower()
        
        if gt in pred:
            correct_count += 1
        else:
            wrong_answers.append({
                'desc': row['Description'],
                'gt': row['ground_truth'],
                'pred': row['model_response']
            })

    # Calculations
    total = len(df)
    accuracy = (correct_count / total) * 100
    time_per_q = total_time / total

    # Write the report
    with open(report_file, "w") as f:
        f.write(f"model tested: {args.model}\n")
        f.write(f"total questions: {total}\n")
        f.write(f"correct answers: {correct_count}\n")
        f.write(f"correct percentage: {accuracy:.2f}%\n")
        f.write(f"total time used: {total_time:.2f}s\n")
        f.write(f"time per question: {time_per_q:.2f}s\n")
        f.write("-" * 50 + "\n")
        f.write("WRONG ANSWERS LIST:\n\n")
        
        for item in wrong_answers:
            f.write(f"Description: {item['desc']}\n")
            f.write(f"Expected: {item['gt']} | LLM Answered: {item['pred']}\n")
            f.write("-" * 20 + "\n")

    print(f"Report generated: {report_file}")

if __name__ == "__main__":
    main()
