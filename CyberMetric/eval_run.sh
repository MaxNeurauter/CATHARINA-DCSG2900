#!/bin/bash

# Define the array of models to test, sorted by size to test the waters first
MODELS=(
    "ministral-3:8b"
    "qwen3-vl:8b"
    "gemma3:12b"
    "ministral-3:14b"
    "qwen3-vl:32b"
    "llama4:16x17b"
)

# Set the dataset file you want to use
DATASET="CyberMetric-500-v1.json"

echo "========================================================"
echo "  PRE-FLIGHT CHECK: Clearing memory..."
echo "========================================================"

# Find any models currently loaded into memory (skipping the header row)
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
echo "Starting CyberMetric evaluation batch job for ${#MODELS[@]} models..."
echo "Using dataset: $DATASET"
echo "--------------------------------------------------------"

for MODEL in "${MODELS[@]}"; do
    echo "========================================================"
    echo " Starting evaluation for Model: $MODEL"
    echo "========================================================"
    
    # Execute the Python script for the current model
    python3 CyberMetric_ollama.py "$MODEL" --file "$DATASET"
    
    echo " Finished evaluating $MODEL."
    
    # Force Ollama to unload the model from memory immediately
    echo " Unloading $MODEL from memory..."
    ollama stop "$MODEL"
    
    # A 10-second pause to allow your system's RAM/VRAM to fully clear out
    echo "Sleeping for 10 seconds to let resources settle before the next model..."
    sleep 10
done

echo "========================================================"
echo " All evaluations complete! Check folder for the results JSON files."
