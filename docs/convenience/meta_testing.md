# Meta-Programming & Testing Convenience

## Decorators / Annotations

Wrap or modify functions/classes at definition time.

**Python / Java / Kotlin / Swift**:

```python
@cache
@validate_input
def process(x: int) -> str: ...

# equivalent to: process = cache(validate_input(process))
```

```kotlin
@Deprecated("Use newMethod() instead")
fun oldMethod() { ... }
```

**Nomi** — decorators via `@` syntax already work:

```nomi
@cache
func fib(n):
    if n <= 1: return n
    return fib(n - 1) + fib(n - 2)
```

---

## Macros

Compile-time code generation and transformation.

**Rust (declarative macros)**:

```rust
macro_rules! vec_of {
    ($($x:expr),*) => { vec![$($x),*] }
}
let v = vec_of![1, 2, 3];
```

**Elixir**:

```elixir
defmacro unless(condition, do: block) do
    quote do
        if !unquote(condition), do: unquote(block)
    end
end
```

**Lisp (syntax-rules / defmacro)**:

```lisp
(defmacro when (condition &body body)
  `(if ,condition (progn ,@body)))
```

**Julia**:

```julia
macro sayhello(name)
    return :( println("Hello, ", $name) )
end
@sayhello "world"
```

**Nomi** — long-term.  `quote:` boundary for code-as-data, rewrite rules
(`expr /. pattern -> replacement`), and macro-style expansion (Track 6).

---

## Compile-Time Execution

Run arbitrary code during compilation.

**Zig (comptime) / Nim / D**:

```zig
const size = comptime computeSize();
const table = comptime generateLookupTable();
```

---

## Inline Tests / Doctests / Examples

Tests embedded in documentation or function definitions.

**Rust (doc tests)**:

```rust
/// Adds two numbers.
///
/// ```
/// assert_eq!(add(2, 3), 5);
/// ```
fn add(a: i32, b: i32) -> i32 { a + b }
```

**Python (doctest)**:

```python
def add(a, b):
    """
    >>> add(2, 3)
    5
    """
    return a + b
```

**Elixir (doctest)**:

```elixir
@doc """
Adds two numbers.

    iex> add(2, 3)
    5
"""
def add(a, b), do: a + b
```

**Nomi** (Track 8 — `examples:` blocks):

```nomi
func add(a, b):
    examples:
        add(2, 3) -> 5
        add(0, 0) -> 0
    return a + b
```

---

## Assert / Verify with Diagnostics

Assertions that show the actual values, not just "assertion failed".

**Kotlin (power-assert — via compiler plugin) / pytest**:

```kotlin
assert(person.name == "Alice")
// AssertionError: person.name == "Alice" is false
//   person.name = "Bob"
```

**Python (pytest)**:

```python
assert person.name == "Alice"
# E   AssertionError: assert 'Bob' == 'Alice'
```

---

## Code Generation / Scaffolding

Generate boilerplate from specifications.

**OpenAPI / GraphQL codegen / Protocol Buffers / Thrift**:

Generate types, serializers, and clients from schema definitions.

---

## Implementation Priority

| Feature | Effort | Impact |
|---------|--------|--------|
| Decorators | **done** | — |
| Inline tests / examples | medium | high |
| Assert with diagnostics | medium | high |
| Macros | very high | high (long-term) |
| Compile-time execution | very high | medium |
| Code generation | medium | medium |
