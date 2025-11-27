def gen():
    for i in range(2):
        for j in range(2):
            yield f"outer={i}, inner={j}, first"
            yield f"outer={i}, inner={j}, second"
    return "done"

g = gen()
results = []
try:
    while True:
        results.append(next(g))
except StopIteration as e:
    results.append(e.value)

print("Results:", results)
# Should get: 
# outer=0, inner=0, first
# outer=0, inner=0, second  
# outer=0, inner=1, first
# outer=0, inner=1, second
# outer=1, inner=0, first
# outer=1, inner=0, second
# outer=1, inner=1, first
# outer=1, inner=1, second
# done
