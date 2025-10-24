#!/usr/bin/env python3
"""
SEO Image Converter - Main Entry Point
AI-powered image optimization with SEO-friendly naming using Ollama/Qwen2.5-VL
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """Main entry point - launch GUI by default, CLI if --cli specified."""

    # Check for CLI flag
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        from src.cli import main as cli_main

        cli_main()
    else:
        # Launch modern Dear PyGui interface (simplified version)
        from src.gui_simple import main as gui_main

        gui_main()


if __name__ == "__main__":
    main()
