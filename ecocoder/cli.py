import argparse
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ecocoder.github import GitHubRepoAnalyzer
from ecocoder.analyzer import CodeAnalyzer
from ecocoder.reporter import ReportGenerator

console = Console()

def display_banner():
    banner = """
    [green]
     ______     ______     ______     ______     ______     ______    
    /\  ___\   /\  ___\   /\  ___\   /\  ___\   /\  ___\   /\  ___\   
    \ \ \____  \ \  __\   \ \  __\   \ \  __\   \ \___  \  \ \___  \  
     \ \_____\  \ \_____\  \ \_____\  \ \_____\  \/\_____\  \/\_____\ 
      \/_____/   \/_____/   \/_____/   \/_____/   \/_____/   \/_____/ 
    [/green]
    
    [yellow]The ESLint for Carbon Emissions[/yellow]
    """
    console.print(Panel.fit(banner, title="Welcome to EcoCoder", subtitle="v0.1.0"))

def main():
    load_dotenv()
    display_banner()
    
    parser = argparse.ArgumentParser(description="Analyze GitHub repository for carbon emissions")
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument("-o", "--output", help="Output format (text, json, html)", default="text")
    parser.add_argument("-d", "--detail", help="Detail level (basic, detailed, comprehensive)", default="basic")
    parser.add_argument("-t", "--token", help="GitHub personal access token")
    
    args = parser.parse_args()
    
    # Get GitHub token from args or environment
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        console.print("[red]Error: GitHub token is required. Set GITHUB_TOKEN environment variable or use --token argument[/red]")
        sys.exit(1)
    
    # Parse repository URL
    repo_url = args.repo_url
    if not repo_url.startswith("https://github.com/"):
        console.print("[red]Error: Only GitHub repositories are supported[/red]")
        sys.exit(1)
    
    repo_path = repo_url.replace("https://github.com/", "")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Analyzing repository...", total=None)
        
        # Clone and analyze repository
        try:
            # Initialize analyzer
            gh_analyzer = GitHubRepoAnalyzer(token)
            code_analyzer = CodeAnalyzer()
            reporter = ReportGenerator()
            
            # Clone repo
            repo_dir = gh_analyzer.clone_repository(repo_path)
            
            # Analyze code
            analysis_result = code_analyzer.analyze_repository(repo_dir)
            
            # Generate emissions report
            emissions_report = code_analyzer.calculate_emissions(analysis_result)
            
            # Generate report
            if args.output == "json":
                report = reporter.generate_json_report(emissions_report, args.detail)
                print(report)
            elif args.output == "html":
                report = reporter.generate_html_report(emissions_report, args.detail)
                print(report)
            else:
                report = reporter.generate_text_report(emissions_report, args.detail)
                console.print(report)
                
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
        finally:
            # Clean up
            if 'repo_dir' in locals():
                gh_analyzer.cleanup(repo_dir)

if __name__ == "__main__":
    main()