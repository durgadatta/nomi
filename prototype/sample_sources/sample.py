# sample_test.py

import math
from collections import defaultdict

CONST = 42

def add(a, b=10):
    """Simple add function"""
    result = a + b
    if result > 50:
        return result
    elif result == 50:
        return 0
    else:
        return -result

def factorial(n):
    f = 1
    for i in range(1, n+1):
        f *= i
    return f

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        return self

p = Point(1, 2)
p.move(3, 4)

squares = [i*i for i in range(5)]
evens = {i for i in range(10) if i % 2 == 0}
mapping = {i: i*i for i in range(5)}

try:
    value = 10 / 0
except ZeroDivisionError as e:
    print("Error:", e)
finally:
    print("Done")

# Lambda, boolean ops, comparisons
double = lambda x: x * 2
check = (CONST > 10) and (double(5) == 10) or not False

# Function call with *args and **kwargs
def demo(*args, **kwargs):
    return sum(args) + sum(kwargs.values())

v = demo(1, 2, 3, x=10, y=5)
