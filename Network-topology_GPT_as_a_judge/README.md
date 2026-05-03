# Network Topology — GPT as a Judge

Uses an OpenAI model to grade LLM responses on network topology diagram analysis. Each response is scored 1–5 against a ground truth description, and results are saved to a CSV summary.

## Prerequisites

- Python 3.7+
- An OpenAI API key with access to the configured model and neccecary funds added to account.

## Setup

**1. Install dependencies**
```bash
pip install openai
```

**2. Set your OpenAI API key**
```bash
export OPENAI_API_KEY="sk-..."
```

Or set `api_key` directly on line 16 of `GPT as a judge.py`.

**3. (Optional) Edit configuration** at the top of `GPT as a judge.py`:
```python
JUDGE_MODEL  = "gpt-5.4"                  # OpenAI model used as judge
RESULTS_DIR  = "Topology_Analysis_Results" # Where model analyses are read from
DATASET_DIR  = "nettverksdatasett"         # Where the network images are
```

## Required input structure

```
Topology_Analysis_Results/
└── <model_name>/
    ├── img_001_analysis.txt
    ├── img_002_analysis.txt
    └── ...
nettverksdatasett/
├── img_001.JPG
└── ...
mapping.json
```

Each `_analysis.txt` file must contain a `LLM RESPONSE:` section and a `Time Taken: X seconds` line.

## Run

```bash
python3 "GPT as a judge.py"
```

## Output

| Path | Contents |
|------|----------|
| `judge_response/<model_name>/img_XXX_judge.txt` | Full judge reasoning and score per image |
| `grading_summary.csv` | Per-model summary: name, successful extractions, average score, average time |

## Scoring rubric

| Score | Label | Criteria |
|-------|-------|----------|
| 5 | Exceptional | Perfect device inventory, correct topology, all flaws and recommendations identified |
| 4 | Good | Main design and primary flaws correct, slightly less precise |
| 3 | Acceptable | General understanding, lacks depth, misses secondary risks |
| 2 | Poor | Misses a major SPOF or misclassifies topology type |
| 1 | Failure | Declares flawed design as optimal, hallucinates devices, or ignores inconclusive images |
