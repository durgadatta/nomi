#!/usr/bin/env python3
"""
Nomi CLI - Run Nomi or Python files
"""

import sys
from pathlib import Path

def main():
    # Get filename from args or use default
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: nomi [filename]")
        print("  filename: .nomi or .py file (default: scripts/demo.nomi)")
        return
    
    filename = sys.argv[1] if len(sys.argv) > 1 else 'scripts/demo.nomi'
    file_path = Path(filename)
    
    if not file_path.exists():
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    
    # TODO(NOMI-ARCH-023): Move the CLI onto prototype.runtime.execute() so
    # command-line errors, stdout/stderr, diagnostics, timings, and mode
    # selection share the same contract as web, notebook, and future REPLs.
    if file_path.suffix == '.nomi' or file_path.name.endswith('.nomi.nb'):
        from prototype.interpreter.nomi.usage import run_eval_loop
    else:
        from prototype.interpreter.python.usage import run_eval_loop
    
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
