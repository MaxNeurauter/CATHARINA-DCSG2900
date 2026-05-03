# AD Vision Benchmark

Evaluates vision-capable LLMs on their ability to identify security misconfigurations in Active Directory screenshots. Each model receives images of AD settings (user attributes, GPOs, ACLs) and is asked to produce a structured security assessment.

## Requirements

- Python 3.7+
- [Ollama](https://ollama.com) installed and running locally

## Install dependencies

```bash
pip install ollama tqdm
```

## Pull required models

The following models must be downloaded via Ollama before running:

```bash
ollama pull gemma3:12b
ollama pull ministral-3:14b
ollama pull ministral-3:8b
ollama pull qwen3-vl:8b
ollama pull qwen3-vl:32b
ollama pull llama4:16x17b
```

## Run

```bash
python run_tests.py
```

The script processes all images in the `Dataset/` directory against each configured model.

## Output

Results are saved to `AD_Vision_Results/` with one subfolder per model:

```
AD_Vision_Results/
├── gemma3_12b/
│   ├── img_001_eval.txt
│   ├── img_002_eval.txt
│   └── ...
└── ...
```

Each `.txt` file contains the image name, model used, processing time, status, and the full LLM security assessment.

## Configuration

Edit `run_tests.py` to change:

- `MODELS_TO_TEST` — list of Ollama model names to evaluate
- `DATASET_DIRECTORY` — path to the folder containing input images (default: `Dataset`)
- `RESULTS_DIRECTORY` — path where results are written (default: `AD_Vision_Results`)
