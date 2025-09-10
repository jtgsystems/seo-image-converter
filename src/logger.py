"""Logging configuration for SEO Image Converter."""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

from .config import config

class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support."""
    
    COLORS = {
        'DEBUG': 'dim white',
        'INFO': 'white',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold red',
    }
    
    def __init__(self, console: Console):
        super().__init__()
        self.console = console
    
    def format(self, record):
        # Get base message
        message = super().format(record)
        
        # Add color based on level
        color = self.COLORS.get(record.levelname, 'white')
        
        return f"[{color}]{message}[/{color}]"

def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup logger with rich formatting and file output."""
    
    # Get logging configuration
    log_config = config.logging
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', 'conversion_log.txt')
    use_colors = log_config.get('console_colors', True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with rich formatting
    if use_colors:
        console = Console(stderr=True)
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )
    else:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # File handler for persistent logging
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logger('seo_image_converter')