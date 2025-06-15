#!/usr/bin/env python
"""
Command-line interface for the search agent.

Usage:
    python main.py "your search query" --difficulty [easy|medium|hard] --model [model_name]

Example:
    python main.py "recent developments in quantum computing" --difficulty medium --model gemini-2.5-pro-preview-05-06
"""

import os
import sys
import argparse
import time
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import re

# Import the agent components
from agent import create_graph_for_direct_use, OutputFormatter, show_spinner, extract_citation_urls
from agent.configuration import Configuration

# Load environment variables
load_dotenv()

# Maximum number of retries for API calls
MAX_RETRIES = 3
# Delay between retries (in seconds)
RETRY_DELAY = 5

def setup_argparse():
    """Set up command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Run a search query with configurable difficulty and model."
    )
    
    parser.add_argument(
        "query", 
        type=str, 
        help="The search query to run"
    )
    
    parser.add_argument(
        "--difficulty", 
        type=str, 
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Difficulty level (affects search depth and quality)"
    )
    
    parser.add_argument(
        "--model", 
        type=str,
        help="The model to use for reasoning (default depends on difficulty)"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    parser.add_argument(
        "--save",
        type=str,
        metavar="FILENAME",
        help="Save the search results to a text file"
    )
    
    parser.add_argument(
        "--retries",
        type=int,
        default=MAX_RETRIES,
        help=f"Maximum number of retries for API calls (default: {MAX_RETRIES})"
    )
    
    return parser

def configure_for_difficulty(difficulty, custom_model=None):
    """Configure the agent based on difficulty level."""
    config = {}
    
    # Base configuration settings
    if difficulty == "easy":
        config = {
            "number_of_initial_queries": 1,
            "max_research_loops": 1,
            "reasoning_model": custom_model or "gemini-2.0-flash"
        }
    elif difficulty == "medium":
        config = {
            "number_of_initial_queries": 3,
            "max_research_loops": 2,
            "reasoning_model": custom_model or "gemini-2.5-flash-preview-05-20"
        }
    elif difficulty == "hard":
        config = {
            "number_of_initial_queries": 5,
            "max_research_loops": 3,
            "reasoning_model": custom_model or "gemini-2.5-pro-preview-05-06"
        }
    
    return config

def validate_environment():
    """Validate that necessary environment variables are set."""
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set.")
        print("Please create a .env file with your Gemini API key or set it manually.")
        sys.exit(1)

def format_output(result, formatter):
    """Format the agent's output for display using rich formatting."""
    try:
        # Extract the answer content
        answer = result["messages"][-1].content if "messages" in result and len(result["messages"]) > 0 else ""
        
        # Display the formatted answer in the console
        formatter.format_answer(answer)
        
        # Extract and display sources if available
        if "sources_gathered" in result and result["sources_gathered"]:
            formatter.display_sources(result["sources_gathered"])
        
        # Return the raw content for file saving
        return answer
    except Exception as e:
        formatter.display_error(f"Error formatting output: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Error occurred while formatting output. See console for details."

def sanitize_text(text):
    """Sanitize text to remove problematic characters for file saving."""
    # Replace any potentially problematic characters or sequences
    # that could cause string formatting issues
    if text is None:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Handle any special cases that might cause issues
    # Fix vertexaisearch URLs that might contain special formatting characters
    text = re.sub(r'\[vertexaisearch\.google\.com/id/([^]]+)\]', 
                  r'[vertexaisearch-google-id-\1]', text)
    
    # Replace other problematic characters
    text = text.replace('{', '{{').replace('}', '}}')
    
    return text

def save_results_to_file(filename, query, answer):
    """Save search results to a file with robust error handling for special characters."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Write the header without formatting
            f.write("SEARCH QUERY: ")
            f.write(sanitize_text(query))
            f.write("\n\n")
            f.write("RESULTS:\n\n")
            
            # Write answer directly without any string formatting
            # This ensures special characters in URLs don't cause formatting issues
            f.write(sanitize_text(answer))
        return True
    except Exception as e:
        print(f"Error saving results to file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_search(query, config, formatter, max_retries=MAX_RETRIES):
    """Run the search with the given query and configuration."""
    # Create initial message
    messages = [HumanMessage(content=query)]
    
    # Initialize state
    state = {
        "messages": messages,
        "reasoning_model": config.get("reasoning_model")
    }
    
    # Show progress for query generation
    formatter.display_progress("Generating search queries", 1.0)
    
    # Create and run the graph
    graph = create_graph_for_direct_use()
    
    # Show progress for search execution
    formatter.display_progress("Executing web search", 1.0)
    
    # Start timing the search
    start_time = time.time()
    
    # Add retry logic for transient errors
    retries = 0
    while retries <= max_retries:
        try:
            result = graph.invoke(state, {"configurable": config})
            break  # Success, exit the retry loop
        except Exception as e:
            error_message = str(e)
            retries += 1
            
            # Check if it's a server overload error (503)
            if "503 UNAVAILABLE" in error_message and "model is overloaded" in error_message:
                if retries <= max_retries:
                    formatter.console.print(f"[warning]Gemini API is overloaded. Retrying ({retries}/{max_retries}) in {RETRY_DELAY} seconds...[/warning]")
                    time.sleep(RETRY_DELAY)
                else:
                    raise Exception(f"Gemini API is overloaded. Please try again later or try a different model.")
            else:
                # For other errors, don't retry
                raise
    
    end_time = time.time()
    
    # Show progress for answer generation
    formatter.display_progress("Generating comprehensive answer", 1.0)
    
    # Display execution time
    execution_time = end_time - start_time
    formatter.display_completion(execution_time)
    
    return result

def main():
    """Main entry point for the CLI application."""
    # Set up argument parsing
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Create formatter
    formatter = OutputFormatter(no_color=args.no_color)
    
    # Validate environment
    validate_environment()
    
    # Configure based on difficulty
    config = configure_for_difficulty(args.difficulty, args.model)
    
    # Display header
    formatter.display_header(args.query, args.difficulty, config.get("reasoning_model"))
    
    try:
        # Run the search with retry logic
        result = run_search(args.query, config, formatter, args.retries)
        answer = format_output(result, formatter)
        
        # Save results if requested
        if args.save:
            try:
                if save_results_to_file(args.save, args.query, answer):
                    formatter.console.print(f"\n[success]Results saved to [bold]{args.save}[/bold][/success]")
                else:
                    formatter.display_error(f"Failed to save results to {args.save}")
            except Exception as save_error:
                formatter.display_error(f"Error saving file: {str(save_error)}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        formatter.display_error(f"Error running search: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 