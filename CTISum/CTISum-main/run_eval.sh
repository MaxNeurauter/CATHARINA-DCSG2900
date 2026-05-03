#!/bin/bash

# Define the array of models to test
MODELS=(
    "ministral-3:8b"
)

# Define the array of Python3 benchmark scripts
BENCHMARKS=(
    "run_ollama_benchmark.py"
    "run_ctisum_ollama.py"
    "run_ctisum_vision.py"
)

# Base directory for all results
BASE_OUTDIR="benchmark_results"

echo "========================================================"
echo "PRE-FLIGHT CHECK: Clearing memory..."
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
echo "Starting Unified Evaluation Batch Job..."
echo "Models: ${#MODELS[@]} | Benchmarks: ${#BENCHMARKS[@]}"
echo "--------------------------------------------------------"

for MODEL in "${MODELS[@]}"; do
    echo "========================================================"
    echo "Starting evaluation suite for Model: $MODEL"
    echo "========================================================"
    
    # Sanitize the model name for the directory (replace ':' with '_')
    SAFE_MODEL_NAME=$(echo "$MODEL" | tr ':' '_')
    MODEL_OUTDIR="$BASE_OUTDIR/$SAFE_MODEL_NAME"
    
    # Create the specific output folder for this model
    mkdir -p "$MODEL_OUTDIR"
    echo "📁 Results will be saved to: $MODEL_OUTDIR"
    
    # Inner loop: Run each benchmark script for the current model
    for SCRIPT in "${BENCHMARKS[@]}"; do
        echo "   Running benchmark: $SCRIPT"
        
        # Execute the Python3 script, passing the dynamic arguments
        python3 "$SCRIPT" --model "$MODEL" --outdir "$MODEL_OUTDIR"
        
        echo "   Finished $SCRIPT."
        echo "   ----------------------------------------"
    done
    
    # Force Ollama to unload the model from memory immediately after its suite finishes
    echo "🧹 Suite complete for $MODEL. Unloading from memory..."
    ollama stop "$MODEL"
    
    # A 10-second pause to allow your system's RAM/VRAM to fully clear out
    echo "Sleeping for 10 seconds before starting the next model..."
    sleep 10
done

echo "========================================================"
echo "All multi-benchmark evaluations complete! Check '$BASE_OUTDIR' for results."