# CTISum

A benchmark and evaluation framework for automatic **Cyber Threat Intelligence (CTI) Summarization**. The tool runs LLMs (via Ollama) against a dataset of CTI reports and measures summarization quality using ROUGE and BERTScore.

Two summarization tasks are supported:
- **general-summary** — full CTI report summarization
- **attack-summary** (APS) — attack-process-focused summarization

---

## Prerequisites

- Python 3.7+
- [Ollama](https://ollama.com) installed and running locally
-  At least one model pulled, e.g. `ollama pull ministral-3:8b`
   ```
4. Python dependencies (install per script or globally):
   ```bash
   pip install ollama tqdm pdf2image
   ```
   Evaluation metrics have their own requirements — see `evaluate-metrics/rouge/` and `evaluate-metrics/bert-score/`.

---

## Dataset Layout

Place your data under the `dataset/` directory:

```
dataset/
├── pdf_file/               # Source PDFs (input for vision script)
├── general-summary/
│   ├── src/                # Source .txt CTI reports
│   └── tgt/                # Reference summaries (.txt)
└── attack-summary/
    ├── src/
    └── tgt/
```

---

## How to Run

All scripts are run from the project root.

### 1. Summarize text reports
```bash
python3 run_ctisum_ollama.py
```
Reads `.txt` files from `dataset/{TASK}/src/`, generates summaries with an Ollama model, and writes results to a `.jsonl` file.

### 2. Extract and summarize PDFs
```bash
python3 run_ctisum_vision.py
```
Converts PDF pages to images, extracts threat intelligence from each page, and saves consolidated summaries as `.txt` files to `dataset/general-summary/src/`.

### 3. Run the full benchmark sweep
```bash
./run_eval.sh
```
Runs all benchmarks across configured models, manages Ollama memory between runs, and saves results under `benchmark_results/{MODEL}/`.

### Advanced: flexible benchmark runner
```bash
python3 run_ollama_benchmark.py --model ministral-3:8b --outdir results/ --dataset dataset/
```

---

## Evaluate Results

```bash
# ROUGE
cd evaluate-metrics/rouge
python rouge.py

# BERTScore
cd evaluate-metrics/bert-score
python bertscore.py
```

Point each script at your `.jsonl` results file (fields: `hyp`, `ref`).

---

## Configuration

Each script has a small set of variables at the top you can edit:

| Variable | Description | Default |
|---|---|---|
| `MODEL` | Ollama model ID | `ministral-3b` |
| `TASK` | `general-summary` or `attack-summary` | `general-summary` |
| `MAX_REPORTS` | Max number of reports to process | `10` |
