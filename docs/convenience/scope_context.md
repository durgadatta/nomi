# Scope & Context Convenience

> Normal forms: Binding + Function. Where clauses and block-call DSLs are
> implemented; implicit parameters, scope functions, and capability scopes
> remain design-needed or research.
>
> Companion: [design_lessons_and_integration.md §4.1](design_lessons_and_integration.md)
> for the binding normal form integration critique.

## Normal Form

Scope and context convenience reduces to the binding and function normal forms:

```text
bind names local to an expression (binding)
attach caller-side code to a call (block)
thread context through a call chain (future capability)
```

Three distinct jobs, three distinct mechanisms. Do not collapse them into one
"context" keyword.

## 1. Where Clause (Local Bindings)

Define bindings local to an expression. Implemented in block and inline forms.

```nomi
area = pi * r * r where:
    pi = 3.14159
    r = 5

result = x * 2 where x = 5
ss(x,y) = s(x)+s(y) where s(n)=n*n
```

Where-clause bindings reuse ordinary binding semantics (constraints, defaults,
diagnostics). They are not a separate declaration island with different scoping.

**Source reference:** Haskell `where`, Nix `let/in`, Python assignment
expressions, SQL CTEs.

**Status:** implemented.

## 2. Block Calls as DSL Context

Builder-DSL and callback patterns reduce to the block-call normal form:

```nomi
html:
    head:
        title("Page")
    body:
        h1: "Welcome"
        p: "Content"
```

The block-call form (`block_call_stmt`) enables this without a dedicated
builder syntax. DSL builders are library functions that yield values to blocks.

**Source reference:** Kotlin trailing lambdas, Ruby blocks, Groovy builders,
Swift trailing closures, Nim indented call blocks.

**Status:** implemented (block_call_stmt).

## 3. Scope Functions (let/apply/also/run/with)

Kotlin defines five scope functions that differ in receiver binding and return
value. Nomi should not copy five overlapping names as syntax.

| Kotlin form | What it does | Nomi equivalent |
|-------------|--------------|-----------------|
| `let` | Value as argument, return block result | `value |> fn` or `(x) => expr` |
| `run` | Value as receiver, return block result | `value where: ...` |
| `apply` | Value as receiver, return value itself | `value where: field = ...` |
| `also` | Value as argument, return value itself | Pipeline with side-effecting stage |
| `with` | Value as receiver (not extension) | `value where: ...` |

The Nomi equivalents use `where` for local bindings, `|>` for value flow, and
block calls for control policies. One mechanism per job.

**Status:** library-first. No new syntax needed; `where` and `|>` cover the
use cases.

## 4. Implicit / Context Parameters

Values automatically threaded through the call chain without explicit argument
passing at every call site. This is a real need (locale, database handles,
permissions, clocks, loggers) but the mechanism must stay inspectable.

**Source reference:** Scala `given`/`using`, Kotlin context receivers,
Haskell type classes, Rust trait resolution.

**Nomi direction (future):** Context parameters should grow from explicit
values, block policies, and future capability scopes — not from implicit
parameter sugar added before the capability model exists.

```nomi
# Future direction — not implemented:
func sort[T](list: list[T]) using Ordering[T] -> list[T]:
    ...

using ordering = int_ordering:
    sorted = sort([3, 1, 2])
```

**Status:** research-only. Wait for capability scopes, explanation traces, and
the block-call model to settle before adding implicit parameter machinery.

## 5. Synthesis Decisions

| Candidate | Status | Decision |
|-----------|--------|----------|
| `where` clause (block form) | implemented | Canonical local-binding form. |
| `where` clause (inline form) | implemented | Keep for single-binding cases. |
| Block-call DSL (builder pattern) | implemented | Reduces to block normal form; no separate builder syntax. |
| Scope functions (let/apply/also/run/with) | library-first | Covered by `where`, `|>`, and explicit lambdas. |
| Implicit/context parameters | research-only | Wait for capability scopes and explanation. |
| `using` blocks | design-needed | Block-call policy for scoped capabilities. |
| World/capability values | research-only | Future layer; needs type-level tracking design. |

## 6. Quality Bar

Add a new scope or context feature only if:

- It reuses ordinary binding semantics (not a parallel scoping system).
- It has a visible boundary keyword (no ambient implicit resolution).
- Diagnostics can name the scope where a name was resolved.
- It does not duplicate `where`, block calls, or pipeline for the same job.
- The expansion into the binding or block normal form is inspectable.
