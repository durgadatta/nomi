"""
Smoke test: Exception handling (try/except/else/finally).

Runs a few inline programs through the Python interpreter to quickly
verify that exception matching, bare except, and else blocks work.

Run manually::

    python3 prototype/tests/smoke/test_exceptions.py
"""

import io
import contextlib
from prototype.interpreter.python.usage import run_eval_loop


def _run_and_print(label, code):
    print(f"\n=== {label} ===")
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run_eval_loop(code=code)
        print(buf.getvalue(), end="")
    except Exception as e:
        print(f"ERROR: {e}")


def test_basic_matching():
    _run_and_print("Basic exception matching", """
try:
    raise ValueError("test")
except ValueError:
    print("Caught ValueError")
""")

def test_catch_as():
    _run_and_print("Exception with 'as'", """
try:
    raise ValueError("test message")
except ValueError as e:
    print(f"Caught with message: {e}")
""")

def test_else_block():
    _run_and_print("Try/except/else", """
try:
    print("No exception")
except:
    print("This should not print")
else:
    print("Else block executed")
print("All tests passed")
""")

def test_if_raise():
    _run_and_print("Conditional raise in try", """
total = 15
try:
    if total > 10:
        raise ValueError("Total too large")
except ValueError as e:
    print(f"Caught: {e}")
    total = -1
print(f"After try-except, total: {total}")
""")


if __name__ == "__main__":
    test_basic_matching()
    test_catch_as()
    test_else_block()
    test_if_raise()
