# Function Convenience

> Status: active synthesis.
>
> Scope: function-shaped convenience syntax only. This doc keeps the source
> language research, but the decision surface is Nomi's function normal form:
> parameters are bindings, the body evaluates, and the result may be checked.

## Design Pressure

Many languages make tiny functions pleasant:

- Haskell, F#, Elm, and Roc use equations, sections, currying, and composition.
- Scala, Swift, Elixir, Clojure, and Kotlin use placeholder or implicit
  parameters.
- Ruby, Kotlin, Julia, Nim, and Gleam make callback-heavy APIs read like
  ordinary blocks.
- Python keeps functions familiar and explicit, but `lambda` is too cramped
  for everyday higher-order code.

The lesson is not "adopt every spelling." The durable need is smaller:

```text
make a function value where the reader can still see its inputs, body, and role
```

Nomi should therefore keep one coherent ladder of function forms. A form lower
on the ladder is acceptable only while it remains obvious.

| Need | Preferred Nomi form | Why |
| --- | --- | --- |
| Named, block-bodied behavior | `func name(params): ...` | Most explicit; best for effects, control flow, examples, and constraints. |
| Named, expression-bodied behavior | `name(params) = expr` | Compact declaration; still names parameters. |
| Piecewise dispatch | contiguous equations with patterns and `when` guards | Function clauses reduce to pattern dispatch over parameters. |
| Anonymous expression | `(x, y) => expr` | Clear function value with explicit parameters. |
| Tiny one-argument transform | `_` or operator section | Pleasant when the argument is visually obvious. |
| Tiny multi-argument relation | `$1 + $2` or `$name` | Useful when explicit order or names improve a short expression. |
| Reusable transform pipeline | `f >>> g` / `f <<< g` today, future teaching may converge on `>>` | Composition builds a function for later; pipeline applies a value now. |
| Local helper derivation | `expr where: ...` | Keeps the main expression first while helper bindings remain local. |

## Normal Form

All accepted function conveniences reduce to this shape:

```text
receive arguments -> bind parameters -> check constraints/patterns/guards ->
evaluate body -> check result if declared -> return value
```

This is the same binding story used by assignment, block parameters, data
fields, and pattern captures. That is the important synthesis: functions are
not a separate mini-language.

```nomi
func normalize(email:(str, contains(email, "@"))) -> str:
    return email.strip().lower()

normalize(email) = email.strip().lower()

normalize = email => email.strip().lower()
```

The three forms differ in ergonomics and teaching order, not in meaning.

## The Coherence Ladder

### 1. Use `func` For Real Behavior

Use `func` when a function has multiple statements, side effects, control flow,
examples, return constraints, or enough logic that a future reader will want a
stable landmark.

```nomi
func import_people(path:Path, min_age:int = 13) -> Result[list[Person], Error]:
    rows = read_csv(path)
    return collect_results(rows |> where(_.age >= min_age) |> map(Person.decode))
```

Do not force expression sugar to carry policy-heavy code. A pleasant language
needs a calm long form.

### 2. Use Equations For Named Expressions

Equation definitions are the compact named-function form.

```nomi
add(a, b) = a + b
double x = x * 2
greet(name, greeting="Hello") = greeting + ", " + name
```

Implemented surface:

- parenthesized equations: `add(a, b) = a + b`;
- no-argument equations: `pi() = 3.14`;
- single-argument no-parens equations: `double x = x * 2`;
- defaults in equation parameters;
- `where` on equations.

Use no-parens equations sparingly. They are lovely for mathematical or
functional definitions, but calls should still use ordinary call syntax:

```nomi
double x = x * 2
result = double(5)
```

This keeps declaration brevity without introducing Haskell-style whitespace
application everywhere.

### 3. Use Piecewise Equations For Pattern Dispatch

Piecewise functions are function clauses. They reduce to ordered pattern
matching over parameters.

```nomi
fact(0) = 1
fact(n) when n > 0 = n * fact(n - 1)

sign(n) when n > 0 = 1
sign(n) when n < 0 = -1
sign(n) = 0
```

Source-language relatives:

| Source | Form | Nomi lesson |
| --- | --- | --- |
| Haskell | multiple equations and guards | Ordered clauses are readable when compact. |
| Elixir | multi-clause `def` | Function dispatch and pattern matching are the same family. |
| OCaml/F#/Rust | `match` inside functions | The long form remains `match`; equations are sugar. |

Critique:

- Good: removes boilerplate from simple classifiers, recursion, and domain
  rules.
- Risk: users may hide complex branching in many tiny clauses.
- Nomi rule: promote to `func` plus `match` once branches need statements,
  tracing, non-trivial diagnostics, or shared setup.

Open design work:

- constrained captures in equation patterns should reuse the shared binding
  engine;
- diagnostics should say which clause failed by pattern, constraint, or guard;
- non-contiguous clauses currently do not merge and should remain a diagnostic
  target.

### 4. Use `=>` For Explicit Anonymous Functions

Arrow functions are expression-level function values.

```nomi
adult = age => age >= 18
full_name = (first, last) => first + " " + last
valid = (user:User) => user.active and user.email != none
```

Use `=>` when a placeholder would make the reader reconstruct parameter names
or order. This is especially true for effects, constraints, nested calls, and
anything longer than one visual phrase.

### 5. Use Holes For Tiny Functions Only

Implicit functions are a convenience family, not a second function language.
For the full scoping reference, see the implicit function appendix
at the end of this document.

Implemented forms:

```nomi
double = _ * 2
upcase = _.upper()
add = _ + _

scale = $1 * 2
combine = $1 + $2
full = $first + " " + $last

plus_two = (+2)
times_two = (2*)
plus = (+)
```

Guidance:

| Situation | Use | Avoid |
| --- | --- | --- |
| One obvious receiver | `_.name`, `_.upper()` | adding `it` as another spelling |
| Two obvious operands | `$1 + $2`, `_ + _` | hiding argument order in a long expression |
| Reused named parameter | `$x + $x` | inventing a local name only visible through magic |
| Operator-only transform | `(+2)`, `(2*)`, `(+)` | dense tacit chains as everyday style |
| Anything with business meaning | `(user) => ...` or `func` | placeholder puzzles |

Do not add Kotlin `it`, Elixir `&1`, Clojure `%`, Swift `$0`, and Scala `_`
as parallel everyday spellings. Nomi already has enough placeholder power:
`_` for the obvious value and `$...` when position or name matters.

### 6. Keep Pipeline And Composition Separate

Pipeline applies a value now:

```nomi
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Composition builds a function for later:

```nomi
clean = strip >>> lower >>> normalize_space
result = clean("  ADA  ")
```

Current prototype tests cover `>>>` and `<<<`. The broader language spec notes
that teaching may later converge on a simpler reference operator such as `>>`.
The design rule is stable either way: do not teach pipeline and composition as
interchangeable syntax. One has data in hand; the other returns a function.

### 7. Use `where` For Local Function Support

`where` is not only function syntax, but it is crucial for pleasant function
definitions because it keeps helper bindings near the expression they explain.

```nomi
area(r) = pi * r * r where:
    pi = 3.14159

score(user) = normalized * weight where:
    normalized = clamp(user.points / max_points, 0, 1)
    weight = plan_weight(user.plan)
```

`where` should reuse ordinary binding semantics. It should not become a
separate declaration island with different scoping, validation, or diagnostics.

## Related But Separate Features

### Block Calls Are Not Just Functions

Ruby blocks, Kotlin trailing lambdas, Julia `do`, Nim block arguments, and
Gleam `use` all flatten callbacks. Nomi's accepted direction is the block-call
normal form, not another lambda punctuation:

```nomi
using(open(path)) -> file:
    text = file.read()

retry(3, on=NetworkError):
    fetch(url)
```

These are ordinary calls with attached caller-side blocks. They belong with
control policy, resources, fixtures, tracing, and future concurrency. Do not
copy brace-based trailing lambda syntax as a second block story.

### Currying And Partial Application Stay Library-First

Haskell and F# make every multi-argument function curried. That is elegant in a
language designed around it, but it would surprise users coming from Python,
JavaScript, Ruby, Swift, or Kotlin.

Nomi should prefer explicit partial functions:

```nomi
add3 = x => add(3, x)
add3 = add(3, _)          # possible future explicit partial form
```

Do not make `add(3)` silently return a function in the everyday layer. It
creates arity ambiguity and weakens call diagnostics.

### Point-Free Style Is A Specialist Tool

Tacit styles from Haskell, J, APL, BQN, Uiua, Joy, and Factor are powerful, but
they can turn ordinary programs into notation puzzles. Nomi can support small
operator sections and composition while rejecting dense point-free style as the
default teaching path.

Readable:

```nomi
mean = values => sum(values) / len(values)
```

Too compressed for everyday Nomi:

```text
mean = +/ % #
```

Keep advanced tacit or array notation in a future fenced layer, if it arrives
at all.

### Context Parameters Are A Future Capability Story

Scala `given/using`, Kotlin context receivers, implicit reader environments,
and effect systems all point at a real need: functions often require context
such as locale, database handles, permissions, clocks, or loggers.

For Nomi, this should grow from explicit values, block policies, and future
capability scopes. Do not add implicit parameters as function sugar before the
capability and explanation model exists.

## Synthesis Decisions

| Candidate | Status | Decision |
| --- | --- | --- |
| `func` declarations | implemented | Canonical long form. |
| Arrow functions | implemented | Canonical anonymous expression form. |
| Equation functions | implemented | Good compact named form. |
| Single-arg no-parens equations | implemented | Accept for declarations only; do not add whitespace calls. |
| Piecewise equations | implemented | Treat as ordered pattern-dispatch clauses. |
| Guards on equations | implemented | Same guard model as `match`. |
| Defaults in equation args | implemented | Reuse parameter binding defaults. |
| `_`, `$1`, `$name` holes | implemented | Keep; require style discipline. |
| Operator sections | implemented | Keep as tiny function sugar. |
| `where` | implemented | Keep as local binding/explanation form. |
| Composition | implemented as `>>>`/`<<<` | Keep concept; settle final teaching spelling with language spec. |
| Method references | design-needed | Prefer holes and explicit lambdas until type/member model is stable. |
| Extension functions | design-needed | Belongs with data/module/dispatch design, not convenience syntax alone. |
| Automatic currying | rejected-for-now | Too surprising for Python-compatible calls and diagnostics. |
| Broad partial application | design-needed | Consider only explicit holes or library helpers. |
| `it`, `%`, `&1`, `$0` aliases | rejected-for-now | Duplicate placeholder family. |
| Do-notation / monad sugar | research-only | Wait for Result/block/effect story. |
| Implicit/context parameters | research-only | Wait for capability scopes and explanation. |
| Dense point-free notation | rejected-for-now for everyday layer | Future fenced advanced layer at most. |

## Quality Bar For New Function Sugar

Add a new function convenience only if all answers are yes:

- Can it be shown as a normal `func`, equation, or `=>` expansion?
- Does it reuse the same parameter binding and constraint semantics?
- Does it improve a common call site without hiding effects or control flow?
- Can diagnostics name the generated parameters, selected clause, or failed
  guard in user language?
- Does it avoid duplicating `_`, `$...`, equations, `where`, pipeline, or
  block calls?

If a candidate only looks nicer in one isolated snippet, keep it in research.
The target is a language whose function syntax becomes easier to remember as
programs grow.

---

## Appendix: Implicit Function Scoping Reference

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

## Design Context

This doc covers Nomi's **Function** normal form. For the broader picture:

- [Language Foundation §Coherence Contract](../language/language_foundation.md) —
  the One Function And Call Story, and how pipelines, composition, and
  collection transforms reduce to ordinary calls.
- [Language Specification §8-9](../language/language_spec.md) — expressions,
  functions, calls, arrow functions, holes, operator sections, and equation
  surface.
- [Language Degrees Of Freedom §Flexible Surface](../language/language_degrees_of_freedom.md) —
  why holes, sections, and pipelines are surface sugar rather than separate
  execution models.
- [Implementation Learnings](../convenience/implementation_learnings.md) —
  rule ordering in `small_stmt`, name shadowing in equation loops.
