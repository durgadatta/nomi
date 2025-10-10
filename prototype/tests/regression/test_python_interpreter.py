import ast
import pytest
from pathlib import Path
from typing import Mapping, Sequence, Set, Generator
import types
import json

# Directory containing test source files
SAMPLE_DIR = Path(__file__).resolve().parents[1]/'data/sample_sources/interpreter'
ALL_SOURCES = SAMPLE_DIR.glob('*.py')

#TODO: put to utils; 
from prototype.interpreter.python.eval_loop import Interpreter

def run_ast(module: ast.Module) -> Dict[str, Any]:
    module = ast.fix_missing_locations(module)
    interpreter = Interpreter()
    try:
        interpreter.eval(module)
        return interpreter.global_env.bindings
    except Exception as e:
        raise RuntimeError(f"Execution failed: {str(e)}") from e
    

def stabilize_value(value):
    """Convert unstable objects to shortest stable string form"""
    
    # Handle collections recursively (preserve original type)
    if isinstance(value, Mapping):
        return type(value)({k: stabilize_value(v) for k, v in value.items()})
    if isinstance(value, Set):
        return type(value)({stabilize_value(v) for v in value})
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return type(value)(stabilize_value(v) for v in value)
    
    # Special cases
    # if isinstance(value, types.LambdaType):
    #     return "lambda"
    # if isinstance(value, Generator):
    #     return "generator"
    # if isinstance(value, types.ModuleType):
    #     return value.__name__

    if (
            callable(value)
            or isinstance(value, (Generator, types.ModuleType))
    ):
        return f'{value.__name__}:class={type(value)}'
    
    # object instances
    if hasattr(value, '__dict__'):
        return f'instance of:{stabilize_value(type(value))}'
    
    return value


def stabilize_locals(local_vars, exclude_private=True):
    """Convert local variables to stable k:v pairs"""
    return {
        name: stabilize_value(value)
        for name, value in local_vars.items()
        if not (exclude_private and name.startswith('_'))
    }




@pytest.mark.parametrize("source_file", ALL_SOURCES, ids=lambda p: p.name)
def test_python_eval_loop(source_file, file_regression):
    code = source_file.read_text()

    tree = ast.parse(code)
    bindings = run_ast(tree)
    stable_bindings = json.dumps(stabilize_locals(bindings), indent=2)
    file_regression.check(stable_bindings)
