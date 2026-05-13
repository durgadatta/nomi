# Implicit Functions in Nomi — Nuance & Comparison

Nomi offers five shorthands for building anonymous functions without
writing explicit parameter lists.  They look similar but differ in how
parameters are named and scoped.  This note makes the distinctions
precise.

## The Five Forms

### 1. Underscore Hole (`_`) — Scala-style

```
double = _ * 2
upcase = _.upper()
add = _ + _
```

- Scope: **outermost** expression containing any `_`.
- Parameter names: `__1`, `__2`, ... in left-to-right occurrence order.
- Single `_` → 1 param.  Two `_` → 2 params.
- `_` stops being a hole if it has been assigned in the same scope (lets
  you use `_` as a throwaway variable).

```nomi
# single hole
inc = _ + 1                       # (__1) => __1 + 1

# two holes (positional by order of appearance)
diff = _ - _                      # (__1, __2) => __1 - __2

# not a hole — _ is an assigned variable
_ = 42
v = _ + 1                         # 43
```

### 2. Positional Dollar Holes (`$1`, `$2`, ...) — Swift-style

```
double = $1 * 2
add = $1 + $2
```

- Scope: outermost expression containing any `$N`.
- Parameter names: `__1`, `__2`, ... exactly as the numbers specify.
- The number after `$` IS the parameter position.  `$3` without `$1` or
  `$2` creates 3 params (the first two unused).

```nomi
third = $3                         # (__1, __2, __3) => __3
sum = $1 + $2                      # (__1, __2) => __1 + __2
```

### 3. Named Dollar Holes (`$name`) — named parameters

```
full = $first + " " + $last
desc = $person.name + " (" + $person.age + ")"
```

- Scope: outermost expression containing any `$name`.
- Parameter names: the identifier after `$` IS the parameter name.
- Duplicate `$x` references map to the same parameter.
- Order: **first-encountered** order (tree walk), then positional `$N`
  appended.

```nomi
dup = $x + $x                      # (x) => x + x
swap = $y + $x                     # (y, x) => y + x
mix = $name + $1                   # (name, __1) => name + __1
```

### 4. Operator Sections (`(+)`, `(+2)`, `(2*)`) — Haskell-style

```
plus_two = (+2)                    # (__s) => __s + 2
times_two = (2*)                   # (__s) => 2 * __s
plus = (+)                         # (__a, __b) => __a + __b
```

- Scope: exactly one parenthesized binary operator.
- `(op rhs)` → `(__s) => __s op rhs`
- `(lhs op)` → `(__s) => lhs op __s`
- `(op)` → `(__a, __b) => __a op __b`
- All binary operators are supported: `+`, `-`, `*`, `/`, `//`, `%`,
  `**`, `<<`, `>>`, `&`, `|`, `^`, `@`.

### 5. Arrow Functions (`=>`) — explicit lambda

```
square = (x) => x * x
add = (a, b) => a + b
inc = x => x + 1                  # single-param no-parens
```

- Fully explicit: you name every parameter.
- Supports multi-line bodies via `func` keyword.

## Comparison Table

| Form | Params named by | Order rule | Duplicates |
|------|----------------|------------|------------|
| `_` | `__1`, `__2`, ... | occurrence | N/A (no reuse) |
| `$1`, `$2` | `__1`, `__2`, ... | explicit number | N/A (no reuse) |
| `$name` | identifier after `$` | first-encountered | merged to 1 param |
| `(+2)` | `__s` or `__a`/`__b` | single/two fixed | N/A |
| `=>` | you write them | your list | — |

## When to Use Which

| Use case | Best form |
|----------|-----------|
| Quick single-arg operation | `_ * 2`, `$1 * 2`, `(+2)` |
| Method call on arg | `_.upper()`, `$1.name` |
| Multiple args, order matters | `(x, y) => x + y` (explicit) |
| Multiple args, names matter | `$first + $last` (self-documenting) |
| Operator-only transform | `(+2)`, `(2*)`, `(+)` |
| One parameter reused | `$x + $x` |
| Need explicit names for clarity | `=>` or `$name` |
| Throwaway/non-hole `_` | `for _ in xs:` |

## Edge Cases

**Mixed `_` + `$N` / `$name` in one expression** — technically works (each
hole type is a separate pass), but produces nested lambdas.  Avoid mixing
hole types.

**`$name` where `name` collides with existing variable** — the `$name`
is replaced with the bare name in the lambda body.  The lambda's own
parameter shadows any outer binding.  This is intentional: the `$`
prefix is only the syntax for creating the parameter, not part of its
runtime name.

```nomi
x = 10
f = $x + 1                        # (x) => x + 1
result = f(5)                      # 6 (uses the param, not outer x=10)
```

**`$1` without `$2`** — if the highest `$N` is `$3`, params `__1` through
`__3` are all created even if `__1` and `__2` are unused in the body.

```nomi
just_third = $3                   # (__1, __2, __3) => __3
```
