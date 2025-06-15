"""
Formatting utilities for terminal output styling.

This module provides functions for styling and formatting terminal output
with colors, layout, and visual elements using colorama and rich libraries.
"""

import re
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

from colorama import Fore, Back, Style, init as colorama_init
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.box import Box, ROUNDED, DOUBLE, HEAVY
from rich.theme import Theme

# Initialize colorama
colorama_init(autoreset=True)

# Custom theme for consistent styling
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "bold green",
    "query": "bold yellow",
    "header": "bold blue",
    "subheader": "bold cyan",
    "section": "magenta",
    "url": "blue underline",
    "highlight": "bold yellow",
    "citation": "dim blue",
    "timestamp": "dim white",
})

# Initialize rich console
console = Console(theme=custom_theme)

# ASCII Art for header
SEARCH_HEADER = r"""
                           _     ____  _            _    
     /\                   | |   |  _ \| |          | |   
    /  \   __ _  ___ _ __ | |_  | |_) | | __ _  ___| | __
   / /\ \ / _` |/ _ \ '_ \| __| |  _ <| |/ _` |/ __| |/ /
  / ____ \ (_| |  __/ | | | |_  | |_) | | (_| | (__|   < 
 /_/    \_\__, |\___|_| |_|\__| |____/|_|\__,_|\___|_|\_\ v3
           __/ |                                         
          |___/                                            
"""

# Difficulty icons
DIFFICULTY_ICONS = {
    "easy": "🟢",
    "medium": "🟡",
    "hard": "🔴"
}

class OutputFormatter:
    """Class for handling rich terminal output formatting."""
    
    def __init__(self, no_color=False):
        self.console = Console(theme=custom_theme, highlight=not no_color)
        self.no_color = no_color
        
    def display_header(self, query: str, difficulty: str, model: str):
        """Display a styled header for the search."""
        # Display ASCII art header
        self.console.print(f"[header]{SEARCH_HEADER}[/header]")
        
        # Create panel with search info
        difficulty_icon = DIFFICULTY_ICONS.get(difficulty.lower(), "⚪")
        search_info = (
            f"[bold]Query:[/bold] [query]{query}[/query]\n"
            f"[bold]Difficulty:[/bold] {difficulty_icon} "
            f"[{'success' if difficulty == 'easy' else 'warning' if difficulty == 'medium' else 'danger'}]{difficulty.upper()}[/]\n"
            f"[bold]Model:[/bold] [info]{model}[/info]\n"
            f"[bold]Date:[/bold] [timestamp]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/timestamp]"
        )
        
        self.console.print(Panel(search_info, 
                               title="[bold]Search Parameters[/bold]", 
                               border_style="cyan",
                               box=ROUNDED,
                               expand=False))
        self.console.print()
    
    def display_progress(self, stage: str, duration=1.0):
        """Display a progress indicator for the current stage."""
        # Show a visually distinct stage header
        self.console.print(f"[bold blue]▶ {stage}[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40, complete_style="cyan", finished_style="green"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(f"[cyan]Processing...", total=100)
            # Simulate progress
            increment = 100 / (duration * 10)
            for _ in range(10):
                progress.update(task, advance=increment)
                time.sleep(duration/10)
    
    def format_answer(self, answer_text: str) -> str:
        """Format the answer text with enhanced styling."""
        # Process markdown-style formatting and apply rich formatting
        # Extract sections (if any)
        sections = re.split(r'(?i)^##?\s+(.+)$', answer_text, flags=re.MULTILINE)
        
        # Display result header
        self.console.print(Panel(
            "[bold]Search Results[/bold]", 
            border_style="green", 
            box=HEAVY
        ))
        
        if len(sections) > 1:
            # Process as structured content with sections
            self._format_structured_content(sections)
        else:
            # Process as regular text
            self._format_regular_content(answer_text)
    
    def _format_structured_content(self, sections: List[str]):
        """Format content that has sections."""
        current_title = None
        
        for i, section in enumerate(sections):
            if i % 2 == 0 and i > 0:
                current_title = sections[i-1].strip()
                self.console.print()
                self.console.print(Panel(
                    f"[subheader]{current_title.upper()}[/subheader]", 
                    border_style="cyan", 
                    box=ROUNDED
                ))
                
                # Format the section content
                content = self._process_text(section)
                self.console.print(Markdown(content))
            elif i == 0 and section.strip():
                # Introduction/summary before any section headers
                self.console.print()
                self.console.print(Panel(
                    "[success]SUMMARY[/success]", 
                    border_style="green", 
                    box=ROUNDED
                ))
                content = self._process_text(section)
                self.console.print(Markdown(content))
    
    def _format_regular_content(self, text: str):
        """Format content that doesn't have explicit sections."""
        # Process text for highlighting and formatting
        processed_text = self._process_text(text)
        
        # Display as markdown
        self.console.print(Markdown(processed_text))
    
    def _process_text(self, text: str) -> str:
        """Process text to enhance formatting."""
        # Remove Google API redirect URLs
        text = re.sub(r'\(https://vertexaisearch\.cloud\.google\.com/grounding-api-redirect/[^\)]+\)', '', text)
        
        # Replace citation patterns with rich formatting
        text = re.sub(r'\[(.*?)\]\((https?://.*?)\)', 
                     r'__\1__ [link=\2][citation]🔗[/citation][/link]', 
                     text)
        
        # Highlight key phrases
        text = re.sub(r'"([^"]+)"', r'**"\1"**', text)
        
        # Format bullet points more prominently
        text = re.sub(r'^(\s*)-\s+(.+)$', r'\1• \2', text, flags=re.MULTILINE)
        
        # Add extra styling for numbers in lists
        text = re.sub(r'^(\s*)(\d+)\.\s+(.+)$', r'\1__\2.__ \3', text, flags=re.MULTILINE)
        
        return text
    
    def display_sources(self, sources: List[Dict[str, Any]]):
        """Display sources in a formatted table."""
        if not sources:
            return
            
        self.console.print()
        self.console.print(Panel(
            "[bold yellow]SOURCES & CITATIONS[/bold yellow]", 
            border_style="yellow", 
            box=ROUNDED
        ))
        
        # Create table for sources
        table = Table(show_header=True, header_style="bold yellow", box=ROUNDED)
        table.add_column("#", style="dim", width=7)
        table.add_column("Title", style="yellow", min_width=20, max_width=30)
        table.add_column("URL", style="cyan", max_width=40)
        
        unique_sources = {}
        for source in sources:
            if isinstance(source, dict) and "value" in source:
                url = source.get("value", "")
                if url not in unique_sources:
                    unique_sources[url] = source.get("label", "Source")
        
        for i, (url, title) in enumerate(unique_sources.items(), 1):
            # Clean up title
            clean_title = title.strip()[:30]
            
            # For Google API redirect URLs, just show "Source Link" instead of the long URL
            display_url = url
            if "vertexaisearch.cloud.google.com/grounding-api-redirect" in url:
                display_url = f"Source #{i} (Click to visit)"
            
            table.add_row(f"[{i}]", clean_title, f"[link={url}]{display_url}[/link]")
            
        self.console.print(table)
        
        # Add citation instructions
        self.console.print()
        self.console.print(Panel(
            "[dim]Links marked with 🔗 in the text correspond to the numbered sources above.[/dim]",
            border_style="dim",
            box=ROUNDED,
            padding=(1, 2)
        ))
    
    def display_error(self, error_message: str):
        """Display an error message."""
        self.console.print(Panel(
            f"[danger]{error_message}[/danger]",
            title="[danger]ERROR[/danger]",
            border_style="red",
            box=HEAVY
        ))
        
    def display_completion(self, execution_time: float):
        """Display completion information."""
        self.console.print()
        self.console.print(Panel(
            f"[success]Search completed in {execution_time:.2f} seconds[/success]", 
            border_style="green", 
            box=ROUNDED
        ))

# Helper function for progress display
def show_spinner(message: str, seconds: int = 1):
    """Show a spinner with a message for a specified number of seconds."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(f"[cyan]{message}", total=None)
        time.sleep(seconds)
        
def highlight_text(text: str, pattern: str) -> str:
    """Highlight a pattern in text."""
    return text.replace(pattern, f"{Fore.YELLOW}{pattern}{Style.RESET_ALL}")

def format_url(url: str) -> str:
    """Format a URL for display."""
    return f"{Fore.BLUE}{url}{Style.RESET_ALL}"

# Helper for extracting sources from response content
def extract_citation_urls(content: str) -> List[Dict[str, str]]:
    """Extract citation URLs from content."""
    urls = []
    matches = re.finditer(r'\[(.*?)\]\((https?://[^)]+)\)', content)
    
    for match in matches:
        if match.group(2) not in [url.get('url') for url in urls]:
            urls.append({
                'label': match.group(1),
                'url': match.group(2)
            })
    
    return urls 