#TODO: collect other resumable examples here as well - now in samples.py, special_cases.py etc.

from contextlib import contextmanager

def gen():
    if True:
        print("before")
        yield 1
        print("after")
    print("done")

print('should print: before after done')
g = gen()
list(g)


@contextmanager
def cm():
    print("enter")
    try:
        yield
    finally:
        print("exit")

def gen():
    with cm():
        print("before yield")
        yield 1
        print("after yield")
    print("done")

list(gen())#print: "enter", "before_yield" "after yield", "exit", "done" 
