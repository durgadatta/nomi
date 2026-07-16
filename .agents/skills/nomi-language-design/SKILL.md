---
name: nomi-language-design
description: Refine Nomi's target language through syntax-first whole-program design, consolidated cross-language evidence, bounded experiments, explicit tradeoffs, and canonical docs updates. Use for language semantics, syntax admission, research synthesis, target programs, and design reviews.
compatibility: codex, opencode, deepseek-tui, claude-code
---

# Nomi Language Design

Use this skill for target-language choices, syntax/semantic reviews,
cross-language synthesis, feature admission, and aspirational programs.

## Authority

Read in this order:

1. `docs/design/README.md` - product promise and language shape.
2. `docs/design/syntax.md` - canonical target source forms.
3. `docs/design/semantics.md` - behavior independent of backends.
4. `docs/design/industrial.md` - package, effect, concurrency, security,
   tooling, and deployment contracts.
5. `docs/design/decisions.md` - accepted, rejected, deferred, and open choices.
6. `docs/design/target.nomi` - whole-language pressure fixture.
7. `docs/research/convergences.md` - consolidated evidence.
8. `docs/research/open_questions.md` - bounded experiments.

Current code and tests describe prototype behavior. They do not define the
target. The old deep-dive corpus is available in Git history at `08f2aad`; use
it only when an open question needs detail that the consolidated research does
not retain.

## Core Posture

Design Nomi as a new language. There is no current source-compatibility
obligation.

Prefer:

- one recognition path per common cognitive act;
- visible mutation, failure, authority, cleanup, and suspension;
- explicit boundaries between structural external values and nominal owned
  data;
- inferred local code and explicit public contracts;
- ordinary functions/values before grammar;
- libraries before scoped notation, scoped notation before global extension;
- whole-program coherence over isolated snippet beauty;
- formatter, diagnostics, tooling, and migration as part of syntax design.

Do not preserve an implemented feature merely because it has tests. Do preserve
runnable CLI/web behavior honestly during migration.

## Design Model

Use these eight recurring user acts as orientation, not a rigid IR taxonomy:

```text
name
transform
model
choose
repeat
fail
touch the world
understand
```

Classify a proposal into one of four layers:

1. core surface;
2. standard mechanically reducible convenience;
3. ordinary library/protocol;
4. explicitly scoped language tool.

If the feature does not need source syntax, stop at layer 3.

## Syntax-First Review

For each proposal, inspect the code shape before abstract virtues.

1. Write the explicit long form.
2. Write the proposed form in a beginner example, production function, and
   failure-heavy example.
3. Identify every reused keyword and punctuation mark.
4. State the semantic fact each token makes visible.
5. Compare interactions with binding, types, data, match, Result, effects,
   resources, async, modules, and formatting.
6. Sketch at least one diagnostic and one formatter rendering.
7. Put the form into `docs/design/target.nomi` or a focused target fragment.
8. Prefer deletion when two forms ask the reader to recognize the same act.

Desugarability is necessary but insufficient. A shorthand that lowers cleanly
can still damage the source language by multiplying recognition paths.

## Current Notation Discipline

Treat these as strong target constraints:

```text
_      pattern wildcard only
where  constraints only
->     function result type only
=>     explicit input/pattern to expression
|>     first-argument call insertion only
?      Option/Result propagation only
?. ??  Option handling only
with   exactly-once resource scope only
```

The rejected syntax table in `docs/design/decisions.md` is deliberate. Do not
reintroduce equation functions, hole lambdas, operator sections, local `where`,
`unless`, postfix conditionals, pattern shortcut statements, collection aliases,
composition operators, or universal block/yield control without new evidence.

## Research Workflow

Start with `docs/research/families.md` and
`docs/research/convergences.md`. Ask whether the question is already answered.

Do new research only when:

- a concrete target program exposes a deficiency;
- two credible Nomi-compatible choices remain;
- the choice changes syntax, semantics, or an industrial contract;
- a bounded experiment can distinguish them.

Research unit:

```text
user pressure
-> semantic mechanism
-> genuine fork
-> interaction cost
-> Nomi candidates
-> experiment or decision
```

When external research is required, prefer official language specifications,
official documentation, standards, and primary papers. Extract decisions, not
tour notes. Update `docs/research/open_questions.md`; do not recreate one deep
dive per language.

## Feature Admission Packet

Before accepting a feature, provide:

- user need and representative programs;
- long form and shorthand, if any;
- parse/name/type/constraint/effect/runtime semantics;
- control-transfer and async behavior;
- failure taxonomy and cleanup behavior;
- formatter output;
- terminal/editor/machine diagnostics;
- inspectable lowering or expansion;
- interaction matrix with neighboring forms;
- rejected alternatives;
- conformance fixtures independent of implementation;
- removal or rollback criteria;
- target demo update.

The proposal owns the burden of proof.

## High-Risk Design Areas

### Binding And Constraints

Keep binding creation distinct from mutation. Preserve atomic tentative bind,
check, and commit. Separate internal contract violations from expected external
decode errors. Test the exact `where` surface across locals, parameters, fields,
and cross-field constraints.

### Functions And Calls

Keep one named form and one explicit anonymous expression form. Avoid automatic
currying, partial application, generated parameters, and equation dispatch.
Parameters are bindings; public results and effects are contracts.

### Data And Boundaries

Use nominal immutable `data` for owned concepts. Use `Unknown`/`Value`,
structural patterns, and explicit decoders for received values. Decode returns
typed accumulated path errors; constructors do not silently coerce.

### Patterns

`match` is the structural choice form. Preserve the distinctions among shape
non-match, guard rejection, and constraint failure. Closed variants should be
exhaustive. Avoid one-case pattern aliases until real code proves a need.

### Failure

Keep `Option`, `Result`, panic, and cancellation distinct. `?.`/`??` are absence
only; `?` is typed propagation only. Error conversion must stay inspectable.

### Resources And Concurrency

Do not infer shared semantics from similar indentation. `with` is exactly-once
acquire/use/release; retry receives a function; loops repeat; generators remain
an open design; async functions and task groups own suspension and child
lifetime.

### Effects And Capabilities

Public effect declarations aid local review. Runtime capability handles grant
actual authority. Check both static ergonomics and host/test/browser behavior.

### Collections And Tables

Use one verb family. Keep strict collections, streams, and table plans distinct
in types. A pipeline inserts a call argument and nothing else. Query notation
must be earned by table-specific programs.

## Whole-Language Test

After any global decision:

1. update `docs/design/syntax.md` and/or `semantics.md`;
2. update `docs/design/decisions.md`;
3. update `docs/design/target.nomi`;
4. scan the target for punctuation or constructs that now conflict;
5. update `docs/research/open_questions.md` if an experiment closed;
6. update `docs/README.md` only if the document topology changed;
7. map implementation work only after the target reads coherently.

Keep target-only code outside `samples/`. Runnable samples are product fixtures
and require parser/runtime/tests/web agreement.

## Documentation Style

- Put target decisions only under `docs/design/`.
- Put consolidated evidence and bounded unknowns under `docs/research/`.
- Put current implementation maps under `docs/orientation/`.
- Put dated judgments under `docs/review/`; promote durable decisions.
- Label implemented, target, experimental, deferred, and rejected explicitly.
- Prefer tables for comparisons and prose for semantics/tradeoffs.
- Do not preserve duplicate essays as archives; Git history is the archive.
- Avoid claims of inevitability when the evidence shows a genuine fork.

## Implementation Handoff

When a design is accepted, hand it to parser/runtime work as conformance rather
than prose alone:

- accepted/rejected source fixtures;
- expected typed Surface and Core shapes;
- values, output, effects, diagnostics, events, cleanup, and cancellation;
- frontend/backend capability expectations;
- migration disposition for old syntax;
- target demo slice that can eventually move to `samples/`.

Use `docs/orientation/implementation_guideline.md` for the current engineering
workflow and the parser/interpreter/test/web skills for implementation.

## Stop Conditions

Stop and keep a proposal open when:

- its best argument is fewer keystrokes;
- it reuses punctuation with an unrelated meaning;
- it hides invocation count, failure, authority, mutation, or suspension;
- its diagnostics require backend implementation vocabulary;
- it works in a snippet but makes the target program less coherent;
- ordinary functions or data have not been tried;
- more research would only add examples rather than distinguish choices.
