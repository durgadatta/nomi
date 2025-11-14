def gen():
    try:
        yield 1
        yield 2
    finally:
        print('finally')


g = gen()

print(f"first yield: {next(g)}")
print('in between')
print(f"second yield: {next(g)}")
try:
    print(next(g))
except StopIteration:
    print('to check if finally is executed')

def gen():
    for x in [1, 2]:
        yield x                # throw() resumes here
        print("after yield")

g = gen()
print(next(g))
try:
    g.throw(ValueError("boom"))
except ValueError:
    print('Error thrown inside for')

    