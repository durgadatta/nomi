# Yield To Block Historical Note

> Status: historical source note; canonical block syntax and semantics live in
> [Block Calls As Control Values](block_calls_feature.md).
>
> Use this file only for Python/Ruby context and implementation caveats. Fold
> current Nomi decisions into `block_calls_feature.md`.

## Purpose

This note preserves why Nomi revisits generalized blocks even though Python
intentionally kept context managers narrow.

The active Nomi decision is:

```text
ordinary call + attached caller-side block; callee invokes block with yield
```

Read [Block Calls As Control Values](block_calls_feature.md) for syntax,
binding, result semantics, diagnostics, and implementation slices.

## Python Pressure

Python's `with` statement and `contextlib` make resource management pleasant,
but they do not naturally express policies such as retry, transaction,
structured tracing, fixtures, and caller-side block parameters as one uniform
language shape.

Relevant Python history:

- [PEP 343](https://peps.python.org/pep-0343/) accepted the modern `with`
  statement and context manager protocol.
- [PEP 310](https://peps.python.org/pep-0310/) explored reliable acquisition
  and release pairs.
- [PEP 340](https://peps.python.org/pep-0340/) explored anonymous block
  statements and was rejected/subsumed.
- Python discussions around block scope and retrying context managers show the
  recurring pressure, but also the risk of hiding control flow.

## Nomi Lesson

The useful lesson is not "copy Ruby blocks into Python." The useful lesson is:

```text
control policies should be ordinary calls that can receive caller-side code
without inventing one keyword per policy
```

That keeps `using`, `retry`, `transaction`, `trace`, `test`, and future
structured-concurrency policies in one block-call family.

## Implementation Caveats

The prototype has historically explored `yield` through Python AST walking.
That creates limits:

- expression-level `yield` is not yet a general continuation mechanism;
- `lhs = yield x` is easier than arbitrary expressions such as
  `v = (yield 2) + (yield 3)`;
- yielded block values should eventually use the same binding engine as
  assignment and function parameters;
- Python generator cleanup and `finally` behavior have subtle GC interactions
  that should not silently define Nomi semantics.

These caveats are implementation source material. The language-facing design
belongs in [Block Calls As Control Values](block_calls_feature.md).
