import ast
import pytest
from pathlib import Path
from typing import Mapping, Sequence, Set, Generator, Dict, Any
import types
import json
import io
import contextlib

# Directory containing test source files
SAMPLE_DIR = Path(__file__).resolve().parents[1]/'data/sample_sources/interpreter'
ALL_SOURCES = SAMPLE_DIR.glob('*.py')


from prototype.interpreter.python.usage import run_eval_loop

    

def stabilize_value(value):
    """Convert unstable objects to shortest stable string form"""
    
    # Handle collections recursively (preserve original type)
    if isinstance(value, Mapping):
        return type(value)({k: stabilize_value(v) for k, v in value.items()})
    if isinstance(value, Set):
        # set are not json-serializable
        return str(type(value)({stabilize_value(v) for v in value}))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return type(value)(stabilize_value(v) for v in value)
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
def test_python_eval_loop(source_file, file_regression, capsys):
    code = source_file.read_text()

    eval_loop_stdout = io.StringIO()
    with capsys.disabled():
        with contextlib.redirect_stdout(eval_loop_stdout):
            bindings = run_eval_loop(code=code)
        stdout_value = eval_loop_stdout.getvalue().split('\n')
    
    stable_bindings = stabilize_locals(bindings)
    stable_bindings['stdout'] = stdout_value
    stable_bindings = json.dumps(stable_bindings, indent=2)
    
    file_regression.check(stable_bindings)
