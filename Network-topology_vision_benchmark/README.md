# Network Topology Vision Benchmark

Evaluates vision-capable LLMs on their ability to analyze network topology diagrams. Each model receives topology images and is asked to produce a structured assessment covering device inventory, architecture type, strengths, weaknesses, and recommendations.

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
python3 run_network_tests.py
```

The script processes all images in the `nettverksdatasett/` directory against each configured model.

## Output

Results are saved to `Topology_Analysis_Results/` with one subfolder per model:

```
Topology_Analysis_Results/
├── gemma3_12b/
│   ├── img_001_analysis.txt
│   ├── img_002_analysis.txt
│   └── ...
└── ...
```

Each `.txt` file contains the image name, model used, processing time, status, and the full LLM analysis.

## Configuration

Edit `run_network_tests.py` to change:

- `MODELS_TO_TEST` — list of Ollama model names to evaluate
- `DATASET_DIRECTORY` — path to the folder containing input images (default: `nettverksdatasett`)
- `RESULTS_DIRECTORY` — path where results are written (default: `Topology_Analysis_Results`)
