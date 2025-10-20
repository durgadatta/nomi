import contextlib

# for parsing test of "with"
with contextlib.suppress(Exception) as dummy:
    a = 1/0

print("with-stmt parsing works")
