# Convenience Review And Roadmap

> Status: working review.  This document critiques the convenience-feature
> notes as a set, reconciles them with current prototype behavior, and ranks
> implementation candidates by fit with Nomi's existing parser, desugar, and
> interpreter structure.

## Review Summary

The `docs/convenience/` folder is useful as a cross-language idea bank, but it
currently mixes four different things:

1. features already implemented in the prototype;
2. features partially implemented but underdocumented;
3. plausible near-term sugar that aligns with the existing architecture;
4. long-term language research that depends on future type, module, or data
   systems.

That mix is expected in a research repo, but it creates a practical risk:
stale "proposal" sections can hide implemented behavior, and ambitious
research notes can look as ready as small parser/desugar changes.  Future work
should keep the idea bank, but every convenience note should label whether a
feature is:

- **implemented**: examples should run in `samples/demo.nomi` or tests;
- **prototype-ready**: mostly grammar/desugar/runtime wiring;
- **design-needed**: semantics are still underspecified;
- **research-only**: useful inspiration, not a current implementation target.

## Current Prototype Surface

These convenience features are already present enough to teach with examples:

| Area | Implemented Surface | Notes |
|------|---------------------|-------|
| Functions | `func`, arrow functions, equations, no-parens single-arg equations, defaults, piecewise equations, guards | `functions.md` still has stale "future" language around some of these. |
| Implicit functions | `_`, `$1`, `$name`, operator sections | This is now a strong local idiom and should be documented as one family. |
| Local bindings | block and inline `where` | Good fit: implemented as desugar, not core runtime magic. |
| Composition | `|>`, `>>>`, `<<<` | The sample now uses `3 |> (dbl >>> inc)` to avoid precedence confusion. |
| Control | `unless`, postfix `return ... if/unless ...`, if-let, while-let, guard-let | Expression-postfix conditionals are still not settled. |
| Pattern matching | match statements, guards, or-patterns, if-let, inline match expressions, indented expression-valued match cases | Full value-producing statement suites remain open. |
| Null handling | `??`, safe method/property/subscript access via `?.` | Elvis `?? return` still needs statement-level lowering. |
| Error handling | single-line `try` expression, `defer` | Multi-line try expressions need the same value-producing block decision as match suites. |
| Collections | ranges `1..5`, `1..<5`, range steps `1..10 by 2`, spread in lists/tuples, comprehensions | Broadcasting remains research-only. |
| Strings | normal strings, raw strings, triple strings, simple f-strings via desugar | `strings.md` is stale about f-string support. |
| Types | type aliases | `data` and native sum types are still future work. |

## Critique By Document

### `functions.md`

Strongest doc in the folder, but it is stale.  It still says operator sections,
composition, positional holes, named holes, no-parens equations, and equation
defaults are not implemented or future-only even though tests cover them.

Examples should be reorganized around Nomi's current function families:

```nomi
double = _ * 2
add = $1 + $2
greet = "Hello, " + $name
twice x = x * 2
sign(n) when n > 0 = 1
sign(n) when n < 0 = -1
sign(n) = 0
```

Near-term implementation candidate from this doc: richer piecewise patterns,
especially `_` wildcard in equation arguments and tuple/list patterns.  This
aligns with existing `PiecewiseFunction` desugaring.

### `patterns.md`

The direction is correct, but the match-as-expression section should be
updated to point at `challenges_match_as_expression.md` and show both forms:

```nomi
label = match n: case 1 => "one"; case _ => "many"

label = match n:
    case 1: "one"
    case _: "many"
```

The if-let section now splits implemented `if pattern = expr`, `while pattern
= expr`, and `guard pattern = expr` from future exhaustiveness and control-flow
diagnostics.

### `collections.md`

The priority table is stale: pipeline, ranges, range-step syntax, and spread
literals are already implemented.  Range steps use `by` instead of the old
`//` proposal because `//` is already floor division:

```nomi
odds = 1..10 by 2       # range(1, 11, 2)
evens = 2..<10 by 2     # range(2, 10, 2)
```

`by` remains usable as an identifier outside the range-step position.

### `null_handling.md`

The doc should mark `??` and `?.method` / `?.attr` as implemented.  It should
also distinguish three different features:

```nomi
name = user?.name ?? "anonymous"     # implemented
first = items?.[0]                   # not implemented
value = config[key] ?? return        # not implemented
```

Safe subscript now fits beside `safe_getattr` and `safe_call` in `calls.lark`
and `ExpressionMixin`.

### `error_handling.md`

The current doc proposes a multi-line `try` expression, but the implemented
surface is single-line:

```nomi
value = try int(raw) except ValueError: 0
```

The long-term `?` operator depends on `Result`/`Option` semantics.  It should
remain design-needed until constructors, variants, and return-type conventions
are settled.

### `strings.md`

This doc is stale.  Triple-quoted strings and simple f-strings work today:

```nomi
name = "Ada"
message = f"Hello {name}"
sql = """
select *
from users
"""
```

The missing parts are richer f-string parity, format specs, and indentation
helpers such as `trim_indent`.

### `types.md`

Type aliases are implemented.  `data`, sealed variants, extension methods, and
declarative operator overloading belong to the language-design spine, not a
quick convenience pass.  They need alignment with `docs/language/`.

### `array_languages.md`

This is valuable research, but most ideas are not near-term syntax.  The best
adoption path is library-first:

```nomi
avg = sum($xs) / len($xs)
result = values |> map(_ * 2) |> filter(_ > 10) |> sum
```

Explicit broadcasting could be revisited later, but implicit element-wise
arithmetic would conflict with Python-compatible list behavior.

## Near-Term Implementation Queue

This queue favors small, reversible changes that compose with existing passes.

| Rank | Feature | Why It Fits | Main Risk |
|------|---------|-------------|-----------|
| Done | `while pattern = expr:` | Reuses `if_let_stmt`, match patterns, `while`, and `break` | Else semantics were intentionally left out. |
| Done | safe subscript `obj?.[index]` | Extends existing safe navigation grammar | Receiver is evaluated once through IIFE lowering. |
| Done | range step `1..10 by 2` | Extends existing range lowering | `by` is a soft keyword and remains valid as a name. |
| Done | guard-let `guard pattern = expr: suite` | Reuses match patterns and early-exit idioms | Exit diagnostics are still future work. |
| 1 | value-producing statement suites for match/try expressions | Unblocks full expression blocks | Requires a Nomi block-value semantic decision. |

## Recommended Implementation Discipline

1. Keep convenience features as grammar plus desugar when possible.
2. Prefer syntax that reduces to existing primitives: `match`, `while`, `if`,
   functions, calls, and returns.
3. Add runnable examples to `samples/demo.nomi` only after tests prove the
   behavior.
4. Do not implement research-only ideas until the active language docs define
   their semantics.
5. Commit one feature at a time, with docs and tests in the same commit.
