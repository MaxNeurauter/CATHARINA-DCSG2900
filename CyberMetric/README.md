# CyberMetric

A benchmark built on the CyberMetric dataset for evaluating LLMs on cybersecurity knowledge using multiple-choice questions on locally running models. Models are tested locally via Ollama and scored on accuracy across topics such as cryptography, PCI DSS, web security, and more.

## Requirements

- Python 3.7+
- [Ollama](https://ollama.com) installed and running locally
- At least one model pulled, e.g. `ollama pull ministral-3:8b`
- Python packages:

```bash
pip install openai tqdm
```

## Datasets

Four benchmark JSON files are included, differing only in size:

| File | Questions |
|---|---|
| `CyberMetric-80-v1.json` | 80 |
| `CyberMetric-500-v1.json` | 500 |
| `CyberMetric-2000-v1.json` | 2 000 |
| `CyberMetric-10000-v1.json` | 10 000 |

## Running a single model

```bash
python3 CyberMetric_ollama.py <model_name> [--file <dataset_file>]
```

Examples:

```bash
# Quick test with the default 80-question dataset
python3 CyberMetric_ollama.py llama4:16x17b

# Full evaluation with the 500-question dataset
python3 CyberMetric_ollama.py mistral --file CyberMetric-500-v1.json
```

The model must already be pulled in Ollama (`ollama pull <model>`).

## Running multiple models (batch)

Edit `eval_run.sh` to set the `MODELS` array and `DATASET`, then run:

```bash
bash eval_run.sh
```

This tests each model sequentially and unloads them between runs to free memory.

## Output

After each run the script prints accuracy, total time, and time per question to the console, and writes a results file:

```
results_<model_name>.json
```

The file contains the final accuracy percentage, timing metrics, and details of every incorrect answer.
