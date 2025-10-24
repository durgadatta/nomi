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
        # Capture Python exec output - Better approach
        python_stdout = io.StringIO()
        with contextlib.redirect_stdout(python_stdout):
            # Create a proper module-like namespace
            namespace = {'__name__': '__main__'}
            exec(compile(code, 'test', 'exec'), namespace)
            # For recursive functions to work, we need to handle the case where
            # functions reference themselves. This approach usually works better.
    
    assert eval_loop_stdout.getvalue() == python_stdout.getvalue()