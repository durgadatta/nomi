# Test 1: Basic yield expression
def gen1():
    x = yield 1
    return x

print("=== Test 1: Basic x = yield y ===")
g = gen1()
val1 = next(g)
print(f"First yield: {val1}")
assert val1 == 1

try:
    g.send(10)
except StopIteration as e:
    print(f"Generator returned: {e.value}")
    assert e.value == 10
print("Test 1 passed\n")

# Test 2: Multiple yield expressions
def gen2():
    x = yield 1
    y = yield 2  
    return x + y

print("=== Test 2: Multiple x = yield y ===")
g = gen2()
a = next(g)
print(f"First yield: {a}")
assert a == 1

b = g.send(10)
print(f"Second yield: {b}")
assert b == 2

try:
    g.send(20)
except StopIteration as e:
    print(f"Generator returned: {e.value}")
    assert e.value == 30
print("Test 2 passed\n")

# Test 3: Multiple yields with prints
def gen3():
    x = yield 1
    print(f"Received x = {x}")
    y = yield 2
    print(f"Received y = {y}") 
    z = yield 3
    print(f"Received z = {z}")
    return x + y + z

print("=== Test 3: Multiple yields with prints ===")
g = gen3()
a = next(g)
print(f"First yield: {a}")
assert a == 1

b = g.send(100)
print(f"Second yield: {b}")
assert b == 2

c = g.send(200)
print(f"Third yield: {c}")
assert c == 3

try:
    g.send(300)
except StopIteration as e:
    print(f"Generator returned: {e.value}")
    assert e.value == 600
print("Test 3 passed\n")

# Test 4: Yield in loop
def gen4():
    total = 0
    for i in range(3):
        x = yield i
        print(f"Iteration {i}, received {x}")
        total += x
    return total

print("=== Test 4: Yield in loop ===")
g = gen4()
a = next(g)
print(f"First yield: {a}")
assert a == 0

b = g.send(10)
print(f"Second yield: {b}")
assert b == 1

c = g.send(20)
print(f"Third yield: {c}")
assert c == 2

try:
    g.send(30)
except StopIteration as e:
    print(f"Generator returned: {e.value}")
    assert e.value == 60
print("Test 4 passed\n")

print("All tests passed")
