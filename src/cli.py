"""Command-line interface for SEO Image Converter."""

import sys
import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel

from .processor import SEOImageProcessor, ProcessingResult
from .logger import logger

console = Console()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

class ProgressTracker:
    """Progress tracking with rich display."""
    
    def __init__(self, total_files: int):
        self.total_files = total_files
        self.progress = None
        self.task = None
        
    def __enter__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TextColumn("[blue]{task.completed}/{task.total}"),
            "•",
            TimeElapsedColumn(),
            console=console,
        )
        self.task = self.progress.add_task("Processing images...", total=self.total_files)
        self.progress.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()
    
    def update(self, completed: int, total: int, result: ProcessingResult):
        """Update progress display."""
        if self.progress and self.task:
            status_emoji = "✅" if result.success else "❌"
            description = f"Processing images... {status_emoji} {result.input_path.name}"
            
            self.progress.update(
                self.task,
                completed=completed,
                description=description
            )

def display_summary_report(report: dict):
    """Display comprehensive summary report."""
    summary = report['summary']
    size_analysis = report['size_analysis']
    
    # Create summary table
    summary_table = Table(title="Processing Summary", show_header=True)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="white")
    
    summary_table.add_row("Total Files", str(summary['total_files']))
    summary_table.add_row("✅ Processed", f"[green]{summary['processed']}[/green]")
    summary_table.add_row("❌ Failed", f"[red]{summary['failed']}[/red]")
    summary_table.add_row("⏭️ Skipped", f"[yellow]{summary['skipped']}[/yellow]")
    summary_table.add_row("⏱️ Total Time", format_duration(summary['processing_time']))
    summary_table.add_row("⚡ Avg Time/Image", f"{summary['average_time_per_image']:.2f}s")
    
    console.print(summary_table)
    console.print()
    
    # Size analysis table
    size_table = Table(title="Size Analysis", show_header=True)
    size_table.add_column("Metric", style="cyan")
    size_table.add_column("Value", style="white")
    
    size_table.add_row("Original Total Size", format_file_size(size_analysis['total_original_size']))
    size_table.add_row("Optimized Total Size", format_file_size(size_analysis['total_optimized_size']))
    size_table.add_row("💾 Total Savings", f"[green]{format_file_size(size_analysis['total_savings_bytes'])}[/green]")
    size_table.add_row("📊 Overall Compression", f"[green]{size_analysis['overall_compression_ratio']:.1f}%[/green]")
    size_table.add_row("📈 Avg Compression/Image", f"{size_analysis['average_compression_per_image']:.1f}%")
    
    console.print(size_table)

def display_detailed_results(results: list, show_all: bool = False):
    """Display detailed results for each processed image."""
    if not results:
        return
    
    # Filter results if not showing all
    display_results = results
    if not show_all:
        # Show failures and top 10 successful conversions by compression ratio
        failures = [r for r in results if not r['success']]
        successes = [r for r in results if r['success']]
        successes.sort(key=lambda x: x.get('compression_ratio', 0), reverse=True)
        display_results = failures + successes[:10]
    
    if not display_results:
        return
    
    # Create detailed results table
    results_table = Table(title="Detailed Results", show_header=True)
    results_table.add_column("Status", width=6)
    results_table.add_column("Input File", style="cyan")
    results_table.add_column("SEO Keywords", style="yellow")
    results_table.add_column("Original", style="white")
    results_table.add_column("Optimized", style="green")
    results_table.add_column("Savings", style="magenta")
    results_table.add_column("Time", style="blue")
    
    for result in display_results:
        status = "✅" if result['success'] else "❌"
        input_name = Path(result['input_file']).name
        keywords = result.get('seo_keywords', 'N/A') or 'N/A'
        original_size = format_file_size(result['original_size'])
        optimized_size = format_file_size(result['optimized_size']) if result['optimized_size'] > 0 else "N/A"
        savings = f"{result['compression_ratio']:.1f}%" if result['success'] else "N/A"
        time_taken = f"{result['processing_time']:.1f}s"
        
        # Truncate long keywords for display
        if len(keywords) > 30:
            keywords = keywords[:27] + "..."
        
        results_table.add_row(
            status, input_name, keywords, original_size, 
            optimized_size, savings, time_taken
        )
    
    console.print(results_table)
    
    if not show_all and len(results) > len(display_results):
        console.print(f"\n[dim]Showing {len(display_results)} of {len(results)} results. Use --detailed for all results.[/dim]")

def display_errors(results: list):
    """Display error information for failed conversions."""
    errors = [r for r in results if not r['success'] and r.get('error')]
    
    if not errors:
        return
    
    console.print(Panel.fit(
        f"[red]Found {len(errors)} errors during processing:[/red]",
        title="Errors",
        border_style="red"
    ))
    
    for result in errors:
        input_name = Path(result['input_file']).name
        error_msg = result.get('error', 'Unknown error')
        console.print(f"[red]❌ {input_name}[/red]: {error_msg}")
    
    console.print()

@click.command()
@click.argument('input_directory', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output directory (default: same as input)')
@click.option('--config-file', '-c', type=click.Path(exists=True, path_type=Path), help='Custom configuration file')
@click.option('--format', type=click.Choice(['webp', 'png', 'jpeg']), help='Output format override')
@click.option('--quality', type=int, help='Quality setting override (format-dependent)')
@click.option('--parallel-jobs', '-j', type=int, help='Number of parallel jobs (0=auto)')
@click.option('--dry-run', is_flag=True, help='Show what would be processed without making changes')
@click.option('--skip-existing', is_flag=True, help='Skip files that already exist in output directory')
@click.option('--no-backup', is_flag=True, help='Do not backup original files')
@click.option('--detailed', is_flag=True, help='Show detailed results for all processed images')
@click.option('--json-output', type=click.Path(path_type=Path), help='Save detailed report as JSON')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress progress output')
def main(input_directory: Path, output: Optional[Path], config_file: Optional[Path],
         format: Optional[str], quality: Optional[int], parallel_jobs: Optional[int],
         dry_run: bool, skip_existing: bool, no_backup: bool, 
         detailed: bool, json_output: Optional[Path], verbose: bool, quiet: bool):
    """
    SEO Image Converter - Optimize images with AI-powered SEO naming.
    
    INPUT_DIRECTORY: Directory containing images to process
    """
    
    try:
        # Load custom config if provided
        if config_file:
            # Reload config with custom file
            from .config import Config
            global config
            config = Config(config_file)
        
        # Apply command-line overrides
        if format:
            config.update('image.formats.output', format)
        if quality and format:
            config.update(f'image.quality.{format}', quality)
        if parallel_jobs is not None:
            config.update('processing.parallel_jobs', parallel_jobs)
        if dry_run:
            config.update('processing.dry_run', True)
        if skip_existing:
            config.update('processing.skip_existing', True)
        if no_backup:
            config.update('processing.backup_originals', False)
        if verbose:
            config.update('logging.level', 'DEBUG')
        
        # Initialize processor
        processor = SEOImageProcessor()
        
        # Display configuration
        if not quiet:
            console.print(Panel.fit(
                f"[bold blue]SEO Image Converter[/bold blue]\n"
                f"Input: {input_directory}\n"
                f"Output: {output or input_directory}\n"
                f"Format: {config.get('image.formats.output', 'webp')}\n"
                f"Parallel Jobs: {processor.max_workers}\n"
                f"Dry Run: {'Yes' if dry_run else 'No'}",
                title="Configuration",
                border_style="blue"
            ))
        
        # Check Ollama availability
        if not processor.ai_analyzer.is_ollama_available():
            console.print(Panel.fit(
                "[yellow]⚠️  Ollama service not available. SEO naming will use fallback method.[/yellow]\n"
                "To enable AI-powered naming:\n"
                "1. Install Ollama: https://ollama.ai\n"
                "2. Start service: ollama serve\n"
                "3. Pull Qwen2.5-VL model: ollama pull qwen2.5vl:7b",
                title="AI Service Warning",
                border_style="yellow"
            ))
        
        # Find images
        image_paths = processor.find_images(input_directory)
        if not image_paths:
            console.print("[red]❌ No supported images found in input directory[/red]")
            sys.exit(1)
        
        # Process images with progress tracking
        progress_tracker = None
        if not quiet:
            progress_tracker = ProgressTracker(len(image_paths))
        
        def progress_callback(completed: int, total: int, result: ProcessingResult):
            if progress_tracker:
                progress_tracker.update(completed, total, result)
        
        # Run processing
        if progress_tracker:
            with progress_tracker:
                report = processor.process_directory(
                    input_directory, output, progress_callback
                )
        else:
            report = processor.process_directory(input_directory, output)
        
        # Display results
        if not quiet:
            console.print("\n")
            display_summary_report(report)
            console.print("\n")
            
            # Show errors first
            display_errors(report['detailed_results'])
            
            # Show detailed results
            display_detailed_results(report['detailed_results'], show_all=detailed)
        
        # Save JSON report if requested
        if json_output:
            with open(json_output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            console.print(f"\n[green]✅ Detailed report saved to: {json_output}[/green]")
        
        # Exit with appropriate code
        failed_count = report['summary']['failed']
        if failed_count > 0:
            console.print(f"\n[yellow]⚠️  Completed with {failed_count} failures[/yellow]")
            sys.exit(1)
        else:
            if not quiet:
                console.print("\n[green]🎉 All images processed successfully![/green]")
            sys.exit(0)
    
    except KeyboardInterrupt:
        console.print("\n[red]❌ Processing interrupted by user[/red]")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(f"\n[red]❌ Fatal error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()