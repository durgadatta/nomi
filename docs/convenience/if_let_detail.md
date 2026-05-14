# If-Let — Pattern-Matching Guard

> Status: **implemented**.  `if pattern = expr: body` desugars to
> `match expr: case pattern: body; case _: pass`.
>
> Focused detail note. For the overall pattern family and admission decisions,
> start with [patterns.md](patterns.md).

## What It Is

If-let combines conditional branching with structural pattern matching.
Instead of testing a boolean:

```nomi
# regular if — tests truthiness
if x > 0:
    sign = "positive"
```

You test whether a value *matches a shape*:

```nomi
# if-let — tests pattern match, binds variables on success
if 42 = x:
    meaning = "found"
```

The form is `if PATTERN = EXPRESSION:` — pattern on the **left**,
expression on the **right**.  The body runs only when `EXPRESSION`
matches `PATTERN`.  If the pattern contains capture names (bare
identifiers), those names are bound to the matched values inside the
body.

## If-Let ≠ Regular If

| | Regular `if` | If-let `if pat = expr` |
|---|---|---|
| **What it tests** | Truthiness of an expression | Structural match of `expr` against `pat` |
| **Binding** | No new bindings | Captures in `pat` are bound in body |
| **Keyword** | `if`, `elif`, `else` | `if`, `else` (no `elif`) |
| **Desugars to** | `if cond: ...` (native) | `match expr: case pat: ...; case _: ...` |
| **Always matches?** | Truthy values only | Capture-only patterns match everything |

### Concrete Differences

#### 1. Regular `if` tests boolean expressions

```nomi
# regular: condition must be a boolean-ish expression
if x > 0:
    print("positive")

if x:                      # truthiness check (x is truthy/falsy)
    print("x is truthy")
```

#### 2. If-let tests structural patterns

```nomi
# if-let: does x equal the literal 42?
x = 42
if 42 = x:
    result = "yes"         # runs (x matches 42)

x = 5
if 42 = x:
    result = "yes"         # does NOT run (x is 5, not 42)
```

#### 3. If-let binds captured variables

```nomi
# capture pattern: val captures whatever value x holds
x = 99
if val = x:
    print(val)             # prints 99 (val bound to x's value)
```

This has **no regular-if equivalent** — a regular `if` cannot introduce
a new variable binding scoped to its body.

#### 4. Regular `if` has `elif`; if-let does not

```nomi
# regular if supports elif chains
if x > 100:
    label = "huge"
elif x > 10:
    label = "big"
else:
    label = "small"

# if-let: no elif — use multiple if-lets or match instead
if 0 = x:
    label = "zero"
if 1 = x:                  # second independent if-let
    label = "one"
```

For multi-pattern branching, use piecewise function guards or `match`
directly:

```nomi
label = describe(x) where:
    describe(n) when n > 100 = "huge"
    describe(n) when n > 10 = "big"
    describe(n) = "small"
```

#### 5. If-let with `else` catches non-matches

```nomi
x = 5
if 42 = x:
    label = "found"
else:
    label = "not found"    # runs (x doesn't match 42)
```

### Pattern Kinds That Work in If-Let

All `match` patterns work:

| Pattern | Example | When it matches |
|---------|---------|----------------|
| **Literal** | `if 42 = x:` | `x == 42` |
| **Capture** | `if val = x:` | Always; binds `val` to `x` |
| **Sequence** | `if [a, b] = xs:` | `xs` is a 2-element iterable |
| **Or** | `if 1 \| 2 = x:` | `x == 1 or x == 2` |
| **Class** | `if Some(v) = opt:` | Haskell/Rust-style variant check |

```nomi
# sequence destructuring
if [a, b, c] = triple:
    sum = a + b + c

# or-pattern
if 1 | 2 | 3 = roll:
    label = "small roll"

# class pattern (if classes with __match_args__ exist)
if Point(x, y) = origin:
    print(x, y)
```

## If-Let vs Match — When to Use Which

| Situation | Use |
|-----------|-----|
| One pattern to check, fallthrough to else | `if pat = val:` |
| Multiple patterns on same value | `match val:` |
| Need guards on patterns | `match val: case pat if cond:` |
| Want the result as an expression | Piecewise function with guards |

## Desugaring Detail

The transformer in `prototype/parser/nomi/functions.py:if_let_stmt`
converts:

```nomi
if pattern = expr:
    body
else:
    else_body
```

Into:

```nomi
match expr:
    case pattern: body
    case _: else_body      # (empty body if no else clause)
```

This means if-let inherits all of `match`'s semantics: guard evaluation,
variable scoping, and pattern-matching precedence.

## Edge Cases

### Pattern is a bare identifier (capture)

```nomi
if x = 42:
    result = x             # x is 42 here
```

`x` is a *new binding* inside the if-body, shadowing any outer `x`.  The
pattern `x` always matches, so this is effectively `x = 42; result = x`
but scoped to the if-body.

### Expression-side variable must be defined

```nomi
if 42 = x:                 # ERROR: name 'x' is not defined
    body
```

The expression on the right of `=` must be evaluable.  Unlike the
capture names on the left, it is not introduced by the if-let.

### Empty else clause

```nomi
if 42 = x:
    result = "yes"
else:
    pass                   # explicit no-op; or omit else entirely
```

Without `else`, a non-match simply does nothing (same as `match` without
a wildcard case).

## Related Features

| Feature | Relationship |
|---------|-------------|
| `match` statement | If-let desugars to it |
| Piecewise guards | Multi-branch alternative to if-let |
| `where` clause | Can host helper functions for complex matching |
| Guarded equations | `sign(n) when n > 0 = 1` — similar conditional spirit |

## Reference: Languages with If-Let

| Language | Syntax |
|----------|--------|
| Rust | `if let Some(v) = opt { ... }` |
| Swift | `if let v = opt { ... }` |
| Kotlin | `if (x is String) { val s = x; ... }` (smart-cast) |
| Scala 3 | `opt match { case Some(v) => ... }` (match preferred) |
| Nomi | `if Some(v) = opt: body` |
