import ast
from prototype.interpreter.python.usage import run_eval_loop
from pathlib import Path



SAMPLE_DIR = Path(__file__).resolve().parents[1]/'data/sample_sources/interpreter'

if __name__ == "__main__":
    file_path = SAMPLE_DIR.joinpath('functions.py')
    bindings = run_eval_loop(file_name=file_path)
    print("\nGlobal Environment:")
    for key, value in bindings.items():
        if key not in ('__builtins__', 'builtins'):
            print(f"{key}: {value}")