import json

# --- CONFIGURATION ---
INPUT_FILE = 'primevul_test_large.jsonl'  # Put your filename here
OUTPUT_FILE = 'scaled_dataset_200.jsonl'
CODE_COLUMN = 'func'  # Change this to 'code', 'snippet', etc.
TARGET_COLUMN = 'target'
# ---------------------

vulnerable = []
non_vulnerable = []

print("Reading dataset...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            # Store the data and the length of the code for sorting
            entry = {'data': data, 'length': len(str(data.get(CODE_COLUMN, "")))}
            
            if data.get(TARGET_COLUMN) == 1:
                vulnerable.append(entry)
            else:
                non_vulnerable.append(entry)
        except json.JSONDecodeError:
            continue

# Sort both lists by length (Shortest first)
vulnerable.sort(key=lambda x: x['length'])
non_vulnerable.sort(key=lambda x: x['length'])

# Take the top 100 of each
final_selection = vulnerable[:100] + non_vulnerable[:100]

# Strip the 'length' helper and keep original format
final_output = [item['data'] for item in final_selection]

print(f"Found {len(vulnerable)} vuln and {len(non_vulnerable)} non-vuln total.")
print(f"Writing {len(final_output)} shortest items to {OUTPUT_FILE}...")

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for item in final_output:
        f.write(json.dumps(item) + '\n')

print("Done! You now have a balanced, short-snippet dataset.")