import pytest
from pathlib import Path
import ast
import io
import contextlib

from prototype.interpreter.python.usage import run_eval_loop



PYTHON_SOURCES = (
    Path(__file__).resolve().parents[1]
    .joinpath("data/sample_sources/interpreter")
    .glob('*.py')
)



@pytest.mark.parametrize("source_file", PYTHON_SOURCES, ids=lambda p: p.name)
def test_eval_loop(source_file, capsys):
    """Test that eval_loop produces identical stdout to Python exec"""  
    code = source_file.read_text() 
    # to be tested
    eval_loop_stdout = io.StringIO()

    #pytest intercepts the stdout; disable it
    with capsys.disabled():
        with contextlib.redirect_stdout(eval_loop_stdout):
            run_eval_loop(code=code)
        
        #baseline
        python_stdout = io.StringIO()
        with contextlib.redirect_stdout(python_stdout):
            exec(compile(code, 'test', 'exec'))

    assert eval_loop_stdout.getvalue() == python_stdout.getvalue()
