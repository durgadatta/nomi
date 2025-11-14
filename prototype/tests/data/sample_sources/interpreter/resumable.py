#TODO: collect other resumable examples here as well - now in samples.py, special_cases.py etc.
def gen():
    if True:
        print("before")
        yield 1
        print("after")
    print("done")

print('should print: before after done')
g = gen()
list(g)
