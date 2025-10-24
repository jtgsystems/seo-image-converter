"""Modern GUI interface for SEO Image Converter using CustomTkinter."""

import sys
import threading
import time
from pathlib import Path
from typing import Optional
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

try:
    import customtkinter as ctk
    from tkinterdnd2 import DND_FILES

    HAS_MODERN_GUI = True
except ImportError:
    HAS_MODERN_GUI = False
    print(
        "Warning: Modern GUI dependencies not available. Install with: pip install customtkinter tkinterdnd2"
    )

from .processor import ProcessingResult, SEOImageProcessor
from .config import config
from .logger import logger


class SEOImageConverterGUI:
    """Modern GUI for SEO Image Converter."""

    def __init__(self):
        """Initialize the GUI application."""
        # Set appearance mode and color theme
        if HAS_MODERN_GUI:
            ctk.set_appearance_mode("dark")  # "system", "dark", "light"
            ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

        # Initialize main window
        if HAS_MODERN_GUI:
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()

        self.root.title("SEO Image Converter - AI-Powered Image Optimization")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Application state
        self.processor = SEOImageProcessor()
        self.processing = False
        self.current_results = None
        self.selected_directory = None
        self.output_directory = None

        # Threading
        self.processing_thread = None

        # Initialize UI
        self._setup_ui()

        # Setup drag and drop if available
        if HAS_MODERN_GUI:
            try:
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind("<<Drop>>", self._on_drop)
            except Exception as e:
                logger.warning(f"Drag and drop setup failed: {e}")

    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Header frame
        self._create_header()

        # Main content area
        self._create_main_content()

        # Status bar
        self._create_status_bar()

    def _create_header(self):
        """Create header with title and configuration."""
        if HAS_MODERN_GUI:
            header_frame = ctk.CTkFrame(self.root)
        else:
            header_frame = ttk.Frame(self.root)

        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # Title
        if HAS_MODERN_GUI:
            title_label = ctk.CTkLabel(
                header_frame,
                text="🚀 SEO Image Converter",
                font=ctk.CTkFont(size=24, weight="bold"),
            )
        else:
            title_label = ttk.Label(
                header_frame, text="SEO Image Converter", font=("Arial", 16, "bold")
            )

        title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Configuration button
        if HAS_MODERN_GUI:
            config_btn = ctk.CTkButton(
                header_frame, text="⚙️ Settings", command=self._open_settings, width=100
            )
        else:
            config_btn = ttk.Button(
                header_frame, text="Settings", command=self._open_settings
            )

        config_btn.grid(row=0, column=2, padx=20, pady=15, sticky="e")

    def _create_main_content(self):
        """Create main content area with tabs."""
        if HAS_MODERN_GUI:
            # Create tabview
            self.tabview = ctk.CTkTabview(self.root)
        else:
            self.tabview = ttk.Notebook(self.root)

        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # Processing tab
        self._create_processing_tab()

        # Results tab
        self._create_results_tab()

        # Logs tab
        self._create_logs_tab()

    def _create_processing_tab(self):
        """Create the main processing interface."""
        if HAS_MODERN_GUI:
            process_frame = self.tabview.add("🔄 Process Images")
        else:
            process_frame = ttk.Frame(self.tabview)
            self.tabview.add(process_frame, text="Process Images")

        process_frame.grid_columnconfigure(0, weight=1)

        # Directory selection section
        self._create_directory_section(process_frame)

        # Options section
        self._create_options_section(process_frame)

        # Progress section
        self._create_progress_section(process_frame)

        # Control buttons
        self._create_control_buttons(process_frame)

    def _create_directory_section(self, parent):
        """Create directory selection section."""
        # Input directory
        if HAS_MODERN_GUI:
            input_frame = ctk.CTkFrame(parent)
        else:
            input_frame = ttk.LabelFrame(parent, text="Input Directory")

        input_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        input_frame.grid_columnconfigure(1, weight=1)

        if HAS_MODERN_GUI:
            ctk.CTkLabel(input_frame, text="📁 Input Directory:").grid(
                row=0, column=0, padx=10, pady=10, sticky="w"
            )

            self.input_dir_var = tk.StringVar()
            input_entry = ctk.CTkEntry(
                input_frame,
                textvariable=self.input_dir_var,
                placeholder_text="Drag & drop folder here or click Browse...",
            )
        else:
            ttk.Label(input_frame, text="Input Directory:").grid(
                row=0, column=0, padx=10, pady=5, sticky="w"
            )

            self.input_dir_var = tk.StringVar()
            input_entry = ttk.Entry(input_frame, textvariable=self.input_dir_var)

        input_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        if HAS_MODERN_GUI:
            browse_btn = ctk.CTkButton(
                input_frame,
                text="Browse",
                command=self._browse_input_directory,
                width=80,
            )
        else:
            browse_btn = ttk.Button(
                input_frame, text="Browse", command=self._browse_input_directory
            )

        browse_btn.grid(row=0, column=2, padx=10, pady=10)

        # Output directory
        if HAS_MODERN_GUI:
            output_frame = ctk.CTkFrame(parent)
        else:
            output_frame = ttk.LabelFrame(parent, text="Output Directory")

        output_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        output_frame.grid_columnconfigure(1, weight=1)

        if HAS_MODERN_GUI:
            ctk.CTkLabel(output_frame, text="💾 Output Directory:").grid(
                row=0, column=0, padx=10, pady=10, sticky="w"
            )
        else:
            ttk.Label(output_frame, text="Output Directory:").grid(
                row=0, column=0, padx=10, pady=5, sticky="w"
            )

        self.output_dir_var = tk.StringVar(value="(Same as input)")

        if HAS_MODERN_GUI:
            output_entry = ctk.CTkEntry(
                output_frame,
                textvariable=self.output_dir_var,
                placeholder_text="(Same as input)",
            )
        else:
            output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var)

        output_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        if HAS_MODERN_GUI:
            output_browse_btn = ctk.CTkButton(
                output_frame,
                text="Browse",
                command=self._browse_output_directory,
                width=80,
            )
        else:
            output_browse_btn = ttk.Button(
                output_frame, text="Browse", command=self._browse_output_directory
            )

        output_browse_btn.grid(row=0, column=2, padx=10, pady=10)

    def _create_options_section(self, parent):
        """Create processing options section."""
        if HAS_MODERN_GUI:
            options_frame = ctk.CTkFrame(parent)
        else:
            options_frame = ttk.LabelFrame(parent, text="Processing Options")

        options_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        options_frame.grid_columnconfigure(1, weight=1)

        # Format selection
        if HAS_MODERN_GUI:
            ctk.CTkLabel(options_frame, text="🖼️ Output Format:").grid(
                row=0, column=0, padx=10, pady=5, sticky="w"
            )

            self.format_var = tk.StringVar(value="webp")
            format_menu = ctk.CTkOptionMenu(
                options_frame, values=["webp", "png", "jpeg"], variable=self.format_var
            )
        else:
            ttk.Label(options_frame, text="Output Format:").grid(
                row=0, column=0, padx=10, pady=5, sticky="w"
            )

            self.format_var = tk.StringVar(value="webp")
            format_menu = ttk.Combobox(
                options_frame,
                textvariable=self.format_var,
                values=["webp", "png", "jpeg"],
                state="readonly",
            )

        format_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Quality setting
        if HAS_MODERN_GUI:
            ctk.CTkLabel(options_frame, text="🎛️ Quality:").grid(
                row=0, column=2, padx=10, pady=5, sticky="w"
            )

            self.quality_var = tk.IntVar(value=85)
            quality_slider = ctk.CTkSlider(
                options_frame,
                from_=50,
                to=100,
                variable=self.quality_var,
                number_of_steps=50,
            )
        else:
            ttk.Label(options_frame, text="Quality:").grid(
                row=0, column=2, padx=10, pady=5, sticky="w"
            )

            self.quality_var = tk.IntVar(value=85)
            quality_slider = ttk.Scale(
                options_frame,
                from_=50,
                to=100,
                variable=self.quality_var,
                orient="horizontal",
            )

        quality_slider.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        if HAS_MODERN_GUI:
            self.quality_label = ctk.CTkLabel(options_frame, text="85")
        else:
            self.quality_label = ttk.Label(options_frame, text="85")

        self.quality_label.grid(row=0, column=4, padx=5, pady=5)

        # Update quality label
        self.quality_var.trace_add("write", self._update_quality_label)

        # Checkboxes
        checkbox_frame = ttk.Frame(options_frame)
        checkbox_frame.grid(
            row=1, column=0, columnspan=5, sticky="ew", padx=10, pady=10
        )

        self.backup_var = tk.BooleanVar(value=True)
        self.skip_existing_var = tk.BooleanVar(value=False)
        self.dry_run_var = tk.BooleanVar(value=False)

        if HAS_MODERN_GUI:
            backup_check = ctk.CTkCheckBox(
                checkbox_frame, text="💾 Backup originals", variable=self.backup_var
            )
            skip_check = ctk.CTkCheckBox(
                checkbox_frame,
                text="⏭️ Skip existing files",
                variable=self.skip_existing_var,
            )
            dry_run_check = ctk.CTkCheckBox(
                checkbox_frame,
                text="🧪 Dry run (preview only)",
                variable=self.dry_run_var,
            )
        else:
            backup_check = ttk.Checkbutton(
                checkbox_frame, text="Backup originals", variable=self.backup_var
            )
            skip_check = ttk.Checkbutton(
                checkbox_frame,
                text="Skip existing files",
                variable=self.skip_existing_var,
            )
            dry_run_check = ttk.Checkbutton(
                checkbox_frame, text="Dry run (preview only)", variable=self.dry_run_var
            )

        backup_check.pack(side="left", padx=10)
        skip_check.pack(side="left", padx=10)
        dry_run_check.pack(side="left", padx=10)

    def _create_progress_section(self, parent):
        """Create progress tracking section."""
        if HAS_MODERN_GUI:
            progress_frame = ctk.CTkFrame(parent)
        else:
            progress_frame = ttk.LabelFrame(parent, text="Progress")

        progress_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        progress_frame.grid_columnconfigure(0, weight=1)

        # Progress bar
        if HAS_MODERN_GUI:
            self.progress_bar = ctk.CTkProgressBar(progress_frame)
        else:
            self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate")

        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        # Progress labels
        label_frame = ttk.Frame(progress_frame)
        label_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        label_frame.grid_columnconfigure(1, weight=1)

        if HAS_MODERN_GUI:
            self.progress_label = ctk.CTkLabel(
                label_frame, text="Ready to process images..."
            )
            self.stats_label = ctk.CTkLabel(label_frame, text="")
        else:
            self.progress_label = ttk.Label(
                label_frame, text="Ready to process images..."
            )
            self.stats_label = ttk.Label(label_frame, text="")

        self.progress_label.grid(row=0, column=0, sticky="w")
        self.stats_label.grid(row=0, column=1, sticky="e")

    def _create_control_buttons(self, parent):
        """Create control buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, pady=20)

        if HAS_MODERN_GUI:
            self.start_button = ctk.CTkButton(
                button_frame,
                text="🚀 Start Processing",
                command=self._start_processing,
                width=150,
                height=40,
                font=ctk.CTkFont(size=14, weight="bold"),
            )

            self.stop_button = ctk.CTkButton(
                button_frame,
                text="⏹️ Stop",
                command=self._stop_processing,
                width=100,
                height=40,
                state="disabled",
            )
        else:
            self.start_button = ttk.Button(
                button_frame, text="Start Processing", command=self._start_processing
            )
            self.stop_button = ttk.Button(
                button_frame,
                text="Stop",
                command=self._stop_processing,
                state="disabled",
            )

        self.start_button.pack(side="left", padx=10)
        self.stop_button.pack(side="left", padx=10)

    def _create_results_tab(self):
        """Create results viewing tab."""
        if HAS_MODERN_GUI:
            results_frame = self.tabview.add("📊 Results")
        else:
            results_frame = ttk.Frame(self.tabview)
            self.tabview.add(results_frame, text="Results")

        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)

        # Results table
        self._create_results_table(results_frame)

    def _create_results_table(self, parent):
        """Create results table with scrollbars."""
        # Create treeview for results
        columns = (
            "Status",
            "Input File",
            "SEO Keywords",
            "Original Size",
            "New Size",
            "Savings",
        )

        self.results_tree = ttk.Treeview(parent, columns=columns, show="headings")

        # Configure columns
        self.results_tree.heading("Status", text="Status")
        self.results_tree.heading("Input File", text="Input File")
        self.results_tree.heading("SEO Keywords", text="SEO Keywords")
        self.results_tree.heading("Original Size", text="Original Size")
        self.results_tree.heading("New Size", text="New Size")
        self.results_tree.heading("Savings", text="Savings %")

        # Configure column widths
        self.results_tree.column("Status", width=60, anchor="center")
        self.results_tree.column("Input File", width=200)
        self.results_tree.column("SEO Keywords", width=250)
        self.results_tree.column("Original Size", width=100, anchor="e")
        self.results_tree.column("New Size", width=100, anchor="e")
        self.results_tree.column("Savings", width=80, anchor="e")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            parent, orient="vertical", command=self.results_tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            parent, orient="horizontal", command=self.results_tree.xview
        )

        self.results_tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Grid layout
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

    def _create_logs_tab(self):
        """Create logs viewing tab."""
        if HAS_MODERN_GUI:
            logs_frame = self.tabview.add("📋 Logs")
        else:
            logs_frame = ttk.Frame(self.tabview)
            self.tabview.add(logs_frame, text="Logs")

        logs_frame.grid_columnconfigure(0, weight=1)
        logs_frame.grid_rowconfigure(0, weight=1)

        # Log text area
        self.log_text = ScrolledText(logs_frame, state="disabled", wrap="word")
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def _create_status_bar(self):
        """Create status bar."""
        if HAS_MODERN_GUI:
            status_frame = ctk.CTkFrame(self.root)
        else:
            status_frame = ttk.Frame(self.root)

        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        status_frame.grid_columnconfigure(0, weight=1)

        if HAS_MODERN_GUI:
            self.status_label = ctk.CTkLabel(status_frame, text="Ready")
        else:
            self.status_label = ttk.Label(status_frame, text="Ready")

        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Ollama status
        self._check_ollama_status()

    def _check_ollama_status(self):
        """Check and display Ollama service status."""
        if self.processor.ai_analyzer.is_ollama_available():
            status_text = "✅ Ollama AI service: Connected"
            if HAS_MODERN_GUI:
                text_color = "green"
            else:
                text_color = "black"
        else:
            status_text = "⚠️ Ollama AI service: Disconnected (will use fallback naming)"
            if HAS_MODERN_GUI:
                text_color = "orange"
            else:
                text_color = "black"

        if HAS_MODERN_GUI:
            self.status_label.configure(text=status_text, text_color=text_color)
        else:
            self.status_label.configure(text=status_text)

    def _update_quality_label(self, *args):
        """Update quality label when slider changes."""
        value = self.quality_var.get()
        self.quality_label.configure(text=str(value))

    def _browse_input_directory(self):
        """Browse for input directory."""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir_var.set(directory)
            self.selected_directory = Path(directory)

    def _browse_output_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            self.output_directory = Path(directory)
        else:
            self.output_dir_var.set("(Same as input)")
            self.output_directory = None

    def _on_drop(self, event):
        """Handle drag and drop files."""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = Path(files[0])
            if file_path.is_dir():
                self.input_dir_var.set(str(file_path))
                self.selected_directory = file_path

    def _open_settings(self):
        """Open settings dialog."""
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()

        # Add settings content here (placeholder)
        if HAS_MODERN_GUI:
            label = ctk.CTkLabel(settings_window, text="Settings panel - Coming soon!")
        else:
            label = ttk.Label(settings_window, text="Settings panel - Coming soon!")

        label.pack(pady=50)

        if HAS_MODERN_GUI:
            close_btn = ctk.CTkButton(
                settings_window, text="Close", command=settings_window.destroy
            )
        else:
            close_btn = ttk.Button(
                settings_window, text="Close", command=settings_window.destroy
            )

        close_btn.pack(pady=20)

    def _start_processing(self):
        """Start image processing in separate thread."""
        if self.processing:
            return

        # Validate input
        if not self.input_dir_var.get():
            messagebox.showerror("Error", "Please select an input directory")
            return

        input_dir = Path(self.input_dir_var.get())
        if not input_dir.exists():
            messagebox.showerror("Error", "Input directory does not exist")
            return

        # Update configuration based on GUI settings
        config.update("image.formats.output", self.format_var.get())
        config.update(f"image.quality.{self.format_var.get()}", self.quality_var.get())
        config.update("processing.backup_originals", self.backup_var.get())
        config.update("processing.skip_existing", self.skip_existing_var.get())
        config.update("processing.dry_run", self.dry_run_var.get())

        # Update UI state
        self.processing = True
        self._update_button_states()

        # Clear previous results
        self._clear_results()

        # Start processing thread
        output_dir = (
            Path(self.output_dir_var.get())
            if self.output_dir_var.get() != "(Same as input)"
            else None
        )

        self.processing_thread = threading.Thread(
            target=self._process_images_thread,
            args=(input_dir, output_dir),
            daemon=True,
        )
        self.processing_thread.start()

    def _stop_processing(self):
        """Stop image processing."""
        self.processing = False
        self._update_button_states()
        self.progress_label.configure(text="Stopping...")

    def _process_images_thread(self, input_dir: Path, output_dir: Optional[Path]):
        """Process images in background thread."""
        try:

            def progress_callback(completed: int, total: int, result: ProcessingResult):
                if not self.processing:
                    return

                # Update progress bar
                progress = completed / total
                self.root.after(
                    0, lambda: self._update_progress(progress, completed, total, result)
                )

            # Process images
            report = self.processor.process_directory(
                input_dir, output_dir, progress_callback
            )

            # Update UI with results
            self.root.after(0, lambda: self._processing_complete(report))

        except Exception as exc:
            logger.error(f"Processing failed: {exc}")
            error_msg = str(exc)
            self.root.after(0, lambda: self._processing_error(error_msg))

    def _update_progress(
        self, progress: float, completed: int, total: int, result: ProcessingResult
    ):
        """Update progress display."""
        if HAS_MODERN_GUI:
            self.progress_bar.set(progress)
        else:
            self.progress_bar["value"] = progress * 100

        status_emoji = "✅" if result.success else "❌"
        self.progress_label.configure(
            text=f"{status_emoji} Processing: {result.input_path.name} ({completed}/{total})"
        )

        # Update stats
        if completed > 0:
            elapsed = time.time() - getattr(self, "_start_time", time.time())
            avg_time = elapsed / completed
            remaining = (total - completed) * avg_time

            stats_text = f"⏱️ {completed}/{total} • {remaining:.0f}s remaining"
            self.stats_label.configure(text=stats_text)

    def _processing_complete(self, report: dict):
        """Handle processing completion."""
        self.processing = False
        self._update_button_states()

        # Update progress
        if HAS_MODERN_GUI:
            self.progress_bar.set(1.0)
        else:
            self.progress_bar["value"] = 100

        # Show results
        self._display_results(report)

        # Show completion message
        summary = report["summary"]
        message = (
            f"Processing Complete!\n\n"
            f"Processed: {summary['processed']}\n"
            f"Failed: {summary['failed']}\n"
            f"Skipped: {summary['skipped']}\n"
            f"Total time: {summary['processing_time']:.1f}s"
        )

        if summary["failed"] == 0:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showwarning("Completed with Errors", message)

        # Switch to results tab
        if HAS_MODERN_GUI:
            self.tabview.set("📊 Results")
        else:
            self.tabview.select(1)

    def _processing_error(self, error: str):
        """Handle processing error."""
        self.processing = False
        self._update_button_states()

        self.progress_label.configure(text="❌ Processing failed")
        messagebox.showerror("Processing Error", f"Processing failed:\n\n{error}")

    def _update_button_states(self):
        """Update button states based on processing status."""
        if self.processing:
            if HAS_MODERN_GUI:
                self.start_button.configure(state="disabled")
                self.stop_button.configure(state="normal")
            else:
                self.start_button.configure(state="disabled")
                self.stop_button.configure(state="normal")
        else:
            if HAS_MODERN_GUI:
                self.start_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
            else:
                self.start_button.configure(state="normal")
                self.stop_button.configure(state="disabled")

    def _clear_results(self):
        """Clear previous results."""
        # Clear results table
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Reset progress
        if HAS_MODERN_GUI:
            self.progress_bar.set(0.0)
        else:
            self.progress_bar["value"] = 0

        self.progress_label.configure(text="Starting processing...")
        self.stats_label.configure(text="")

        # Record start time
        self._start_time = time.time()

    def _display_results(self, report: dict):
        """Display processing results in table."""
        results = report["detailed_results"]

        for result in results:
            status = "✅" if result["success"] else "❌"
            input_file = Path(result["input_file"]).name
            keywords = result.get("seo_keywords", "N/A") or "N/A"

            # Truncate long keywords
            if len(keywords) > 40:
                keywords = keywords[:37] + "..."

            original_size = self._format_file_size(result["original_size"])
            new_size = (
                self._format_file_size(result["optimized_size"])
                if result["optimized_size"] > 0
                else "N/A"
            )
            savings = (
                f"{result['compression_ratio']:.1f}%" if result["success"] else "N/A"
            )

            self.results_tree.insert(
                "",
                "end",
                values=(status, input_file, keywords, original_size, new_size, savings),
            )

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for GUI application."""
    if not HAS_MODERN_GUI:
        print("Installing GUI dependencies...")
        import subprocess

        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "customtkinter", "tkinterdnd2"]
            )
            print("GUI dependencies installed. Please restart the application.")
            sys.exit(0)
        except subprocess.CalledProcessError:
            print("Failed to install GUI dependencies. Using basic GUI.")

    app = SEOImageConverterGUI()
    app.run()


if __name__ == "__main__":
    main()
