import os
import time
from tqdm import tqdm
import ollama

# Prompt to the model
NETWORK_PROMPT = """
Role: You are a Senior Network Architect. Your task is to analyze the provided network topology diagram and evaluate its architectural design, efficiency, and security posture.

Task Instructions:
1. Observation & Inventory: List the primary devices shown (e.g., Routers, Switches, Firewalls/ASAs, Servers, Endpoints) and describe the overall topology type (e.g., Star, Ring, Partial Mesh, Hierarchical).
2. Purpose & Architecture: Briefly state what the intended design appears to be (e.g., a segmented corporate network with a DMZ, a flat Layer 2 network, etc.).
3. Strengths (Pros): Identify the positive aspects of this design. Does it feature good segmentation, redundancy, or logical grouping?
4. Weaknesses & Risks (Cons): Identify the flaws in the design. Point out Single Points of Failure (SPOF), inefficient routing/switching loops, lack of security boundaries, or excessive/unnecessary redundancy that complicates the network.
5. Recommendations: Provide 2-3 actionable recommendations to improve the architecture based on industry best practices (such as the Cisco 3-Tier Hierarchical Model, High Availability (HA) pairs, or VLAN segmentation).

Constraint: If the image is too abstract, blurry, or lacks sufficient context to make a definitive architectural judgment, state that the diagram is inconclusive. Do not invent devices or connections that are not clearly visible.
"""

def evaluate_model_on_topologies(model_name, dataset_dir, results_dir):
    """Runs a specific vision model against all topology images in the dataset."""
    
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory '{dataset_dir}' not found.")
        return

    # Filter for the file extentions 
    valid_extensions = ('.png', '.jpg', '.jpeg', '.JPG')
    image_files = [f for f in os.listdir(dataset_dir) if f.lower().endswith(valid_extensions)]
    
    if not image_files:
        print(f"No images found in '{dataset_dir}'.")
        return

    # Create model-specific output directory
    safe_model_name = model_name.replace(":", "_")
    model_output_dir = os.path.join(results_dir, safe_model_name)
    os.makedirs(model_output_dir, exist_ok=True)

    print(f"Found {len(image_files)} images. Starting evaluation for {model_name}...")
    image_files.sort()

    for image_name in tqdm(image_files, desc=f"Testing {model_name}"):
        image_path = os.path.join(dataset_dir, image_name)
        base_name = os.path.splitext(image_name)[0]
        
        start_time = time.time()
        
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{
                    'role': 'user',
                    'content': NETWORK_PROMPT,
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

        # Build the report
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

        output_file_path = os.path.join(model_output_dir, f"{base_name}_analysis.txt")
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(report_content)

    # Unload model from VRAM
    try:
        ollama.generate(model=model_name, prompt='', keep_alive=0)
    except:
        pass

    print(f"Finished {model_name}. Results: {model_output_dir}\n")
