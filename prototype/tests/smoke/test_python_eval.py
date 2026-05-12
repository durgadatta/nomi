"""
Smoke test: Python interpreter evaluation.

Runs a sample Python source file through the custom Python interpreter
and prints the resulting global environment.

Run manually::

    python3 prototype/tests/smoke/test_python_eval.py
"""

from pathlib import Path
from prototype.interpreter.python.usage import run_eval_loop

SAMPLE_FILE = (
    Path(__file__).resolve().parents[1]
    / "data" / "sample_sources" / "interpreter" / "functions.py"
)


def main():
    bindings = run_eval_loop(file_name=SAMPLE_FILE)
    print("\nGlobal Environment:")
    for key, value in bindings.items():
        if key not in ("__builtins__", "builtins"):
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
