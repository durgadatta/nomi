# Custom decorator with arguments
def retry(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except ValueError:
                    continue
            return None
        return wrapper
    return decorator

# Custom context manager
class MyContext:
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        print(f"Entering {self.name}")
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Exiting {self.name}")
        return False

# Generator function
def fibonacci(n):
    a, b = 0, 1
    results = []
    for _ in range(n):
        #yield a
        results.append(a)
        a, b = b, a + b
    return results

# Decorated function with complex logic
@retry(3)
def risky_operation(x):
    if x < 0:
        raise ValueError("Negative input")
    return x * 2

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


p=Point(1,2)
p.x + p.y

# Nested comprehensions
nested_list = [[i + j for j in range(3)] for i in range(3)]
nested_dict = {i: {j: i * j for j in range(1, 4)} for i in range(1, 3)}

# Lambda with defaults and complex expression
complex_lambda = lambda x, y=10: x + y if x > 0 else x - y

# Generator expression
gen_exp = (x * x for x in range(5))

# Complex match statement
data = {'type': 'point', 'x': 10, 'y': 20}
match data:
    case {'type': 'point', 'x': x, 'y': y}:
        point_result = x + y
    case {'type': 'line', **rest}:
        point_result = sum(rest.values())
    case _:
        point_result = 0

# Main logic with loops, conditionals, and context managers
result = []
total = 0
with MyContext("outer"):
    for i in fibonacci(5):
        with MyContext(f"inner_{i}"):
            if i % 2 == 0:
                total += risky_operation(i)
            else:
                total += complex_lambda(i)
        result.append(i)
    try:
        if total > 10:
            raise ValueError("Total too large")
    except ValueError as e:
        total = -1

# Using generator expression
gen_sum = 0 #sum(gen_exp)

# Slice and subscript operations
slice_result = result[1:4:2]

# Import and advanced math
import math
angle = math.pi / 4
trig_result = math.sin(angle) + math.cos(angle)


#simple generator
print('\n***testing simple generator****\n')
def gen():
    yield 1
    yield 2
    yield 3
    yield 4

g = gen()
first_g = next(g)
print(f'{first_g=}')
second_g = next(g)
print(f'{second_g=}')
next(g)
next(g)

non_g = None
try:
    non_g = next(g)
except StopIteration:
    non_g = 'intercepted'
    print('successfully intercepted StopIteration')
print(f'{non_g=}')


# Print results
print(f"Nested list: {nested_list}")
print(f"Nested dict: {nested_dict}")
print(f"Fibonacci result: {result}")
print(f"Total: {total}")
print(f"Point result: {point_result}")
print(f"Generator sum: {gen_sum}")
print(f"Slice result: {slice_result}")
print(f"Trig result: {trig_result}")
