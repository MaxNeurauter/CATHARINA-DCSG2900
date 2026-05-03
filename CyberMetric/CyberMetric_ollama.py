import json
import re
import time
import argparse
from tqdm import tqdm
from openai import OpenAI

class CyberMetricEvaluator:
    def __init__(self, model_name, file_path):
        # Connects to your local Ollama instance
        self.client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama' 
        )
        self.file_path = file_path
        self.model_name = model_name

    def read_json_file(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def extract_answer(response):
        if response.strip():  # Checks if the response is not empty
            match = re.search(r"ANSWER:?\s*([A-D])", response, re.IGNORECASE)
            if match:
                return match.group(1).upper()  # Return the matched letter in uppercase
        return None

    def ask_llm(self, question, answers, max_retries=5):
        options = ', '.join([f"{key}) {value}" for key, value in answers.items()])
        prompt = f"Question: {question}\nOptions: {options}\n\nChoose the correct answer (A, B, C, or D) only. Always return in this format: 'ANSWER: X' "
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a security expert who answers questions."},
                        {"role": "user", "content": prompt},
                    ]
                )
                if response.choices:
                    result = self.extract_answer(response.choices[0].message.content)
                    if result:
                        return result
                    else:
                        print("Incorrect answer format detected. Attempting the question again.")
            except Exception as e:
                print(f"Error: {e}. Attempting the question again in {2 ** attempt} seconds.")
                time.sleep(2 ** attempt)
        return None

    def run_evaluation(self, output_filename=None):
        json_data = self.read_json_file()
        questions_data = json_data['questions']
        total_questions = len(questions_data)

        correct_count = 0
        incorrect_answers = []

        # Start the timer
        start_time = time.time()

        with tqdm(total=total_questions, desc="Processing Questions") as progress_bar:
            for item in questions_data:
                question = item['question']
                answers = item['answers']
                correct_answer = item['solution']

                llm_answer = self.ask_llm(question, answers)
                if llm_answer == correct_answer:
                    correct_count += 1
                else:
                    incorrect_answers.append({
                        'question': question,
                        'correct_answer_letter': correct_answer,
                        'correct_answer_text': answers.get(correct_answer, "Unknown"),
                        'llm_answer_letter': llm_answer,
                        'llm_answer_text': answers.get(llm_answer, "Unknown") if llm_answer else "No valid answer"
                    })

                accuracy_rate = correct_count / (progress_bar.n + 1) * 100
                progress_bar.set_postfix_str(f"Accuracy: {accuracy_rate:.2f}%")
                progress_bar.update(1)

        # Stop the timer
        end_time = time.time()

        # Calculate time metrics
        total_time_used = end_time - start_time
        time_per_question = total_time_used / total_questions if total_questions > 0 else 0
        final_accuracy = (correct_count / total_questions) * 100

        print(f"\nFinal Accuracy: {final_accuracy:.2f}%")
        print(f"Total Time Used: {total_time_used:.2f} seconds")
        print(f"Average Time per Question: {time_per_question:.2f} seconds/question")

        if incorrect_answers:
            print("\nIncorrect Answers:")
            for item in incorrect_answers:
                print(f"Question: {item['question']}")
                print(f"Expected Answer: {item['correct_answer_letter']}) {item['correct_answer_text']}")
                print(f"LLM Answer: {item['llm_answer_letter']}) {item['llm_answer_text']}\n")

        # Dynamically name the output file based on the model if one isn't provided
        if not output_filename:
            # Replace characters that might cause file path issues
            safe_model_name = self.model_name.replace(":", "-").replace("/", "-")
            output_filename = f"results_{safe_model_name}.json"

        # Save results to a file, including the new time metrics
        results_data = {
            "model_tested": self.model_name,
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "final_accuracy_percentage": final_accuracy,
            "total_time_seconds": total_time_used,             
            "time_per_question_seconds": time_per_question,    
            "incorrect_details": incorrect_answers
        }
        
        with open(output_filename, 'w') as outfile:
            json.dump(results_data, outfile, indent=4)
        print(f"\n✅ Results successfully saved to {output_filename}")

if __name__ == "__main__":
    # Setup argparse to handle command-line inputs
    parser = argparse.ArgumentParser(description="Evaluate a local Ollama model against the CyberMetric dataset.")
    parser.add_argument("model", help="The name of the Ollama model to test (e.g., llama3, mistral)")
    parser.add_argument("--file", default="CyberMetric-80-v1.json", help="Path to the dataset JSON file (defaults to CyberMetric-80-v1.json)")
    
    args = parser.parse_args()
    
    print(f"Starting evaluation using model: {args.model}")
    print(f"Using dataset file: {args.file}\n")
    
    evaluator = CyberMetricEvaluator(model_name=args.model, file_path=args.file)
    evaluator.run_evaluation()
