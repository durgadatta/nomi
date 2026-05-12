import ast
import pytest
from pathlib import Path
import json
import io
import contextlib

from prototype.interpreter.helpers import get_run_eval_loop
from prototype.tests.shared_utils import stabilize_value, stabilize_locals

SAMPLE_DIR = Path(__file__).resolve().parents[1]/'data/sample_sources/interpreter'
ALL_SOURCES = list(SAMPLE_DIR.glob('*.py')) + list(SAMPLE_DIR.glob('*.nomi'))


@pytest.mark.parametrize("source_file", ALL_SOURCES, ids=lambda p: p.name)
def test_eval_loop(source_file, file_regression, capsys, interpreter_mode):
    ext = source_file.suffix
    if ext == '.py' and interpreter_mode != 'python':
        pytest.skip(f".py source requires 'python' interpreter mode, got {interpreter_mode!r}")
    if ext == '.nomi' and interpreter_mode == 'python':
        pytest.skip(f".nomi source requires 'nomi' or 'reduced' interpreter mode, got {interpreter_mode!r}")

    code = source_file.read_text()

    run_eval_loop = get_run_eval_loop(interpreter_mode)

    eval_loop_stdout = io.StringIO()
    with capsys.disabled():
        with contextlib.redirect_stdout(eval_loop_stdout):
            bindings = run_eval_loop(code=code)
        stdout_value = eval_loop_stdout.getvalue().split('\n')
    
    stable_bindings = stabilize_locals(bindings)
    stable_bindings['stdout'] = stdout_value
    stable_bindings = json.dumps(stable_bindings, indent=2)
    
    file_regression.check(stable_bindings)
