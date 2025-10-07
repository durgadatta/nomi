# sample_test.py
"""
Comprehensive Python parsing test — exercises most AST constructs.
"""

import math
from functools import lru_cache as cache
from typing import Callable
import tempfile

CONST = 42
PI = math.pi

# --- Simple function with defaults, returns, and control flow ---
def add(a, b=10):
    """Simple add function"""
    result = a + b
    if result > 50:
        return result
    elif result == 50:
        return 0
    else:
        return -result


# --- Function with loops and conditionals ---
def factorial(n):
    f = 1
    for i in range(1, n + 1):
        f *= i
    return f


# --- Function with while and break/continue ---
def find_first_even(nums):
    i = 0
    while i < len(nums):
        if nums[i] % 2 == 0:
            break
        i += 1
    else:
        return None
    return nums[i]


# --- Nested function + closure + annotations ---
def outer(x: int) -> Callable[[int], int]:
    def inner(y: int = 5) -> int:
        return x + y
    return inner


# --- Decorators, *args, **kwargs, kwonly ---
@cache
def demo(*args, scale=1, **kwargs):
    total = sum(args) + sum(kwargs.values())
    return total * scale


# --- Class definition with methods and comprehension attributes ---
class Point:
    kind = "2D"
    all_points = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
        Point.all_points.append(self)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        return self

    @property
    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


# --- Instance creation and method chaining ---
p = Point(1, 2)
p.move(3, 4)

# --- Comprehensions ---
squares = [i * i for i in range(5)]
evens = {i for i in range(10) if i % 2 == 0}
mapping = {i: i * i for i in range(5)}
gen = (i ** 2 for i in range(3))

# --- Tuple/list/dict unpacking ---
a, b, *rest = [1, 2, 3, 4]
x, y = (10, 20)
merged = {**mapping, "extra": 99}

# --- Try/Except/Finally + raise ---
try:
    value = 10 / 0
except ZeroDivisionError as e:
    print("Error:", e)
    value = None
finally:
    print("Done (finally block executed)")

# --- Boolean ops, comparisons, ternary ---
double = lambda x: x * 2
check = (CONST > 10) and (double(5) == 10) or not False
result = "ok" if check else "fail"

# --- Function call with *args, **kwargs ---
nums = [1, 2, 3]
opts = {"x": 10, "y": 5}
v = demo(*nums, **opts, scale=2)

# --- With statement, aliasing ---
with tempfile.TemporaryFile() as fp:
    fp.write(b'Hello world!')
    fp.seek(0)
    fp.read()


# --- Slices, subscripts, and complex literals ---
data = [i for i in range(10)]
subset = data[2:8:2]
matrix = [[i + j for j in range(3)] for i in range(3)]

# --- Assertions, pass, del ---
assert len(matrix) == 3
pass
del subset

# --- F-string and formatted output ---
name = "World"
greeting = f"Hello, {name}! The value is {CONST * 2}"

# --- Match statement (Python 3.10+) ---
def classify(value):
    match value:
        case 0:
            return "zero"
        case 1 | 2:
            return "small"
        case _:
            return "other"

# --- Lambda with defaults, *args, **kwargs ---
combine = lambda a, b=1, *args, **kw: (a + b, args, kw)

# --- Complex comprehension nesting ---
nested = [(x, y) for x in range(3) for y in range(3) if x != y]

# --- End marker ---
if __name__ == "__main__":
    print("All tests passed.")
    print("factorial(5):", factorial(5))
    print("Point magnitude:", p.magnitude)
    print("Check result:", check)
    print("Greeting:", greeting)
