@echo off
REM Run the search agent with the provided arguments

REM Check if any arguments are provided
if "%1"=="" (
    echo Usage: run_search.bat "your search query" [--difficulty easy|medium|hard] [--model model_name]
    echo Example: run_search.bat "recent developments in quantum computing" --difficulty medium
    exit /b 1
)

REM Run the Python script with all provided arguments
python main.py %* 