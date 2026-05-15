# Meta-Programming & Testing Convenience

> Normal forms: Explanation + Block. Decorators are implemented; inline tests,
> examples, and checks are design-settled per the explanation normal form;
> macros remain research-only.
>
> Deep research: [cross_language_synthesis_master.md §4.8](../research/cross_language_synthesis_master.md)
> (capstone explanation normal form),
> [package_docs_and_examples_deep_dive.md](../research/package_docs_and_examples_deep_dive.md)
> (10-system docs survey: Rustdoc, ExDoc, Julia, Sphinx, Scribble, Go, Javadoc, TypeDoc, LP, Diataxis).
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
explanation anchors simultaneously — three purposes, one form. This is the
Rust doc-test / Elixir doctest model: examples are executable and run as
part of the test suite.

```nomi
func add(a, b):
    examples:
        add(2, 3) => 5
        add(0, 0) => 0
        add(-1, 1) => 0
    return a + b
```

Each `examples:` entry is an assertion: the expression on the left, `=>`, and
the expected value on the right. The `examples:` block is a first-class
explanation normal form construct.

**Execution model:**
- `examples:` blocks are extracted at compile time and run as part of the
  test suite (same as Rustdoc's `cargo test` runs doc tests, ExDoc's `mix test`
  runs doctests).
- Failed examples produce diagnostics naming: the expression, the expected value,
  the actual value, and the source location (file, line, column).
- Examples can reference the enclosing function's parameters but not its local
  variables — they test the function's external contract.
- Examples on `data` types test constructors, constraints, and derived operations.

**Diagnostic format** (from cross-language synthesis, Rustdoc/Elixir/Elm model):

```text
example failed at line 42:
    add(2, 3) => 5
    returned: 6
    expected: 5
```

**Source reference:** Rust doc tests (`///` + `assert_eq!` run by `cargo test`),
Elixir doctest (`iex>` prompts in `@doc`), Python doctest (`>>>` prompts),
Racket Scribble `@examples`, Darklang traces.
**Status:** design-settled; implementation deferred.

## 3. Check Statements

Invariants verified at runtime with diff-oriented output. `check` is a
statement-level assertion that produces structured diagnostics on failure —
not just "assertion failed" with a stack trace.

```nomi
check normalize_email(" A@B.COM ") == "a@b.com"
check items.len() > 0 else "items must not be empty"
```

On failure, the diagnostic shows:
- The full expression that failed
- The value of each subexpression (introspected, like Kotlin power-assert)
- Expected vs actual for comparison checks
- Source location

This is the Kotlin power-assert / pytest assert-introspection model: the
compiler or runtime instruments the expression to capture intermediate values.

**Relationship to `examples:`:** `examples:` blocks are definition-attached
tests (test the declared contract); `check:` statements are inline invariants
(test internal assumptions). Both produce trace records in the explanation
normal form.

**Relationship to `explain`:** Both `examples:` failures and `check:` failures
produce trace records that `explain` can render. The trace record includes the
expression tree, subexpression values, and the failing node — enabling `explain`
to show "why did this check fail?" interactively.

**Source reference:** Kotlin power-assert, pytest assert introspection, Rust
`assert_eq!` with `#[track_caller]`, Darklang trace-driven assertions.
**Status:** design-settled; implementation deferred.

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
| `examples:` blocks | design-settled | Core explanation feature; Rustdoc/Elixir doctest model. |
| `check:` statements | design-settled | Diff-oriented runtime invariants; power-assert model. |
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
