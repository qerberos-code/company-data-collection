#!/usr/bin/env python3
"""
Company Data Collection Prototype
Agentic AI system for collecting, preparing, and validating company data from Wikipedia.
"""

import os
import sys
import argparse
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.settings import settings
from src.database.connection import db_manager
from src.agents.company_data_agent import CompanyDataAgent


def setup_logging():
    """Setup logging configuration."""
    # Remove default logger
    logger.remove()
    
    # Add console logging
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file logging
    os.makedirs("logs", exist_ok=True)
    logger.add(
        settings.log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days"
    )


def initialize_database():
    """Initialize the database."""
    logger.info("Initializing database...")
    try:
        db_manager.create_tables()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


def run_agentic_collection(company_name: str) -> dict:
    """Run the agentic AI collection process."""
    logger.info(f"Starting agentic collection for {company_name}")
    
    try:
        agent = CompanyDataAgent()
        result = agent.process_company(company_name)
        
        if result['success']:
            logger.info(f"Successfully processed {company_name}")
        else:
            logger.error(f"Failed to process {company_name}: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in agentic collection for {company_name}: {e}")
        return {
            'success': False,
            'company_name': company_name,
            'error': str(e)
        }


def display_results(results: list, console: Console):
    """Display results in a formatted table."""
    table = Table(title="Company Data Collection Results")
    
    table.add_column("Company", style="cyan", no_wrap=True)
    table.add_column("Status", style="green" if all(r['success'] for r in results) else "red")
    table.add_column("Details", style="white")
    
    for result in results:
        status = "✅ Success" if result['success'] else "❌ Failed"
        details = result.get('result', result.get('error', 'No details'))[:100] + "..." if len(str(result.get('result', result.get('error', 'No details')))) > 100 else str(result.get('result', result.get('error', 'No details')))
        
        table.add_row(
            result['company_name'],
            status,
            details
        )
    
    console.print(table)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Company Data Collection Prototype")
    parser.add_argument(
        "--company",
        default=settings.target_company,
        help="Company name to process (default: Alphabet Inc.)"
    )
    parser.add_argument(
        "--companies",
        nargs="+",
        help="Multiple company names to process"
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database tables"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        settings.log_level = "DEBUG"
    setup_logging()
    
    console = Console()
    
    # Display banner
    banner = Panel.fit(
        "[bold blue]Company Data Collection Prototype[/bold blue]\n"
        "[italic]Agentic AI system for Wikipedia data collection, preparation, and validation[/italic]",
        border_style="blue"
    )
    console.print(banner)
    
    # Initialize database if requested
    if args.init_db:
        if not initialize_database():
            console.print("[red]Failed to initialize database. Exiting.[/red]")
            sys.exit(1)
        console.print("[green]Database initialized successfully.[/green]")
        return
    
    # Determine companies to process
    if args.companies:
        company_names = args.companies
    else:
        company_names = [args.company]
    
    console.print(f"[yellow]Processing {len(company_names)} company(ies): {', '.join(company_names)}[/yellow]")
    
    # Process companies
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        for company_name in company_names:
            task = progress.add_task(f"Processing {company_name}...", total=None)
            
            result = run_agentic_collection(company_name)
            results.append(result)
            
            progress.update(task, description=f"Completed {company_name}")
    
    # Display results
    display_results(results, console)
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    summary_panel = Panel.fit(
        f"[bold]Summary:[/bold] {successful}/{total} companies processed successfully\n"
        f"[bold]Success Rate:[/bold] {(successful/total)*100:.1f}%",
        border_style="green" if successful == total else "yellow" if successful > 0 else "red"
    )
    console.print(summary_panel)
    
    # Exit with appropriate code
    if successful == total:
        console.print("[green]All companies processed successfully![/green]")
        sys.exit(0)
    elif successful > 0:
        console.print("[yellow]Some companies processed successfully.[/yellow]")
        sys.exit(1)
    else:
        console.print("[red]No companies processed successfully.[/red]")
        sys.exit(2)


if __name__ == "__main__":
    main()
