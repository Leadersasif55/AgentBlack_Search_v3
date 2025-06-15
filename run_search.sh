#!/bin/bash
# Run the search agent with the provided arguments

# Check if any arguments are provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run_search.sh \"your search query\" [--difficulty easy|medium|hard] [--model model_name]"
    echo "Example: ./run_search.sh \"recent developments in quantum computing\" --difficulty medium"
    exit 1
fi

# Run the Python script with all provided arguments
python main.py "$@" 