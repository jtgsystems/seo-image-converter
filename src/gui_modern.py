"""Modern SEO Image Converter GUI using latest Dear PyGui 2.1.0 patterns."""

import os
import sys
import time
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

import dearpygui.dearpygui as dpg

from .processor import SEOImageProcessor
from .config import config
from .logger import logger

class SEOImageConverterGUI:
    """Modern SEO Image Converter using latest Dear PyGui 2.1.0 patterns."""
    
    def __init__(self):
        """Initialize with modern patterns and proper resource management."""
        self.processor = SEOImageProcessor()
        self.processing = False
        self.current_results = None
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="GUI-Worker")
        self.pending_futures = set()  # Track active futures for cleanup
        
        # Setup Dear PyGui with modern approach
        dpg.create_context()
        self._setup_themes()
        self._create_gui()
        self._setup_viewport()
    
    def _setup_themes(self):
        """Setup modern themes using latest 2.1.0 theming system."""
        # Modern dark theme
        with dpg.theme(tag="modern_theme"):
            with dpg.theme_component(dpg.mvAll):
                # 2025 dark theme colors
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (15, 15, 15, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (25, 25, 25, 255))
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (35, 35, 35, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (40, 40, 40, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (60, 60, 60, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (80, 80, 80, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 119, 200, 120))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 119, 200, 180))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 119, 200, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (0, 119, 200, 100))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (0, 119, 200, 150))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (0, 119, 200, 200))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))
                
                # Modern styling with larger font
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 15, 15)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 8)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8)
        
        # Add larger font for better readability
        with dpg.font_registry():
            # Load larger default font (16px instead of default 13px)
            try:
                large_font = dpg.add_font("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
                dpg.bind_font(large_font)
            except:
                # Fallback to system default if font loading fails
                logger.warning("Could not load custom font, using system default")
        
        # Success theme
        with dpg.theme(tag="success_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 127, 255))
        
        # Error theme
        with dpg.theme(tag="error_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 99, 71, 255))
        
        # Warning theme
        with dpg.theme(tag="warning_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 193, 7, 255))
        
        # Apply global theme
        dpg.bind_theme("modern_theme")
    
    def _setup_viewport(self):
        """Setup viewport with modern settings."""
        dpg.create_viewport(
            title="🚀 SEO Image Converter - AI-Powered 2025", 
            width=1200, 
            height=800,
            min_width=800,
            min_height=600,
            resizable=True,
            decorated=True
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
    
    def _create_gui(self):
        """Create modern GUI layout."""
        with dpg.window(tag="main_window"):
            
            # Header with modern styling
            self._create_header()
            
            # Main content with child windows for better organization
            with dpg.child_window(height=550, border=False):
                
                # Input section
                self._create_input_section()
                
                # Options section  
                self._create_options_section()
                
                # Progress section
                self._create_progress_section()
                
                # Control buttons
                self._create_control_section()
            
            # Results section in separate child window
            with dpg.child_window(height=-50, border=True, tag="results_section"):
                self._create_results_section()
            
            # Status bar
            self._create_status_bar()
        
        # Set as primary window
        dpg.set_primary_window("main_window", True)
        
        # Initialize status check
        self._check_ollama_status()
    
    def _create_header(self):
        """Create modern header section."""
        with dpg.group(horizontal=True):
            dpg.add_text("🚀 SEO Image Converter", color=(0, 119, 200))
            dpg.add_spacer(width=20)
            self.ollama_status = dpg.add_text("⚠️ Checking AI service...", color=(255, 193, 7))
        
        dpg.add_text("AI-Powered Image Optimization • Dear PyGui 2.1.0 • 2025", color=(150, 150, 150))
        dpg.add_separator()
    
    def _create_input_section(self):
        """Create input directory selection section."""
        with dpg.collapsing_header(label="📁 Input & Output Directories", default_open=True):
            
            # Input directory
            with dpg.group(horizontal=True):
                dpg.add_text("Input Directory:", width=120)
                self.input_dir = dpg.add_input_text(
                    hint="Select directory containing images...",
                    width=-150
                )
                dpg.add_button(
                    label="Browse",
                    callback=self._browse_input_directory,
                    width=130
                )
            
            dpg.add_spacer(height=8)
            
            # Output directory
            with dpg.group(horizontal=True):
                dpg.add_text("Output Directory:", width=120)
                self.output_dir = dpg.add_input_text(
                    hint="Leave empty to use input directory",
                    width=-150
                )
                dpg.add_button(
                    label="Browse",
                    callback=self._browse_output_directory,
                    width=130
                )
    
    def _create_options_section(self):
        """Create processing options section."""
        with dpg.collapsing_header(label="🎛️ Processing Options", default_open=True):
            
            # Format and quality controls
            with dpg.group(horizontal=True):
                dpg.add_text("Output Format:")
                self.format_combo = dpg.add_combo(
                    ["webp", "png", "jpeg"],
                    default_value="webp",
                    width=120
                )
                
                dpg.add_spacer(width=20)
                
                dpg.add_text("Quality:")
                self.quality_slider = dpg.add_slider_int(
                    min_value=50,
                    max_value=100,
                    default_value=85,
                    width=150,
                    callback=self._update_quality_label
                )
                
                self.quality_label = dpg.add_text("85")
            
            dpg.add_spacer(height=8)
            
            # Processing options
            with dpg.group(horizontal=True):
                self.backup_checkbox = dpg.add_checkbox(
                    label="💾 Backup originals",
                    default_value=True
                )
                
                dpg.add_spacer(width=20)
                
                self.skip_existing_checkbox = dpg.add_checkbox(
                    label="⏭️ Skip existing files",
                    default_value=False
                )
                
                dpg.add_spacer(width=20)
                
                self.dry_run_checkbox = dpg.add_checkbox(
                    label="🧪 Preview mode",
                    default_value=False
                )
    
    def _create_progress_section(self):
        """Create progress tracking section."""
        with dpg.collapsing_header(label="📈 Progress", default_open=True):
            
            self.progress_bar = dpg.add_progress_bar(
                overlay="Ready to process images...",
                width=-1,
                height=25
            )
            
            dpg.add_spacer(height=5)
            
            with dpg.group(horizontal=True):
                self.progress_text = dpg.add_text("Status: Ready")
                dpg.add_spacer(width=50)
                self.stats_text = dpg.add_text("")
    
    def _create_control_section(self):
        """Create control buttons section."""
        dpg.add_spacer(height=15)
        
        with dpg.group(horizontal=True):
            self.start_button = dpg.add_button(
                label="🚀 Start Processing",
                callback=self._start_processing,
                width=220,
                height=45
            )
            
            dpg.add_spacer(width=15)
            
            self.stop_button = dpg.add_button(
                label="⏹️ Stop",
                callback=self._stop_processing,
                width=120,
                height=45,
                enabled=False
            )
            
            dpg.add_spacer(width=15)
            
            dpg.add_button(
                label="📂 Open Output",
                callback=self._open_output_folder,
                width=160,
                height=45
            )
            
            dpg.add_spacer(width=15)
            
            dpg.add_button(
                label="💾 Export Results",
                callback=self._export_results,
                width=160,
                height=45
            )
    
    def _create_results_section(self):
        """Create results display section."""
        dpg.add_text("📊 Processing Results")
        
        # Summary stats
        with dpg.group(horizontal=True):
            self.total_files_text = dpg.add_text("Total: 0")
            dpg.add_spacer(width=20)
            self.processed_text = dpg.add_text("Processed: 0")
            dpg.bind_item_theme(self.processed_text, "success_theme")
            dpg.add_spacer(width=20)
            self.failed_text = dpg.add_text("Failed: 0")
            dpg.bind_item_theme(self.failed_text, "error_theme")
            dpg.add_spacer(width=20)
            self.savings_text = dpg.add_text("Saved: 0 MB")
        
        dpg.add_spacer(height=10)
        
        # Results table with modern styling
        with dpg.table(
            header_row=True,
            borders_innerH=True,
            borders_outerV=True,
            borders_innerV=False,
            height=-1,
            tag="results_table",
            scrollY=True
        ):
            dpg.add_table_column(label="Status", width_fixed=True, init_width_or_weight=60)
            dpg.add_table_column(label="Original File", width_stretch=True, init_width_or_weight=200)
            dpg.add_table_column(label="SEO Keywords", width_stretch=True, init_width_or_weight=300)
            dpg.add_table_column(label="Size Reduction", width_fixed=True, init_width_or_weight=120)
    
    def _create_status_bar(self):
        """Create modern status bar."""
        dpg.add_separator()
        
        with dpg.group(horizontal=True):
            self.status_text = dpg.add_text("Ready", color=(0, 119, 200))
            dpg.add_spacer(width=50)
            self.memory_text = dpg.add_text("Memory: 0 MB")
            dpg.add_spacer(width=50)
            dpg.add_text("v1.0.0 • 2025", color=(100, 100, 100))
    
    def _update_quality_label(self, sender, value):
        """Update quality label dynamically."""
        dpg.set_value(self.quality_label, str(value))
    
    def _retry_operation(self, func, max_retries=3, delay=1.0):
        """Retry operation with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"Retry {attempt + 1}/{max_retries} failed: {e}")
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
        
    def _check_ollama_status(self):
        """Check Ollama AI service status with thread-safe GUI updates and retry logic."""
        def check_status():
            try:
                # Use retry mechanism for robust status checking
                available = self._retry_operation(
                    lambda: self.processor.ai_analyzer.is_ollama_available(),
                    max_retries=2,
                    delay=0.5
                )
                
                # Thread-safe GUI update using callback
                def update_gui():
                    if available:
                        dpg.set_value(self.ollama_status, "✅ AI Service: Online")
                        dpg.bind_item_theme(self.ollama_status, "success_theme")
                    else:
                        dpg.set_value(self.ollama_status, "⚠️ AI Service: Offline")
                        dpg.bind_item_theme(self.ollama_status, "warning_theme")
                
                # Schedule GUI update on main thread
                if hasattr(dpg, 'split_frame'):
                    dpg.split_frame()
                update_gui()
                    
            except Exception as e:
                def update_error():
                    dpg.set_value(self.ollama_status, "❌ AI Service: Connection Failed")
                    dpg.bind_item_theme(self.ollama_status, "error_theme")
                
                if hasattr(dpg, 'split_frame'):
                    dpg.split_frame()
                update_error()
                logger.error(f"Ollama status check failed after retries: {e}")
        
        # Use thread pool executor with future tracking
        future = self.executor.submit(check_status)
        self.pending_futures.add(future)
        
        # Cleanup completed futures
        def cleanup_future(fut):
            self.pending_futures.discard(fut)
        future.add_done_callback(cleanup_future)
    
    def _browse_input_directory(self):
        """Browse for input directory - runs on main thread to avoid GUI conflicts."""
        try:
            # Use native file dialog on main thread
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            root.lift()  # Bring to front
            
            directory = filedialog.askdirectory(
                title="Select Input Directory",
                mustexist=True
            )
            root.destroy()
            
            if directory:
                dpg.set_value(self.input_dir, directory)
                logger.info(f"Input directory selected: {directory}")
                
        except Exception as e:
            logger.error(f"Directory selection error: {e}")
            self._show_modal_error("Directory Selection Error", str(e))
    
    def _browse_output_directory(self):
        """Browse for output directory - runs on main thread to avoid GUI conflicts."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            root.lift()  # Bring to front
            
            directory = filedialog.askdirectory(
                title="Select Output Directory",
                mustexist=True
            )
            root.destroy()
            
            if directory:
                dpg.set_value(self.output_dir, directory)
                logger.info(f"Output directory selected: {directory}")
                
        except Exception as e:
            logger.error(f"Directory selection error: {e}")
            self._show_modal_error("Directory Selection Error", str(e))
    
    def _start_processing(self):
        """Start image processing with modern error handling."""
        try:
            # Validate inputs
            input_dir = dpg.get_value(self.input_dir)
            if not input_dir:
                self._show_modal_error("Input Error", "Please select an input directory")
                return
            
            input_path = Path(input_dir)
            if not input_path.exists():
                self._show_modal_error("Path Error", "Input directory does not exist")
                return
            
            # Update configuration
            self._apply_settings()
            
            # Update UI state
            self.processing = True
            self._update_button_states()
            self._clear_results()
            
            # Get output directory
            output_dir_val = dpg.get_value(self.output_dir)
            output_path = Path(output_dir_val) if output_dir_val else None
            
            # Start processing in thread pool with future tracking
            future = self.executor.submit(self._process_images_thread, input_path, output_path)
            self.pending_futures.add(future)
            
            # Cleanup completed futures
            def cleanup_future(fut):
                self.pending_futures.discard(fut)
            future.add_done_callback(cleanup_future)
            
            logger.info("Processing started")
            dpg.set_value(self.status_text, "Processing...")
            
        except Exception as e:
            logger.error(f"Start processing error: {e}")
            self._show_modal_error("Processing Error", str(e))
    
    def _stop_processing(self):
        """Stop processing gracefully."""
        self.processing = False
        self._update_button_states()
        dpg.set_value(self.progress_text, "Status: Stopping...")
        dpg.set_value(self.status_text, "Stopped")
        logger.info("Processing stopped by user")
    
    def _apply_settings(self):
        """Apply current GUI settings to configuration."""
        try:
            format_val = dpg.get_value(self.format_combo)
            quality_val = dpg.get_value(self.quality_slider)
            
            config.update('image.formats.output', format_val)
            config.update(f'image.quality.{format_val}', quality_val)
            config.update('processing.backup_originals', dpg.get_value(self.backup_checkbox))
            config.update('processing.skip_existing', dpg.get_value(self.skip_existing_checkbox))
            config.update('processing.dry_run', dpg.get_value(self.dry_run_checkbox))
            
            # Recreate processor with new settings
            self.processor = SEOImageProcessor()
            
        except Exception as e:
            logger.error(f"Settings application error: {e}")
    
    def _process_images_thread(self, input_dir: Path, output_dir: Optional[Path]):
        """Process images in background thread with thread-safe GUI updates."""
        try:
            def progress_callback(completed, total, result):
                if not self.processing:
                    return
                
                # Thread-safe GUI updates
                def update_progress():
                    progress = completed / total if total > 0 else 0
                    dpg.set_value(self.progress_bar, progress)
                    
                    status_emoji = "✅" if result.success else "❌"
                    status_text = f"Status: {status_emoji} {result.input_path.name}"
                    dpg.set_value(self.progress_text, status_text)
                    
                    stats_text = f"Progress: {completed}/{total} ({progress*100:.0f}%)"
                    dpg.set_value(self.stats_text, stats_text)
                
                # Ensure GUI updates happen on main thread
                if hasattr(dpg, 'split_frame'):
                    dpg.split_frame()
                update_progress()
            
            # Process images
            report = self.processor.process_directory(input_dir, output_dir, progress_callback)
            
            if self.processing:  # Only complete if not cancelled
                # Thread-safe completion callback
                def complete_on_main_thread():
                    self._processing_complete(report)
                
                if hasattr(dpg, 'split_frame'):
                    dpg.split_frame()
                complete_on_main_thread()
            
        except Exception:
            if self.processing:
                # Thread-safe error callback
                def error_on_main_thread():
                    self._processing_error(str(e))
                
                if hasattr(dpg, 'split_frame'):
                    dpg.split_frame()
                error_on_main_thread()
    
    def _processing_complete(self, report: dict):
        """Handle processing completion with modern UI updates."""
        self.processing = False
        self.current_results = report
        self._update_button_states()
        
        # Update progress
        dpg.set_value(self.progress_bar, 1.0)
        dpg.configure_item(self.progress_bar, overlay="Processing Complete!")
        dpg.set_value(self.progress_text, "Status: ✅ Completed")
        dpg.set_value(self.status_text, "Complete")
        
        # Update summary
        summary = report['summary']
        size_analysis = report['size_analysis']
        
        dpg.set_value(self.total_files_text, f"Total: {summary['total_files']}")
        dpg.set_value(self.processed_text, f"Processed: {summary['processed']}")
        dpg.set_value(self.failed_text, f"Failed: {summary['failed']}")
        
        savings_mb = size_analysis['total_savings_bytes'] / 1024 / 1024
        compression = size_analysis['overall_compression_ratio']
        dpg.set_value(self.savings_text, f"Saved: {savings_mb:.1f} MB ({compression:.1f}%)")
        
        # Populate results table
        self._populate_results_table(report['detailed_results'])
        
        # Show completion notification
        if summary['failed'] == 0:
            self._show_modal_info("Success!", f"✅ Successfully processed {summary['processed']} images")
        else:
            self._show_modal_warning("Completed with Issues", 
                                   f"⚠️ Processed {summary['processed']} images with {summary['failed']} failures")
        
        logger.info("Processing completed successfully")
    
    def _processing_error(self, error: str):
        """Handle processing error."""
        self.processing = False
        self._update_button_states()
        
        dpg.set_value(self.progress_text, "Status: ❌ Error")
        dpg.set_value(self.status_text, "Error")
        
        self._show_modal_error("Processing Failed", error)
        logger.error(f"Processing failed: {error}")
    
    def _populate_results_table(self, results: List[dict]):
        """Populate results table with processed image data."""
        # Clear existing results
        if dpg.does_item_exist("results_table"):
            children = dpg.get_item_children("results_table", slot=1)
            if children:
                for child in children:
                    dpg.delete_item(child)
        
        # Add new results (limit to first 50 for better performance)
        for result in results[:50]:
            with dpg.table_row(parent="results_table"):
                
                # Status icon
                status = "✅" if result['success'] else "❌"
                status_cell = dpg.add_text(status)
                if result['success']:
                    dpg.bind_item_theme(status_cell, "success_theme")
                else:
                    dpg.bind_item_theme(status_cell, "error_theme")
                
                # Filename (truncated)
                filename = Path(result['input_file']).name
                if len(filename) > 30:
                    filename = filename[:27] + "..."
                dpg.add_text(filename)
                
                # SEO keywords (truncated)
                keywords = result.get('seo_keywords', 'N/A') or 'N/A'
                if len(keywords) > 40:
                    keywords = keywords[:37] + "..."
                dpg.add_text(keywords)
                
                # Size reduction
                if result['success']:
                    reduction = f"{result['compression_ratio']:.1f}%"
                    reduction_cell = dpg.add_text(reduction)
                    if result['compression_ratio'] > 0:
                        dpg.bind_item_theme(reduction_cell, "success_theme")
                else:
                    dpg.add_text("Failed")
    
    def _clear_results(self):
        """Clear previous results from display."""
        # Clear table
        if dpg.does_item_exist("results_table"):
            children = dpg.get_item_children("results_table", slot=1)
            if children:
                for child in children:
                    dpg.delete_item(child)
        
        # Reset displays
        dpg.set_value(self.progress_bar, 0.0)
        dpg.configure_item(self.progress_bar, overlay="Ready to process...")
        dpg.set_value(self.progress_text, "Status: Ready")
        dpg.set_value(self.stats_text, "")
        dpg.set_value(self.total_files_text, "Total: 0")
        dpg.set_value(self.processed_text, "Processed: 0")
        dpg.set_value(self.failed_text, "Failed: 0")
        dpg.set_value(self.savings_text, "Saved: 0 MB")
    
    def _update_button_states(self):
        """Update button states based on processing status."""
        dpg.configure_item(self.start_button, enabled=not self.processing)
        dpg.configure_item(self.stop_button, enabled=self.processing)
    
    def _open_output_folder(self):
        """Open output folder in system file manager."""
        def open_folder():
            try:
                output_dir = dpg.get_value(self.output_dir)
                if not output_dir:
                    output_dir = dpg.get_value(self.input_dir)
                
                if output_dir and Path(output_dir).exists():
                    import platform
                    
                    system = platform.system()
                    if system == "Linux":
                        os.system(f"xdg-open '{output_dir}'")
                    elif system == "Darwin":  # macOS
                        os.system(f"open '{output_dir}'")
                    elif system == "Windows":
                        os.startfile(output_dir)
                    else:
                        self._show_modal_warning("Unsupported OS", 
                                               f"Cannot open folder on {system}")
                else:
                    self._show_modal_warning("Folder Not Found", 
                                           "Output directory does not exist")
                    
            except Exception as e:
                logger.error(f"Open folder error: {e}")
                self._show_modal_error("Open Folder Error", str(e))
        
        future = self.executor.submit(open_folder)
        self.pending_futures.add(future)
        future.add_done_callback(lambda f: self.pending_futures.discard(f))
    
    def _export_results(self):
        """Export results to JSON file."""
        if not self.current_results:
            self._show_modal_warning("No Results", "No processing results to export")
            return
        
        def export():
            try:
                import tkinter as tk
                from tkinter import filedialog
                import json
                
                root = tk.Tk()
                root.withdraw()
                
                filename = filedialog.asksaveasfilename(
                    title="Export Results",
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
                )
                root.destroy()
                
                if filename:
                    with open(filename, 'w') as f:
                        json.dump(self.current_results, f, indent=2, default=str)
                    
                    self._show_modal_info("Export Successful", 
                                        f"Results exported to:\n{filename}")
                    logger.info(f"Results exported to: {filename}")
                    
            except Exception as e:
                logger.error(f"Export error: {e}")
                self._show_modal_error("Export Failed", str(e))
        
        future = self.executor.submit(export)
        self.pending_futures.add(future)
        future.add_done_callback(lambda f: self.pending_futures.discard(f))
    
    def _show_modal_error(self, title: str, message: str):
        """Show modern error modal."""
        with dpg.window(label=title, modal=True, width=450, height=200, 
                       pos=[400, 300], tag=f"error_modal_{time.time()}"):
            dpg.add_text(message, color=(255, 99, 71), wrap=420)
            dpg.add_separator()
            dpg.add_spacer(height=10)
            dpg.add_button(
                label="OK",
                callback=lambda: dpg.delete_item(dpg.last_container()),
                width=-1,
                height=35
            )
    
    def _show_modal_warning(self, title: str, message: str):
        """Show modern warning modal."""
        with dpg.window(label=title, modal=True, width=450, height=200,
                       pos=[400, 300], tag=f"warning_modal_{time.time()}"):
            dpg.add_text(message, color=(255, 193, 7), wrap=420)
            dpg.add_separator()
            dpg.add_spacer(height=10)
            dpg.add_button(
                label="OK",
                callback=lambda: dpg.delete_item(dpg.last_container()),
                width=-1,
                height=35
            )
    
    def _show_modal_info(self, title: str, message: str):
        """Show modern info modal."""
        with dpg.window(label=title, modal=True, width=450, height=200,
                       pos=[400, 300], tag=f"info_modal_{time.time()}"):
            dpg.add_text(message, color=(0, 255, 127), wrap=420)
            dpg.add_separator()
            dpg.add_spacer(height=10)
            dpg.add_button(
                label="OK",
                callback=lambda: dpg.delete_item(dpg.last_container()),
                width=-1,
                height=35
            )
    
    def run(self):
        """Run the application with modern loop."""
        try:
            # Modern DPG render loop
            while dpg.is_dearpygui_running():
                dpg.render_dearpygui_frame()
                
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application runtime error: {e}")
        finally:
            # Graceful shutdown with proper resource cleanup
            self.processing = False
            
            # Cancel pending futures
            for future in list(self.pending_futures):
                future.cancel()
            
            # Wait for executor shutdown with timeout
            try:
                self.executor.shutdown(wait=True, timeout=5.0)
            except:
                logger.warning("Forced executor shutdown after timeout")
            
            dpg.destroy_context()

def main():
    """Main entry point with modern error handling."""
    try:
        app = SEOImageConverterGUI()
        app.run()
    except Exception as e:
        print(f"Application startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()