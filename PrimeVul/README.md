# PrimeVul

This benchmark uses the parts of the PrimeVul dataset and is a vulnerability-detection benchmark that evaluates local LLMs (via Ollama) on C/C++ code snippets. Each snippet is classified as **vulnerable (1)** or **safe (0)**, and the tool reports accuracy metrics across the full test set.

## Prerequisites

- Python 3.7+
- [Ollama](https://ollama.com) installed and running locally
- At least one model pulled, e.g. `ollama pull ministral-3:8b`

Install Python dependencies:

```bash
pip install requests tqdm
```

## Files

| File | Description |
|------|-------------|
| `evaluate_single_model.py` | Core evaluation engine — sends code snippets to Ollama and records predictions |
| `extractor.py` | Dataset preparation utility — extracts a balanced subset from the full dataset |
| `run_eval.sh` | Batch evaluation script — runs multiple models sequentially |
| `scaled_dataset_200.jsonl` | Pre-balanced dataset (100 vulnerable + 100 safe samples) |
| `primevul_test.jsonl` | Full test dataset |

## How to run

### Batch evaluation (recommended)

Evaluates all pre-configured models in sequence and writes a `results_<MODEL>.txt` for each:

```bash
chmod +x run_eval.sh
./run_eval.sh
```

Edit the `MODELS` array in `run_eval.sh` to change which models are tested.

### Single model

```bash
python3 evaluate_single_model.py --model <MODEL> --file scaled_dataset_200.jsonl --max_examples 200
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--model` | Yes | Ollama model name (e.g. `ministral-3:8b`, `llama4:16x17b`) |
| `--file` | Yes | Path to JSONL dataset file |
| `--max_examples` | No (default: 20) | Number of samples to evaluate |

### Prepare a custom dataset

```bash
python3 extractor.py
```

Reads `primevul_test.jsonl`, picks the shortest 100 vulnerable and 100 safe samples, and writes `scaled_dataset_200.jsonl`. Edit the constants at the top of `extractor.py` to change the size or balance ratio.

## Output

Each `results_<MODEL>.txt` contains:

- Overall accuracy (%)
- Correct / wrong / invalid prediction counts
- Vulnerable-sample breakdown
- Safe-sample breakdown
- Total execution time
- Per-sample prediction log
