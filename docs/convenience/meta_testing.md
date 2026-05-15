# Meta-Programming & Testing Convenience

> Normal forms: Explanation + Block. Decorators are implemented; inline tests,
> examples, and checks are design-needed; macros remain research-only.
>
> Companion: [design_lessons_and_integration.md §4.8](design_lessons_and_integration.md)
> for the explanation normal form integration critique.

## Normal Form

Testing and meta-programming reduce to explanation (semantic events become
traces, examples, or diagnostics) and block (test fixtures and scoped setup
are block policies).

```text
decorator → function wrapper (apply at definition time)
example → inline test + explanation anchor
macro → scoped syntax expansion (future layer)
```

## 1. Decorators / Annotations

Wrap or modify functions/classes at definition time. Python-compatible `@`
syntax works.

```nomi
@cache
func fib(n):
    if n <= 1: return n
    return fib(n - 1) + fib(n - 2)
```

**Source reference:** Python decorators, Java annotations, Kotlin annotations,
Swift property wrappers.

**Status:** implemented (Python-compatible).

## 2. Inline Tests / Examples

Tests embedded in function or data definitions. Serve as docs, tests, and
explanation anchors simultaneously.

```nomi
# Future direction — design-needed:
func add(a, b):
    examples:
        add(2, 3) => 5
        add(0, 0) => 0
    return a + b
```

The `examples:` block should produce diagnostics in user language when a case
fails: expected value, actual value, and source location.

**Source reference:** Rust doc tests, Python doctest, Elixir doctest, Racket
contracts, Darklang traces.

**Status:** design-needed.

## 3. Check Statements

Invariants verified at runtime with diff-oriented output.

```nomi
# Future direction — design-needed:
check normalize_email(" A@B.COM ") == "a@b.com"
```

On failure, the diagnostic shows the expression, the expected and actual values,
and the source location — not just "assertion failed."

**Source reference:** Kotlin power-assert, pytest assert introspection.

**Status:** design-needed.

## 4. Macros

Compile-time code generation and transformation. Powerful but risks creating
uninspectable private syntax.

**Source reference:** Rust `macro_rules!`/proc macros, Elixir macros, Lisp
`defmacro`, Julia `@macro`, Nim templates.

**Nomi direction (future layer):** `quote:` boundary for code-as-data, scoped
rewrite rules (`expr /. pattern -> replacement`), and inspectable expansion.
Postpone until normal forms, source spans, and desugaring explanations are
mature.

**Status:** research-only.

## 5. Synthesis Decisions

| Candidate | Status | Decision |
|-----------|--------|----------|
| Decorators (`@`) | implemented | Python-compatible; keep as metadata/transformation. |
| `examples:` blocks | design-needed | Core explanation feature; inline docs + tests + trace. |
| `check:` statements | design-needed | Diff-oriented runtime invariants. |
| Macros | research-only | Defer until `quote:` boundary and scoped expansion exist. |
| Compile-time execution | research-only | `comptime`-style requires non-Python compilation target. |
| Code generation / scaffolding | library-first | Use data declarations and decoders; not a language feature. |

## 6. Quality Bar

Add a new testing or meta-programming feature only if:

- Diagnostics speak in user concepts (expected value, actual value, source
  location).
- Examples compose with normal-form reduction (show the desugared form when
  relevant).
- Macros and code generation have inspectable expansion (no hidden syntax
  transformation).
- The feature does not duplicate decorators, `check`, or `examples:` for the
  same job.
