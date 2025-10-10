import ast
from prototype.interpreter.python.eval_loop import Interpreter
from typing import Dict, Any
from pathlib import Path



SAMPLE_DIR = Path(__file__).resolve().parents[1]/'data/sample_sources/interpreter'


def run_ast(module: ast.Module) -> Dict[str, Any]:
    module = ast.fix_missing_locations(module)
    interpreter = Interpreter()
    try:
        interpreter.eval(module)
        return interpreter.global_env.bindings
    except Exception as e:
        raise RuntimeError(f"Execution failed: {str(e)}") from e

if __name__ == "__main__":
    code = SAMPLE_DIR.joinpath('sample.py').read_text(encoding='utf-8')
    tree = ast.parse(code)
    bindings = run_ast(tree)
    print("\nGlobal Environment:")
    for key, value in bindings.items():
        if key not in ('__builtins__', 'builtins'):
            print(f"{key}: {value}")