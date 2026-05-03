import os
import time
from tqdm import tqdm
import ollama

# Prompt to model
EVALUATION_PROMPT = """
Role: You are an AD Security Auditor. Your task is to analyze the provided image of Active Directory configurations (User attributes, GPOs, or ACLs) to determine their security posture.

Task Instructions:
1. Observation: First, list the key settings or attributes you see in the image (e.g., "Account is sensitive" is unchecked).
2. Assessment: State if the configuration is Secure, Misconfigured, or Critically Vulnerable.
3. Attack Path: If vulnerable, identify the specific attack vector (e.g., Kerberoasting, AS-REP Roasting, Silver Ticket, or Privilege Escalation) and explain the technical impact.
4. Remediation: Provide a clear, step-by-step fix.

Constraint: If the image is too blurry or lacks context to provide a definitive answer, state that the data is inconclusive. Do not speculate.
"""

def evaluate_model_on_images(model_name, dataset_dir, results_dir):
    """Runs a specific vision model against all images in the dataset directory."""
    
    # Ensure the dataset directory exists
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory '{dataset_dir}' not found.")
        return

    # Filter for standard image formats
    valid_extensions = ('.png', '.jpg', '.jpeg')
    image_files = [f for f in os.listdir(dataset_dir) if f.lower().endswith(valid_extensions)]
    
    if not image_files:
        print(f"No images found in '{dataset_dir}'.")
        return

    # Create a safe folder name for the models results
    safe_model_name = model_name.replace(":", "_")
    model_output_dir = os.path.join(results_dir, safe_model_name)
    os.makedirs(model_output_dir, exist_ok=True)

    print(f"Found {len(image_files)} images. Starting evaluation for {model_name}...")
    
    # Sort files to ensure images are processed in order
    image_files.sort()

    for image_name in tqdm(image_files, desc=f"Testing {model_name}"):
        image_path = os.path.join(dataset_dir, image_name)
        base_name = os.path.splitext(image_name)[0]
        
        start_time = time.time()
        
        try:
            # Send the image and prompt to the model
            response = ollama.chat(
                model=model_name,
                messages=[{
                    'role': 'user',
                    'content': EVALUATION_PROMPT,
                    'images': [image_path]
                }]
            )
            llm_output = response['message']['content']
            status = "SUCCESS"
            
        except Exception as e:
            llm_output = f"ERROR: Failed to generate response. Details: {e}"
            status = "FAILED"
            print(f"\n[!] Error with {model_name} on {image_name}: {e}")

        time_taken = time.time() - start_time

        # Format the output record
        report_content = (
            f"Image Analyzed: {image_name}\n"
            f"Model Used: {model_name}\n"
            f"Time Taken: {time_taken:.2f} seconds\n"
            f"Status: {status}\n"
            f"{'='*50}\n"
            f"LLM RESPONSE:\n"
            f"{llm_output}\n"
            f"{'='*50}\n"
        )

        # Save to individual text file (e.g. img_001_eval.txt)
        output_file_path = os.path.join(model_output_dir, f"{base_name}_eval.txt")
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(report_content)

    # ==========================================
    # RESOURCE CLEANUP
    # ==========================================
    print(f"\nUnloading {model_name} from memory to free up VRAM...")
    try:
        # Sending an empty prompt with keep_alive=0 unloads the model immediately
        ollama.generate(model=model_name, prompt='', keep_alive=0)
    except Exception as e:
        print(f"[!] Warning: Could not explicitly unload {model_name}: {e}")

    print(f"Finished testing {model_name}. Results saved to {model_output_dir}\n")
