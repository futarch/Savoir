#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def cleanup_python_cache():
    """Remove Python cache files and directories."""
    # Get the current directory
    current_dir = Path('.')
    
    # Find and remove __pycache__ directories
    for cache_dir in current_dir.rglob('__pycache__'):
        print(f"Removing {cache_dir}")
        shutil.rmtree(cache_dir)
    
    # Find and remove .pyc, .pyo, .pyd files
    for ext in ['*.pyc', '*.pyo', '*.pyd']:
        for cache_file in current_dir.rglob(ext):
            print(f"Removing {cache_file}")
            cache_file.unlink()
    
    # Find and remove log files
    for log_file in current_dir.rglob('*.log'):
        print(f"Removing {log_file}")
        log_file.unlink()
    
    print("Python cache and log files cleanup completed!")

if __name__ == '__main__':
    cleanup_python_cache() 