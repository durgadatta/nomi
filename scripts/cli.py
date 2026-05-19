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
    
    if file_path.suffix == '.nomi' or file_path.name.endswith('.nomi.nb'):
        mode = "nomi"
    else:
        mode = "python"
    
    print(f"Running: {filename}")
    print("-" * 40)

    from prototype.runtime import execute

    result = execute(filename=file_path, mode=mode)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    bindings = result.bindings
    
    print("-" * 40)
    print("Global Environment:")
    for key, value in bindings.items():
        if key not in ('__builtins__', 'builtins'):
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
