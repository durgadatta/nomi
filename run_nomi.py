#!/usr/bin/env python3
"""
Nomi/Python Runner - Simple version
Usage: python run_nomi.py [filename]
"""

import sys
from pathlib import Path

# Import both evaluation loops
from prototype.interpreter.python.usage import run_eval_loop as run_python
from prototype.interpreter.nomi.usage import run_eval_loop as run_nomi

def main():
    # Get filename from args or use default
    filename = sys.argv[1] if len(sys.argv) > 1 else 'demo.nomi'
    file_path = Path(filename)
    
    if not file_path.exists():
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    
    # Choose interpreter based on file extension
    if file_path.suffix == '.nomi':
        run_eval_loop = run_nomi
    else:  # .py or any other extension
        run_eval_loop = run_python
    
    print(f"Running: {filename}")
    print("-" * 40)
    
    bindings = run_eval_loop(file_name=file_path)
    
    print("-" * 40)
    print("Global Environment:")
    for key, value in bindings.items():
        if key not in ('__builtins__', 'builtins'):
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()