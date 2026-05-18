# Adversarial Design Critique

> Status: active critique.
>
> Scope: documentation-only. This is a deliberately skeptical review of Nomi's
> current language direction, feature bundle, and spec-convergence process. It
> does not replace the foundation or spec; it names failure modes that those
> documents must keep answering.

## Purpose

Nomi's design has a strong coherence story: small normal forms, pleasant
surface syntax, explicit data boundaries, and explainable semantics. That story
is promising. It is also fragile.

This critique takes the hostile reviewer position:

```text
Assume the design is overconfident.
Assume local features will interact badly.
Assume docs make unsettled ideas sound done.
Assume implementation debt will distort the language.
```

The goal is not to slow Nomi down. The goal is to force sharper decisions
before syntax, samples, and implementation habits harden.

## Executive Critique

Nomi's largest risk is not lack of inspiration. It is trying to be the
coherent synthesis of Python, ML-family data/patterns, Ruby/Gleam block
control, SQL/dataframe flow, Pydantic/CUE boundaries, and Racket/Darklang
explanation before the operational substrate can carry that load.

The design should therefore treat the next pass as a reduction exercise:

```text
fewer promises
clearer feature packets
harder status labels
one operational spec
one current capability matrix
```

If Nomi cannot explain a feature through diagnostics, source spans, and
normal-form reduction, the feature is not spec-ready no matter how attractive
the syntax is.

## Risk Register

| Risk | Severity | Why it matters | Required response |
| --- | --- | --- | --- |
| Spec overpromises target syntax | High | `language_spec.md` can read more implemented than reality, while target fixtures use syntax the parser cannot handle. | Add a current capability matrix and mark target-only syntax aggressively. |
| Too many normal forms become too many concepts | High | Eight normal forms are elegant for designers, but users may experience them as eight subsystems. | First-hour docs must teach only values, bindings, calls, functions, constraints, and diagnostics before the full map. |
| Boundary model becomes abstract before practical | High | `Data.decode`, config, provenance, redaction, `Result`, and explanation are central but not yet one concrete packet. | Write data-boundary and failure-taxonomy feature specs before adding more surface syntax. |
| Explanation becomes a slogan | High | "Explainable" can remain aspirational if no event schema exists. | Define semantic event records before feature-specific diagnostics proliferate. |
| Block calls absorb too many policies | Medium | `using`, `retry`, `transaction`, `trace`, tests, and concurrency may share syntax but have different failure and cancellation rules. | Define a block-policy prelude with explicit body/policy/cleanup failure behavior. |
| Flow/query/table design hides binding scope | Medium | Pipelines are easy; row/group scopes are where data languages become confusing. | Keep query syntax deferred until row, group, aggregate, and plan explanation scopes are specified. |
| Python parity becomes ambiguous | Medium | Nomi relies on Python familiarity while intentionally departing from Python statements, data, errors, and constraints. | Keep a migration/interop note that names exact parity and departure points. |
| Target demos become fake proof | Medium | A beautiful target script can mask unresolved parser, diagnostics, and runtime questions. | Treat target scripts as design tests only; never move them into `samples/` before tests pass. |
| Library-first becomes a parking lot | Medium | "Library-first" can defer hard language decisions indefinitely. | Give every library-first candidate an evaluation condition: what usage would justify syntax? |
| Advanced layers leak taste pressure | Medium | Symbolic rewrite, rank notation, effects, and macros can distort the everyday language even while deferred. | Require explicit fences and expansion display before any advanced notation enters examples. |

## Feature Critique

### Binding And Constraints

The one-binding story is Nomi's strongest design move, but it risks becoming
too broad. Assignment, parameters, pattern captures, data fields, imports,
exception aliases, and decoder fields are similar, not identical.

Hard questions:

- Does rebinding a constrained local re-run the original constraint or replace
  the constraint set?
- Are import aliases really constraints, or just name bindings?
- Does pattern matching diagnose constraint failure or treat it as non-match?
- Can constraints depend on earlier fields without creating order surprises?

Recommendation: define a shared `BindingTarget` contract before adding more
constraint-bearing syntax. Every binding site should say whether failure
diagnoses, skips, returns `Err`, or raises.

### Data And Decode

`data` plus `Data.decode` is the right anti-schema-language move. The danger is
that decode wants many policies at once: defaults, optional fields, extra
fields, merge, provenance, nested paths, redaction, partial success, and
collect-all-errors.

Hard questions:

- Does decode fail fast or collect all errors?
- Where do defaults appear in diagnostics?
- Are unknown fields ignored, preserved, warned, or rejected?
- How does config merge provenance survive after decode?
- Can `@secret` and `@pii` be enforced outside display/explain?

Recommendation: create `docs/features/data_decode_boundary_feature.md` before
hardening more `data` examples in the spec.

### Pattern, Match, And Conditional Binding

The pattern story is coherent, but easy to overextend. `match`, if-let,
guard-let, piecewise functions, destructuring assignment, decode fields, and
future recognizers are all pattern-like. If all of them share one engine, users
need very clear failure vocabulary.

Hard questions:

- Is pattern failure silent everywhere except exhaustive `match`?
- Do guards and constraints share syntax but differ in diagnostics?
- Are mapping patterns partial by default?
- Can view patterns or recognizers hide expensive or failing work?

Recommendation: postpone view patterns and recognizers until ordinary mapping,
list, variant, and constrained captures have source-spanned diagnostics.

### Function Convenience

Nomi currently wants named functions, arrows, equations, piecewise equations,
holes, operator sections, composition, and where clauses. Each is defensible.
Together they risk becoming the convenience stack Nomi criticizes elsewhere.

Hard questions:

- How many ways should a beginner see to make a function in the first hour?
- Are holes and `$name` placeholders teachable without becoming a second
  lambda language?
- When should equations be preferred over `func` plus `match`?
- Can formatter rules make these forms visually consistent?

Recommendation: define a teaching ladder and keep only `func` and `=>` in the
first-hour path. Treat holes, equations, sections, and composition as
second-hour convenience.

### Flow, Collections, Query, And Tables

Pipelines are low risk. Query/table syntax is high risk. Most data languages
break user intuition at row scope, grouping scope, laziness, planner behavior,
and missing/null semantics.

Hard questions:

- Is `_` a whole row, a column receiver, or a placeholder function argument?
- What does `group(by=_.tags)` mean when tags is a list?
- Are table operations eager values or lazy plans?
- Does `where` filter false, `none`, `Err`, or only booleans?

Recommendation: specify collection/table verbs as ordinary functions and plan
values first. Do not add row shorthand until the explanation model can show
row/group binding.

### Blocks, Policies, And Effects

One block-call story is powerful. It can also become too magical if every
effectful idea is routed through a policy call.

Hard questions:

- Does `return` inside a block return from the block, policy, or enclosing
  function?
- How are cleanup errors combined with body errors?
- Can `retry` safely re-run a block with side effects?
- What authority does a block policy receive from `world`?
- How does cancellation interact with cleanup?

Recommendation: define the block-policy prelude around `using`, `retry`,
`transaction`, `trace`, and `test` before concurrency is revisited.

### Absence, Result, And Exceptions

The three-story taxonomy is correct: absence, expected failure, unexpected
error. The risk is visual overload: `?`, `?.`, `??`, `Option`, `Result`,
exceptions, pattern non-match, and constraint failure all appear near the same
code.

Hard questions:

- Is `none` a singleton value, an `Option` case, or both?
- Should `Option[T]` be explicit in user code if `none` exists?
- Can a future `?` operator coexist with `?.` without confusing users?
- Are decode failures `Err`, diagnostics, or binding errors?

Recommendation: write a failure taxonomy feature before admitting `?`
propagation. Keep `?.` and `??` absence-only.

### Explanation And Examples

Explanation is Nomi's most important differentiator and its easiest promise to
fake. Examples, traces, diagnostics, query plans, decode paths, and AI-readable
events need one data model, not just shared rhetoric.

Hard questions:

- What is the minimum event record?
- How are values redacted?
- Can users diff explanations across versions?
- Are examples run at compile time, test time, doc time, or runtime?
- What happens when examples depend on IO, clocks, randomness, or packages?

Recommendation: create an explanation-event schema and make feature specs use
it before adding more feature-specific diagnostics.

## Global Language Critique

### The "Coherent Synthesis" Claim Is Hard To Prove

Nomi's pitch is attractive precisely because it synthesizes several beloved
traditions. But a synthesis can fail even when each ingredient is good.

The proof should not be essay quality. It should be operational:

- a first-hour tutorial;
- a capability matrix;
- a target demo;
- a spec section per normal form;
- an implementation slice;
- diagnostics and tests.

### The Design May Be Too Documentation-Heavy

The docs are rich, but richness can become friction. A contributor or future
agent may not know whether to trust the spec, foundation, interaction map,
target fixtures, feature docs, or research notes.

Recommendation: enforce the operational spec convergence loop from
`spec_readiness_map.md`. Every critique, research note, and target fixture
should either promote a decision into a feature packet/spec section or remain
clearly source-only.

### The Prototype May Bias The Language Accidentally

Python AST and Python-compatible interpreter layers are useful bootstrap
tools. They are also a semantic gravity well. Nomi could accidentally inherit
Python constraints where it intends a cleaner model: statement/expression
boundaries, exception behavior, object/data distinctions, and source-span loss.

Recommendation: keep building Nomi-owned surface/core nodes and inspectable
lowering before adding more syntax that Python AST represents awkwardly.

## Near-Term Suggestions

1. Build the current capability matrix before expanding runnable samples.
2. Write the data decode boundary feature packet.
3. Write the failure taxonomy feature packet.
4. Define the explanation event schema.
5. Define the block policy prelude.
6. Add a first-hour tutorial that deliberately excludes most conveniences.
7. Keep `demo_target.nomi` compact and ordinary; use it to reject global
   incoherence, not to showcase every idea.
8. Add implementation TODO anchors only at architectural pressure points, and
   keep the central audit synchronized with those IDs.

## Decision Pressure

The next design pass should be willing to reject or defer attractive features
if they do not improve the operational spec. Nomi should become smaller before
it becomes larger.
