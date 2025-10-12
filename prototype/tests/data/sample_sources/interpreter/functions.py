# Comprehensive Function Feature Tests

print("=== FUNCTION FEATURE TESTS ===")

# 1. Basic Functions
print("\n1. BASIC FUNCTIONS")

def simple_function():
    return "Hello from simple function"

def function_with_args(a, b):
    return f"a={a}, b={b}"

def function_with_defaults(a, b=10, c=20):
    return f"a={a}, b={b}, c={c}"

print(f"simple_function(): {simple_function()}")
print(f"function_with_args(1, 2): {function_with_args(1, 2)}")
print(f"function_with_defaults(5): {function_with_defaults(5)}")
print(f"function_with_defaults(5, 6): {function_with_defaults(5, 6)}")
print(f"function_with_defaults(5, 6, 7): {function_with_defaults(5, 6, 7)}")

# 2. Functions with *args and **kwargs
print("\n2. *ARGS AND **KWARGS")

def function_with_star_args(*args):
    return f"args: {args}, count: {len(args)}"

def function_with_kwargs(**kwargs):
    return f"kwargs: {kwargs}"

def function_with_both(a, b, *args, **kwargs):
    return f"a={a}, b={b}, args={args}, kwargs={kwargs}"

print(f"function_with_star_args(1, 2, 3): {function_with_star_args(1, 2, 3)}")
print(f"function_with_kwargs(x=1, y=2): {function_with_kwargs(x=1, y=2)}")
print(f"function_with_both(1, 2, 3, 4, x=5, y=6): {function_with_both(1, 2, 3, 4, x=5, y=6)}")

# 3. Lambda Functions
print("\n3. LAMBDA FUNCTIONS")

square = lambda x: x * x
add = lambda x, y=10: x + y
complex_lambda = lambda x, *args, **kwargs: f"x={x}, args={args}, kwargs={kwargs}"

print(f"square(5): {square(5)}")
print(f"add(3): {add(3)}")
print(f"add(3, 7): {add(3, 7)}")
print(f"complex_lambda(1, 2, 3, a=4): {complex_lambda(1, 2, 3, a=4)}")

# 4. Nested Functions and Closures
print("\n4. NESTED FUNCTIONS AND CLOSURES")

def outer_function(x):
    def inner_function(y):
        return x + y
    return inner_function

def counter(initial=0):
    count = initial
    def increment(step=1):
        nonlocal count
        count += step
        return count
    return increment

def make_multiplier(factor):
    def multiplier(x):
        return x * factor
    return multiplier

# Test closures
closure_func = outer_function(10)
print(f"closure_func(5): {closure_func(5)}")

counter1 = counter()
counter2 = counter(100)
print(f"counter1(): {counter1()}")
print(f"counter1(2): {counter1(2)}")
print(f"counter2(): {counter2()}")
print(f"counter2(5): {counter2(5)}")

double = make_multiplier(2)
triple = make_multiplier(3)
print(f"double(5): {double(5)}")
print(f"triple(5): {triple(5)}")

# 5. Generator Functions
print("\n5. GENERATOR FUNCTIONS")

def simple_generator():
    yield 1
    yield 2
    yield 3

def fibonacci_generator(limit):
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1

def generator_with_loop(n):
    for i in range(n):
        yield i * 2

# Test generators
print("Simple generator:", list(simple_generator()))
print("Fibonacci generator:", list(fibonacci_generator(6)))
print("Generator with loop:", list(generator_with_loop(5)))

# Test generator iteration
gen = simple_generator()
print(f"next(gen): {next(gen)}")
print(f"next(gen): {next(gen)}")
print(f"next(gen): {next(gen)}")

# 6. Recursive Functions
print("\n6. RECURSIVE FUNCTIONS")

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci_recursive(n):
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

def sum_list(lst):
    if not lst:
        return 0
    return lst[0] + sum_list(lst[1:])

print(f"factorial(5): {factorial(5)}")
print(f"fibonacci_recursive(6): {fibonacci_recursive(6)}")
print(f"sum_list([1, 2, 3, 4, 5]): {sum_list([1, 2, 3, 4, 5])}")

# 7. Function Decorators
print("\n7. FUNCTION DECORATORS")

def simple_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

def timer_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

def repeat_decorator(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            results = []
            for i in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

# Test decorators
@simple_decorator
def decorated_add(a, b):
    return a + b

@repeat_decorator(3)
def repeat_hello(name):
    return f"Hello, {name}!"

print(f"decorated_add(3, 4): {decorated_add(3, 4)}")
print(f"repeat_hello('World'): {repeat_hello('World')}")

# 8. Higher-Order Functions
print("\n8. HIGHER-ORDER FUNCTIONS")

def apply_function(func, value):
    return func(value)

def compose(f, g):
    return lambda x: f(g(x))

def filter_even(numbers):
    return list(filter(lambda x: x % 2 == 0, numbers))

def map_square(numbers):
    return list(map(lambda x: x * x, numbers))

def reduce_sum(numbers):
    from functools import reduce
    return reduce(lambda x, y: x + y, numbers, 0)

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f"apply_function(square, 5): {apply_function(square, 5)}")
print(f"filter_even(numbers): {filter_even(numbers)}")
print(f"map_square(numbers): {map_square(numbers)}")
print(f"reduce_sum(numbers): {reduce_sum(numbers)}")

# Compose example
add_one = lambda x: x + 1
multiply_by_two = lambda x: x * 2
composed = compose(add_one, multiply_by_two)
print(f"compose(add_one, multiply_by_two)(5): {composed(5)}")

# 9. Function Annotations (if supported)
print("\n9. FUNCTION ANNOTATIONS")

def annotated_function(x: int, y: str = "default") -> str:
    return f"x={x}, y={y}"

print(f"annotated_function(10, 'test'): {annotated_function(10, 'test')}")

# 10. Complex Control Flow in Functions
print("\n10. COMPLEX CONTROL FLOW")

def function_with_try_except(x, y):
    try:
        result = x / y
        return f"Division successful: {result}"
    except ZeroDivisionError:
        return "Cannot divide by zero"
    finally:
        print("This always executes")

def function_with_loops(n):
    result = []
    for i in range(n):
        if i % 2 == 0:
            continue
        if i > 7:
            break
        result.append(i)
    else:
        result.append(-1)  # Only executes if no break
    return result

def function_with_comprehensions(data):
    # List comprehension with condition
    squares = [x*x for x in data if x > 0]
    # Dict comprehension
    square_dict = {x: x*x for x in data}
    # Set comprehension  
    unique_squares = {x*x for x in data}
    return squares, square_dict, unique_squares

print(f"function_with_try_except(10, 2): {function_with_try_except(10, 2)}")
print(f"function_with_try_except(10, 0): {function_with_try_except(10, 0)}")
print(f"function_with_loops(10): {function_with_loops(10)}")

data = [1, -2, 3, -4, 5, 1, 3]
squares, square_dict, unique_squares = function_with_comprehensions(data)
print(f"function_with_comprehensions([1, -2, 3]): squares={squares}, dict={square_dict}, set={unique_squares}")

# 11. Global and Nonlocal
print("\n11. GLOBAL AND NONLOCAL")

global_var = "global"

def test_global():
    global global_var
    global_var = "modified_global"
    return global_var

def test_nonlocal():
    outer_var = "outer"
    def inner():
        nonlocal outer_var
        outer_var = "modified_outer"
        return outer_var
    return inner()

print(f"Before test_global: {global_var}")
print(f"test_global(): {test_global()}")
print(f"After test_global: {global_var}")
print(f"test_nonlocal(): {test_nonlocal()}")

# 12. Function Attributes
print("\n12. FUNCTION ATTRIBUTES")

def function_with_attrs(x):
    return x * 2

# Set function attributes
function_with_attrs.description = "Doubles the input"
function_with_attrs.author = "Test Suite"
function_with_attrs.version = 1.0

print(f"function_with_attrs(5): {function_with_attrs(5)}")
print(f"function_with_attrs.description: {function_with_attrs.description}")
print(f"function_with_attrs.author: {function_with_attrs.author}")

print("\n=== ALL FUNCTION TESTS COMPLETE ===")

# Summary
test_results = {
    "basic_functions": simple_function() == "Hello from simple function",
    "default_args": function_with_defaults(5) == "a=5, b=10, c=20",
    "star_args": function_with_star_args(1, 2, 3).startswith("args: (1, 2, 3)"),
    "lambdas": square(5) == 25,
    "closures": outer_function(10)(5) == 15,
    "generators": all([
        list(simple_generator()) == [1, 2, 3],
        list(fibonacci_generator(5)) == [0, 1, 1, 2, 3]
    ]),
    "recursion": factorial(5) == 120,
    "decorators": decorated_add(3, 4) == 7,
    "higher_order": apply_function(square, 5) == 25,
    "control_flow": function_with_try_except(10, 2).startswith("Division successful"),
    "global_scope": test_global() == "modified_global"
}

print("\nTEST SUMMARY:")
for test_name, passed in test_results.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {test_name}: {status}")

total_passed = sum(test_results.values())
total_tests = len(test_results)
print(f"\nTotal: {total_passed}/{total_tests} tests passed")