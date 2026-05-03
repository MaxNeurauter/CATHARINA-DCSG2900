# CTIBench-RCM

Benchmark tool for evaluating LLMs on **Ransomware Classification Mapping (RCM)** built upon CTIBench RCM benchmark— given a CVE description, can the model identify the correct CWE code? Part of the CTIBench suite ([NeurIPS 2024](https://arxiv.org/abs/2406.07599)).

Models are queried locally via [Ollama](https://ollama.ai), and accuracy is measured by checking whether the ground-truth CWE ID appears anywhere in the model's response.

---

## Requirements

- Python 3.7+
- [Ollama](https://ollama.ai) installed and running (`ollama serve`)
- Python packages:

```bash
pip install pandas ollama tqdm
```

---

## Running

Runs inference + evaluation for all configured models automatically.

```bash
python3 run_suite.py
```

Edit the top of `run_suite.py` to change the model list or question limit:

```python
MODELS = ["gemma3:12b", "ministral-3:14b", ...]
LIMIT = 100
```


## Output

Results are saved to `rcm_results_<limit>/results_<model_name>.txt` and include accuracy, timing, and a list of wrong answers with expected vs. actual responses.

Intermediate responses are stored in `evaluation/responses/rcm_<model_name>.tsv`.

---

## Dataset

`data/cti-rcm.tsv` — 1000 CVE descriptions each paired with the correct CWE ID (ground truth). The model is given the CVE description and asked to identify the CWE.
