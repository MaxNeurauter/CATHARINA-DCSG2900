import os
import glob
import base64
from io import BytesIO
from pdf2image import convert_from_path
import ollama

# --- Configuration ---
PDF_DIR = "dataset/pdf_file/"
OUTPUT_DIR = "dataset/general-summary/src/"
MODEL = "ministral-3:8b"
MAX_REPORTS = 5 

# Prompt for individual pages
PAGE_PROMPT = "Extract the key threat intelligence from this page. Focus on actors, malware, and technical indicators."
# Prompt for the final consolidation
FINAL_PROMPT = "Based on the page-by-page notes above, write a single, professional Executive Summary of the entire threat report. Organize it by: Overview, Target Industries, Technical Analysis, and Conclusion."

def pdf_to_base64_images(pdf_path):
    """Converts PDF pages to base64 encoded strings."""
    images = convert_from_path(pdf_path, dpi=150)
    encoded_images = []
    for img in images:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        encoded_images.append(base64.b64encode(buffered.getvalue()).decode('utf-8'))
    return encoded_images

def process_reports():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Find all PDFs
    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    print(f"Found {len(pdf_files)} PDF reports. Processing up to {MAX_REPORTS}...")

    # List slicing limit to the run
    for pdf_path in pdf_files[:MAX_REPORTS]:
        report_name = os.path.basename(pdf_path)
        output_filename = report_name.replace('.pdf', '.txt')
        
        # Check if already processed to save time
        if os.path.exists(os.path.join(OUTPUT_DIR, output_filename)):
            print(f"Skipping {report_name} (already exists).")
            continue

        print(f"\n>>> Summarizing entire PDF: {report_name}")
        
        try:
            images = pdf_to_base64_images(pdf_path)
            page_summaries = []
            
            # Step 1: Analyze each page
            for i, img_b64 in enumerate(images):
                print(f"  Reading Page {i+1}/{len(images)}...")
                response = ollama.chat(
                    model=MODEL,
                    messages=[{'role': 'user', 'content': PAGE_PROMPT, 'images': [img_b64]}]
                )
                page_summaries.append(f"--- Page {i+1} Notes ---\n{response['message']['content']}")

            # Step 2: Synthesize all notes into one summary
            print(f"  Generating final Executive Summary...")
            combined_notes = "\n\n".join(page_summaries)
            final_response = ollama.chat(
                model=MODEL,
                messages=[{'role': 'user', 'content': f"Here are the notes from the report:\n{combined_notes}\n\n{FINAL_PROMPT}"}]
            )
            
            # Save final single summary
            with open(os.path.join(OUTPUT_DIR, output_filename), "w") as f:
                f.write(final_response['message']['content'])
                
            print(f"Success! Final summary saved: {output_filename}")

        except Exception as e:
            print(f"Error processing {report_name}: {e}")

if __name__ == "__main__":
    process_reports()