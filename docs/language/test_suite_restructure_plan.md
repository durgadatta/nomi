# Test Suite Restructure Plan

> Status: active migration plan; initial setup, smoke promotion, and the
> largest function-style split are complete. Contract and regression
> rationalization are still pending.
>
> Scope: organize the growing test suite in small, reviewable phases. This plan
> names target structure, run tiers, ownership rules, migration phases, and
> quality gates. Track completed setup work here as the tree changes.

## Purpose

Nomi's tests have grown for the right reason: the language now has parser
experiments, runtime modes, desugar invariants, public runtime APIs, notebooks,
web bridge behavior, samples, and regression snapshots.

The problem is no longer lack of coverage. The problem is that a contributor
cannot always tell which test to add, which subset to run, or whether a failing
test means:

```text
parse shape changed
lowering changed
runtime semantics changed
reduced-interpreter invariant changed
public runtime API changed
frontend behavior changed
sample output changed
```

The restructure goal is:

```text
many tests -> clear responsibility -> fast local loop -> explicit full gates
```

## Progress Summary

Completed:

- Phase 0/1: rules, marker declarations, and `prototype/tests/README.md`.
- Phase 6: `smoke/` is now a real `pytest -m smoke` tier.
- Phase 2, first target: `functional/test_nomi_func_styles.py` has been fully
  drained into feature packets and removed.

Still pending:

- Split or bless the remaining `functional/` files.
- Move cheap public API and adapter checks from `e2e/` into `contracts/`.
- Make regression snapshot scope more explicit.
- Decide whether `functional/` remains as a compatibility bucket.

## Current Snapshot

Current tracked test files by top-level bucket:

| Bucket | Test files | Current role |
| --- | ---: | --- |
| `unit/` | 30 | Parser, desugar, interpreter, runtime, tool internals. |
| `features/` | 9 | Feature-owned language runtime packets introduced during migration. |
| `functional/` | 10 | Compatibility bucket for behavior tests not yet moved or blessed. |
| `regression/` | 3 | Snapshot regression for interpreter/sample files and Python AST. |
| `e2e/` | 7 | CLI, web bridge, notebook, report scripts, scenario tests. |
| `smoke/` | 4 | Tiny checkout-alive checks collected by default and selectable with `pytest -m smoke`. |

Resolved pressure points:

- `functional/test_nomi_func_styles.py` was the largest kitchen-sink file. It
  has been split into feature packets for holes, equations, where clauses,
  composition, implicit multiplication, type aliases, try-expr, spread, and
  defer.

Remaining pressure points:

- `regression/test_interpreter.py` multiplies samples by interpreter mode and
  also pulls every user-facing file from `samples/`.
- Unit tests are mostly layer-owned, while functional tests are mostly
  feature-owned; this makes the intended home for new language tests fuzzy.
- Frontend/e2e tests share the same top-level bucket even when some are cheap
  contract checks and others exercise notebook/web surfaces.
- There is no marker/run-tier vocabulary beyond path selection and
  `--interpreter-modes`.

## Non-Goals

- Do not delete coverage to make the suite look smaller.
- Do not move files until the target layout and command tiers are documented.
- Do not combine test movement with semantic changes.
- Do not regenerate snapshots as part of pure organization work.
- Do not make every test feature-driven; low-level unit tests should stay close
  to the module they protect.

## Design Principles

1. **One axis per test file.** A file should be primarily layer-owned, feature-
   owned, contract-owned, snapshot-owned, or frontend-owned.
2. **Feature packets span layers.** A non-trivial language feature should have a
   predictable packet: parse, lowering/core, diagnostics, runtime,
   reduced-invariant, docs/sample regression when user-facing.
3. **Snapshots are gates, not the main development loop.** Behavior tests should
   prove intent; snapshots should catch broad drift and teaching-sample output.
4. **Interpreter modes are explicit cost multipliers.** New Nomi syntax should
   default to `nomi_mode`; use all `interpreter_mode` only for Python parity.
5. **Public API contracts should be small and stable.** Runtime facade,
   sessions, CLI, web, and notebook should have narrow contract tests before
   broad e2e tests.
6. **Fast failure first.** Parse/lowering tests should fail before a full
   sample regression run discovers the same problem.
7. **No hidden suite.** If `smoke/` exists, it should either become a documented
   run tier or be migrated into ordinary markers.

## Target Test Taxonomy

The future suite should be understandable by question:

| Question | Home | Typical command |
| --- | --- | --- |
| Did one internal module behave correctly? | `unit/` | `pytest prototype/tests/unit/...` |
| Did a language feature parse/lower/run as intended? | `features/<feature>/` or current `functional/` during migration | `pytest prototype/tests/features/<feature>` |
| Did a public runtime/tool contract change? | `contracts/` | `pytest prototype/tests/contracts` |
| Did sample or artifact output intentionally change? | `regression/` | `pytest prototype/tests/regression/...` |
| Did CLI/web/notebook integration work end-to-end? | `e2e/` | `pytest prototype/tests/e2e` |
| Is the checkout alive in under a minute? | `smoke/` marker or documented path | `pytest -m smoke` or equivalent |

## Target Layout

This is a target map, not an immediate move plan:

```text
prototype/tests/
  conftest.py
  support/
    ast.py
    snapshots.py
    runtime.py
    sources.py

  unit/
    parser/
    parser/desugar/
    interpreter/python/
    interpreter/nomi/
    runtime/
    tools/

  features/
    functions/
      test_parse.py
      test_lowering.py
      test_runtime.py
      test_diagnostics.py
    patterns/
    flow/
    binding_constraints/
    data/
    absence_result/
    block_calls/

  contracts/
    test_runtime_api.py
    test_runtime_session.py
    test_interpreter_modes.py
    test_parser_backend_contract.py

  regression/
    interpreter/
      test_sample_outputs.py
      snapshots/
    ast/
      test_python_ast_snapshots.py
      snapshots/
    diagnostics/
      test_diagnostic_snapshots.py

  e2e/
    cli/
    web/
    notebook/
    reports/

  smoke/
    test_cli_smoke.py
    test_parser_smoke.py
    test_runtime_smoke.py
```

During migration, `functional/` can remain as a compatibility bucket. New large
feature work should prefer `features/<feature>/` once that directory exists.

## Proposed Run Tiers

### Tier 0: Smoke

Purpose: "Is the checkout alive?"

Contents:

- import parser/runtime;
- parse a tiny Nomi program;
- execute a tiny Nomi program;
- CLI help or tiny file;
- no snapshots;
- no notebook/browser/server startup.

Target command:

```bash
pytest -m smoke
```

Open design choice: either keep `prototype/tests/smoke/` and remove
`collect_ignore`, or migrate smoke tests into ordinary paths with a `smoke`
marker.

### Tier 1: Focused Edit Loop

Purpose: "Did my module or feature change work?"

Examples:

```bash
pytest prototype/tests/unit/parser/desugar
pytest prototype/tests/features/functions --interpreter-modes reduced
pytest prototype/tests/unit/runtime
```

Rules:

- no full sample snapshot runs;
- prefer `nomi_mode` for Nomi-only syntax;
- use reduced mode when testing desugar/core invariants.

### Tier 2: Feature Gate

Purpose: "Can this feature move forward?"

Feature packet:

- parse shape;
- lowering/core shape;
- runtime behavior in `nomi` and `reduced`;
- common diagnostics;
- reduced-interpreter invariant when relevant;
- docs reference or feature manifest status;
- sample regression only when user-facing.

Target command shape:

```bash
pytest prototype/tests/features/<feature>
```

### Tier 3: Contract Gate

Purpose: "Did public runtime/tooling contracts stay stable?"

Contents:

- `prototype.runtime.execute`;
- `prototype.runtime.inspect`;
- `RuntimeSession`;
- mode registry;
- parser/backend artifact contracts;
- syntax inspection tool;
- CLI/web/notebook adapter contracts that do not require broad e2e runs.

Target command:

```bash
pytest prototype/tests/contracts prototype/tests/unit/runtime
```

### Tier 4: Regression Gate

Purpose: "Did broad outputs change intentionally?"

Contents:

- interpreter sample snapshots;
- user-facing `samples/` snapshots;
- Python AST snapshots;
- future diagnostic snapshots.

Target commands:

```bash
pytest prototype/tests/regression/test_interpreter.py
pytest --force-regen prototype/tests/regression/test_interpreter.py
```

Rules:

- snapshot changes must be reviewed as output changes, not hidden in broad
  refactors;
- adding a file under `samples/` remains a deliberate regression-suite change;
- target-only syntax stays under `docs/language/`, not `samples/`.

### Tier 5: Frontend/E2E Gate

Purpose: "Do user-facing tools still work?"

Contents:

- CLI;
- web runtime bridge;
- notebook kernel/launcher;
- report script;
- scenario-level language interactions.

Target command:

```bash
pytest prototype/tests/e2e
```

## Migration Phases

### Phase 0: Document And Freeze The Rules

Docs-only work:

- add this plan;
- link it from docs and skills;
- document the meaning of each suite bucket;
- define first marker names before adding them.

Exit gate:

- contributors can decide where a new test belongs without reading old PRs.

### Phase 1: Add Metadata Without Moving Tests

Low-risk setup:

- add pytest marker declarations for `smoke`, `feature`, `contract`,
  `regression`, `frontend`, `slow`, `snapshot`;
- add a short `prototype/tests/README.md`;
- add helper docs for `interpreter_mode` vs `nomi_mode`;
- document command tiers.

Status:

- Done: marker declarations live in `pyproject.toml`.
- Done: `prototype/tests/README.md` documents current buckets, target buckets,
  interpreter fixtures, and run tiers.

Exit gate:

- existing tests still collect exactly as before unless a marker is explicitly
  selected.

### Phase 2: Split The Largest Functional Files

Start with `functional/test_nomi_func_styles.py`.

Suggested destination packets:

| Current cluster | Target feature packet |
| --- | --- |
| holes and `$` holes | `features/functions/test_holes_runtime.py` |
| equations, piecewise, guarded equations | `features/functions/test_equations_runtime.py` |
| `where` | `features/functions/test_where_runtime.py` or `features/scope/` if scope grows. |
| sections and composition | `features/functions/test_composition_runtime.py` |
| implicit multiplication | `features/math/test_implicit_mul_runtime.py` |
| type aliases | `features/data/test_type_alias_runtime.py` |
| try-expr and defer | `features/absence_result/` or `features/block_calls/` depending on ownership. |
| spread | `features/flow/test_spread_runtime.py` |

Rules:

- move one cluster per commit;
- preserve test names where possible;
- do not alter semantics during movement;
- run old path/new path diff through focused pytest after each move.

Status:

- Done: hole-lambda runtime tests moved from
  `functional/test_nomi_func_styles.py` to
  `features/functions/test_holes_runtime.py`.
- Done: `where` runtime tests moved from
  `functional/test_nomi_func_styles.py` to
  `features/functions/test_where_runtime.py`.
- Done: equation, piecewise, guarded-equation, default-argument, and
  return-annotation runtime tests moved from
  `functional/test_nomi_func_styles.py` to
  `features/functions/test_equations_runtime.py`.
- Done: operator-section and function-composition runtime tests moved from
  `functional/test_nomi_func_styles.py` to
  `features/functions/test_composition_runtime.py`.
- Done: implicit-multiplication runtime tests moved from
  `functional/test_nomi_func_styles.py` to
  `features/math/test_implicit_mul_runtime.py`.
- Done: type-alias runtime tests moved from
  `functional/test_nomi_func_styles.py` to
  `features/data/test_type_alias_runtime.py`.
- Done: try-expression runtime tests moved from
  `functional/test_nomi_func_styles.py` to
  `features/absence_result/test_try_expr_runtime.py`.
- Done: spread-literal runtime tests moved from
  `functional/test_nomi_func_styles.py` to
  `features/flow/test_spread_runtime.py`.
- Done: defer runtime tests moved from `functional/test_nomi_func_styles.py`
  to `features/block_calls/test_defer_runtime.py`.
- Done: `functional/test_nomi_func_styles.py` was removed after all semantic
  clusters were moved into feature packets.
- Done: data-declaration runtime tests moved from
  `functional/test_data_declarations.py` to
  `features/data/test_declarations_runtime.py`.

Exit gate:

- Complete for `functional/test_nomi_func_styles.py`: all listed clusters have
  feature-packet homes and focused old/new migration checks preserved behavior.

Next candidates:

- `functional/test_nomi_collection_convenience.py` -> `features/flow/`.
- `functional/test_nomi_pattern_convenience.py` and
  `functional/test_nomi_unless.py` -> `features/patterns/` or
  `features/flow/` depending on ownership.

### Phase 3: Introduce Feature Packets For New Work

For every new accepted feature, create the packet upfront:

```text
features/<feature>/
  test_parse.py
  test_lowering.py
  test_runtime.py
  test_diagnostics.py
  README.md or docs link
```

Only add files that the feature needs. Do not create empty placeholders.

Exit gate:

- feature coverage is visible in the directory tree and can later be generated
  into a capability matrix.

### Phase 4: Separate Contract Tests From E2E

Move cheap public API checks out of broad e2e files when they do not need a
real frontend surface.

Candidates:

- runtime-session ownership assertions;
- web bridge session/cache contract;
- notebook kernel runtime-session ownership;
- parser/interpreter contract checks.

Exit gate:

- `e2e/` means "whole surface works," while `contracts/` means "public seam
  stayed stable."

### Phase 5: Rationalize Regression Snapshots

Keep snapshots, but make their scope visible:

- interpreter behavior snapshots;
- sample teaching-output snapshots;
- Python AST snapshots;
- future diagnostics snapshots.

Potential improvements:

- move snapshot files under named `snapshots/` subdirectories;
- add a generated index of sample files included in snapshots;
- add a guard that target-only docs files are not accidentally pulled into
  regression;
- add a snapshot review checklist to PR docs.

Exit gate:

- snapshot churn is easier to review and no longer feels like "the tests are
  too many"; it is an explicit broad-output gate.

### Phase 6: Retire Or Formalize `smoke/`

The `smoke/` tests were originally ignored by collection. Choose one:

1. Promote them to `pytest -m smoke` and include marker declarations.
2. Keep them as manual scripts and document that clearly.
3. Migrate their useful assertions into unit/contract tests and remove the
   bucket later.

Preferred path: promote to marker-based smoke tests so there is a tiny
first-line command.

Status:

- Done: `smoke/` is promoted into normal pytest collection and each smoke file
  is marked with `pytest.mark.smoke`.
- Done: smoke checks are assertion-based and no longer write manual inspection
  artifacts.

## Feature Coverage Matrix

The test restructure should feed the future feature/capability matrix from
`syntax_substrate_todo_audit.md`.

Suggested columns:

| Feature | Parse | Lower/Core | Runtime | Reduced | Diagnostics | Regression | Web | Notebook | Docs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functions/equations | yes | yes | yes | yes | partial | samples | n/a | n/a | yes |
| binding constraints | yes | partial | yes | yes | partial | sample | n/a | n/a | yes |
| data declarations | yes | direct Python AST | yes | yes | partial | no | n/a | n/a | yes |
| block calls | yes | surface node | yes | partial | partial | sample | n/a | n/a | yes |

The first version can be a Markdown table. Do not automate it until the
directory structure stabilizes.

## Naming Rules

Use names that tell the semantic promise:

```text
test_<feature>_<condition>_<expected_behavior>
```

Examples:

- `test_where_binding_does_not_leak`
- `test_match_expr_guard_falls_through`
- `test_constraint_failure_reports_user_message`
- `test_runtime_session_reuses_cached_ast_for_repeated_source`

Avoid names that only describe implementation:

- `test_node_attr_exists`
- `test_transformer_returns_call`

Implementation-shape tests are allowed in `unit/parser`, but feature tests
should name the user-visible behavior.

## Duplication Policy

Some duplication is useful. Too much duplication makes the suite feel huge.

Keep:

- one parser/AST shape test for a syntax form;
- one runtime behavior test for the same form;
- one sample/regression example once user-facing;
- one reduced-invariant test when desugaring is the point.

Avoid:

- testing the same happy path in unit, functional, e2e, and snapshot unless
  each layer catches a different failure;
- using snapshots as the only proof of semantics;
- adding a new e2e scenario when a feature packet test would catch the bug.

## Command Reference Target

The eventual docs should expose:

```bash
# Tiny confidence check
pytest -m smoke

# Unit tests only
pytest prototype/tests/unit

# One language feature
pytest prototype/tests/features/functions

# Public runtime/tool contracts
pytest prototype/tests/contracts

# Sample/output snapshots
pytest prototype/tests/regression

# User-facing tooling
pytest prototype/tests/e2e

# Full suite
pytest
```

Until the restructure happens, keep using the current commands in `AGENTS.md`.

## Open Questions

1. Should `functional/` disappear eventually, or remain as "multi-module but
   not feature-owned"?
2. Answered: smoke tests are included in default `pytest` and selectable with
   `pytest -m smoke`.
3. Should sample snapshots run in every full local suite, or only in CI and
   explicit regression gates?
4. Answered for new/migrated feature packets: they live under
   `prototype/tests/features/`.
5. Should markers or path conventions be the primary user interface?
6. Should generated feature coverage matrices be checked in, generated in CI,
   or kept as docs-only for now?

## Recommended Next Migration

After the completed `test_nomi_func_styles.py` split:

1. Move `functional/test_data_declarations.py` into `features/data/` in one
   behavior-preserving commit.
2. Move cheap runtime/session/web/notebook ownership assertions from `e2e/`
   into `contracts/`.
3. Add a regression snapshot index or checklist before moving snapshot files.
