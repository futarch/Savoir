#!/usr/bin/env python
"""
Script to run all R2R API tests.

This script runs all the tests for the R2R API integration to verify
that the API is being called correctly from the different functions
in the R2R folder.
"""

import pytest
import sys
import os

def main():
    """Run all R2R API tests."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the parent directory to the path so we can import the app
    parent_dir = os.path.dirname(script_dir)
    sys.path.insert(0, parent_dir)
    
    # Run the tests
    print("Running R2R API tests...")
    result = pytest.main([
        os.path.join(script_dir, "test_r2r_api.py"),
        os.path.join(script_dir, "test_r2r_client.py"),
        os.path.join(script_dir, "test_r2r_errors.py"),
        os.path.join(script_dir, "test_r2r_utils.py"),
        "-v"
    ])
    
    # Exit with the same code as pytest
    sys.exit(result)

if __name__ == "__main__":
    main() 