# Implementation Guideline

> Status: current implementation orientation.
>
> Scope: how to change the experimental runtimes while moving toward the
> canonical target under [`docs/design`](../design/README.md).

## Authority Boundary

The Python/Lark/Python-AST and Rust/WASM/JavaScript paths are laboratories.
They must remain testable and useful during migration, but neither defines the
language.

Use this order:

```text
target syntax and semantics
-> versioned Surface/Core contracts
-> conformance fixtures
-> parser and backend implementations
```

When current behavior conflicts with the target, record the mismatch and plan a
small migration. Do not preserve a design merely because regression snapshots
exist. Do preserve the web and CLI as honest runnable surfaces while changing
them.

Read before broad work:

- [Target Design](../design/README.md)
- [Syntax](../design/syntax.md)
- [Semantics](../design/semantics.md)
- [Industrial Model](../design/industrial.md)
- [Decision Ledger](../design/decisions.md)
- [Artifacts And Usage](artifacts_and_usage.md)
- [Exploratory Implementation Doctrine](exploratory_implementation_doctrine.md)

## Current Roads

Python-hosted path:

```text
source
-> layered Lark grammar and tree transforms
-> Nomi/Python AST lowering
-> optional SurfaceNode islands
-> desugar passes
-> layered interpreter
```

Browser path:

```text
source
-> Rust/WASM parser payload
-> JavaScript lowering
-> Core IR
-> JavaScript Core runtime
```

Core experiments can also project Python AST into Core IR and select direct or
JavaScript-backed evaluation. Inspect resolved paths with:

```bash
python3 -m tools.syntax.inspect --stage resolved-pipelines
python3 -m tools.syntax.inspect --stage parser-frontends
python3 -m tools.syntax.inspect --stage eval-backends
```

## Target Artifact Road

The target architecture is:

```text
source
-> lossless CST with spans
-> Surface AST
-> name/type/constraint/effect analysis
-> typed Surface
-> small backend-independent Core IR
-> interpreter, bytecode, native, or Wasm backend
```

Diagnostics and semantic events are sibling artifacts, not strings emitted by
one backend. Module interfaces and package/build graphs are versioned artifacts
too. See [Industrial Model](../design/industrial.md).

## Layer Discipline

Use four user-facing layers:

| Layer | Implementation rule |
| --- | --- |
| Core surface | Preserve source identity in Surface; lower to explicit semantic Core operations. |
| Standard convenience | Reduce mechanically before backend evaluation while retaining source maps. |
| Library/protocol | Implement as ordinary typed modules; do not add grammar for API brevity. |
| Scoped language tool | Fence parsing/expansion, type the boundary, preserve hygiene and source maps. |

Backends are not a fifth source-language layer. They consume common artifacts.

Current implemented conveniences that the target rejects may remain behind a
prototype compatibility profile during migration. Do not extend them or cite
their implementation as design precedent.

## Feature Contract

Every implemented target feature should declare:

```text
target status
surface owner
typed semantics
Core operation or reduction
formatter support
diagnostic codes
parser frontends
runtime backends
CLI/web/notebook evidence
tests and conformance fixtures
temporary compatibility behavior
```

`prototype/syntax/features.py` currently carries part of this contract. Change
it incrementally rather than growing another registry.

## Change Workflow

1. Confirm the behavior in target docs or add a bounded design experiment.
2. Write accepted and rejected source fixtures.
3. Add or update the Nomi-owned Surface representation and spans.
4. Define type, constraint, effect, and control behavior before backend logic.
5. Lower to Core or an explicitly temporary compatibility artifact.
6. Add focused tests at the owning layer.
7. Exercise every claimed parser/runtime route.
8. Update runnable samples only when support is complete.
9. Regenerate/check web artifacts and run the broader suite.

For intentional semantic changes, update tests to the target. For mechanical
migrations, behavior should remain stable and tests should not change meaning.

## High-Risk Work

Treat these as cross-pipeline changes:

- immutable binding, `var`, `set`, and closure capture;
- constraint timing and atomic commit;
- product/variant data and exhaustiveness;
- `Option`, `Result`, postfix propagation, and cause conversion;
- strict decode, accumulated errors, provenance, and redaction;
- `with`, `defer`, cleanup failure, and cancellation;
- effect checking and host capabilities;
- async tasks, child lifetime, and error groups;
- public module interfaces and package identity.

These normally need syntax, analysis, runtime, diagnostics, conformance, CLI,
web, and notebook consideration together.

## Working Rules

- Prefer facade-first changes over package moves.
- Keep old imports working during a mechanical migration, not indefinitely.
- Preserve source spans and stable diagnostic fields at every boundary.
- Keep parse, type, lower, run, diagnose, format, and frontend support as
  separate capability axes.
- Do not add evaluator behavior for a target convenience that can reduce.
- Do not lower through hidden functions when that changes `return`, `await`,
  cleanup, or source-level diagnostics.
- Keep host exceptions and objects behind explicit adapter boundaries.
- Update repo-local skills when a workflow or authority path changes.
- Leave target-only code outside `samples/`.

## Useful Commands

```bash
pytest
pytest --interpreter-modes reduced
NOMI_VERIFY_CORE=1 pytest
NOMI_USE_CORE_IR=1 pytest

python3 -m tools.syntax.inspect samples/demo.nomi --stage raw-tree
python3 -m tools.syntax.inspect samples/demo.nomi --stage surface-ast
python3 -m tools.syntax.inspect samples/demo.nomi --stage core
python3 -m tools.syntax.inspect samples/demo.nomi --stage core-verify

python3 scripts/make_web.py --check
scripts/build_wasm.sh --check
python3 scripts/check_web_runtime.py
python3 -m tools.jupyter.check_nomi_kernel
```

AI output is design or implementation material until reconciled with target
docs, code, conformance evidence, and the user's current intent.
