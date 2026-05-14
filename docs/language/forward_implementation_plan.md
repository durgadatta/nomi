# Forward Implementation Plan

> Status: active planning document.
>
> Scope: implementation planning, not implementation. This document translates
> the design spine into a practical sequence of work, with decision gates,
> caveats, test expectations, and open questions.

## Purpose

Nomi now has a richer design spine:

- [Language Foundation](language_foundation.md)
- [Language Direction And Gap Map](language_direction_and_gap_map.md)
- [Docs Eagle Eye Review](docs_eagle_eye_review.md)
- [Language Degrees Of Freedom](language_degrees_of_freedom.md)
- [Target Program Fixtures](target_program_fixtures.md)
- [Target Language Tour](target_language_tour.md)
- [Design Proposal Template](design_proposal_template.md)
- [Flexible Syntax Substrate Plan](flexible_syntax_substrate_plan.md)
- [Syntax Substrate TODO Audit](syntax_substrate_todo_audit.md)
- [Language Feature Todos](implementation_todos.md)

This plan answers a narrower question:

```text
How should implementation proceed without letting current prototype mechanics
collapse the language ambition?
```

The plan is intentionally staged. Each phase should leave the language more
coherent even if later phases are postponed.

## Planning Principles

1. **Design gate before code**: no major feature begins until its normal form,
   diagnostics, examples, and open questions are written down.
2. **Small semantic commits**: each implementation slice should prove one
   semantic claim through focused tests.
3. **Docs and tests move together**: accepted behavior updates specs, runnable
   examples, and regression snapshots in the same implementation wave.
4. **Do not chase all syntax first**: implement semantic anchors before adding
   more convenience surface.
5. **Python parity remains evidence, not a prison**: preserve parity where Nomi
   intentionally follows Python; depart explicitly where Nomi's model requires
   it.
6. **Diagnostics are first-class**: if a feature cannot explain failure, it is
   not done.
7. **Defer advanced layers**: symbolic rewrite, dense array notation, effect
   typing, scoped notation, and concurrency should wait until everyday
   semantics are stable.

## Phase Overview

| Phase | Theme | Main deliverable | Gate |
| --- | --- | --- | --- |
| 0 | Baseline and inventory | implementation map and current feature matrix | Current behavior documented and tests selectable. |
| 0A | Declarative syntax substrate | manifests, inspection, spans, profiles, and feature test matrix | New syntax can be parsed and inspected before runtime semantics. |
| 1 | Binding engine | `BindingError`, `Constraint`, `BindingTarget`, source-aware diagnostics | Assignment constraints use shared representation. |
| 2 | Parameter and pattern binding | function/block/pattern targets reuse binding engine | No partial bindings leak on failure. |
| 3 | Product `data` and decode | owned values plus explicit external boundary conversion | Data fields reuse binding constraints. |
| 4 | `Result` and failure taxonomy | expected failure separated from absence and exceptions | Fixtures can express parse/decode failures without `?`. |
| 5 | Flow and collection vocabulary | stable pipeline semantics plus library verbs | Transform stages are explainable. |
| 6 | Block policies | `using`, `retry`, `transaction`, `trace`, `test` as block-call family | Block entry/yield/cleanup diagnostics exist. |
| 7 | Examples and explanation | examples, checks, trace records, `explain` | Failures speak Nomi vocabulary. |
| 8 | Package/adoption surface | first-hour guide, stdlib plan, module/package path | A Python user can run useful examples. |
| 9 | Advanced fenced layers | quote/rewrite, capabilities, scoped notation, rank/shape | Explicit boundaries and expansion display exist first. |

The order is not rigid, but phases 1-3 are dependency-heavy and should not be
skipped. Phase 0A is the recommended runway before broad syntax experiments:
it does not need to finish completely, but enough of it should exist that a new
feature has one declared home, one inspection path, and one test template.

## Phase 0: Baseline And Inventory

Goal: know exactly what the current prototype supports, what is partial, and
what is purely aspirational.

Work:

- Create a current-feature matrix with columns:
  `syntax`, `parser`, `interpreter modes`, `tests`, `samples`, `docs status`.
- Mark features as `implemented`, `partial`, `planned`, or `rejected-for-now`.
- Separate user-facing syntax from Python-hosted implementation artifacts.
- Identify stale docs where implemented behavior and design target diverge.

Likely files:

- `docs/convenience/README.md`
- `docs/convenience/implementation_learnings.md`
- `docs/language/implementation_todos.md`
- `samples/demo.nomi`
- `samples/demo_terse.nomi`
- `prototype/tests/data/sample_sources/interpreter/`

Tests:

```bash
pytest --interpreter-modes reduced prototype/tests/unit/parser/desugar
pytest prototype/tests/functional
pytest prototype/tests/regression/test_interpreter.py
```

Caveats:

- The regression suite includes user-facing samples, so sample edits are
  semantic changes.
- Some docs intentionally describe future behavior; do not "correct" them down
  to current implementation without preserving the design target.

Exit gate:

- A reader can tell which features are real, partial, future, and rejected.

## Phase 0A: Declarative Syntax Substrate

Goal: make the grammar, parser, lowering, interpreter, and tests ready for
fast syntax experiments without committing every experiment to the default
language.

Design decisions before coding:

- Minimal `SyntaxFeature` manifest shape.
- Feature statuses and which statuses enter the default parser.
- Surface AST versus core AST naming and ownership.
- Source-span representation and whether Python AST keeps spans by side table.
- Inspection output format for humans and agents.
- Named experiment profiles: `default`, `lab`, `target-tour`, `docs-only`.

Implementation slices:

1. Add passive feature manifests and keep current behavior unchanged.
2. Add `tools.syntax.inspect` for raw tree, transformed tree, and current
   Python AST.
3. Add source spans for a few high-value nodes.
4. Wrap existing desugar passes in metadata.
5. Add parse/lowering snapshot templates for syntax features.
6. Add feature profiles only after the parser API can cache by feature set.

Likely files:

- `prototype/grammar/assemble.py`
- `prototype/parser/nomi/usage.py`
- `prototype/parser/nomi/ast_.py`
- `prototype/parser/nomi/functions.py`
- `prototype/parser/nomi/desugar/`
- `prototype/interpreter/python/interpreter.py`
- `prototype/interpreter/reduced/interpreter.py`
- `prototype/tests/conftest.py`
- `.agents/skills/nomi-*`

Tests/checks:

- parser cache tests for distinct feature sets;
- inspection CLI snapshots for pipeline, block call, match, where, and holes;
- reduced-interpreter invariant tests for removed nodes;
- feature-template tests proving a new syntax package has required metadata.

Caveats:

- This is a workflow substrate, not a plugin system. Keep manifests static and
  boring until real feature packages prove what they need.
- Do not migrate every old syntax form at once. Put new and awkward forms on
  the new path first.
- Runtime semantics should not change in this phase except where needed to
  preserve current behavior under the new inspection path.

Exit gate:

- A new syntax proposal can declare its status, grammar, normal form,
  diagnostics, tests, docs, and feature profile before any runtime semantics
  are implemented.

## Phase 1: Binding Engine

Goal: make binding constraints a real semantic substrate rather than scattered
annotation behavior.

Design decisions before coding:

- Exact shape of `BindingError`.
- Whether `BindingError` subclasses `TypeError`, wraps it, or replaces it.
- Constraint representation: type constraint, predicate constraint, expression
  constraint, message, source span.
- Constraint truth rule: must return `true`, truthy, or non-false/non-none?
- Rebinding rule and deletion rule.

Implementation slices:

1. Add `Constraint` value representation.
2. Add `BindingError` with structured fields.
3. Add `BindingTarget` for simple name targets.
4. Route annotated assignment through the new engine.
5. Preserve compatibility shims where tests currently expect `TypeError`.

Likely files:

- `prototype/interpreter/nomi/binding.py`
- `prototype/interpreter/nomi/env.py`
- `prototype/interpreter/python/binding.py`
- `prototype/parser/nomi/...` if syntax changes are needed
- `prototype/tests/functional/`
- `prototype/tests/unit/`

Tests:

- focused assignment success/failure tests;
- rebinding keeps/replaces constraints;
- failed binding does not commit;
- multiple constraints preserve the failing expression;
- `else "message"` once syntax exists.

Caveats:

- Python AST annotations are a bootstrap substrate. Avoid baking Python AST
  limitations into the semantic model.
- Existing behavior may rely on plain `TypeError`; transition carefully.
- Source spans may be incomplete until Nomi-owned nodes mature.

Exit gate:

- Assignment constraints use the same structured binding path and produce
  explainable failures.

## Phase 2: Parameter, Block, And Pattern Binding

Goal: reuse the binding engine everywhere names enter scope.

Design decisions before coding:

- Grouped parameter constraint syntax: `x:(int, x > 0)`.
- Arrow function constraint support or clear rejection.
- Block parameter mapping: one value, many values, tuple/list expansion,
  defaults, wrong arity.
- Pattern failure versus constraint failure in direct assignment and `match`.
- Whether constrained match capture failure is case non-match or diagnostic.

Implementation slices:

1. Route function call argument binding through `BindingTarget`.
2. Add grouped parameter constraint parsing/lowering.
3. Use binding engine for block parameters.
4. Use binding engine for destructuring targets.
5. Use tentative binding for match captures.

Likely files:

- `prototype/parser/nomi/functions.py`
- `prototype/parser/nomi/ast_.py`
- `prototype/interpreter/python/function.py`
- `prototype/interpreter/nomi/functions.py`
- `prototype/interpreter/python/patterns.py`
- `prototype/interpreter/nomi/generator_state.py`
- `prototype/interpreter/python/generator_state.py`

Tests:

- parameter constraints with positional/keyword/default/varargs;
- block parameter constraints prevent body execution;
- destructuring assignment rollback;
- match case constraint failure does not leak captures;
- reduced interpreter parity after desugaring.

Caveats:

- Function argument mapping is Python-compatible and subtle. Do not reimplement
  it in a weaker ad hoc path.
- Block calls currently use resumable generator mechanics; this is delicate.
- Pattern matching may already depend on Python-like behavior; preserve where
  Nomi has not explicitly diverged.

Exit gate:

- Assignment, parameters, block parameters, and pattern captures all share one
  binding story in behavior and diagnostics.

## Phase 3: Product `data` And Explicit Decode

Goal: introduce owned program data and explicit boundary conversion without
adding a peer `schema` language.

Design decisions before coding:

- Product `data` syntax and constructor behavior.
- Field defaults, optional fields, extra fields, missing fields.
- Decode return mode: raise `BindingError`, return `Result`, or offer both
  through separate APIs.
- Field provenance representation.
- Display/equality rules.

Implementation slices:

1. Specify and parse minimal product `data`.
2. Lower or represent data declarations without losing field spans.
3. Construct values with field binding constraints.
4. Add `Data.decode(raw)` for mappings.
5. Add decode diagnostics with field paths.

Likely files:

- `prototype/grammar/layers/`
- `prototype/parser/nomi/`
- `prototype/interpreter/nomi/`
- new runtime data module if useful
- `prototype/tests/functional/`
- `samples/`

Tests:

- construct valid data;
- fail field constraint;
- default field;
- missing/extra field policy;
- decode with provenance;
- pattern match on data if supported in same phase or deferred explicitly.

Caveats:

- Do not introduce `shape` as a shortcut for decode pressure.
- Decide whether data values are nominal, structural, or hybrid early enough
  for match and display.
- Avoid overfitting to Python dataclasses if Nomi's owned data model differs.

Exit gate:

- A fixture like `SignupRequest.decode(request.json)` can be specified and
  tested with clear diagnostics.

## Phase 4: `Result` And Failure Taxonomy

Goal: separate absence, expected failure, exceptions, constraint failure, and
pattern non-match.

Design decisions before coding:

- Standard `Result[T, E]` representation.
- Standard `Option` or optional-value conventions, if any.
- Whether `decode` returns `Result` by default.
- Error conversion rules.
- Whether propagation `?` is still deferred.

Implementation slices:

1. Add `Result` as ordinary data or prelude value.
2. Add helper functions: `Ok`, `Err`, `then`, `map`, `collect_results`.
3. Ensure match can destructure result variants.
4. Update fixtures to prefer explicit `match` before `?`.
5. Only then revisit propagation syntax.

Tests:

- construct/match `Ok` and `Err`;
- collect many row decode results;
- ensure `none ?? fallback` does not catch `Err`;
- ensure exceptions remain exceptions.

Caveats:

- Rust/Zig/Roc-style propagation is tempting but premature until return
  constraints and conversions are clear.
- Go-style explicit errors are readable but can become repetitive; helper
  functions should be tried before syntax.

Exit gate:

- Expected failures in decode/parse flows are expressible without exceptions or
  optional chaining.

## Phase 5: Flow, Collections, And Query Vocabulary

Goal: make ordinary collection and table transformations readable before adding
query syntax.

Design decisions before coding:

- Pipeline argument insertion rules.
- Placeholder interaction with pipeline.
- Canonical verb names: `where`, `select`, `derive`, `group`, `join`, `sort`,
  `window`, `fold`.
- Eager collections versus plan values.
- `explain` behavior for transforms.

Implementation slices:

1. Stabilize `|>` tests and docs.
2. Provide library verbs over lists/iterables.
3. Add simple plan value if needed for explanation.
4. Add fixture-backed examples for CSV/table transforms.
5. Defer query block syntax until verbs prove insufficient.

Tests:

- pipeline lowers to ordinary calls;
- placeholder position behavior;
- list transformations;
- failures in pipeline stage include stage name/source;
- plan/explain tests if plans are introduced.

Caveats:

- Do not copy SQL before the flow vocabulary is stable.
- Do not let `_` become a full second lambda language.
- Lazy execution changes failure timing; diagnostics must make that visible.

Exit gate:

- Fixture 4 notebook transformation has a library-first path and explanation
  story.

## Phase 6: Block Policies

Goal: turn block calls into a usable policy abstraction, not just syntax.

Design decisions before coding:

- `return` inside block: returns from function, block, or policy?
- Cleanup errors versus body errors.
- Retry semantics and idempotence warnings.
- Transaction commit/rollback semantics.
- Trace records for block entry/yield/resume/cancel.

Implementation slices:

1. Clarify existing block call semantics with tests.
2. Route block parameters through binding engine.
3. Implement `using` as a standard policy.
4. Implement `trace` as a low-risk explanation policy.
5. Add `retry` and `transaction` after failure semantics are clearer.

Tests:

- block receives yielded values;
- constrained block parameter failure;
- nested block policies;
- cleanup on success/failure;
- trace records include block events.

Caveats:

- The generator/coroutine substrate is already delicate; refactor only with
  focused tests around pause/resume/send/throw.
- Policy names should start as library conventions, not one keyword per policy.

Exit gate:

- `using`, `trace`, and one retry/transaction-style policy are explainable as
  the same block-call mechanism.

## Phase 7: Examples, Trace, And Explain

Goal: make explanation a visible feature across earlier phases.

Design decisions before coding:

- Trace record schema.
- `explain(value)` output shape.
- Example block syntax and scope.
- Relationship between examples, tests, docs, and notebooks.

Implementation slices:

1. Add trace records for binding failures.
2. Add trace records for decode and match.
3. Add trace records for pipeline stages.
4. Add `examples:` blocks for functions.
5. Connect examples to tests and docs.

Tests:

- structured diagnostics include source, value, failed rule, binding kind;
- `explain` on decode failure;
- example success/failure;
- snapshot tests for user-facing messages.

Caveats:

- Snapshot tests can become brittle; separate stable semantic fields from
  presentation details where possible.
- Do not expose Python internal AST names in user diagnostics.

Exit gate:

- Users can ask why a boundary, branch, pipeline, or example failed.

## Phase 8: Adoption Surface

Goal: make the language usable as a small everyday tool, not only a research
prototype.

Design decisions before coding:

- First-hour tutorial scope.
- Standard prelude and standard library naming.
- Module/package layout.
- Python interop boundaries.
- Formatting and style rules.

Implementation/docs slices:

1. Write first-hour Nomi doc.
2. Write prelude/stdlib shape note.
3. Write module/package/interoperability note.
4. Add runnable samples for CLI, CSV, config, HTTP boundary.
5. Keep web playground and notebook examples aligned.

Tests/checks:

- sample regression suite;
- web manifest freshness;
- notebook smoke checks;
- CLI e2e tests.

Caveats:

- Adoption work is not glamorous but determines whether the language feels real.
- Standard library promises should be conservative until names and errors are
  stable.

Exit gate:

- A Python user can read docs, run examples, and understand the errors without
  knowing the implementation.

## Phase 9: Advanced Fenced Layers

Goal: add long-horizon power without damaging everyday Nomi.

Candidates:

- `quote:` and rewrite rules;
- capability/world values;
- scoped notation via `use`;
- rank/shape collection functions;
- structured concurrency;
- effect handlers or typed effects.

Preconditions:

- source spans and expansion display exist;
- diagnostics can point through transformations;
- normal forms are stable;
- target fixtures prove the everyday layer is coherent.

Caveats:

- These features are exciting and dangerous. They should not be used to avoid
  hard decisions in binding, data, failure, flow, or blocks.

Exit gate:

- Each advanced layer is fenced, inspectable, and ignorable by everyday users.

## Cross-Phase Risks

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Python AST overfitting | The bootstrap substrate may constrain Nomi semantics. | Introduce Nomi-owned nodes/spans at feature boundaries. |
| Too much syntax too early | Pleasantness becomes memorization burden. | Use degrees-of-freedom ladder and library-first trials. |
| Diagnostics postponed | Retrofitting explanation is expensive. | Add trace/diagnostic fields with each semantic feature. |
| Block/coroutine fragility | Resumable control touches evaluation deeply. | Keep block changes small and heavily tested. |
| `Result`/exception confusion | Failure model becomes hard to teach. | Maintain explicit taxonomy and examples. |
| Query DSL drift | Tables become a second language. | Keep verbs and plan values before query syntax. |
| Docs/spec divergence | Agents and humans implement different languages. | Update docs, fixtures, samples, and tests together. |
| Adoption neglect | The language remains impressive but unusable. | Treat first-hour docs, stdlib, tooling, and interop as design tasks. |

## Open Questions Register

High-priority questions:

1. Should decode return `Result` by default, raise structured `BindingError`,
   or expose both `decode` and `decode!`-style variants?
2. What exact truth rule should constraints use?
3. How much source-span fidelity is possible before replacing Python AST as the
   semantic substrate?
4. Should `data` values be immutable by default?
5. What is the default policy for missing, extra, and optional fields?
6. How does `return` behave inside block-policy bodies?
7. What does `explain` return: string, structured value, rendered report, or
   all three through display policy?
8. How should lazy pipeline/query failures report timing and source stage?
9. What is the minimum module/package design needed before examples scale?
10. Which advanced feature, if any, should be used as the first scoped
    extension proof: units, regex captures, or symbolic rewrite?

Lower-priority but important:

- user-defined display policy;
- typed templates and escaping;
- duration/time-zone literal semantics;
- secrets and redaction;
- formatter doctrine;
- package publishing;
- AI-readable expansion format.

## Recommended Next Three Work Packages

### Package A: Binding Engine Foundation

Deliver:

- `BindingError`
- `Constraint`
- simple-name `BindingTarget`
- assignment constraint migration
- focused tests and docs updates

Why first:

Binding is the normal form for parameters, data fields, patterns, decode, and
block parameters. It unlocks most later work.

### Package B: Data Boundary Spec Before Code

Deliver docs first:

- focused `data_decode_boundary_feature.md`
- missing/extra/default/optional field policy
- decode failure examples
- provenance and redaction model

Why second:

Decode drives the most useful adoption fixtures, but it should not be
implemented until field and failure semantics are settled.

### Package C: Trace/Diagnostic Skeleton

Deliver:

- minimal trace record schema
- diagnostic field conventions
- `explain` shape decision
- binding/decode/pipeline examples

Why third:

It prevents every feature from inventing its own error story.

These packages can overlap in design, but implementation should keep Package A
as the first critical path.

## Commit Discipline

For implementation work:

- one semantic slice per commit;
- focused failing test first where possible;
- update docs in the same commit when behavior changes;
- update samples only after focused tests pass;
- regenerate regression snapshots only when output intentionally changes;
- do not mix advanced syntax exploration with core semantic refactors.

For design work:

- use [Design Proposal Template](design_proposal_template.md);
- link source-language research to [Language Family Coverage Map](../research/language_family_coverage_map.md);
- classify freedom level with [Language Degrees Of Freedom](language_degrees_of_freedom.md);
- test examples against [Target Program Fixtures](target_program_fixtures.md)
  and [Target Language Tour](target_language_tour.md);
- promote decisions into `docs/language/` or `docs/features/`.
