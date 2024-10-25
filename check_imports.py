import os
import sys
from pathlib import Path

def check_file_for_config(file_path):
    """Check a Python file for incorrect Config references."""
    with open(file_path, 'r') as f:
        content = f.read()
        line_number = 1
        for line in content.split('\n'):
            if 'Config' in line and 'class Config' not in line:
                print(f"Found potential Config reference in {file_path}:{line_number}")
                print(f"Line: {line.strip()}")
            line_number += 1

def main():
    """Check all Python files in the project for Config references."""
    project_root = Path(__file__).parent
    print(f"Checking files in {project_root}")
    
    for path in project_root.rglob('*.py'):
        if '__pycache__' not in str(path):
            print(f"\nChecking {path}")
            check_file_for_config(path)

if __name__ == "__main__":
    main()