def make_func():
    x = []
    
    def func(y, lst=x):  # Default captures x when func is DEFINED
        lst.append(y)
        return lst
    
    return func

f = make_func()
print("f(1):", f(1))  # [1]
print("f(2):", f(2))  # [1, 2]

# Different function should have different default
g = make_func()
print("g(3):", g(3))  # [3] (not [1, 2, 3])
