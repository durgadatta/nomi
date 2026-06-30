# First-Hour Nomi

> Status: active teaching plan; not a complete tutorial yet.
>
> Purpose: define the smallest first learning path before advanced syntax,
> data boundaries, effects, or symbolic layers appear.

## Goal

The first hour should prove that Nomi is useful without a feature catalogue.
A beginner should learn:

```text
values -> names -> calls -> functions -> constraints -> diagnostics
```

Everything else waits until the learner has a stable mental model.

## Competitive First-Hour Test: 2026-06-30

Nomi's first hour should be competitive with Python's first hour, not merely
different from it. Python succeeds because a learner can type useful
expressions quickly, read code without ceremony, and discover the standard
library later. Nomi should preserve that low floor while showing one advantage
Python does not make first-class: checked local meaning with helpful
diagnostics.

The first-hour test:

| Moment | Learner experience | Nomi advantage |
| --- | --- | --- |
| Calculator | Values evaluate immediately. | Familiar expression syntax; no project ceremony. |
| Text | Strings, interpolation, and display feel ordinary. | One readable interpolation path; no early string-format menu. |
| Names | `name = value` makes a local fact. | Binding is the mental model that later explains parameters, fields, and patterns. |
| Calls | Builtins and tiny library functions do useful work. | Calls stay Python-readable while remaining compatible with later constraints. |
| Functions | `func` names reusable behavior. | Function declarations are explicit and teach argument binding. |
| Constraints | A bad value fails at the binding boundary. | The error can name the value, rule, source, and repair hint. |
| Boring task preview | A small file/config/API example appears only after the basics. | Data boundaries are visible instead of hidden in dicts and ad hoc checks. |

Do not make the first hour compete with Mathematica, Julia, Ruby, or Racket
yet. Their power belongs in later layers. The first hour competes with
Python's approachability and improves on Python's validation and diagnostic
story.

## First-Hour Scope

Include:

- numbers, strings, booleans, lists, mappings;
- binding with `name = value`;
- calling functions;
- defining `func`;
- simple `if`;
- simple loops or collection calls only as needed;
- constrained binding with one clear error;
- `print` or display;
- one tiny file/config example only after decode is introduced later.

Exclude:

- pipelines and composition;
- match and algebraic data;
- block policies;
- async/concurrency;
- macros, quote, rewrite;
- query/table syntax;
- advanced type/effect language.

## Example Path

```nomi
name = "Ada"
print("Hello, {name}")

func greet(name:str) -> str:
    return "Hello, {name}"

age:int, age >= 0 else "Age must be positive" = 42
print(greet(name))
```

The first diagnostic lesson should show:

```nomi
age:int, age >= 0 else "Age must be positive" = -1
```

and explain the binding, value, rule, and repair hint.

## Target Lesson Sequence

This is the intended teaching ladder. Items marked target-only should not move
into runnable samples until parser, runtime, tests, and snapshots agree.

1. **Use Nomi as a calculator:** numbers, strings, booleans, lists, mappings.
2. **Name values:** assignment, display, and simple mistakes such as an
   unknown name.
3. **Call functions:** `len`, `contains`, `print`, and one or two text/list
   helpers.
4. **Write `func`:** one named transformation with a return value.
5. **Check a binding:** type and predicate constraints with one custom message.
6. **Read a diagnostic:** show the source, value, rule, and repair hint.
7. **Preview boring usefulness:** point to paths, files, JSON, CSV, CLI args,
   and `Data.decode(...)` as the next lesson, but do not teach the full data
   boundary yet.

The lesson should avoid a class/object detour. Data declarations, patterns,
pipelines, blocks, and result handling are important, but they belong after the
learner trusts names, calls, functions, constraints, and diagnostics.

## Integration Comments

- First-hour examples should become runnable samples only after implementation
  and snapshots agree.
- The first-hour path should use `explain` vocabulary but not require users to
  know the event model.
- Feature docs should mark whether a feature belongs before or after the first
  hour.
- The first-hour tutorial should include one intentional error. A language that
  wants to be serious must teach failure as part of normal use, not as a later
  troubleshooting appendix.
