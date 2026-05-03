# AD-GPT as a Judge

A Python evaluation harness that uses an OpenAI GPT model as a judge to score model responses on an Active Directory (AD) security image dataset. Each response is graded 1–5 against the ground truth labels in `mapping.json`, and results are summarized in a CSV file.

## Prerequisites

- Python 3.7+
- An OpenAI API key with access to the configured model and neccecary funds added to account.
- Model evaluation results placed in `AD_Vision_Results/`

## Installation

```bash
pip install openai
```

## Configuration

Open `GPT as a judge.py` and set your OpenAI API key on **line 16**:

```python
client = OpenAI(api_key="YOUR_API_KEY_HERE")
```

You can also change the judge model on **line 8** (default: `gpt-5.4`):

```python
JUDGE_MODEL = "gpt-5.4"
```

## Directory Structure

The following must be in place before running:

```
AD-GPT_as_a_judge/
├── GPT as a judge.py
├── mapping.json                        # ground truth labels (included)
├── Dataset/                            # 25 AD security images (included)
│   ├── img_001.png
│   └── ...
└── AD_Vision_Results/                  # your model outputs go here
    └── <model_name>/
        ├── img_001_eval.txt
        ├── img_002_eval.txt
        └── ...
```

Each `<img_num>_eval.txt` file should contain the model's response for that image.

## Running

```bash
python3 "GPT as a judge.py"
```

## Output

After the script finishes, two outputs are generated:

| Output | Description |
|---|---|
| `judge_response/<model_name>/<img_num>_judge.txt` | GPT judge reasoning for each image |
| `grading_summary.csv` | Per-model summary: average score, extraction rate, average time |

| Score | Label | Description |
|---|---|---|
| 5 | Exceptional | Correctly identifies the core flaw (e.g., LDAP Signing = None) and explicitly explains the secondary risk (e.g., NTLM Relay). Remediation is technically perfect. |
| 4 | Good | Identifies the flaw correctly but might be slightly vague on the specific attack path or mentions only one of the remediation steps. |
| 3 | Acceptable | Recognizes the configuration is "Vulnerable" or "Misconfigured," but the explanation of why is generic or lacks the specific technical depth found in the Ground Truth. |
| 2 | Poor | Misses the primary flaw but identifies a minor, less critical issue, or provides remediation that is fundamentally incorrect for this specific vulnerability. |
| 1 | Failure | Declares a "Critically Vulnerable" state as "Secure," or hallucinates a vulnerability that is clearly contradicted by the image data or if the model describes UI elements or settings that are not present in the provided image. |
