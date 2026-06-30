# Operational Implementation Plan 2026-06-30

> Status: active operational plan.
>
> Scope: implementation planning for the current feature-packet sequence. This
> document does not add syntax by itself. It translates active feature packets
> into ordered implementation slices, concrete files, tests, validation gates,
> and commit boundaries.

## Purpose

The recent consolidation pass produced three active implementation targets:

- [Binding, Data, And Pattern Integration Feature](../features/binding_data_pattern_integration_feature.md)
- [Collection, Table, And Rank Integration Feature](../features/collection_table_rank_integration_feature.md)
- [Block Policy Prelude Feature](../features/block_policy_prelude_feature.md)

This plan makes those packets operational. The goal is not to implement the
entire future language in one sweep. The goal is to build the shared substrate
that lets Nomi add serious language features without hardcoding three parallel
systems for binding, data, patterns, tables, blocks, diagnostics, and
frontends.

The implementation rule:

```text
shared metadata and passive nodes first
then one small behavior path
then diagnostics/events
then frontend/capability truth
then samples
```

The first successful phase should make one narrow path genuinely better while
making the next paths easier, not harder.

## Current Substrate To Build On

The repository already has useful hooks. The implementation should extend these
instead of inventing new side channels.

| Existing hook | Current role | Operational use |
| --- | --- | --- |
| `prototype/syntax/features.py` | `SyntaxFeature`, layer metadata, capability axes, docs/tests/samples. | Add feature-owned capability truth and future metadata fields only where needed. |
| `prototype/syntax/surface.py` | `SurfaceNode`, `SourceSpan`, `BlockCall`, passive `BindingTarget`, `DataDecl`. | Add passive records before changing semantics. |
| `prototype/runtime/diagnostics.py` | `Diagnostic`, `RuntimeEvent`, `RuntimeEventCollector`, semantic event families. | Add feature producers without private event shapes. |
| `prototype/runtime/api.py` | `ExecutionResult`, runtime facade, inspection stages. | Keep CLI/web/notebook converging on one result contract. |
| `prototype/runtime/host_capabilities.json` | Declared host capability manifest. | Extend toward policy/capability honesty. |
| `prototype/parser/nomi/lowering/*` | Feature-specific lowering mixins. | Migrate one source construct at a time into owned surface shapes. |
| `prototype/tests/unit/syntax/test_feature_capabilities.py` | Capability-axis contract tests. | Keep status honest before and after feature promotion. |
| `prototype/tests/unit/runtime/test_execution_result_contract.py` | Diagnostic/event/result record tests. | Add event producer assertions here or nearby. |
| `prototype/tests/features/*` | Feature behavior tests. | Add focused behavior fixtures per promoted packet. |
| `tools.syntax.inspect` | Inspect features, capabilities, pipelines, core, passes, expansions. | Validate each slice is inspectable. |

## Implementation Principles

1. **No new permanent syntax before ownership.** A feature first names its
   owner, layer, normal forms, status, diagnostics, tests, and capability axes.
2. **Passive shape before behavior.** Add records such as `BindingTarget`,
   `Constraint`, `FlowStep`, `CollectionPlan`, and `BlockPolicy` before routing
   runtime semantics through them.
3. **One event vocabulary.** Binding, decode, match, pipeline, query, block,
   capability, example, and rewrite producers must use `RuntimeEvent`.
4. **Capability honesty beats demos.** Target-only examples stay outside
   runnable samples until parser, lowering, runtime, tests, and frontends agree.
5. **Default behavior stays stable.** Named profiles, future query blocks,
   broadcast syntax, and block policies should begin as passive or library-first
   additions unless a slice explicitly promotes behavior.
6. **Commit by proof boundary.** Each commit should leave the repo validated and
   explain what capability became more truthful.

## Workstream Map

| Workstream | Feature packet | Primary normal form | First operational target |
| --- | --- | --- | --- |
| A. Capability and metadata truth | all packets | explanation | feature-owned status/capability fields and inspect output |
| B. Binding/data/pattern | binding/data/pattern packet | binding | shared `BindingTarget` + `Constraint` model for current constrained assignment/parameters |
| C. Decode diagnostics | binding/data/pattern packet + decode packet | data boundary | structured `DecodeError` shapes and field-path events before broad `Data.decode` runtime |
| D. Pattern captures | binding/data/pattern packet + patterns | pattern | passive constrained-capture representation before runtime matching changes |
| E. Flow and collection verbs | collection/table/rank packet | flow | canonical prelude verb contracts and `FlowStep` inspection |
| F. Table plans | collection/table/rank packet | flow + explanation | passive `CollectionPlan` with explainable schema/provenance shape |
| G. Block policy prelude | block policy packet | block | `BlockPolicy` metadata and events for existing block-call/yield path |
| H. Host capability policy | block policy packet + state/capability | capability | capability grants/denials in event vocabulary |
| I. Frontend and fixtures | all packets | explanation | capability matrix, target fixtures, web/notebook labels |

## Phase 0: Baseline And Guardrails

Goal: confirm the repo is healthy before changing implementation behavior.

Commands:

```bash
python3 .codex/scripts/agent_doctor.py
python3 -m tools.syntax.inspect --stage capabilities
python3 -m tools.syntax.inspect --stage resolved-pipelines
pytest prototype/tests/unit/syntax/test_feature_capabilities.py
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
```

Commit rule:

- No behavior changes.
- If any baseline command fails, fix or document the failure before feature
  work starts.

## Phase 1: Feature Packet Metadata And Capability Truth

Goal: make the three new packets visible to the implementation substrate
without pretending their target syntax is implemented.

Likely files:

- `prototype/syntax/features.py`
- `prototype/tests/unit/syntax/test_feature_capabilities.py`
- `docs/language/current_capability_matrix.md`
- `docs/language/implementation_todos.md`

Implementation slices:

1. Add docs-only or target-only `SyntaxFeature` entries for:
   - `binding-data-pattern-integration`
   - `collection-table-rank-integration`
   - `block-policy-prelude`
2. Mark them as `design-needed` or `research-only` with `coverage.target_only`
   and `docs=True`, but `parse/lower/run/explain/web/notebook=False` unless an
   implemented surface already proves the axis.
3. Update capability table tests so these integration packets are visible but
   cannot overstate implementation.
4. Regenerate or refresh `current_capability_matrix.md` from
   `tools.syntax.inspect`.

Validation:

```bash
pytest prototype/tests/unit/syntax/test_feature_capabilities.py
python3 -m tools.syntax.inspect --stage capabilities
python3 .codex/scripts/agent_doctor.py
```

Commit message:

```text
Declare integration packet capability rows
```

## Phase 2: Shared Runtime Event Producer Helpers

Goal: add small helper APIs for feature producers while preserving the existing
`RuntimeEvent` V1 record shape.

Likely files:

- `prototype/runtime/diagnostics.py`
- `prototype/tests/unit/runtime/test_execution_result_contract.py`
- `docs/features/explanation_trace_feature.md`

Implementation slices:

1. Add helper functions for:
   - `record_decode_event`
   - `record_match_event`
   - `record_pipeline_event`
   - `record_block_policy_event`
   - `record_capability_event`
2. Keep helpers thin wrappers around `RuntimeEventCollector.semantic_event`.
3. Add tests that helper records use approved `SEMANTIC_EVENT_KINDS`, stable
   actions, failure kinds, redaction, and next-step fields.
4. Do not yet change parser or interpreter behavior.

Validation:

```bash
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
python3 .codex/scripts/agent_doctor.py
```

Commit message:

```text
Add shared semantic event producer helpers
```

## Phase 3: BindingTarget And Constraint Metadata

Goal: make current constrained assignment and parameter behavior route through
shared metadata without changing user syntax.

Likely files:

- `prototype/syntax/surface.py`
- `prototype/parser/nomi/lowering/data_decl.py`
- `prototype/interpreter/nomi/binding.py`
- `prototype/interpreter/nomi/env.py`
- `prototype/interpreter/nomi/binding_error.py`
- `prototype/tests/unit/syntax/test_surface_nodes.py`
- `prototype/tests/features/binding_constraints/test_parameter_constraints_runtime.py`
- `prototype/tests/unit/interpreter/nomi/test_binding_error.py`

Implementation slices:

1. Extend passive `BindingTarget` with enough fields for:
   - target kind,
   - capture names,
   - structural requirement placeholder,
   - constraints tuple,
   - redaction,
   - message,
   - span.
2. Add a passive `Constraint` dataclass that preserves source expression,
   kind, subject, message, span, and redaction.
3. Adapt data fields to use the richer passive shape while preserving lowering.
4. Adapt current binding runtime to preserve original constraint source where
   possible.
5. Keep existing behavior compatible: current tests should still pass before
   deeper commit/rollback work.

Validation:

```bash
pytest prototype/tests/unit/syntax/test_surface_nodes.py
pytest prototype/tests/unit/interpreter/nomi/test_binding_error.py
pytest prototype/tests/features/binding_constraints/test_parameter_constraints_runtime.py
```

Commit message:

```text
Add shared binding target constraint metadata
```

## Phase 4: Tentative Binding Commit/Rollback

Goal: implement the core checked-receipt behavior for the already-supported
binding surfaces first.

Likely files:

- `prototype/interpreter/nomi/binding.py`
- `prototype/interpreter/nomi/env.py`
- `prototype/interpreter/nomi/functions.py`
- `prototype/tests/features/binding_constraints/test_parameter_constraints_runtime.py`
- new tests under `prototype/tests/features/binding_constraints/`

Implementation slices:

1. Define a small internal binding transaction or temporary frame helper.
2. Use it for assignment constraint checks.
3. Use it for function parameter constraints after argument mapping.
4. Assert failed constraints do not commit or mutate visible names.
5. Keep the existing `BindingError` compatibility path.

Validation:

```bash
pytest prototype/tests/features/binding_constraints
pytest prototype/tests/unit/interpreter/nomi/test_env.py
pytest prototype/tests/e2e/test_nomi_scenarios.py
```

Commit message:

```text
Route constrained bindings through tentative commit
```

## Phase 5: Decode Boundary Skeleton

Goal: add structured decode errors and event shape before broad data decoding
runtime.

Likely files:

- `prototype/runtime/diagnostics.py`
- `prototype/interpreter/nomi/binding_error.py` or a new runtime value module
- `prototype/tests/features/data/`
- `docs/features/data_decode_boundary_feature.md`

Implementation slices:

1. Add passive value shapes for `DecodeError` and `DecodeErrorList`.
2. Include source identity, field path, expected rule, raw value summary,
   redaction, and next step.
3. Add event tests through `record_decode_event`.
4. Add docs-only target fixtures for `Data.decode` if runtime is still pending.
5. Do not add a `shape` keyword.

Validation:

```bash
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
pytest prototype/tests/features/data
```

Commit message:

```text
Add decode error and event skeleton
```

## Phase 6: Pattern And Destructuring Binding Preparation

Goal: prepare constrained pattern captures without changing broad match
semantics prematurely.

Likely files:

- `prototype/syntax/surface.py`
- `prototype/parser/nomi/lowering/match_expr.py`
- `prototype/tests/features/patterns/test_pattern_convenience_runtime.py`
- `prototype/tests/unit/syntax/test_surface_nodes.py`
- `prototype/tests/unit/syntax/test_core_ir_patterns.py`

Implementation slices:

1. Add passive pattern/capture target representation, using `BindingTarget`.
2. Move current `match_expr` IIFE lowering behind a passive `MatchExpr` surface
   shape if practical.
3. Add tests proving current match behavior is unchanged.
4. Add target-only parse/lowering fixtures for constrained captures if grammar
   support is not ready.
5. Add `record_match_event` tests that distinguish shape miss, guard failure,
   and constraint failure.

Validation:

```bash
pytest prototype/tests/features/patterns
pytest prototype/tests/unit/syntax/test_core_ir_patterns.py
pytest prototype/tests/unit/parser/test_parse_snapshots.py
```

Commit message:

```text
Prepare match captures for shared binding targets
```

## Phase 7: FlowStep Metadata And Collection Prelude Contracts

Goal: make ordinary collection flow inspectable before table/query syntax.

Likely files:

- `prototype/syntax/surface.py`
- `prototype/parser/nomi/desugar/pipeline.py`
- `prototype/syntax/features.py`
- `prototype/tests/features/flow/`
- `prototype/tests/unit/parser/desugar/test_expansion_inspection.py`
- `docs/convenience/flow_and_collections.md`

Implementation slices:

1. Add passive `FlowStep` metadata for pipeline inspection if it can be done
   without changing runtime behavior.
2. Declare canonical prelude verbs in docs and capability rows:
   `where`, `select`, `fold`, `scan`, `sort`, `take`, `collect`,
   `collect_results`.
3. Add library-first tests for implemented aliases only.
4. Add event helper tests for `record_pipeline_event`.
5. Keep row shorthand `.field`, table plans, query blocks, and broadcast syntax
   target-only until their boundaries are represented.

Validation:

```bash
pytest prototype/tests/features/flow
pytest prototype/tests/unit/parser/desugar/test_expansion_inspection.py
python3 -m tools.syntax.inspect --stage expansions --source "xs |> select(_)"
```

Commit message:

```text
Add flow step metadata plan contracts
```

## Phase 8: Table And CollectionPlan Skeleton

Goal: define table/plan value shapes and explain contracts without introducing
query blocks.

Likely files:

- `prototype/runtime/backends/values.py` or a new table/plan module
- `prototype/runtime/diagnostics.py`
- `prototype/tests/unit/runtime/`
- `prototype/tests/features/flow/`
- `docs/features/collection_table_rank_integration_feature.md`

Implementation slices:

1. Add passive `TableSchema`, `ColumnSchema`, `CollectionPlan`, and plan-step
   records as runtime values or dataclasses.
2. Add tests for plan JSON/record shape.
3. Add `record_query_event` tests for schema, plan stage, backend capability,
   and materialization trigger.
4. Add target fixtures for lazy `scan_csv -> where -> group -> summarize ->
   explain`.
5. Do not add `query:` syntax yet.

Validation:

```bash
pytest prototype/tests/unit/runtime
pytest prototype/tests/features/flow
```

Commit message:

```text
Add passive collection plan value shapes
```

## Phase 9: BlockPolicy Metadata And Events

Goal: attach policy identity and shared events to existing block-call/yield
machinery.

Likely files:

- `prototype/syntax/surface.py`
- `prototype/parser/nomi/lowering/block_call.py`
- `prototype/interpreter/nomi/generator_state.py`
- `prototype/interpreter/nomi/interpreter.py`
- `prototype/runtime/diagnostics.py`
- `prototype/tests/features/block_calls/`
- `prototype/tests/unit/runtime/test_execution_result_contract.py`

Implementation slices:

1. Add passive `BlockPolicy` metadata or a policy record connected to
   `BlockCall`.
2. Preserve existing block-call lowering and runtime behavior.
3. Emit or test no-op event helpers for enter/yield/bind/resume/cleanup.
4. Add behavior tests only for currently implemented block behavior.
5. Keep `using`, `retry`, `transaction`, `trace`, and `world` as prelude/target
   policies until library/runtime support exists.

Validation:

```bash
pytest prototype/tests/features/block_calls
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
pytest prototype/tests/unit/syntax/test_core_ir_block_calls.py
```

Commit message:

```text
Add block policy metadata and events
```

## Phase 10: Capability Grants And Host Policy Diagnostics

Goal: connect block policies to declared host capability names without adding
an effect type system.

Likely files:

- `prototype/runtime/host_capabilities.json`
- `prototype/runtime/host_capabilities.py`
- `prototype/runtime/diagnostics.py`
- `prototype/tests/contracts/test_host_capabilities_contract.py`
- `docs/features/state_and_capability_model.md`
- `docs/features/block_policy_prelude_feature.md`

Implementation slices:

1. Add passive `CapabilityGrant`/denial event helpers.
2. Extend host capability manifest only with facts that can be enforced or
   inspected today.
3. Add denial/escape diagnostics as passive records first.
4. Add tests for manifest consistency and event shape.
5. Keep full `world(...)` execution policy target-only until host adapters can
   enforce scopes.

Validation:

```bash
pytest prototype/tests/contracts/test_host_capabilities_contract.py
pytest prototype/tests/unit/runtime/test_inspect_capabilities.py
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
```

Commit message:

```text
Add capability grant diagnostic skeleton
```

## Phase 11: Target Fixtures And Capability Matrix Refresh

Goal: create target programs that exercise the integrated language direction
without pretending unsupported syntax is runnable.

Likely files:

- `docs/language/target_program_fixtures.md`
- `docs/language/demo_target.nomi`
- `docs/language/current_capability_matrix.md`
- maybe `prototype/tests/data/target_sources/` if a docs-only fixture directory
  is introduced later

Implementation slices:

1. Add target-only examples for:
   - decode + binding + pattern capture,
   - CSV decode + flow + group + explain,
   - `using`/`retry`/`transaction`/`trace`,
   - capability denial,
   - shape/broadcast mismatch.
2. Label every target-only fixture explicitly.
3. Keep runnable `samples/` unchanged unless tests prove behavior.
4. Refresh capability matrix after metadata changes.

Validation:

```bash
python3 -m tools.syntax.inspect --stage capabilities
python3 .codex/scripts/agent_doctor.py
```

Commit message:

```text
Add target fixtures for integrated feature packets
```

## Phase 12: Frontend And Broad Regression Gate

Goal: run broad validation only after a coherent group of implementation
slices lands.

Commands:

```bash
python3 scripts/check_web_runtime.py
pytest -q
python3 .codex/scripts/agent_doctor.py
```

If generated browser/runtime artifacts become stale:

```bash
python3 scripts/make_web.py
python3 scripts/build_wasm.sh
python3 scripts/check_web_runtime.py
```

Commit rule:

- Commit generated artifacts only when the task is specifically about those
  artifacts and the check proves they are intended.

## Recommended Commit Sequence

This is the concrete order for the next implementation phase:

1. `Declare integration packet capability rows`
2. `Add shared semantic event producer helpers`
3. `Add shared binding target constraint metadata`
4. `Route constrained bindings through tentative commit`
5. `Add decode error and event skeleton`
6. `Prepare match captures for shared binding targets`
7. `Add flow step metadata plan contracts`
8. `Add passive collection plan value shapes`
9. `Add block policy metadata and events`
10. `Add capability grant diagnostic skeleton`
11. `Add target fixtures for integrated feature packets`
12. `Refresh capability matrix after integrated feature planning`

Each commit should include:

- one implementation concern,
- focused tests,
- any docs status update needed for capability honesty,
- a clean `git status`,
- a note about what remains target-only.

## Stop And Review Gates

Pause implementation and review the plan when any of these happen:

- a slice requires grammar changes that would make target-only syntax parse by
  default;
- a feature wants a private diagnostic/event shape;
- query blocks, dot broadcasting, `world(...)`, or constrained pattern captures
  are about to become runnable before their passive representation exists;
- a frontend requires a separate output/error contract;
- a broad test failure suggests Python AST, Core IR, and JS runtime disagree on
  the same source feature;
- the capability matrix would need to say `yes` based only on prose.

## Near-Term Definition Of Done

The next implementation phase is successful when Nomi can truthfully show:

- integrated feature packets appear in capability inspection as target/design
  rows;
- binding constraints preserve source-aware `Constraint` metadata;
- current assignment/parameter constraint failures use tentative commit
  semantics;
- decode, match, pipeline, block, and capability event helpers exist and are
  tested;
- table/plan and block-policy records exist as passive, inspectable shapes;
- target fixtures demonstrate the intended cognitive language without entering
  runnable samples too early;
- `agent_doctor`, focused tests, capability inspection, and broad gates pass at
  the right points.

That gives the implementation a real spine: one binding story, one flow story,
one block-policy story, and one explanation story.
