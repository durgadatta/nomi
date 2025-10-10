"""
Comprehensive Python parsing test — exercises a wide range of AST constructs.
"""

import math
import operator
from functools import lru_cache as cache, reduce
from typing import Callable, List, Dict, Optional, Union, Tuple
from collections import namedtuple
import tempfile
import re

# --- Constants and Global Variables ---
CONST = 42
PI = math.pi
GLOBAL_COUNTER = 0

# --- Simple function with defaults, returns, and control flow ---
def add(a: float, b: float = 10.0) -> float:
    """Add two numbers with conditional logic."""
    result = a + b
    if result > 50:
        return result
    elif result == 50:
        return 0
    else:
        return -result

# --- Function with nested loops, continue, and break ---
def matrix_sum(matrix: List[List[int]]) -> int:
    total = 0
    for row in matrix:
        for elem in row:
            if elem < 0:
                continue
            if elem > 100:
                break
            total += elem
        else:
            continue
        break
    return total

# --- Function with while, break, and else ---
def find_first_divisible(numbers: List[int], divisor: int) -> Optional[int]:
    i = 0
    while i < len(numbers):
        if numbers[i] % divisor == 0:
            return numbers[i]
        i += 1
    else:
        return None

# --- Nested functions, closures, and type annotations ---
def outer(x: int) -> Callable[[int], int]:
    def inner(y: int = 5) -> int:
        nonlocal x
        x += 1
        return x + y
    return inner

# --- Decorators, *args, **kwargs, keyword-only arguments ---
@cache
def compute_sum(*args, scale: float = 1.0, **kwargs) -> float:
    """Compute sum of args and kwargs values, scaled."""
    total = sum(args) + sum(kwargs.values())
    return total * scale

# --- Class with inheritance, classmethod, staticmethod, and properties ---
class Vector:
    kind = "vector"
    _registry = []

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        Vector._registry.append(self)

    @classmethod
    def count_vectors(cls) -> int:
        return len(cls._registry)

    @staticmethod
    def distance(p1, p2) -> float:
        return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5

    @property
    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __str__(self) -> str:
        return f"Vector({self.x}, {self.y})"

class Point(Vector):
    kind = "2D_point"

    def move(self, dx: float, dy: float) -> "Point":
        self.x += dx
        self.y += dy
        return self

# --- Named tuple ---
Coordinate = namedtuple("Coordinate", ["x", "y"])

# --- Comprehensions (list, set, dict, nested) ---
squares = [i * i for i in range(10)]
evens = {i for i in range(20) if i % 2 == 0}
mapping = {f"key{i}": i * i for i in range(5)}
nested = [(x, y) for x in range(3) for y in range(3) if x + y < 4]
gen_exp = (i ** 3 for i in range(4))

# --- Unpacking (tuple, list, dict) ---
a, b, *rest, last = [1, 2, 3, 4, 5]
x, y = Coordinate(10, 20)
merged = {**mapping, "extra": 100}

# --- Exception handling with multiple except clauses ---
def safe_divide(a: float, b: float) -> Optional[float]:
    try:
        result = a / b
    except ZeroDivisionError as e:
        print(f"Error: {e}")
        return None
    except TypeError as e:
        print(f"Type Error: {e}")
        return None
    else:
        return result
    finally:
        print("Division attempt completed")

# --- Boolean operations, comparisons, and ternary operator ---
is_valid = (CONST > 20) and (len(squares) == 10) or not False
status = "success" if is_valid else "failure"

# --- Lambda with defaults, *args, **kwargs ---
complex_op = lambda x, y=1, *args, **kwargs: (x + y, sum(args), sum(kwargs.values()))

# --- Function calls with unpacking ---
nums = [1, 2, 3, 4]
kwargs = {"a": 5, "b": 10}
result = compute_sum(*nums, **kwargs, scale=2)

# --- With statement with multiple context managers ---
def process_files():
    with tempfile.TemporaryFile() as f1, tempfile.TemporaryFile() as f2:
        f1.write(b"Test1")
        f2.write(b"Test2")
        f1.seek(0)
        f2.seek(0)
        return f1.read(), f2.read()

# --- Slices, subscripts, and complex literals ---
data = list(range(15))
sliced = data[1:10:2]
matrix = [[i * j for j in range(4)] for i in range(4)]
complex_num = 3 + 4j

# --- Assertions, pass, del, and global/nonlocal ---
def update_global():
    global GLOBAL_COUNTER
    GLOBAL_COUNTER += 1
    assert GLOBAL_COUNTER > 0
    pass

# --- F-strings with expressions ---
name = "Python"
version_info = f"Running {name} version {CONST / 2:.2f}"

# --- Match statement with complex patterns (Python 3.10+) ---
def parse_input(value: Union[int, str, list]) -> str:
    match value:
        case 0:
            return "zero"
        case int(n) if n > 0:
            return "positive"
        case str(s) if re.match(r"\d+", s):
            return "numeric string"
        case ["error", *rest]:
            return f"error with {rest}"
        case _:
            return "unknown"

# --- Generator function ---
def fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# --- Walrus operator (Python 3.8+) ---
def process_data(data: List[int]) -> List[int]:
    return [y for x in data if (y := x * 2) > 10]

# --- Set operations and built-in functions ---
unique_nums = {1, 2, 2, 3}
sorted_squares = sorted(squares, reverse=True)
reduced = reduce(operator.add, squares, 0)

# --- Type hints with Union, Optional, and complex types ---
def process_value(value: Union[int, str], default: Optional[int] = None) -> Tuple[bool, str]:
    return (isinstance(value, int), str(value))


if __name__ == "__main__":
    # Create instances and test methods
    p1 = Point(3, 4)
    p2 = Point(0, 0)
    p1.move(1, 1)
    
    # Test various constructs
    #print(f"Factorial(5): {factorial(5)}")
    print(f"Point magnitude: {p1.magnitude}")
    print(f"Vector count: {Vector.count_vectors()}")
    print(f"Distance between points: {Vector.distance(p1, p2)}")
    print(f"Safe divide: {safe_divide(10, 2)}")
    print(f"Status: {status}")
    print(f"Version info: {version_info}")
    print(f"Fibonacci: {list(fibonacci(6))}")
    print(f"Processed data: {process_data([1, 2, 3, 4, 5])}")
    print(f"Parsed input: {parse_input(['error', 1, 2])}")
    print("All tests completed successfully.")
    