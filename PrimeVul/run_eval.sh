#!/bin/bash

# --- KONFIGURASJON ---
DATASET="scaled_dataset_200.jsonl"
MODELS=(
    "ministral-3:8b"
    "qwen3-vl:8b"
    "gemma3:12b"
    "ministral-3:14b"
    "qwen3-vl:32b"
    "llama4:16x17b"
)

echo "========================================================"
echo "PRE-FLIGHT CHECK: Clearing memory..."
echo "========================================================"

# Finner kjørende modeller og stopper dem
LOADED_MODELS=$(ollama ps | awk 'NR>1 {print $1}')

if [ -n "$LOADED_MODELS" ]; then
    for LM in $LOADED_MODELS; do
        echo "Found running model: $LM. Unloading it now..."
        ollama stop "$LM"
    done
    echo "Sleeping for 5 seconds to let the system reclaim memory..."
    sleep 5
else
    echo "No models currently loaded. Memory is clear!"
fi

echo ""
echo "Starting evaluation batch job for ${#MODELS[@]} models..."
echo "Using dataset: $DATASET"
echo "--------------------------------------------------------"

for MODEL in "${MODELS[@]}"; do
    echo "========================================================"
    echo "Starting evaluation for Model: $MODEL"
    echo "========================================================"
    
    # Kjører python-scriptet og sender med modellnavn og dataset
    python3 evaluate_single_model.py --model "$MODEL" --file "$DATASET" --max_examples 200
    
    # Tvinger Ollama til å frigjøre minnet
    echo "Unloading $MODEL from memory..."
    ollama stop "$MODEL"
    
    echo "Sleeping for 10 seconds to let resources settle before the next model..."
    sleep 10
done

echo "========================================================"
echo "All evaluations complete! Check your folder for the results txt files."