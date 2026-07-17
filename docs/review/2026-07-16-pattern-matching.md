# Pattern Matching Design Pass

> Status: current-to-target implementation bridge and dated review evidence.
> Canonical language behavior lives under `docs/design/`.

## Pass Packet

- Research: `docs/research/pattern_matching.md`
- Canonical design: `docs/design/pattern_matching.md`
- Focused target: `docs/design/pattern_matching_target.nomi`
- Implementation bridge: `docs/review/2026-07-16-pattern-matching.md`

The packet is registered in `config/design_passes.json` with status
`implementing`.

## Verdict

The prototype has a surprisingly broad Python-shaped pattern surface, but it
does not implement the target semantic center. Its strongest reusable assets
are parser coverage, Python AST interoperability, and the Core runtime's
rollback experiment. Its largest liabilities are capture leakage, truthy and
potentially repeated guards, lossy Core representation, missing exhaustiveness,
and several convenience syntaxes the target now rejects.

Do not polish the existing `match`/`case` behavior into an accidental
specification. Standalone target patterns now have dedicated Surface nodes and
conformance data; match containers, typed Core representation, and runtime
semantics must migrate toward the target packet without routing back through
Python AST authority.

## Target Delta

| Area | Current prototype | Accepted target |
| --- | --- | --- |
| Arm syntax | Python-like `case`, `if` guards, inline semicolon form | no `case`; `when`; indented `=>` or `:` arms |
| Match completeness | unmatched statement silently does nothing | every match exhaustive |
| Capture commit | Python runtime writes directly into current environment | tentative, atomic, immutable arm frame |
| Successful scope | captures leak after the arm | captures end with the arm |
| Guard type/effects | ordinary truthiness and host evaluation | pure deterministic `Bool`, once |
| Pattern domain | Python class/value/sequence/mapping patterns | closed nominal and strict structural Nomi values |
| Sequence matching | arbitrary iterable can be materialized | strict list/tuple only; never consume a stream |
| Collection remainder | Python `*name`/`**name` split | one pattern-only `..`/`..name` family |
| Map matching | Python-oriented `dict` subset semantics | exact unless `..`/`..rest` makes openness visible |
| Choice aliases | `if let`, `while let`, `guard let`, piecewise functions | `match` only |
| Binding failure | refutable destructuring can fail at runtime | binding patterns statically irrefutable |
| Coverage | no usefulness or exhaustiveness pass | typed matrix analysis with witnesses |
| Representation | Python `ast.Match*`; lossy general Core nodes | dedicated lossless Pattern Surface and typed Core contract |

## Current Implementation Map

### Grammar and lowering

- `prototype/grammar/layers/patterns.lark` defines `match` plus mandatory
  `case`, guards spelled `if`, Python literals, captures, wildcard, sequence,
  mapping, class, or, and `as` patterns.
- `prototype/grammar/layers/expressions.lark` adds inline semicolon matches and
  expression cases.
- `prototype/grammar/layers/statements.lark` adds `if let`, `while let`, and
  `guard` pattern shortcuts.
- `prototype/parser/python/patterns.py` lowers directly to Python
  `ast.Match*`. Constrained captures are folded into guards rather than
  represented as a distinct Nomi contract.
- `prototype/parser/nomi/rust_payload.py` reconstructs patterns from text and
  supports only a partial Python-AST-shaped subset. It is not a lossless
  parser-frontend contract.
- The separate target-only path now uses
  `prototype/grammar/pattern_surface.lark`,
  `prototype/parser/nomi/pattern_surface.py`, and Rust `pattern-json` to emit
  Pattern Surface v1. It is not connected to default parsing or execution.

### Runtime and IR

- `prototype/interpreter/python/patterns.py` mutates the active environment as
  nested matching proceeds. Failed nested patterns, alternatives, and guards
  can expose captures; successful captures remain after the arm.
- The Python interpreter accepts truthy guard values, silently returns when no
  case matches, materializes general iterables for sequence patterns, and
  limits maps to host `dict`.
- `prototype/syntax/core.py` represents `Match` and `PatternTest` but reuses
  expression nodes such as `Load`, `Sequence`, and `MappingLiteral` as
  patterns. Capture versus loaded value is ambiguous, and several source forms
  have no faithful Core shape.
- `prototype/runtime/backends/core_runtime.py` snapshots and restores its frame
  on pattern or guard failure. That experiment is directionally correct, but
  successful bindings still occupy the surrounding frame and the pattern set
  is narrow.
- `prototype/runtime/js/core_runtime.js` mirrors the Core rollback behavior but
  also keeps successful bindings in the current frame, uses JavaScript
  truthiness, and returns nil for an unmatched match.

### Tests and product surfaces

- `prototype/tests/features/patterns/` primarily locks in current Python-like
  syntax and includes assertions that captures leak after `match`.
- `prototype/tests/unit/syntax/test_core_ir_patterns.py` and
  `prototype/tests/unit/runtime/test_core_runtime_patterns.py` cover the Core
  experiment, including rollback on some failed attempts.
- Regression samples exercise implemented convenience syntax, so snapshots
  describe current product behavior rather than the new target.
- `prototype/grammar/nomi.ref.lark`, VS Code completion/hover data, TextMate
  grammar, snippets, Rust/Wasm payload handling, and browser manifests all
  still recognize or advertise `case` and other retired forms.

## Critical Semantic Gaps

### 1. Pattern authority stops at standalone fragments

Pattern Surface v1 now owns standalone target pattern structure, exact map
openness, source, spans, and frontend diagnostics. It does not yet represent
match mode, arms, guards, coverage evidence, capture transactions, or typed
Core lowering. Python AST and the current general Core nodes remain
transitional and must not become authority for those missing contracts.

### 2. Environment mutation precedes success

The Python interpreter commits captures while testing. Fixing only the guard
rollback would still leave nested and or-pattern failures incorrect. The
matcher must return a candidate capture set without mutating lexical state;
the arm owns a fresh frame only after guard success.

### 3. Coverage is absent

Runtime fallthrough cannot distinguish a deliberately open statement match
from a forgotten domain case, and the target no longer permits the former.
Exhaustiveness and usefulness need typed constructor information, dedicated
patterns, and structured witnesses before the target form is promoted.

### 4. Structural matching can execute or consume too much

Materializing arbitrary iterables can consume a one-pass source and run user
code. Class patterns and user equality/attribute lookup similarly blur shape
with calls. Target matching is restricted to compiler-known nominal values and
strict structural values.

### 5. Frontend parity stops at the fixture boundary

Lark and Rust now share one versioned standalone-fragment schema and fixture
set. That does not yet cover the complete target literal codec, match arms,
Core/runtime values, VS Code tooling, or the web product. The default Rust
payload bridge still reconstructs current Python-shaped patterns from text.

## Ordered Bridge

### Phase 0: Conformance packet

**Status (2026-07-16): structural fixture framework complete; lexical closure
pending.** Pattern Surface v1 now has a canonical schema, target-derived
positive/negative fixtures, structured diagnostics, and exact Lark/Rust
payload parity for that fixture set. A coherence audit found backend drift for
escape decoding; schema validation and reserved-name checks are now
deterministic, while a shared codec and relational span gate remain. Those
must close before the standalone-fragment gate is considered complete. Arm
mode, guards, coverage witnesses, values, and scopes remain part of the
match-container passes below.

1. Treat `docs/design/pattern_matching_target.nomi` as target-only source.
2. Derive accepted/rejected parse fixtures and diagnostic records from it.
3. Record expected arm mode, captures, guard type/effect, coverage witnesses,
   values, and scopes in backend-neutral fixture data.

**Gate:** another parser author can produce the same lossless Pattern Surface
without consulting Python AST or an interpreter.

### Phase 1: Dedicated Surface patterns

**Status (2026-07-16): pattern-node slice complete; match containers
pending.** Dedicated nodes, UTF-8 spans, fragment grammar, and the Rust
`pattern-json` producer are in place without changing the default runnable
grammar. `MatchExpression`, `MatchStatement`, arms, and the no-`case` target
profile are the next slice.

1. Add lossless Pattern Surface nodes for every accepted target form.
2. Add `MatchExpression`, `MatchStatement`, and arm nodes with source spans.
3. Add a target grammar profile using no `case` and `when` guards.
4. Keep current runnable syntax capability-gated until the target path reaches
   runtime parity; do not mix both syntaxes in one profile.
5. Replace Rust payload text reconstruction with the versioned Surface schema.

**Gate:** Lark and Rust frontends emit equivalent serialized Surface fixtures
for every positive and negative target case.

### Phase 2: Transactional matcher

1. Implement one backend-neutral pattern-attempt contract returning
   `{matched, captures, trace}` without environment mutation.
2. Create an arm-local immutable frame only after one pure Boolean guard
   succeeds.
3. Scope the frame to the arm body and remove it on every exit.
4. Restrict list/map/nominal tests to strict language values.
5. Make unmatched Core execution a structured integrity failure.

**Gate:** failed nested patterns, failed alternatives, and false guards leak no
bindings; successful captures are unavailable after `match` in Python and
JavaScript runtimes.

### Phase 3: Typed coverage and usefulness

1. Add constructor-space metadata for closed `data`, Option, Result, Bool,
   tuples, lists, maps, Unknown, and Any.
2. Implement a Maranget-style usefulness matrix over typed patterns.
3. Emit witness patterns for missing space and references to covering arms for
   useless rows.
4. Ignore guarded rows for coverage proof.
5. Reject refutable patterns in binding, parameter, and loop-target contexts.

**Gate:** nested closed-domain fixtures have stable exhaustive, missing, and
useless-arm diagnostics in CLI, editor protocol, and browser result records.

### Phase 4: Target pattern set

1. Implement nominal product/variant, tuple, strict-list/rest, exact/open map,
   or, and as patterns.
2. Enforce duplicate capture and alternative binding rules.
3. Enforce pure `Bool` guards and once-only evaluation.
4. Separate pattern mismatch, guard rejection, decode error, and runtime
   integrity failure in semantic events and explanation traces.

**Gate:** every construct in the focused target has value, scope, diagnostic,
and explanation conformance coverage.

### Phase 5: Product migration

1. Update the generated grammar reference, feature metadata, syntax inspector,
   VS Code grammar/completion/hover/snippets, and notebook highlighting.
2. Update the Rust/Wasm worker, JavaScript runtime, Pyodide fallback, web
   examples, and manifests in one declared capability slice.
3. Replace current tests and snapshots that intentionally assert retired
   syntax or leaked scope.
4. Remove `case`, inline match, `if let`, `while let`, `guard let`, class
   patterns, and piecewise pattern dispatch after no supported path needs them.
5. Promote the focused fixture or a compact derivative into `samples/` only
   when CLI and browser execute it identically.

**Gate:** `pytest`, web runtime checks, manifest freshness, editor tests, and a
browser smoke snippet all agree on target syntax and semantics.

## Immediate Action List

| Order | Action | Completion evidence |
| --- | --- | --- |
| 1 | **Complete:** define serialized Pattern Surface schema and fixture framework. | Canonical schema, two producers, structured fixtures, and capability registration. |
| 2 | **Partial:** close standalone-fragment coherence. | Schema validation, reserved names, quote spelling, and separator shape are covered; shared scalar codec, complete lexical fixtures, and relational span validation remain. |
| 3 | Parse target statement and expression arms without `case`. | Lark/Rust Match Surface snapshots with mode, guards, bodies, and spans. |
| 4 | Add candidate-capture matcher API and arm frame. | Focused rollback/scope tests in both runtimes. |
| 5 | Add typed constructor-space and usefulness prototype. | Exhaustive, missing-witness, and useless-arm fixtures. |
| 6 | Add exact/open map and strict list semantics. | No iterable consumption; stable extra-key traces. |
| 7 | Migrate Rust/Wasm and editor surfaces. | Surface parity and extension tests. |
| 8 | Switch web examples and remove retired forms. | Browser runtime check and regenerated manifest. |

## Coherence Audit Follow-Up

The post-implementation audit closed stale status/authority language and made
schema validation, reserved captures, canonical quote spelling, and numeric
separator shape deterministic. It also identified work that should not be
hidden inside the match-container implementation:

1. **Shared scalar literal codec:** Pattern Surface currently fences itself to
   the cross-frontend subset. Replace Python `ast.literal_eval` and the Rust
   lexer decoder with one specified Nomi escape/interpolation/value contract,
   then cover ordinary, raw, multiline, bytes, brace escaping, Unicode, and
   invalid escapes from shared fixtures.
2. **Relational document validation:** verify root/child/entry/rest/capture span
   containment, UTF-8 boundaries, map openness/rest consistency, node arity,
   and diagnostic exclusivity independently of either producer.
3. **Version/promotion policy:** v1 is experimental while no external consumer
   depends on it. Declare compatibility rules only when editor, browser, or
   runtime consumers are admitted; until then change the schema directly.
4. **Product capability honesty:** the Wasm export proves transport, not web
   feature support. Keep feature `web`/`notebook` capability false until a
   user-facing or tooling consumer validates and displays the artifact.
5. **Target vocabulary ownership:** reserved names are currently mirrored in
   target docs, JSON Schema, Python, and Rust, with conformance tests catching
   producer drift. Extract one declarative target-vocabulary artifact before
   the target grammar grows, then generate or validate every projection.

## Migration Risks

- A grammar-only syntax switch would leave the existing leak semantics hidden
  under prettier target spelling.
- Reusing Python `ast.Match*` as the new Surface would make exact map openness
  and Nomi coverage metadata awkward or lossy.
- Running old and new arm syntaxes in one default grammar would create the
  recognition duplication this pass is intended to remove.
- Building exhaustiveness before types and nominal constructor metadata exist
  would encourage unsound heuristics.
- Updating Python tests without JavaScript/web conformance would repeat the
  current frontend split.
- Treating fixture equality as grammar completeness would preserve hidden
  Lark/Rust differences in literal values and identifier admission.

## Pass Retrospective

### Evidence That Changed The Design

The strongest change was not a new pattern form but a stricter boundary.
Swift/Gleam's distinction between irrefutable binding and refutable choice made
the current runtime-failing list destructure look inconsistent with Nomi's
binding story. Swift's exhaustive statement switches, Erlang/Racket's explicit
failure on no clause, and the local-reasoning goal also outweighed Python's
silent unmatched statement behavior. The target now requires every `match` to
be exhaustive.

A final punctuation audit also changed the surface. Python-style `*tail` and
`**rest` made `**` mean both exponentiation and map openness. Rust and Gleam
showed that one `..` remainder family can cover strict list and record shape;
Nomi now uses `[head, ..tail]`, `{key: pattern, ..}`, and
`{key: pattern, ..rest}` while keeping `*` and `**` arithmetic-only.

Research into Scala extractors, F# active patterns, GHC views, and Racket match
expanders showed that extensibility imports call/effect/evaluation questions
into the pattern engine. Nomi therefore keeps the initial pattern set closed.

### Workflow Friction

The previous consolidated docs named patterns but did not own their detailed
syntax, coverage, scoping, or migration contract. Historical research was rich
but mixed stale target choices with evidence, and there was no deterministic
way for an agent discussing `match` to discover all relevant artifacts.

### Durable Improvement

This pass introduced `config/design_passes.json`,
`docs/orientation/design_pass_workflow.md`, and
`python3 -m tools.design_passes check`. Hooks, skills, prompt templates, and
the agent doctor consume the same registry, so future passes can route from a
topic to research, canonical design, target source, bridge, validation, and a
required retrospective without another parallel index.

### Next Pass

First complete the bounded standalone-fragment coherence items above, most
importantly the shared scalar-literal contract and relational validator. Then
add lossless `MatchExpression`, `MatchStatement`, and arm Surface containers
and parse target statement/value arms without `case` in an explicitly selected
target profile. Do not change default runnable syntax or lower target matches
into Python AST until the transactional matcher exists.
