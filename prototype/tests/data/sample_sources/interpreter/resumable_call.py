def receiver(a, b, c=None):
    return f"a={a}, b={b}, c={c}"

def gen():
    result = receiver(
        (yield 1),
        (yield 2),
        c=(yield 3)
    )
    return result

g = gen()
val1 = next(g)  # 1
print(f"val1 = {val1}")
assert val1 == 1, f"Expected 1, got {val1}"

val2 = g.send(10)  # 2
print(f"val2 = {val2}")
assert val2 == 2, f"Expected 2, got {val2}"

val3 = g.send(20)  # 3
print(f"val3 = {val3}")
assert val3 == 3, f"Expected 3, got {val3}"

try:
    g.send(30)  # "a=10, b=20, c=30"
except StopIteration as e:
    result = e.value
    print(f"Final result = {result}")
    assert result == "a=10, b=20, c=30", f"Expected 'a=10, b=20, c=30', got {result}"

print("Call with yields test passed")
