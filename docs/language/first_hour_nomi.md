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

## Integration Comments

- First-hour examples should become runnable samples only after implementation
  and snapshots agree.
- The first-hour path should use `explain` vocabulary but not require users to
  know the event model.
- Feature docs should mark whether a feature belongs before or after the first
  hour.

