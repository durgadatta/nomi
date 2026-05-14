# Docs Eagle Eye Review

> Status: active planning review.
>
> Scope: repository documentation as a whole. This document records a
> high-altitude scan of `docs/` to find hidden gaps, duplicated pressure, and
> planning notes that were not obvious from any one feature file.

## Purpose

Nomi now has a large documentation landscape: active language direction,
focused feature specs, comparative convenience research, philosophical notes,
implementation plans, substrate TODOs, archived design reviews, and drafts.
That richness is valuable, but it creates a new problem:

```text
the project can know something in one document
while still failing to act on it in the planning spine.
```

This review scans the whole docs set from above and asks:

```text
What is the current shape of knowledge?
What is missing between vision and implementation?
What should be promoted, deduplicated, or turned into concrete next artifacts?
```

It is not a replacement for the canonical specs. It is a planning lens for the
next passes.

## Scan Summary

The docs folder currently has several layers:

| Layer | Role | Current condition |
| --- | --- | --- |
| `docs/language/` | Decision surface, target syntax, implementation planning | Strong and increasingly canonical, but now needs a status/decision ledger. |
| `docs/features/` | Focused design pillars | Strong for binding, blocks, collections, symbolic computation; missing a few bridge specs. |
| `docs/convenience/` | Comparative syntax research and implementation learnings | Rich, but some older per-feature notes are partly stale relative to newer synthesis docs. |
| `docs/research/` | Deeper source pressure and philosophical synthesis | Valuable; some ideas should be promoted into focused specs only after normal-form reduction. |
| `docs/notes/` | Philosophy, ambition, risk framing | Useful upstream framing; should stay non-spec. |
| `docs/orientation/` | Runtime/tooling/process map | Useful, but should be refreshed as parser substrate work changes the architecture. |
| `docs/archive/design_review/` | Historical AI-assisted and exploratory material | Correctly archived; still useful as quarry, not authority. |
| `docs/drafts/` | Large combined or raw synthesis artifacts | Useful for hidden concepts, but too large to be read as active direction. |

The active spine is coherent. The biggest remaining issue is **bridge debt**:
several important concepts are named across the docs but do not yet have their
own planning artifact or implementation gate.

## What Is Strong

### 1. The Normal-Form Doctrine Is Stable

Many docs converge on the same set of memory anchors:

```text
binding
function
pattern
flow
block
absence/result
data boundary
explanation
```

This is a major strength. It gives every syntax idea a place to reduce and
protects the language from feature collage.

Keep doing this:

- require every syntax proposal to name its normal form;
- require tooling eventually to show the expansion;
- reject forms that create a second validation, pattern, block, query, or
  failure language.

### 2. The Target Examples Are Now Pulling Their Weight

`target_program_fixtures.md` and `target_language_tour.md` changed the docs
from abstract aspiration into concrete taste pressure. They expose where
syntax has to compose:

- data declarations meet decode;
- decode meets provenance;
- provenance meets explanation;
- block calls meet resources, retry, transactions, tasks, and tests;
- table flow meets diagnostics;
- future notation stays fenced.

These examples should become regression material for design, even before they
become parser tests.

### 3. The Parser Substrate Work Has A Clear Path

`flexible_syntax_substrate_plan.md` and
`syntax_substrate_todo_audit.md` now give implementation architecture a clear
north-south line:

```text
feature manifest
-> parse/lower inspection
-> source spans
-> surface AST
-> core AST
-> Python AST backend
-> diagnostics and normal-form expansion
```

This is the correct ground for the grander design. Without it, every ambitious
syntax feature would become a scattered one-off.

### 4. Research Is Properly Fenced

The docs mostly distinguish:

- active decision surface;
- focused feature design;
- comparative syntax research;
- philosophical source material;
- archived/draft source material.

That separation is healthy. It lets the project be ambitious without making
every interesting idea a commitment.

## Hidden Gaps

### Gap 1: No Central Decision Ledger

Many important decisions are repeated across docs:

- `data` is owned program data.
- `shape` is not a first-layer peer to `data`.
- `?.` and `??` are absence-only.
- `Result` handles expected failure.
- pipeline applies a value now; composition builds a function later.
- block policies share one caller-side block model.
- advanced notation needs explicit fences.

These decisions are stable enough to deserve a central ledger.

Recommended artifact:

```text
docs/language/design_decision_ledger.md
```

Why it matters:

Without a decision ledger, agents and humans must rediscover settled choices
by reading many docs. That is how old attractive alternatives sneak back in.

### Gap 2: No Current Capability Matrix

The docs now have target fixtures, a target tour, and implementation plans, but
there is no single matrix saying:

```text
syntax | parser | lowering | runtime | tests | docs | status
```

This makes it hard to tell whether a feature is real, partial, future, or
rejected.

Recommended artifact:

```text
docs/language/current_capability_matrix.md
```

It should cover at least:

- functions and equations;
- constraints;
- `where`;
- underscore and positional holes;
- pipeline/composition;
- match and if-let;
- `?.` and `??`;
- `defer`, `with`, block calls;
- imports/modules;
- f-strings/strings;
- type aliases;
- examples/tests/traces;
- future `data`, `decode`, `Result`, `quote`, `use`.

Why it matters:

This is the bridge between docs and user trust. It prevents the target tour
from being confused with current support, and it helps choose implementation
work by evidence rather than vibe.

### Gap 3: Standard Library Shape Is Still Mostly A Promise

The docs repeatedly say Python's success depends on ordinary tasks being easy:
files, paths, text, JSON, CSV, HTTP, time, subprocesses, tables, tests,
notebooks, config, secrets, environment variables.

But there is not yet a standard library shape document.

Recommended artifact:

```text
docs/language/prelude_and_standard_library_plan.md
```

First sections:

- values and names in the default prelude;
- `Path`, `Secret`, `Duration`, `Instant`, `Result`, `Option`;
- files/text/JSON/CSV;
- CLI/env/config layering;
- HTTP request/response boundaries;
- table/list transform vocabulary;
- diagnostics/explain/test helpers;
- Python interop rules.

Why it matters:

Pleasant syntax cannot carry adoption alone. A broadly loved language needs
boring power within reach.

### Gap 4: Decode Boundary Deserves Its Own Feature Spec

Binding constraints are well covered. Data boundary pressure appears across:

- `binding_constraints_feature.md`;
- `target_program_fixtures.md`;
- `target_language_tour.md`;
- `language_spec.md`;
- config/source-provenance research;
- CUE/Nickel/Pkl/Pydantic comparisons.

But decode itself needs a focused spec.

Recommended artifact:

```text
docs/features/data_decode_boundary_feature.md
```

It should answer:

- Does `Data.decode(value)` always return `Result`?
- Does decode collect all field errors or fail fast by default?
- How do defaults, optional fields, extra fields, and missing fields work?
- How are source paths represented for JSON, CSV, CLI, env, config, HTTP?
- How does redaction work for `Secret`?
- How does decode interact with `explain`?
- How are nested decoders composed?

Why it matters:

Decode is likely the first feature that makes Nomi feel materially better than
Python for everyday work. It needs first-class design.

### Gap 5: Failure Taxonomy Is Spread Too Widely

The docs correctly insist that absence, expected failure, exceptions, pattern
non-match, and constraint failure must remain distinct. But the details are
scattered across null handling, error handling, patterns, binding, spec, and
target examples.

Recommended artifact:

```text
docs/features/failure_taxonomy_feature.md
```

Minimum table:

| Kind | Surface | Meaning | Recoverable? | Typical diagnostic |
| --- | --- | --- | --- | --- |
| absence | `none`, `some`, `?.`, `??` | value not present | yes | missing optional value |
| expected failure | `Result`, `Ok`, `Err` | operation failed normally | yes | parse/decode/io error |
| exception | `raise`, `try` | exceptional control/error | maybe | stack and cause |
| pattern non-match | `match`, if-let | structure did not fit | yes | case skipped |
| constraint failure | binding/decode | value unacceptable | boundary dependent | failed constraint |

Why it matters:

If this taxonomy is not crisp, future `?`, decode, match, and block policies
will blur.

### Gap 6: Explanation Needs A Single Model

Many docs say explanation is core:

- examples as docs/tests;
- binding diagnostics;
- decode provenance;
- pipeline stage traces;
- block yield/retry/cleanup traces;
- query plans;
- symbolic rewrites;
- AI/tooling expansion.

But there is no focused `explain`/trace design spec.

Recommended artifact:

```text
docs/features/explanation_trace_feature.md
```

Key object:

```text
TraceEvent:
    kind
    source_span
    value_before
    value_after
    decision
    failed_constraint
    child_events
    redaction_policy
```

Why it matters:

Nomi's strongest adoption wedge may be not just nicer syntax, but a runtime
that can explain boundary and transformation failures in language terms.

### Gap 7: State, Mutation, And Capability Are Under-Specified

The docs wisely defer ownership/regions/effect theory. But everyday programs
still mutate:

- variables are rebound;
- lists/maps are updated;
- files and databases change;
- caches and sessions exist;
- HTTP handlers use external state;
- transactions and retries need idempotence policy.

Recommended artifact:

```text
docs/features/state_and_capability_model.md
```

First-layer scope:

- rebinding versus mutation;
- owned immutable data update with `with:`;
- mutable containers as library values;
- transaction blocks as state policy;
- `world` as a practical capability value;
- what `trace` records when authority is used.

Why it matters:

If state is only postponed, the first useful programs will invent ad hoc
answers. A modest practical model is better than a future perfect theory.

### Gap 8: Teaching Path Is Still Missing

There are strong target examples and specs, but no first-hour learning doc.

Recommended artifact:

```text
docs/language/first_hour_nomi.md
```

It should teach only:

1. values and names;
2. calls and functions;
3. constraints on bindings;
4. small data values;
5. `match`/`Result` only when needed;
6. `explain` as the friend at the boundary.

It should avoid symbolic rewrite, capabilities, query syntax, advanced block
policy, effect theory, and macros.

Why it matters:

A language can be conceptually beautiful and still lose users in the first ten
minutes.

### Gap 9: Research Promotion Needs A Checklist

The archive and drafts contain lots of ideas. The docs say "promote only the
smallest useful piece," but there is no concrete review checklist for archive
promotion.

Recommended addition to the proposal process:

```text
Archive promotion checklist:
- What is the durable need?
- Which active normal form absorbs it?
- Which active doc already covers part of it?
- What is the smallest new decision?
- What source examples are kept?
- What source examples are rejected?
- What target fixture changes?
```

Why it matters:

This prevents old broad proposals from re-entering as polished duplication.

### Gap 10: Read-By-Task Paths Need Maintenance

`docs/README.md` now includes a `Read By Task` section. Keep that section
current whenever a new canonical planning or feature doc is added, because a
contributor often starts with a task:

- add syntax;
- change interpreter semantics;
- design data decode;
- update web playground;
- write research synthesis;
- make a user-facing sample;
- implement parser feature.

Why it matters:

This reduces agent drift and makes the documentation useful in the exact
moment of work.

## Cross-Cutting Insight: Construction And Elimination

The drafts contain a valuable lens that deserves promotion into planning:

```text
construction: provide enough information to make a value
elimination: use a value by exposing the structure it guarantees
```

This unifies several areas:

| Area | Construction | Elimination |
| --- | --- | --- |
| product data | `User(id, email)` | field access, destructuring |
| variants/results | `Ok(value)`, `Err(error)` | `match result` |
| decode | external mapping -> owned value | decode diagnostics and field paths |
| constraints | accepted binding | failed judgement explanation |
| patterns | pattern declarations | case choice and captures |
| examples/tests | expected construction | assertion failure explanation |
| symbolic syntax | `quote:` syntax value | rewrite/pattern over syntax |

Planning note:

Data, decode, pattern matching, variants, and diagnostics should be designed
as one construction/elimination family. This may be a better organizing
principle than treating "types," "schemas," "patterns," and "errors" as
separate tracks.

## Cross-Cutting Insight: Three Boundaries

Across the docs, most hard problems are boundary problems:

| Boundary | Question | Examples |
| --- | --- | --- |
| Data boundary | When does external mess become owned meaning? | decode, constraints, config, HTTP, CSV |
| Control boundary | Who owns time-shaped execution? | block calls, retry, transaction, using, tasks |
| Power boundary | When does advanced capability become visible and fenced? | world, quote, rewrite, use units, macros |

Planning note:

The next focused specs should make these boundaries explicit. They are likely
more teachable than abstract categories like "type system," "effect system,"
or "metaprogramming."

## Cross-Cutting Insight: Diagnostics Are The Product

The docs often say diagnostics are first-class. The eagle-eye view makes this
stronger:

```text
Nomi's adoption wedge may be explainable precision.
```

Python is already readable. Nomi must be not only readable, but more helpful
when reality is messy:

- bad CLI args;
- malformed CSV rows;
- unknown JSON fields;
- missing config secrets;
- failed constraints;
- unexpected `none`;
- retry exhaustion;
- transaction rollback;
- wrong pattern;
- unsupported query lowering.

Planning note:

Every major feature spec should include an "Explanation Contract" section:

```text
What happened?
Where did it happen?
What value was involved?
What rule was being checked?
What can the user do next?
What is redacted?
```

## Immediate Planning Recommendations

### 1. Add The Missing Bridge Specs

Create focused specs in this order:

1. `docs/features/data_decode_boundary_feature.md`
2. `docs/features/failure_taxonomy_feature.md`
3. `docs/features/explanation_trace_feature.md`
4. `docs/language/current_capability_matrix.md`
5. `docs/language/prelude_and_standard_library_plan.md`
6. `docs/features/state_and_capability_model.md`
7. `docs/language/first_hour_nomi.md`
8. `docs/language/design_decision_ledger.md`

This order starts with the everyday core and ends by consolidating decisions.

### 2. Make Each Feature Spec Include The Same Sections

For consistency, new feature specs should include:

```text
Purpose
User pressure
Normal forms
Surface examples
Reduction
Diagnostics / explanation contract
Source provenance, if relevant
Current implementation status
Parser/lowering implications
Tests and fixtures
Open questions
Rejected alternatives
```

This is lighter than a formal spec but strong enough for implementation.

### 3. Refresh Stale Per-Feature Convenience Docs

`convenience/README.md` now separates synthesis docs from focused detail notes.
Do not rewrite every per-feature file at once. Instead:

- keep `review_and_roadmap.md`, `syntax_synthesis_matrix.md`, and
  `expanded_language_research.md` as the active convenience spine;
- update individual docs only when implementing or specifying that feature;
- add a short "canonical decision now lives in ..." pointer at the top of
  stale docs when needed.

### 4. Turn Target Fixtures Into A Design Test Suite

Before implementation:

- classify each fixture line as current, prototype-ready, design-needed, or
  future-layer;
- connect each fixture to a feature spec;
- add expected normal-form expansions for selected snippets.

Later:

- parse current/prototype-ready fixtures;
- parse future fixtures only in explicit syntax-lab mode;
- keep the target tour as the whole-program coherence test.

### 5. Keep Read-By-Task As The Glue Layer

The read-by-task table now lives in [docs/README.md](../README.md). Update that
table instead of duplicating task-entry paths in individual docs.

## Risks If We Do Not Add These Bridges

- The target tour will become beautiful but disconnected from implementation
  reality.
- Agents will reread broad docs and produce duplicate roadmap notes.
- Syntax decisions will be repeated instead of referenced.
- Decode, failure, and explanation will be implemented in separate ad hoc
  paths.
- State and capability will be postponed until everyday programs force rushed
  answers.
- The standard library story will lag behind syntax ambition.
- Users will see future examples and current behavior as one blurry promise.

## What To Avoid

- Do not collapse research docs down to current implementation.
- Do not turn every hidden gap into immediate code.
- Do not write another giant combined synthesis doc as the next move.
- Do not make the active docs depend on the archive for core decisions.
- Do not add syntax just because the target tour can make it look elegant.

## Next Exact Pass

The most useful next docs-only pass is:

1. Create `current_capability_matrix.md`.
2. Classify target fixtures against current/parser/runtime status.
3. Start `data_decode_boundary_feature.md` using the construction/elimination
   lens.

The most useful next code-adjacent pass is:

1. Add `tools.syntax.inspect` for raw parse tree and Python AST.
2. Add small parser snapshots for existing syntax.
3. Begin feature-manifest skeleton with no behavior migration.

Both paths support the same goal: keep the grand vision attached to the ground.
