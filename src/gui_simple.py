"""Simple working GUI using Dear PyGui - Latest 2025 Framework."""

import os
import threading
from pathlib import Path
from typing import Optional

import dearpygui.dearpygui as dpg

from .processor import SEOImageProcessor
from .config import config
from .logger import logger

class SEOImageConverterGUI:
    """Simple SEO Image Converter GUI using Dear PyGui."""
    
    def __init__(self):
        """Initialize the application."""
        self.processor = SEOImageProcessor()
        self.processing = False
        self.current_results = None
        
        # Setup Dear PyGui
        dpg.create_context()
        self._create_gui()
        
        # Create and setup viewport
        dpg.create_viewport(
            title="SEO Image Converter - AI-Powered Optimization (2025)", 
            width=1000, 
            height=700
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
    
    def _create_gui(self):
        """Create the main GUI."""
        with dpg.window(label="SEO Image Converter", tag="main_window"):
            
            # Header
            dpg.add_text("🚀 SEO Image Converter - Latest 2025 Framework", color=[66, 150, 250])
            dpg.add_text("AI-Powered Image Optimization with Qwen2.5-VL + Dear PyGui 2.1.0", color=[100, 100, 100])
            dpg.add_separator()
            
            # Status
            self.ollama_status = dpg.add_text("⚠️ Checking AI service...", color=[255, 193, 7])
            dpg.add_separator()
            
            # File selection
            dpg.add_text("📁 Input Directory:")
            with dpg.group(horizontal=True):
                self.input_dir = dpg.add_input_text(
                    hint="Select directory containing images...", 
                    width=600
                )
                dpg.add_button(
                    label="Browse", 
                    callback=self._browse_input_directory
                )
            
            dpg.add_spacer(height=10)
            
            dpg.add_text("💾 Output Directory (optional):")
            with dpg.group(horizontal=True):
                self.output_dir = dpg.add_input_text(
                    hint="Leave empty to use input directory", 
                    width=600
                )
                dpg.add_button(
                    label="Browse", 
                    callback=self._browse_output_directory
                )
            
            dpg.add_separator()
            
            # Options
            dpg.add_text("🎛️ Processing Options:")
            
            with dpg.group(horizontal=True):
                dpg.add_text("Format:")
                self.format_combo = dpg.add_combo(
                    ["webp", "png", "jpeg"], 
                    default_value="webp",
                    width=100
                )
                
                dpg.add_text("Quality:")
                self.quality_slider = dpg.add_slider_int(
                    min_value=50,
                    max_value=100, 
                    default_value=85,
                    width=150
                )
                
                self.quality_label = dpg.add_text("85")
            
            # Checkboxes
            with dpg.group(horizontal=True):
                self.backup_checkbox = dpg.add_checkbox(
                    label="💾 Backup originals", 
                    default_value=True
                )
                self.skip_existing_checkbox = dpg.add_checkbox(
                    label="⏭️ Skip existing", 
                    default_value=False
                )
                self.dry_run_checkbox = dpg.add_checkbox(
                    label="🧪 Dry run", 
                    default_value=False
                )
            
            dpg.add_separator()
            
            # Progress
            dpg.add_text("📈 Progress:")
            self.progress_bar = dpg.add_progress_bar(
                overlay="Ready to process images...",
                width=-1
            )
            
            self.progress_text = dpg.add_text("Status: Ready")
            
            # Control buttons
            dpg.add_spacer(height=10)
            
            with dpg.group(horizontal=True):
                self.start_button = dpg.add_button(
                    label="🚀 Start Processing",
                    callback=self._start_processing,
                    width=200,
                    height=40
                )
                
                self.stop_button = dpg.add_button(
                    label="⏹️ Stop", 
                    callback=self._stop_processing,
                    width=100,
                    height=40,
                    enabled=False
                )
                
                dpg.add_button(
                    label="📂 Open Output Folder",
                    callback=self._open_output_folder,
                    width=180,
                    height=40
                )
            
            # Results section  
            dpg.add_separator()
            dpg.add_text("📊 Results:")
            
            # Summary
            with dpg.group(horizontal=True):
                self.total_files_text = dpg.add_text("Total: 0")
                self.processed_text = dpg.add_text("Processed: 0", color=[0, 255, 127])
                self.failed_text = dpg.add_text("Failed: 0", color=[255, 99, 71])
                self.savings_text = dpg.add_text("Savings: 0 MB", color=[66, 150, 250])
            
            # Results table (simplified)
            with dpg.table(
                header_row=True,
                borders_innerH=True,
                borders_outerV=True,
                height=200,
                tag="results_table"
            ):
                dpg.add_table_column(label="Status")
                dpg.add_table_column(label="File")
                dpg.add_table_column(label="Keywords")
                dpg.add_table_column(label="Savings")
        
        # Set main window as primary
        dpg.set_primary_window("main_window", True)
        
        # Check Ollama status
        self._check_ollama_status()
    
    def _check_ollama_status(self):
        """Check Ollama AI service status."""
        def check():
            try:
                available = self.processor.ai_analyzer.is_ollama_available()
                if available:
                    dpg.set_value(self.ollama_status, "✅ Ollama AI Service: Connected")
                    dpg.configure_item(self.ollama_status, color=[0, 255, 127])
                else:
                    dpg.set_value(self.ollama_status, "⚠️ Ollama AI Service: Disconnected")
                    dpg.configure_item(self.ollama_status, color=[255, 193, 7])
            except Exception as e:
                dpg.set_value(self.ollama_status, "❌ Ollama AI Service: Error")
                dpg.configure_item(self.ollama_status, color=[255, 99, 71])
                logger.error(f"Error checking Ollama status: {e}")
        
        threading.Thread(target=check, daemon=True).start()
    
    def _browse_input_directory(self):
        """Browse for input directory."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            directory = filedialog.askdirectory(title="Select Input Directory")
            root.destroy()
            
            if directory:
                dpg.set_value(self.input_dir, directory)
                logger.info(f"Selected input directory: {directory}")
                
        except Exception as e:
            logger.error(f"Error selecting directory: {e}")
    
    def _browse_output_directory(self):
        """Browse for output directory."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            directory = filedialog.askdirectory(title="Select Output Directory")
            root.destroy()
            
            if directory:
                dpg.set_value(self.output_dir, directory)
                logger.info(f"Selected output directory: {directory}")
                
        except Exception as e:
            logger.error(f"Error selecting directory: {e}")
    
    def _start_processing(self):
        """Start image processing."""
        try:
            input_dir = dpg.get_value(self.input_dir)
            if not input_dir:
                self._show_error("Please select an input directory")
                return
            
            input_path = Path(input_dir)
            if not input_path.exists():
                self._show_error("Input directory does not exist")
                return
            
            # Update configuration
            config.update('image.formats.output', dpg.get_value(self.format_combo))
            config.update(f'image.quality.{dpg.get_value(self.format_combo)}', dpg.get_value(self.quality_slider))
            config.update('processing.backup_originals', dpg.get_value(self.backup_checkbox))
            config.update('processing.skip_existing', dpg.get_value(self.skip_existing_checkbox))
            config.update('processing.dry_run', dpg.get_value(self.dry_run_checkbox))
            
            # Update processor
            self.processor = SEOImageProcessor()
            
            # Update UI state
            self.processing = True
            dpg.configure_item(self.start_button, enabled=False)
            dpg.configure_item(self.stop_button, enabled=True)
            
            # Clear previous results
            self._clear_results()
            
            # Get output directory
            output_dir_val = dpg.get_value(self.output_dir)
            output_path = Path(output_dir_val) if output_dir_val else None
            
            # Start processing thread
            threading.Thread(
                target=self._process_images_thread,
                args=(input_path, output_path),
                daemon=True
            ).start()
            
            logger.info("Started image processing")
            
        except Exception as e:
            logger.error(f"Error starting processing: {e}")
            self._show_error(f"Failed to start processing: {e}")
    
    def _stop_processing(self):
        """Stop processing."""
        self.processing = False
        dpg.configure_item(self.start_button, enabled=True)
        dpg.configure_item(self.stop_button, enabled=False)
        dpg.set_value(self.progress_text, "Status: Stopped by user")
    
    def _process_images_thread(self, input_dir: Path, output_dir: Optional[Path]):
        """Process images in background thread."""
        try:
            def progress_callback(completed, total, result):
                if not self.processing:
                    return
                
                progress = completed / total if total > 0 else 0
                dpg.set_value(self.progress_bar, progress)
                
                status_emoji = "✅" if result.success else "❌"
                status_text = f"Status: {status_emoji} {result.input_path.name} ({completed}/{total})"
                dpg.set_value(self.progress_text, status_text)
            
            # Process images
            report = self.processor.process_directory(input_dir, output_dir, progress_callback)
            
            if self.processing:  # Only update if not cancelled
                self._processing_complete(report)
            
        except Exception as e:
            if self.processing:
                self._processing_error(str(e))
    
    def _processing_complete(self, report: dict):
        """Handle processing completion."""
        self.processing = False
        self.current_results = report
        
        dpg.configure_item(self.start_button, enabled=True)
        dpg.configure_item(self.stop_button, enabled=False)
        
        dpg.set_value(self.progress_bar, 1.0)
        dpg.set_value(self.progress_text, "Status: ✅ Complete!")
        
        # Update summary
        summary = report['summary']
        size_analysis = report['size_analysis']
        
        dpg.set_value(self.total_files_text, f"Total: {summary['total_files']}")
        dpg.set_value(self.processed_text, f"Processed: {summary['processed']}")
        dpg.set_value(self.failed_text, f"Failed: {summary['failed']}")
        
        savings_mb = size_analysis['total_savings_bytes'] / 1024 / 1024
        dpg.set_value(self.savings_text, f"Savings: {savings_mb:.1f} MB ({size_analysis['overall_compression_ratio']:.1f}%)")
        
        # Add some results to table
        results = report['detailed_results'][:10]  # Show first 10
        
        for result in results:
            with dpg.table_row(parent="results_table"):
                status = "✅" if result['success'] else "❌"
                dpg.add_text(status)
                
                filename = Path(result['input_file']).name
                if len(filename) > 25:
                    filename = filename[:22] + "..."
                dpg.add_text(filename)
                
                keywords = result.get('seo_keywords', 'N/A') or 'N/A'
                if len(keywords) > 30:
                    keywords = keywords[:27] + "..."
                dpg.add_text(keywords)
                
                savings = f"{result['compression_ratio']:.1f}%" if result['success'] else "N/A"
                dpg.add_text(savings)
        
        # Show completion message
        if summary['failed'] == 0:
            self._show_info(f"✅ Successfully processed {summary['processed']} images!")
        else:
            self._show_info(f"⚠️ Processed {summary['processed']} images with {summary['failed']} failures")
        
        logger.info("Processing completed")
    
    def _processing_error(self, error: str):
        """Handle processing error."""
        self.processing = False
        dpg.configure_item(self.start_button, enabled=True)
        dpg.configure_item(self.stop_button, enabled=False)
        
        dpg.set_value(self.progress_text, "Status: ❌ Error")
        self._show_error(f"Processing failed: {error}")
        
        logger.error(f"Processing failed: {error}")
    
    def _clear_results(self):
        """Clear previous results."""
        # Clear table
        if dpg.does_item_exist("results_table"):
            children = dpg.get_item_children("results_table", slot=1)
            if children:
                for child in children:
                    dpg.delete_item(child)
        
        # Reset display
        dpg.set_value(self.progress_bar, 0.0)
        dpg.set_value(self.progress_text, "Status: Starting...")
        dpg.set_value(self.total_files_text, "Total: 0")
        dpg.set_value(self.processed_text, "Processed: 0")
        dpg.set_value(self.failed_text, "Failed: 0")
        dpg.set_value(self.savings_text, "Savings: 0 MB")
    
    def _open_output_folder(self):
        """Open output folder."""
        try:
            output_dir = dpg.get_value(self.output_dir)
            if not output_dir:
                output_dir = dpg.get_value(self.input_dir)
            
            if output_dir and Path(output_dir).exists():
                import platform
                if platform.system() == "Linux":
                    os.system(f"xdg-open '{output_dir}'")
                elif platform.system() == "Darwin":
                    os.system(f"open '{output_dir}'")
                else:
                    os.startfile(output_dir)
            else:
                self._show_error("Output directory not found")
                
        except Exception as e:
            logger.error(f"Error opening folder: {e}")
            self._show_error(f"Failed to open folder: {e}")
    
    def _show_error(self, message: str):
        """Show error popup."""
        with dpg.window(label="Error", modal=True, width=400, height=150, pos=[300, 250]):
            dpg.add_text(message, color=[255, 99, 71])
            dpg.add_separator()
            dpg.add_button(
                label="OK", 
                callback=lambda: dpg.delete_item(dpg.last_container()), 
                width=-1
            )
    
    def _show_info(self, message: str):
        """Show info popup."""
        with dpg.window(label="Information", modal=True, width=400, height=150, pos=[300, 250]):
            dpg.add_text(message, color=[0, 255, 127])
            dpg.add_separator()
            dpg.add_button(
                label="OK", 
                callback=lambda: dpg.delete_item(dpg.last_container()), 
                width=-1
            )
    
    def run(self):
        """Run the application."""
        try:
            dpg.start_dearpygui()
        finally:
            dpg.destroy_context()

def main():
    """Main entry point."""
    try:
        app = SEOImageConverterGUI()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()