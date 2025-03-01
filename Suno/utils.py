"""
Utility functions for the Suno Downloader.
"""

import os
import sys
import logging
import time
from pathlib import Path


def setup_logger():
    """Set up and return logger instance."""
    # Create logger
    logger = logging.getLogger('suno_downloader')
    logger.setLevel(logging.INFO)
    
    # Create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create file handler and set level
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / f"suno_downloader_{timestamp}.log")
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter to handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def format_size(size_bytes):
    """Format bytes to human-readable size."""
    if size_bytes == 0:
        return "0B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1
    
    return f"{size_bytes:.2f}{units[unit_index]}"


def create_directory(directory_path):
    """Create directory if it doesn't exist."""
    try:
        if not directory_path.exists():
            directory_path.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        logging.error(f"Error creating directory {directory_path}: {e}")
        return False


def is_valid_url(url):
    """Check if url is valid."""
    if not url:
        return False
    
    url = url.lower()
    return url.startswith('http://') or url.startswith('https://')


def sanitize_input(text):
    """Sanitize input text to prevent injection."""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    return ''.join(c for c in text if c.isalnum() or c in '-_.@')


def handle_keyboard_interrupt():
    """Handle keyboard interrupt (Ctrl+C)."""
    print("\nProcess interrupted by user. Exiting...")
    sys.exit(0)


def rate_limit_sleep(last_request_time, min_delay=1.0):
    """Sleep to respect rate limits."""
    if last_request_time is None:
        return time.time()
    
    elapsed = time.time() - last_request_time
    if elapsed < min_delay:
        remaining = min_delay - elapsed
        time.sleep(remaining)
    
    return time.time()


def truncate_string(text, max_length=100):
    """Truncate string to max_length."""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."
