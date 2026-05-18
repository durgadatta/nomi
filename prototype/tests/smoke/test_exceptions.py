import io
import contextlib

import pytest

from prototype.interpreter.python.usage import run_eval_loop

pytestmark = pytest.mark.smoke


def _run_stdout(code):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_eval_loop(code=code)
    return buf.getvalue()


def test_basic_matching():
    output = _run_stdout("""
try:
    raise ValueError("test")
except ValueError:
    print("Caught ValueError")
""")
    assert "Caught ValueError" in output


def test_catch_as():
    output = _run_stdout("""
try:
    raise ValueError("test message")
except ValueError as e:
    print(f"Caught with message: {e}")
""")
    assert "Caught with message: test message" in output


def test_else_block():
    output = _run_stdout("""
try:
    print("No exception")
except:
    print("This should not print")
else:
    print("Else block executed")
print("All tests passed")
""")
    assert "Else block executed" in output
    assert "All tests passed" in output


def test_if_raise():
    output = _run_stdout("""
total = 15
try:
    if total > 10:
        raise ValueError("Total too large")
except ValueError as e:
    print(f"Caught: {e}")
    total = -1
print(f"After try-except, total: {total}")
""")
    assert "After try-except, total: -1" in output
