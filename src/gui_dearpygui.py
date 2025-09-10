"""Modern GUI interface using Dear PyGui - Latest 2025 Framework."""

import os
import sys
import threading
import time
import json
from pathlib import Path
from typing import Optional, List, Dict, Callable
import traceback

import dearpygui.dearpygui as dpg
from PIL import Image

from .processor import SEOImageProcessor, ProcessingResult
from .config import config
from .logger import logger

class SEOImageConverterGUI:
    """Modern GUI using Dear PyGui - Latest 2025 Python GUI Framework."""
    
    def __init__(self):
        """Initialize the Dear PyGui application."""
        
        # Application state
        self.processor = SEOImageProcessor()
        self.processing = False
        self.current_results = None
        self.selected_directory = None
        self.output_directory = None
        self.processing_thread = None
        
        # GUI state
        self.progress_value = 0.0
        self.total_files = 0
        self.processed_files = 0
        
        # Initialize Dear PyGui
        self._setup_dpg()
        
    def _setup_dpg(self):
        """Setup Dear PyGui context and styling."""
        dpg.create_context()
        
        # Configure Dear PyGui for high DPI
        dpg.configure_app(docking=True, docking_space=True)
        
        # Create fonts (skip fonts for now to avoid loading issues)
        # with dpg.font_registry():
        #     self.default_font = dpg.add_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        #     self.header_font = dpg.add_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            
        # Setup themes
        self._setup_theme()
        
        # Create main window
        self._create_main_window()
        
        # Create viewport
        dpg.create_viewport(
            title="SEO Image Converter - AI-Powered Optimization", 
            width=1200, 
            height=800,
            min_width=800,
            min_height=600
        )
        
        # Setup Dear PyGui
        dpg.setup_dearpygui()
        
        # Set primary window
        dpg.set_primary_window("main_window", True)
        # dpg.bind_font(self.default_font)  # Skip font binding for now
    
    def _setup_theme(self):
        """Setup modern dark theme with SEO branding colors."""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                # Dark theme colors
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (23, 23, 23, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (30, 30, 30, 255))
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (40, 40, 40, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (45, 45, 48, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (66, 66, 69, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (85, 85, 89, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (16, 29, 44, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (30, 55, 85, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (20, 20, 20, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (80, 80, 83, 255))
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (66, 150, 250, 255))
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (66, 150, 250, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (66, 150, 250, 100))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (66, 150, 250, 150))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (66, 150, 250, 200))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (66, 150, 250, 79))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (66, 150, 250, 128))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (66, 150, 250, 171))
                dpg.add_theme_color(dpg.mvThemeCol_Tab, (58, 58, 58, 220))
                dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (100, 100, 100, 220))
                dpg.add_theme_color(dpg.mvThemeCol_TabActive, (66, 150, 250, 220))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))
                
                # Modern spacing and styling
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 6, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 14)
                dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 12)
                
        # Success theme for completed items
        with dpg.theme(tag="success_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 127, 255))
                
        # Error theme for failed items
        with dpg.theme(tag="error_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 99, 71, 255))
                
        # Warning theme  
        with dpg.theme(tag="warning_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 193, 7, 255))
        
        dpg.bind_theme(global_theme)
    
    def _create_main_window(self):
        """Create the main application window."""
        with dpg.window(tag="main_window", label="SEO Image Converter"):
            
            # Header section
            self._create_header()
            
            # Main content with tabs
            with dpg.tab_bar(tag="main_tabs"):
                
                # Processing tab
                with dpg.tab(label="🔄 Process Images", tag="process_tab"):
                    self._create_process_tab()
                
                # Results tab
                with dpg.tab(label="📊 Results", tag="results_tab"):
                    self._create_results_tab()
                    
                # Settings tab
                with dpg.tab(label="⚙️ Settings", tag="settings_tab"):
                    self._create_settings_tab()
                
                # Logs tab
                with dpg.tab(label="📋 Logs", tag="logs_tab"):
                    self._create_logs_tab()
            
            # Status bar
            self._create_status_bar()
    
    def _create_header(self):
        """Create application header."""
        with dpg.group(horizontal=True):
            dpg.add_text("🚀 SEO Image Converter", color=(66, 150, 250))
            # dpg.bind_item_font(dpg.last_item(), self.header_font)  # Skip font binding
            
            dpg.add_spacer(width=50)
            
            # Ollama status indicator
            self.ollama_status = dpg.add_text("⚠️ Checking AI service...", color=(255, 193, 7))
            
        dpg.add_separator()
        
        # Check Ollama status
        self._check_ollama_status()
    
    def _create_process_tab(self):
        """Create the main processing interface."""
        
        # Directory selection
        with dpg.collapsing_header(label="📁 Directory Selection", default_open=True):
            
            with dpg.group(horizontal=True):
                dpg.add_text("Input Directory:")
                dpg.add_same_line(spacing=20)
                self.input_dir_text = dpg.add_input_text(
                    hint="Select or drag & drop image directory...",
                    width=-150
                )
                dpg.add_button(
                    label="Browse", 
                    callback=self._browse_input_directory,
                    width=130
                )
            
            dpg.add_spacer(height=5)
            
            with dpg.group(horizontal=True):
                dpg.add_text("Output Directory:")
                dpg.add_same_line(spacing=10)
                self.output_dir_text = dpg.add_input_text(
                    hint="(Same as input if empty)",
                    width=-150
                )
                dpg.add_button(
                    label="Browse", 
                    callback=self._browse_output_directory,
                    width=130
                )
        
        # Processing options
        with dpg.collapsing_header(label="🎛️ Processing Options", default_open=True):
            
            with dpg.table(header_row=False, borders_innerH=True, borders_outerH=False, 
                          borders_innerV=False, borders_outerV=False):
                
                dpg.add_table_column()
                dpg.add_table_column()
                dpg.add_table_column()
                
                with dpg.table_row():
                    dpg.add_text("🖼️ Output Format:")
                    self.format_combo = dpg.add_combo(
                        items=["webp", "png", "jpeg"],
                        default_value="webp",
                        width=100
                    )
                    dpg.add_spacer()
                
                with dpg.table_row():
                    dpg.add_text("🎚️ Quality:")
                    self.quality_slider = dpg.add_slider_int(
                        min_value=50,
                        max_value=100,
                        default_value=85,
                        width=150,
                        callback=self._update_quality_label
                    )
                    self.quality_label = dpg.add_text("85")
                
                with dpg.table_row():
                    dpg.add_text("🔧 Parallel Jobs:")
                    self.parallel_jobs = dpg.add_slider_int(
                        min_value=1,
                        max_value=16,
                        default_value=self.processor.max_workers,
                        width=150
                    )
                    dpg.add_text(f"(Auto: {self.processor.max_workers})")
            
            dpg.add_separator()
            
            # Checkboxes
            with dpg.group(horizontal=True):
                self.backup_checkbox = dpg.add_checkbox(label="💾 Backup originals", default_value=True)
                dpg.add_same_line(spacing=30)
                self.skip_existing_checkbox = dpg.add_checkbox(label="⏭️ Skip existing files", default_value=False)
                dpg.add_same_line(spacing=30)
                self.dry_run_checkbox = dpg.add_checkbox(label="🧪 Dry run (preview)", default_value=False)
        
        # Progress section
        with dpg.collapsing_header(label="📈 Progress", default_open=True):
            
            self.progress_bar = dpg.add_progress_bar(
                overlay="Ready to process images...",
                width=-1,
                height=25
            )
            
            dpg.add_spacer(height=5)
            
            with dpg.group(horizontal=True):
                self.progress_text = dpg.add_text("Status: Ready")
                dpg.add_same_line()
                self.stats_text = dpg.add_text("", pos=[400, 0])
        
        # Control buttons
        dpg.add_spacer(height=10)
        
        with dpg.group(horizontal=True):
            self.start_button = dpg.add_button(
                label="🚀 Start Processing",
                callback=self._start_processing,
                width=200,
                height=40
            )
            
            dpg.add_same_line(spacing=20)
            
            self.stop_button = dpg.add_button(
                label="⏹️ Stop Processing",
                callback=self._stop_processing,
                width=150,
                height=40,
                enabled=False
            )
            
            dpg.add_same_line(spacing=20)
            
            dpg.add_button(
                label="📂 Open Output Folder",
                callback=self._open_output_folder,
                width=180,
                height=40
            )
    
    def _create_results_tab(self):
        """Create results viewing interface."""
        
        # Results summary
        with dpg.collapsing_header(label="📊 Summary", default_open=True):
            
            with dpg.table(header_row=True, borders_innerV=True):
                dpg.add_table_column(label="Metric", width_fixed=True, init_width_or_weight=150)
                dpg.add_table_column(label="Value", width_stretch=True)
                
                # Placeholder rows - will be updated dynamically
                with dpg.table_row():
                    dpg.add_text("Total Files")
                    self.total_files_text = dpg.add_text("0")
                
                with dpg.table_row():
                    dpg.add_text("Processed")
                    self.processed_text = dpg.add_text("0", color=(0, 255, 127))
                
                with dpg.table_row():
                    dpg.add_text("Failed")
                    self.failed_text = dpg.add_text("0", color=(255, 99, 71))
                
                with dpg.table_row():
                    dpg.add_text("Total Savings")
                    self.savings_text = dpg.add_text("0 MB")
                
                with dpg.table_row():
                    dpg.add_text("Compression Ratio")
                    self.compression_text = dpg.add_text("0%")
        
        # Detailed results table
        with dpg.collapsing_header(label="📋 Detailed Results", default_open=True):
            
            with dpg.table(
                header_row=True, 
                borders_innerV=True, 
                borders_outerV=True,
                scrollY=True,
                height=300,
                tag="results_table"
            ):
                dpg.add_table_column(label="Status", width_fixed=True, init_width_or_weight=60)
                dpg.add_table_column(label="Input File", width_fixed=True, init_width_or_weight=200)
                dpg.add_table_column(label="SEO Keywords", width_fixed=True, init_width_or_weight=250)
                dpg.add_table_column(label="Original Size", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="New Size", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Savings", width_fixed=True, init_width_or_weight=80)
        
        # Export options
        dpg.add_spacer(height=10)
        
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="📄 Export Results (JSON)",
                callback=self._export_results_json,
                width=200
            )
            
            dpg.add_same_line(spacing=20)
            
            dpg.add_button(
                label="📊 Export Results (CSV)",
                callback=self._export_results_csv,
                width=200
            )
    
    def _create_settings_tab(self):
        """Create settings interface."""
        
        with dpg.collapsing_header(label="🤖 AI Configuration", default_open=True):
            
            dpg.add_text("Ollama Endpoint:")
            dpg.add_input_text(
                default_value=config.ollama.get('endpoint', 'http://localhost:11434/api/generate'),
                width=-1,
                tag="ollama_endpoint"
            )
            
            dpg.add_spacer(height=5)
            
            dpg.add_text("LLaVA Model:")
            dpg.add_combo(
                items=["llava:latest", "llava:7b", "llava:13b", "llava:34b"],
                default_value=config.ollama.get('model', 'llava:latest'),
                width=-1,
                tag="llava_model"
            )
            
            dpg.add_spacer(height=5)
            
            dpg.add_text("SEO Keywords Count:")
            dpg.add_slider_int(
                min_value=5,
                max_value=15,
                default_value=config.seo.get('keyword_count', 8),
                width=-1,
                tag="seo_keywords"
            )
        
        with dpg.collapsing_header(label="🖼️ Image Processing", default_open=True):
            
            dpg.add_text("Maximum Image Dimension:")
            dpg.add_input_int(
                default_value=config.image.get('optimization', {}).get('max_dimension', 1920),
                width=-1,
                tag="max_dimension"
            )
            
            dpg.add_spacer(height=5)
            
            dpg.add_checkbox(
                label="Strip Metadata",
                default_value=config.image.get('optimization', {}).get('strip_metadata', True),
                tag="strip_metadata"
            )
            
            dpg.add_checkbox(
                label="Progressive JPEG",
                default_value=config.image.get('optimization', {}).get('progressive', True),
                tag="progressive_jpeg"
            )
        
        dpg.add_spacer(height=20)
        
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="💾 Save Settings",
                callback=self._save_settings,
                width=150
            )
            
            dpg.add_same_line(spacing=20)
            
            dpg.add_button(
                label="🔄 Reset to Defaults",
                callback=self._reset_settings,
                width=150
            )
    
    def _create_logs_tab(self):
        """Create logs viewing interface."""
        
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="🗑️ Clear Logs",
                callback=self._clear_logs,
                width=100
            )
            
            dpg.add_same_line(spacing=10)
            
            dpg.add_button(
                label="💾 Save Logs",
                callback=self._save_logs,
                width=100
            )
            
            dpg.add_same_line(spacing=10)
            
            self.auto_scroll_checkbox = dpg.add_checkbox(
                label="Auto Scroll",
                default_value=True
            )
        
        dpg.add_spacer(height=5)
        
        # Log text area (using child window for better scrolling)
        with dpg.child_window(height=-1, border=True, tag="logs_window"):
            self.log_text = dpg.add_text("Application logs will appear here...", wrap=-1)
    
    def _create_status_bar(self):
        """Create status bar at bottom."""
        dpg.add_separator()
        
        with dpg.group(horizontal=True):
            self.status_text = dpg.add_text("Ready", color=(66, 150, 250))
            
            dpg.add_same_line()
            dpg.add_spacer(width=50)
            
            # Memory usage indicator  
            self.memory_text = dpg.add_text("Memory: 0 MB", pos=[300, 0])
            
            dpg.add_same_line()
            dpg.add_spacer(width=100)
            
            # Version info
            dpg.add_text("v1.0.0", pos=[500, 0], color=(128, 128, 128))
    
    def _check_ollama_status(self):
        """Check Ollama service status."""
        def check_status():
            try:
                available = self.processor.ai_analyzer.is_ollama_available()
                
                if available:
                    dpg.set_value(self.ollama_status, "✅ AI Service: Connected")
                    dpg.configure_item(self.ollama_status, color=(0, 255, 127))
                else:
                    dpg.set_value(self.ollama_status, "⚠️ AI Service: Disconnected")
                    dpg.configure_item(self.ollama_status, color=(255, 193, 7))
                    
            except Exception as e:
                logger.error(f"Error checking Ollama status: {e}")
                dpg.set_value(self.ollama_status, "❌ AI Service: Error")
                dpg.configure_item(self.ollama_status, color=(255, 99, 71))
        
        # Check status in background thread
        threading.Thread(target=check_status, daemon=True).start()
    
    def _update_quality_label(self, sender, value):
        """Update quality label when slider changes."""
        dpg.set_value(self.quality_label, str(value))
    
    def _browse_input_directory(self):
        """Browse for input directory."""
        try:
            # Use system dialog (Dear PyGui file dialogs are more complex)
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            
            directory = filedialog.askdirectory(title="Select Input Directory")
            root.destroy()
            
            if directory:
                dpg.set_value(self.input_dir_text, directory)
                self.selected_directory = Path(directory)
                logger.info(f"Selected input directory: {directory}")
                
        except Exception as e:
            logger.error(f"Error selecting input directory: {e}")
            self._show_error("Error", f"Failed to open directory selector:\n{e}")
    
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
                dpg.set_value(self.output_dir_text, directory)
                self.output_directory = Path(directory)
                logger.info(f"Selected output directory: {directory}")
                
        except Exception as e:
            logger.error(f"Error selecting output directory: {e}")
            self._show_error("Error", f"Failed to open directory selector:\n{e}")
    
    def _start_processing(self):
        """Start image processing."""
        try:
            # Validate input
            input_dir = dpg.get_value(self.input_dir_text)
            if not input_dir:
                self._show_error("Error", "Please select an input directory")
                return
            
            input_path = Path(input_dir)
            if not input_path.exists():
                self._show_error("Error", "Input directory does not exist")
                return
            
            # Update configuration
            self._apply_settings()
            
            # Update UI state
            self.processing = True
            self._update_button_states()
            
            # Clear previous results
            self._clear_results()
            
            # Get output directory
            output_dir = dpg.get_value(self.output_dir_text)
            output_path = Path(output_dir) if output_dir else None
            
            # Start processing thread
            self.processing_thread = threading.Thread(
                target=self._process_images_thread,
                args=(input_path, output_path),
                daemon=True
            )
            self.processing_thread.start()
            
            logger.info("Started image processing")
            
        except Exception as e:
            logger.error(f"Error starting processing: {e}")
            self._show_error("Error", f"Failed to start processing:\n{e}")
    
    def _stop_processing(self):
        """Stop image processing."""
        self.processing = False
        self._update_button_states()
        
        dpg.set_value(self.progress_text, "Status: Stopping...")
        dpg.configure_item(self.progress_bar, overlay="Stopping processing...")
        
        logger.info("Processing stopped by user")
    
    def _process_images_thread(self, input_dir: Path, output_dir: Optional[Path]):
        """Process images in background thread."""
        try:
            def progress_callback(completed: int, total: int, result: ProcessingResult):
                if not self.processing:
                    return
                
                # Update progress
                progress = completed / total if total > 0 else 0
                
                # Schedule UI update on main thread
                dpg.set_value(self.progress_bar, progress)
                
                status_emoji = "✅" if result.success else "❌"
                status_text = f"Status: {status_emoji} {result.input_path.name} ({completed}/{total})"
                dpg.set_value(self.progress_text, status_text)
                
                overlay_text = f"Processing: {completed}/{total} ({progress*100:.0f}%)"
                dpg.configure_item(self.progress_bar, overlay=overlay_text)
                
                # Update stats
                if completed > 0:
                    stats = f"Processed: {completed} | Remaining: {total - completed}"
                    dpg.set_value(self.stats_text, stats)
            
            # Process images
            report = self.processor.process_directory(input_dir, output_dir, progress_callback)
            
            # Update UI with results
            self._processing_complete(report)
            
        except Exception as e:
            logger.error(f"Processing thread failed: {e}")
            logger.error(traceback.format_exc())
            self._processing_error(str(e))
    
    def _processing_complete(self, report: dict):
        """Handle processing completion."""
        self.processing = False
        self.current_results = report
        self._update_button_states()
        
        # Update progress
        dpg.set_value(self.progress_bar, 1.0)
        dpg.configure_item(self.progress_bar, overlay="Processing Complete!")
        dpg.set_value(self.progress_text, "Status: ✅ Complete")
        
        # Update results
        self._update_results_display(report)
        
        # Switch to results tab
        dpg.set_value("main_tabs", "results_tab")
        
        # Show completion message
        summary = report['summary']
        message = (
            f"Processing Complete!\n\n"
            f"✅ Processed: {summary['processed']}\n"
            f"❌ Failed: {summary['failed']}\n"
            f"⏭️ Skipped: {summary['skipped']}\n"
            f"⏱️ Total time: {summary['processing_time']:.1f}s"
        )
        
        if summary['failed'] == 0:
            self._show_info("Success", message)
        else:
            self._show_warning("Completed with Errors", message)
        
        logger.info("Processing completed successfully")
    
    def _processing_error(self, error: str):
        """Handle processing error."""
        self.processing = False
        self._update_button_states()
        
        dpg.set_value(self.progress_text, "Status: ❌ Error")
        dpg.configure_item(self.progress_bar, overlay="Processing Failed")
        
        self._show_error("Processing Error", f"Processing failed:\n\n{error}")
        
        logger.error(f"Processing failed: {error}")
    
    def _update_button_states(self):
        """Update button states based on processing status."""
        dpg.configure_item(self.start_button, enabled=not self.processing)
        dpg.configure_item(self.stop_button, enabled=self.processing)
    
    def _clear_results(self):
        """Clear previous results from display."""
        # Clear results table
        if dpg.does_item_exist("results_table"):
            # Remove all rows except header
            children = dpg.get_item_children("results_table", slot=1)
            if children:
                for child in children:
                    dpg.delete_item(child)
        
        # Reset progress
        dpg.set_value(self.progress_bar, 0.0)
        dpg.configure_item(self.progress_bar, overlay="Ready to process images...")
        dpg.set_value(self.progress_text, "Status: Ready")
        dpg.set_value(self.stats_text, "")
    
    def _update_results_display(self, report: dict):
        """Update results display with processing report."""
        try:
            summary = report['summary']
            size_analysis = report['size_analysis']
            
            # Update summary table
            dpg.set_value(self.total_files_text, str(summary['total_files']))
            dpg.set_value(self.processed_text, str(summary['processed']))
            dpg.set_value(self.failed_text, str(summary['failed']))
            
            # Format file sizes
            total_savings = size_analysis['total_savings_bytes']
            dpg.set_value(self.savings_text, self._format_file_size(total_savings))
            dpg.set_value(self.compression_text, f"{size_analysis['overall_compression_ratio']:.1f}%")
            
            # Update detailed results table
            results = report['detailed_results']
            
            for result in results[:100]:  # Limit to first 100 results for performance
                with dpg.table_row(parent="results_table"):
                    # Status
                    status = "✅" if result['success'] else "❌"
                    status_text = dpg.add_text(status)
                    if result['success']:
                        dpg.bind_item_theme(status_text, "success_theme")
                    else:
                        dpg.bind_item_theme(status_text, "error_theme")
                    
                    # Input file
                    input_name = Path(result['input_file']).name
                    if len(input_name) > 25:
                        input_name = input_name[:22] + "..."
                    dpg.add_text(input_name)
                    
                    # SEO keywords
                    keywords = result.get('seo_keywords', 'N/A') or 'N/A'
                    if len(keywords) > 35:
                        keywords = keywords[:32] + "..."
                    dpg.add_text(keywords)
                    
                    # Original size
                    dpg.add_text(self._format_file_size(result['original_size']))
                    
                    # New size
                    new_size = self._format_file_size(result['optimized_size']) if result['optimized_size'] > 0 else "N/A"
                    dpg.add_text(new_size)
                    
                    # Savings
                    savings = f"{result['compression_ratio']:.1f}%" if result['success'] else "N/A"
                    savings_text = dpg.add_text(savings)
                    if result['success'] and result['compression_ratio'] > 0:
                        dpg.bind_item_theme(savings_text, "success_theme")
                        
        except Exception as e:
            logger.error(f"Error updating results display: {e}")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _apply_settings(self):
        """Apply current GUI settings to configuration."""
        try:
            # Image settings
            output_format = dpg.get_value(self.format_combo)
            quality = dpg.get_value(self.quality_slider)
            parallel_jobs = dpg.get_value(self.parallel_jobs)
            
            config.update('image.formats.output', output_format)
            config.update(f'image.quality.{output_format}', quality)
            config.update('processing.parallel_jobs', parallel_jobs)
            
            # Processing options
            config.update('processing.backup_originals', dpg.get_value(self.backup_checkbox))
            config.update('processing.skip_existing', dpg.get_value(self.skip_existing_checkbox))
            config.update('processing.dry_run', dpg.get_value(self.dry_run_checkbox))
            
            # Update processor with new settings
            self.processor = SEOImageProcessor()
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            # Update config from GUI
            if dpg.does_item_exist("ollama_endpoint"):
                config.update('ollama.endpoint', dpg.get_value("ollama_endpoint"))
            if dpg.does_item_exist("llava_model"):
                config.update('ollama.model', dpg.get_value("llava_model"))
            if dpg.does_item_exist("seo_keywords"):
                config.update('seo.keyword_count', dpg.get_value("seo_keywords"))
            if dpg.does_item_exist("max_dimension"):
                config.update('image.optimization.max_dimension', dpg.get_value("max_dimension"))
            if dpg.does_item_exist("strip_metadata"):
                config.update('image.optimization.strip_metadata', dpg.get_value("strip_metadata"))
            if dpg.does_item_exist("progressive_jpeg"):
                config.update('image.optimization.progressive', dpg.get_value("progressive_jpeg"))
            
            # Save config to file
            config.save()
            
            self._show_info("Success", "Settings saved successfully!")
            logger.info("Settings saved")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            self._show_error("Error", f"Failed to save settings:\n{e}")
    
    def _reset_settings(self):
        """Reset settings to defaults."""
        # This would reload default config
        self._show_info("Reset", "Settings reset to defaults")
    
    def _open_output_folder(self):
        """Open output folder in file manager."""
        try:
            output_dir = dpg.get_value(self.output_dir_text)
            if not output_dir:
                output_dir = dpg.get_value(self.input_dir_text)
            
            if output_dir and Path(output_dir).exists():
                import os
                import platform
                
                if platform.system() == "Windows":
                    os.startfile(output_dir)
                elif platform.system() == "Darwin":  # macOS
                    os.system(f"open '{output_dir}'")
                else:  # Linux
                    os.system(f"xdg-open '{output_dir}'")
                    
            else:
                self._show_warning("Warning", "Output directory not found")
                
        except Exception as e:
            logger.error(f"Error opening output folder: {e}")
            self._show_error("Error", f"Failed to open folder:\n{e}")
    
    def _export_results_json(self):
        """Export results as JSON."""
        if not self.current_results:
            self._show_warning("Warning", "No results to export")
            return
        
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            filename = filedialog.asksaveasfilename(
                title="Save Results as JSON",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            root.destroy()
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.current_results, f, indent=2, default=str)
                
                self._show_info("Success", f"Results exported to:\n{filename}")
                logger.info(f"Results exported to JSON: {filename}")
                
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            self._show_error("Error", f"Failed to export JSON:\n{e}")
    
    def _export_results_csv(self):
        """Export results as CSV."""
        if not self.current_results:
            self._show_warning("Warning", "No results to export")
            return
        
        try:
            import csv
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            filename = filedialog.asksaveasfilename(
                title="Save Results as CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            root.destroy()
            
            if filename:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow([
                        'Status', 'Input File', 'SEO Keywords', 'Original Size (MB)', 
                        'New Size (MB)', 'Compression Ratio (%)', 'Processing Time (s)'
                    ])
                    
                    # Write data
                    for result in self.current_results['detailed_results']:
                        writer.writerow([
                            'Success' if result['success'] else 'Failed',
                            Path(result['input_file']).name,
                            result.get('seo_keywords', 'N/A') or 'N/A',
                            f"{result['original_size'] / 1024 / 1024:.2f}",
                            f"{result['optimized_size'] / 1024 / 1024:.2f}" if result['optimized_size'] > 0 else 'N/A',
                            f"{result['compression_ratio']:.1f}" if result['success'] else 'N/A',
                            f"{result['processing_time']:.2f}"
                        ])
                
                self._show_info("Success", f"Results exported to:\n{filename}")
                logger.info(f"Results exported to CSV: {filename}")
                
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            self._show_error("Error", f"Failed to export CSV:\n{e}")
    
    def _clear_logs(self):
        """Clear log display."""
        dpg.set_value(self.log_text, "Logs cleared.")
    
    def _save_logs(self):
        """Save logs to file."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            filename = filedialog.asksaveasfilename(
                title="Save Logs",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            root.destroy()
            
            if filename:
                log_content = dpg.get_value(self.log_text)
                with open(filename, 'w') as f:
                    f.write(log_content)
                
                self._show_info("Success", f"Logs saved to:\n{filename}")
                
        except Exception as e:
            logger.error(f"Error saving logs: {e}")
            self._show_error("Error", f"Failed to save logs:\n{e}")
    
    def _show_error(self, title: str, message: str):
        """Show error modal."""
        with dpg.window(label=title, modal=True, width=400, height=200, pos=[400, 300], tag="error_modal"):
            dpg.add_text(message, wrap=380)
            dpg.add_separator()
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("error_modal"), width=-1)
    
    def _show_warning(self, title: str, message: str):
        """Show warning modal."""
        with dpg.window(label=title, modal=True, width=400, height=200, pos=[400, 300], tag="warning_modal"):
            dpg.add_text(message, wrap=380, color=(255, 193, 7))
            dpg.add_separator()
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("warning_modal"), width=-1)
    
    def _show_info(self, title: str, message: str):
        """Show info modal."""
        with dpg.window(label=title, modal=True, width=400, height=200, pos=[400, 300], tag="info_modal"):
            dpg.add_text(message, wrap=380, color=(0, 255, 127))
            dpg.add_separator()
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("info_modal"), width=-1)
    
    def run(self):
        """Run the Dear PyGui application."""
        try:
            dpg.show_viewport()
            
            # Main render loop
            while dpg.is_dearpygui_running():
                dpg.render_dearpygui_frame()
                
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            logger.error(traceback.format_exc())
        finally:
            dpg.destroy_context()

def main():
    """Main entry point for Dear PyGui application."""
    try:
        app = SEOImageConverterGUI()
        app.run()
    except ImportError as e:
        print(f"Error importing Dear PyGui: {e}")
        print("Please install Dear PyGui: pip install dearpygui")
        sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()