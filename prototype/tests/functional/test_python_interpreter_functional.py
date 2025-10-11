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

def test_original_fibonacci():
    """Test the original failing Fibonacci case"""
    code = """
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

print("Fibonacci 5:", list(fib(5)))
print("Fibonacci 3:", list(fib(3)))
"""
    
    print("=== Testing Original Fibonacci ===")
    try:
        eval_loop_stdout = io.StringIO()
        with contextlib.redirect_stdout(eval_loop_stdout):
            run_eval_loop(code=code)
        
        python_stdout = io.StringIO()
        with contextlib.redirect_stdout(python_stdout):
            exec(compile(code, 'test', 'exec'))
        
        print(f"Your output:\n{eval_loop_stdout.getvalue()}")
        print(f"Python output:\n{python_stdout.getvalue()}")
        print(f"Match: {eval_loop_stdout.getvalue() == python_stdout.getvalue()}")
    except Exception as e:
        print(f"Error: {e}")

#test_original_fibonacci()

def test_original_sample():
    """Test the original sample file that was failing"""
    code = """
# Test the context manager part that was failing
class MyContext:
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        print(f"Entering {self.name}")
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Exiting {self.name}")
        return False

# This was only showing 1 inner context instead of multiple
result = []
with MyContext("outer"):
    for i in range(3):
        with MyContext(f"inner_{i}"):
            result.append(i)
print("Result:", result)
"""
    
    print("=== Testing Original Sample Context ===")
    try:
        eval_loop_stdout = io.StringIO()
        with contextlib.redirect_stdout(eval_loop_stdout):
            run_eval_loop(code=code)
        
        python_stdout = io.StringIO()
        with contextlib.redirect_stdout(python_stdout):
            exec(compile(code, 'test', 'exec'))
        
        print(f"Your output:\n{eval_loop_stdout.getvalue()}")
        print(f"Python output:\n{python_stdout.getvalue()}")
    except Exception as e:
        print(f"Error: {e}")

#test_original_sample()


def test_loop_in_generator():
    """Test loops inside generators"""
    test_cases = [
        ("range_loop", """
def gen():
    for i in range(3):
        yield i
print("Range loop:", list(gen()))
"""),
    ]
    
    for name, code in test_cases:
        print(f"\n=== Testing {name} ===")
        try:
            eval_loop_stdout = io.StringIO()
            with contextlib.redirect_stdout(eval_loop_stdout):
                run_eval_loop(code=code)
            
            python_stdout = io.StringIO()
            with contextlib.redirect_stdout(python_stdout):
                exec(compile(code, 'test', 'exec'))
            
            print(f"Your output: {eval_loop_stdout.getvalue()!r}")
            print(f"Python output: {python_stdout.getvalue()!r}")
        except Exception as e:
            print(f"Error: {e}")

#test_loop_in_generator()


def test_loop_as_single_statement():
    """Confirm that loops are single statements"""
    code = """
def gen():
    # This entire for loop is one statement
    for i in range(3):
        yield i
    # But it should yield 3 times, not once!

g = gen()
print("First:", next(g))
print("Second:", next(g)) 
print("Third:", next(g))
"""
    
    print("=== Testing Loop as Single Statement ===")
    try:
        eval_loop_stdout = io.StringIO()
        with contextlib.redirect_stdout(eval_loop_stdout):
            run_eval_loop(code=code)
        
        print(f"Your output:\n{eval_loop_stdout.getvalue()}")
    except Exception as e:
        print(f"Error: {e}")

#test_loop_as_single_statement()

def test_exception_propagation():
    """Test if YieldException properly propagates through for loop"""
    code = """
def gen():
    for i in range(3):
        print(f"Before yield {i}")
        yield i
        print(f"After yield {i}")

g = gen()
print("First next:", next(g))
print("Second next:", next(g))
print("Third next:", next(g))
"""
    
    print("=== Exception Propagation Test ===")
    try:
        eval_loop_stdout = io.StringIO()
        with contextlib.redirect_stdout(eval_loop_stdout):
            run_eval_loop(code=code)
        
        print(f"Your output:\n{eval_loop_stdout.getvalue()}")
    except Exception as e:
        print(f"Error: {e}")

test_exception_propagation()