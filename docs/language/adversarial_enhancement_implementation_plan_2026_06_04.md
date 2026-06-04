# Adversarial Enhancement Implementation Plan 2026-06-04

> Status: active implementation plan.
>
> Scope: staged plan for implementing the gates and enhancement queue from
> [Adversarial Language Design Enhancement Notes 2026-06-04](adversarial_language_design_enhancement_notes_2026_06_04.md).
> This document is not a new design critique. It translates that critique into
> concrete repo changes, commit passes, tests, and exit gates.

## Goal

Implement the adversarial enhancement notes without turning Nomi into a bag of
interfaces. The implementation target is one shared spine:

```text
feature packet
  -> feature manifest and capability axes
  -> runtime event schema
  -> command/data/failure model where applicable
  -> CLI/JSON/accessibility rendering
  -> tests and docs lifecycle checks
```

The plan deliberately delays new surface syntax. Nomi should first make the
existing doctrine executable: normal forms, feature ownership, semantic events,
capability honesty, projection tests, and first-hour restraint.

## Dependency Order

The critique's enhancement queue becomes this dependency graph:

```text
admission gates
  -> event schema
     -> failure taxonomy
     -> decode/data boundary
     -> command values
        -> UI projection
        -> agent preview/replay
  -> first-hour Nomi
  -> stdlib/capability baseline
```

Do not implement command palettes, notebook controls, visual projections, or
agent actions before `RuntimeEvent` and `Command` have stable records.

## Phase 0: Make Admission Gates Executable

Purpose: turn the adversarial checklist into required proposal and lifecycle
metadata.

Implementation slices:

1. Extend [Design Proposal Template](design_proposal_template.md) with a
   "Human Interface Impact" section:
   - text form;
   - command-palette name;
   - CLI rendering;
   - JSON/event rendering;
   - notebook/web rendering;
   - accessibility rendering;
   - agent preview;
   - undo/replay;
   - capability;
   - failure kind;
   - long form.
2. Add an "Adversarial Admission Gate" checklist to the template that mirrors
   the twelve questions in the enhancement notes.
3. Add docs lifecycle tests that ensure the template mentions command,
   accessibility, agent preview, event, capability, failure, and long form.
4. Update [Implementation Todos](implementation_todos.md) so the first track
   points at this plan as the gate before new user-facing feature work.

Likely files:

- `docs/language/design_proposal_template.md`
- `docs/language/implementation_todos.md`
- `prototype/tests/unit/tools/test_docs_lifecycle.py`

Checks:

```bash
pytest prototype/tests/unit/tools/test_docs_lifecycle.py
git diff --check
```

Exit gate:

- A new proposal cannot look complete while omitting events, capability,
  accessible rendering, agent preview, failure kind, and long-form reduction.

Recommended commit:

```text
Require adversarial admission fields in design proposals
```

## Phase 1: Define Runtime Event Schema V1

Purpose: replace placeholder semantic events with a stable inspectable record
that can support diagnostics, decode, command execution, UI projection, agent
logs, and replay.

Current basis:

- [runtime diagnostics](../../prototype/runtime/diagnostics.py) already defines
  `Diagnostic`, `RuntimeEvent`, `RuntimeEventCollector`, semantic event
  families, and the first binding-constraint event producer.
- [runtime API](../../prototype/runtime/api.py) and
  [runtime session](../../prototype/runtime/session.py) already carry events
  through `ExecutionResult`.

Implementation slices:

1. Add explicit fields to `RuntimeEvent`:
   - `id`;
   - `parent_id`;
   - `phase`;
   - `feature`;
   - `operation`;
   - `source_span`;
   - `value_summary`;
   - `capability`;
   - `failure_kind`;
   - `redaction`;
   - `next_step`;
   - `payload`.
2. Preserve compatibility with the existing `name` shape for one pass:
   - keep `name` as a computed or stored compatibility field;
   - add `to_record()` for JSON/event rendering;
   - keep current tests passing with minimal assertion changes.
3. Update `RuntimeEventCollector.event()` and `.semantic_event()` to populate
   the schema.
4. Migrate `record_binding_error()` to use:
   - `feature="binding-constraints"`;
   - `operation="constraint_failed"`;
   - `failure_kind="constraint"`;
   - `capability="binding.constraints"`;
   - a redacted `value_summary` instead of only raw `repr`.
5. Add schema tests that verify required keys, stable JSON shape, parent-child
   support, and unknown semantic families still fail.

Likely files:

- `prototype/runtime/diagnostics.py`
- `prototype/runtime/api.py`
- `prototype/runtime/session.py`
- `prototype/tests/unit/runtime/test_execution_result_contract.py`

Checks:

```bash
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
pytest prototype/tests/unit/tools/test_docs_lifecycle.py
git diff --check
```

Exit gate:

- Every runtime event can render as a JSON-safe record with phase, feature,
  operation, capability, failure kind, redaction, and next-step slots.
- Binding-constraint failures remain the first real event family and now use
  the same event schema future features will use.

Recommended commits:

```text
Add structured runtime event records
Migrate binding constraint events to event schema
```

## Phase 2: Expand Feature Capability Axes

Purpose: make feature honesty cover human-facing surfaces, not just
parse/lower/run/reduce.

Current basis:

- [syntax feature registry](../../prototype/syntax/features.py) already has
  `SyntaxFeature`, `FeatureCapabilityAxes`, docs/tests/sample declarations,
  and rendered capability tables.
- [feature capability tests](../../prototype/tests/unit/syntax/test_feature_capabilities.py)
  already prevent overstating explanation, web, and notebook coverage.

Implementation slices:

1. Extend `FeatureCapabilityAxes` with conservative false defaults:
   - `event_producing`;
   - `command_exposed`;
   - `accessibility_rendering`;
   - `agent_previewable`;
   - `undo_replay`;
   - `capability_declared`.
2. Update `render_feature_capability_table()` to include the new axes.
3. Update tests so existing implemented features default to `no` for the new
   axes unless explicitly proven.
4. Mark binding constraints as `event_producing=True` only after Phase 1
   stabilizes the event schema.
5. Add a policy test that any `command_exposed=True`,
   `agent_previewable=True`, or `undo_replay=True` feature must also declare
   `event_producing=True`.

Likely files:

- `prototype/syntax/features.py`
- `prototype/tests/unit/syntax/test_feature_capabilities.py`
- `docs/orientation/artifacts_and_usage.md`
- `web/manifest_metadata.json` and manifest generation paths only if the table
  already feeds web metadata.

Checks:

```bash
pytest prototype/tests/unit/syntax/test_feature_capabilities.py
pytest prototype/tests/contracts/test_web_manifest_metadata_contract.py
python3 scripts/make_web.py --check
git diff --check
```

Exit gate:

- Feature tables can honestly answer whether a feature emits events, has a
  command surface, renders accessibly, can be previewed by agents, has
  undo/replay, and declares capabilities.

Recommended commits:

```text
Track human-facing feature capability axes
Conservatively mark event-producing feature coverage
```

## Phase 3: Define Failure Taxonomy Before More Operators

Purpose: stop failure vocabulary from fragmenting across constraints, decode,
patterns, blocks, queries, and host exceptions.

Implementation slices:

1. Add a small `FailureKind` vocabulary:
   - `absence`;
   - `pattern`;
   - `constraint`;
   - `decode`;
   - `result`;
   - `capability`;
   - `exception`;
   - `internal`.
2. Keep the first implementation as constants or a simple enum in the runtime
   diagnostics module; do not add a type-system feature yet.
3. Add `failure_kind` validation in `Diagnostic` and `RuntimeEvent` helpers.
4. Update binding constraint diagnostics to use `constraint`.
5. Add docs explaining how `none`, pattern failure, constraint failure, decode
   failure, expected `Result`, and unexpected exceptions differ.

Likely files:

- `prototype/runtime/diagnostics.py`
- `prototype/tests/unit/runtime/test_execution_result_contract.py`
- `docs/convenience/absence_and_result.md`
- `docs/language/language_foundation.md`

Checks:

```bash
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
git diff --check
```

Exit gate:

- Runtime diagnostics and events share one failure-kind vocabulary.
- New feature packets have a fixed list to choose from instead of inventing
  feature-specific failure names.

Recommended commit:

```text
Introduce shared runtime failure kinds
```

## Phase 4: Build Explanation Rendering Contracts

Purpose: make `explain` a product spine by giving events multiple renderings
before adding many event producers.

Implementation slices:

1. Add rendering helpers for event records:
   - machine JSON record;
   - compact CLI text;
   - accessibility/plain-text summary.
2. Add an inspection command or runtime helper that can expose diagnostics and
   events from `execute()`.
3. Add one CLI-level smoke test for a binding-constraint failure that asserts:
   - normal runtime failure;
   - structured diagnostic;
   - structured event;
   - text rendering mentions feature, operation, and next step.
4. Keep richer web/notebook rendering out of scope until projection contracts
   exist.

Likely files:

- `prototype/runtime/diagnostics.py`
- `prototype/runtime/api.py`
- `scripts/cli.py`
- `prototype/tests/unit/runtime/test_execution_result_contract.py`
- `prototype/tests/e2e/`

Checks:

```bash
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
pytest prototype/tests/e2e
git diff --check
```

Exit gate:

- A feature event can be rendered as JSON, CLI text, and accessibility-oriented
  plain text from the same record.

Recommended commits:

```text
Add runtime event rendering helpers
Expose runtime events through CLI inspection
```

## Phase 5: Write The Data Boundary And Decode Feature Packet

Purpose: prevent JSON, YAML, TOML, forms, CLI args, env, schemas, API
responses, and UI controls from becoming separate mini-languages.

Design slices:

1. Create a feature packet under `docs/features/` for data boundary and decode.
2. Specify:
   - raw representation with source path;
   - decode into owned Nomi data;
   - constraints/defaults/redaction;
   - provenance;
   - unknown-field policy;
   - accumulated errors;
   - partial success policy;
   - event production.
3. Add target examples for:
   - JSON decode;
   - environment and CLI args;
   - config layering;
   - form/control input mapping.
4. Explicitly refuse a separate forms DSL and a separate config language.

Implementation slices:

1. Add passive data-boundary event producers first, even before full decode
   syntax exists.
2. Add a minimal library-first decode helper over Python dictionaries or JSON:
   - no new grammar;
   - explicit input value;
   - accumulated decode errors;
   - `RuntimeEvent` output.
3. Add tests for success, unknown field, constraint failure, redaction, and
   accumulated errors.

Likely files:

- `docs/features/data_boundary_decode_feature.md`
- `docs/convenience/data_and_types.md`
- `docs/language/target_program_fixtures.md`
- `prototype/runtime/diagnostics.py`
- a small runtime/library module under `prototype/` once implementation begins;
- `prototype/tests/features/data/`

Checks:

```bash
pytest prototype/tests/features/data
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
git diff --check
```

Exit gate:

- Decode has a feature packet, examples, failure kinds, event schema, and
  library-first implementation path before any decode syntax is promoted.

Recommended commits:

```text
Specify data boundary and decode feature packet
Add library-first decode events
Test decode failure provenance and redaction
```

## Phase 6: Define Command Values And Registry

Purpose: unify CLI commands, command palettes, UI buttons, notebook actions,
shortcuts, and agent tool calls under one inspectable artifact.

Design slices:

1. Create a command-values feature packet.
2. Define the `Command` record:
   - `name`;
   - `intent`;
   - `inputs`;
   - `normal_form`;
   - `required_capabilities`;
   - `preview`;
   - `execute`;
   - `undo_or_recover`;
   - `event_schema`;
   - `accessibility_summary`.
3. Specify the alias rule:
   - shortcut, menu item, button, command-palette entry, CLI command, and
     agent action are renderings of one command value.
4. Specify what does not count:
   - hidden handlers;
   - gesture-only actions;
   - agent-only plans;
   - UI state changes with no event.

Implementation slices:

1. Add passive `Command` dataclass and registry under runtime/tooling.
2. Register existing safe introspection commands first:
   - inspect capabilities;
   - render feature table;
   - maybe run source with events.
3. Add preview-only behavior before mutation.
4. Emit command execution events.
5. Add tests for registry uniqueness, capability declarations, preview shape,
   and event output.

Likely files:

- `docs/features/command_values_feature.md`
- `prototype/runtime/commands.py`
- `prototype/runtime/diagnostics.py`
- `prototype/tests/unit/runtime/test_commands.py`
- `prototype/tests/unit/runtime/test_execution_result_contract.py`
- `scripts/cli.py`

Checks:

```bash
pytest prototype/tests/unit/runtime/test_commands.py
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
git diff --check
```

Exit gate:

- The repo has one command artifact that can back CLI actions, future command
  palettes, notebooks, and agent previews.

Recommended commits:

```text
Specify command values as shared UI artifact
Add passive runtime command registry
Emit command execution events
```

## Phase 7: Add Projection Contract Tests

Purpose: make "UI is projection" testable before building richer UI.

Implementation slices:

1. Define projection contract fixtures:
   - canonical event/data record;
   - CLI text rendering;
   - JSON/event rendering;
   - accessibility/plain-text rendering.
2. Add tests for binding constraint events and command execution events.
3. Add a web/notebook placeholder contract that stays conservative:
   - feature may declare `web=False` or `notebook=False`;
   - if either becomes true, it must prove event and accessibility rendering.
4. Extend manifest metadata checks so web does not imply unsupported event,
   command, or accessibility coverage.

Likely files:

- `prototype/tests/contracts/`
- `prototype/tests/unit/runtime/`
- `prototype/tests/contracts/test_web_manifest_metadata_contract.py`
- `web/manifest_metadata.json`
- `docs/orientation/artifacts_and_usage.md`

Checks:

```bash
pytest prototype/tests/contracts
pytest prototype/tests/unit/runtime
python3 scripts/make_web.py --check
git diff --check
```

Exit gate:

- No feature can claim a UI projection without a canonical event/data record
  and at least one non-visual rendering.

Recommended commit:

```text
Add event projection contract tests
```

## Phase 8: Treat Agent Interaction As Unsafe UI

Purpose: keep AI integrations from becoming private semantics.

Current basis:

- [AI Collaboration](../orientation/ai_collaboration.md) defines the
  collaboration doctrine.
- The repo-local `nomi-ai-native` skill defines how to choose between docs,
  skills, hooks, MCP/RAG, subagents, commands, and tests.

Implementation slices:

1. Update AI collaboration docs to require this flow for agent-mediated
   changes that affect Nomi behavior:

   ```text
   prompt -> plan -> command values -> preview/diff -> capability confirmation
          -> execution -> events -> summary
   ```

2. Add a reusable agent handoff/checkpoint template that asks for:
   - command/value or patch preview;
   - affected feature manifest;
   - capability/failure/event impact;
   - tests run;
   - replay notes.
3. Add smoke tests only for deterministic assets:
   - hook scripts;
   - templates if represented as files;
   - docs lifecycle checks for required headings.
4. Avoid claiming that natural-language prompts are executable source.

Likely files:

- `docs/orientation/ai_collaboration.md`
- `.agents/skills/nomi-ai-native/SKILL.md`
- possibly `.codex/commands/` or `.agents/commands/` if reusable commands are
  already the chosen repo pattern;
- `prototype/tests/unit/tools/test_agent_hooks.py`
- `prototype/tests/unit/tools/test_docs_lifecycle.py`

Checks:

```bash
pytest prototype/tests/unit/tools/test_agent_hooks.py
pytest prototype/tests/unit/tools/test_docs_lifecycle.py
git diff --check
```

Exit gate:

- Agent-facing workflows cannot present a natural-language plan as the only
  durable representation of a semantic change.

Recommended commits:

```text
Document agent preview and replay contract
Add agent handoff template checks
```

## Phase 9: Shrink First-Hour Nomi

Purpose: keep the teaching path from collapsing under Nomi's research breadth.

Implementation slices:

1. Create a first-hour guide that teaches only:
   - values;
   - names;
   - calls;
   - `func`;
   - simple arrows where needed;
   - binding constraints;
   - `print`;
   - one diagnostic/explain example.
2. Add a runnable first-hour sample under `samples/` only if the syntax is
   implemented today.
3. Keep delayed features explicit:
   - holes;
   - `$name`;
   - sections;
   - composition;
   - equations;
   - `where`;
   - match;
   - block calls;
   - data declarations;
   - decode;
   - result taxonomy;
   - UI controls;
   - agents.
4. Add regression snapshot coverage for the runnable sample.

Likely files:

- `docs/language/first_hour_nomi.md`
- `docs/README.md`
- `samples/first_hour.nomi`
- `prototype/tests/regression/test_interpreter.py`

Checks:

```bash
pytest prototype/tests/regression/test_interpreter.py
git diff --check
```

Exit gate:

- A newcomer can run one small file and learn the core without seeing the
  second-hour convenience layer.

Recommended commits:

```text
Add first-hour Nomi guide
Add first-hour runnable sample
```

## Phase 10: Standard Library And Capability Baseline

Purpose: prevent syntax from compensating for missing everyday libraries.

Design slices:

1. Write a standard-library capability baseline for:
   - paths/files;
   - text;
   - JSON/CSV/TOML/YAML;
   - CLI args/env;
   - HTTP;
   - time;
   - subprocess;
   - config;
   - secrets;
   - tables;
   - tests;
   - command registry;
   - diagnostics/explain rendering.
2. Classify each item as:
   - implemented today;
   - Python-hosted helper;
   - planned library;
   - capability-gated;
   - rejected from core language.
3. Extend host capabilities only where the runtime can honestly test them.

Implementation slices:

1. Start with docs and host capability manifest alignment.
2. Add tiny, boring helpers only after capability names and event behavior are
   clear.
3. Add contract tests per host/backend before claiming web/notebook support.

Likely files:

- `docs/language/stdlib_capability_baseline.md`
- `prototype/runtime/host_capabilities.py`
- `prototype/runtime/host_capabilities.json`
- `prototype/tests/contracts/test_host_capabilities_contract.py`
- `docs/orientation/artifacts_and_usage.md`

Checks:

```bash
pytest prototype/tests/contracts/test_host_capabilities_contract.py
pytest prototype/tests/unit/runtime/test_inspect_capabilities.py
git diff --check
```

Exit gate:

- Everyday world-contact areas have names, capability posture, test posture,
  and honest host support before they become syntax pressure.

Recommended commits:

```text
Specify standard library capability baseline
Align host capability manifest with stdlib baseline
```

## Phase 11: Promote Feature Packets Only After The Spine Exists

Purpose: resume ordinary language feature work with stricter gates.

Promotion rule:

No new user-facing feature should move to `prototype-ready` or `implemented`
unless it has:

- owner;
- layer/status;
- normal form;
- long form;
- docs/spec section;
- tests;
- event behavior;
- failure kind;
- capability posture;
- CLI or JSON rendering;
- accessibility rendering answer;
- command/agent answer if user-action-facing;
- rejected alternatives.

Implementation slices:

1. Update `SyntaxFeature` entries as features gain event and projection
   coverage.
2. Add event producers feature by feature:
   - decode;
   - block policy;
   - pipeline;
   - command execution;
   - query plan later.
3. Promote only one feature packet at a time.

Checks:

```bash
pytest prototype/tests/unit/syntax/test_feature_capabilities.py
pytest prototype/tests/unit/runtime/test_execution_result_contract.py
pytest prototype/tests/features
git diff --check
```

Exit gate:

- Feature promotion becomes boring: update the manifest, add event producer,
  add tests, update docs, prove projections.

Recommended commit pattern:

```text
Emit <feature> semantic events
Mark <feature> event coverage
Add <feature> projection tests
```

## Suggested Multi-Pass Commit Schedule

Use small commits in this order:

1. `Require adversarial admission fields in design proposals`
2. `Add structured runtime event records`
3. `Migrate binding constraint events to event schema`
4. `Introduce shared runtime failure kinds`
5. `Track human-facing feature capability axes`
6. `Conservatively mark event-producing feature coverage`
7. `Add runtime event rendering helpers`
8. `Expose runtime events through CLI inspection`
9. `Specify data boundary and decode feature packet`
10. `Add library-first decode events`
11. `Test decode failure provenance and redaction`
12. `Specify command values as shared UI artifact`
13. `Add passive runtime command registry`
14. `Emit command execution events`
15. `Add event projection contract tests`
16. `Document agent preview and replay contract`
17. `Add agent handoff template checks`
18. `Add first-hour Nomi guide`
19. `Add first-hour runnable sample`
20. `Specify standard library capability baseline`
21. `Align host capability manifest with stdlib baseline`

Stop after any commit that reveals semantic disagreement. Update the feature
packet and tests before continuing.

## Risk Controls

Do not:

- add new grammar before events, failure kinds, and capability axes are ready;
- add UI controls before command values exist;
- add agent workflows that cannot replay from commands, diffs, and events;
- mark web/notebook/accessibility support true because a feature happens to
  run in that environment;
- split config, forms, schemas, API responses, and UI controls into separate
  semantic systems;
- treat `explain` as a pretty-printer instead of a record-driven contract.

Prefer:

- docs-first feature packets;
- passive records before behavior changes;
- conservative capability flags;
- focused tests before broad suite runs;
- library-first decode and command experiments;
- one feature promotion at a time.

## Definition Of Done For The Whole Enhancement Queue

The adversarial enhancement notes are implemented when:

1. Design proposals require HCI/admission-gate answers.
2. Runtime events have a stable schema and JSON/text/accessibility renderings.
3. Runtime diagnostics and events share one failure-kind vocabulary.
4. Feature manifests expose human-facing capability axes honestly.
5. Data boundary/decode has a feature packet and at least one library-first
   implementation with provenance, redaction, accumulated errors, and events.
6. Command values have a registry, preview shape, capability declaration, and
   execution events.
7. UI projection claims are tested through canonical event/data records.
8. Agent-mediated behavior is documented as previewable/replayable command
   proposals, not executable natural language.
9. First-hour Nomi has a small runnable guide and sample.
10. Standard-library/capability baseline names everyday world-contact surfaces
    without turning them into premature syntax.

At that point, Nomi can resume feature growth with a sharper admission system:

```text
source idea -> user need -> normal form -> event/failure/capability
            -> command/data projection -> tests -> syntax only if still needed
```
