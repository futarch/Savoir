#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def cleanup_python_cache():
    """Remove Python cache files and directories."""
    current_dir = Path('.')
    patterns = ['__pycache__', '*.pyc', '*.pyo', '*.pyd', '*.log']
    
    for pattern in patterns:
        for item in current_dir.rglob(pattern):
            print(f"Removing {item}")
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    
    print("Python cache and log files cleanup completed!")

if __name__ == '__main__':
    cleanup_python_cache() 