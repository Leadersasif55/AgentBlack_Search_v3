# Agent Black v3 - AI-Powered Search Agent CLI

An advanced, CLI-based research agent that performs comprehensive, multi-step research on any topic.

This tool was adapted from the original [gemini-fullstack-langgraph-quickstart](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) project, converting a full-stack web application into a powerful, standalone command-line utility.

## Features

-   **Dynamic Research**: Run search queries directly from your terminal.
-   **Configurable Difficulty**: Adjust search depth (`easy`, `medium`, `hard`) to control the thoroughness of the research.
-   **Model Selection**: Choose the exact Gemini model you want to use for reasoning.
-   **Rich Output**: Enjoy beautiful, colorful terminal output with formatted text, progress indicators, and tables.
-   **Cited Sources**: Get comprehensive answers with a full list of sources used for the research.
-   **Save Results**: Save complete search reports to a text file for later use.

## Setup

1.  **Clone the Repository**:
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Install Dependencies**:
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set Up Your API Key**:
    -   Create a `.env` file in the root directory. You can copy the `.env.example` if it exists.
    -   Add your Google Gemini API key to the `.env` file:
        ```
        GEMINI_API_KEY="your_api_key_here"
        ```
    -   You can get a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

## Usage

You can run searches directly using `python main.py` or use the provided helper scripts.

**Directly:**
```bash
python main.py "your search query" [options]
```

**Using Helper Scripts:**
The `run_search.sh` (for Linux/macOS) and `run_search.bat` (for Windows) scripts provide an easy way to run a default query.

### Options

-   `query`: (Required) The search query you want to run, enclosed in quotes.
-   `--difficulty`: Set the search difficulty (`easy`, `medium`, `hard`). Default is `medium`.
-   `--model`: Specify which model to use. If not provided, a default is chosen based on the difficulty level.
-   `--save FILENAME`: Save the full report to a text file.
-   `--no-color`: Disable colored output.
-   `--retries N`: Set the maximum number of retries for API calls.

### Examples

**Basic Search (Medium Difficulty):**
```bash
python main.py "recent developments in quantum computing"
```

**Easy Search and Save to File:**
```bash
python main.py "history of artificial intelligence" --difficulty medium --save ai_history.txt
```

**Hard Search with a Specific Model:**
```bash
python main.py "climate change solutions" --difficulty hard --model gemini-2.5-pro-preview-05-06
```

## Credits

This project is a CLI adaptation of the awesome [gemini-fullstack-langgraph-quickstart](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) by Google. It utilizes the core LangGraph agent logic for its research capabilities. 