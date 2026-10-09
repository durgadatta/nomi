# Frontier checkpoint: 2026-10-08

> Status: current planning-only handoff, refreshed 2026-10-09. This supersedes the earlier
> documentation-only checkpoint at 22c7bbd; that historical record remains in Git.
> It preserves context, not a claim that unfinished code is ready.

## Latest instruction and next step

The user first requested committed plans followed by sustained implementation,
then explicitly narrowed the current phase: **focus on plan and strategy, with
potential implementation hints, before further implementation**.

The 2026-10-09 user request explicitly authorizes committing all pending work,
then continuing detailed planning until the remaining choices require executable
experiments. Actual implementation belongs in a fresh session.

Implementation and delegated fixes stopped. Continue with
[FRONTIER_PLAN.md](../../FRONTIER_PLAN.md), starting at its P1 growth-journey
comparison after the strategy checkpoint. Do not automatically resume repairs,
add infrastructure, or promote partial code. Committing the experiments preserves
them; it does not accept the architecture or mark their milestones complete.

Read the latest user instruction and actual Git state first. The preservation
checkpoint includes the source changes, new tests and supporting documentation
listed below, so a clean checkout can reconstruct the experiments. Ignored
reports remain local. Reassess the eventual implementation from the selected
contract and recorded findings rather than taking committed code as acceptance.

## Committed context

Baseline was a clean main at 7db4ed5. Subsequent local commits before this
planning revision are:

| Commit | What it preserves |
| --- | --- |
| 581b549 | Initial frontier vision, delivery waves and verification discipline |
| 903aa97 | Detailed S1 checking, S2 continuation and S3 integration plans |
| 22c7bbd | Earlier pause checkpoint, before successful implementation edits |
| 6f97222 | S0 feedback-cycle plan |
| fcc0b2d | Canonical exploration plus inferred-or-declared checked-contract direction |
| 8d80f34 | Prior high-level priorities, dependencies and feedback gates |

The canonical direction has advanced beyond mandatory public annotations.
General inference, public generic contracts, dynamic adapters and policy syntax
remain unresolved. Explicit mutation remains the current target. Interpreter
modes are implementation/test choices, not user assurance tiers.

The frontier plan now uses F0-F6 outcome labels so they cannot be confused with
the roadmap's M1/M2 milestones. P0-P5 are planning checkpoints; S0-S3 identify
older experimental implementation slices. Existing A and D owners remain
authoritative.

## Preserved experimental inventory

All rows below are **experimental work included in the preservation checkpoint**,
including their related documentation and tests. They remain unfinished; this
session does not change their implementation or weaken the failing expectations.

| Slice | Files/areas | State and limitation |
| --- | --- | --- |
| S0 feedback evidence | tools/check_receipt.py; prototype/tests/unit/tools/test_check_receipt.py | Explicit argv runner, local logs/receipts and source fingerprint prototype; not attestation or accepted infrastructure |
| S0 discovery | .codex/prompts/feedback-cycle.md; .claude/commands/feedback-cycle.md; edits to .codex/prompts/checkpoint.md, review.md, .agents/README.md and docs/orientation/ai_collaboration.md | Draft workflow integration preserved with its tool |
| S1 source facts | prototype/analysis/__init__.py, model.py, source.py; prototype/tests/unit/analysis/ | Conservative scalar/direct-call experiment with known-types/pure restrictions; no complete public or generic inference |
| S1 facade | prototype/runtime/api.py, __init__.py; prototype/tests/unit/runtime/test_source_check_api.py | Draft non-executing check route and versioned record |
| S2 continuation | prototype/interpreter/python/continuation.py and generator_state.py; nomi/generator_state.py; reduced/interpreter.py | Host-generator-backed continuation candidate; confirmed protocol/fencing blockers below |
| S2 new regressions | prototype/tests/unit/interpreter/python/test_generator_completion_ownership.py and test_generator_protocol_review.py | Native/hosted expected traces; newest cases intentionally expose unresolved defects |
| S3 CLI/example | scripts/cli.py, scripts/check_invoice.nomi, pyproject.toml; prototype/tests/e2e/test_cli_source_check.py | Draft check flags, invoice and installed-wheel exercise |
| Product orientation | README.md and docs/orientation/implementation_layers.md | Descriptions of candidate behavior; read together with the limitations here |
| Generated inventory | web/manifest.json and web/manifest_metadata.json | Candidate inventory grew from 123 to 127 runtime files for three analyzer files and continuation.py; 11 samples unchanged; WASM unchanged |

No existing pre-session tests/skips/snapshots were edited for these slices.
The new test files were iterated during this task. Do not assume the candidate
mechanism is preferred merely because these files now exist.

## Findings that matter for the strategy

The initial continuation probes found lost left operands after suspension and
failed-child exceptions bypassing waiting cleanup/handlers. The candidate fixed
those reproductions and several send/close/collection cases, but independent
review exposed a deeper host-protocol boundary:

1. Intermediate host generator frames convert source StopIteration to
   RuntimeError before source handlers/context managers can catch or suppress it.
   Preserve source exception identity and active exception state; do not infer
   provenance from an exception message or cause alone.
2. Throwing a GeneratorExit subclass as a class bypasses the candidate's special
   handling and mishandles a source handler that yields.
3. The unsupported-suspension validator skips entire nested definitions. Defaults,
   decorators, class bases and lambda defaults evaluate in the enclosing scope;
   these can escape the fence after body effects have already occurred.

A source-exception carrier and scope-aware traversal are possible experiments,
not accepted fixes. Compare their complexity with explicit frames or a narrower
supported boundary before resuming. Hosted compatibility does not settle Nomi
target generators or D2 completion semantics.

The analysis experiment also exposed important boundaries: an unknown operation
can invalidate earlier facts; annotations can be executable in the hosted path;
one concrete call is not a public generic proof. Lark-lowered locations were
not trustworthy, so the candidate reports missing positions rather than inventing
them. Its CPython frontend reports converted Unicode coordinates. These facts
argue for explicit source/evidence ownership, not a particular permanent AST.

## Historical checks, not current promotion evidence

Python 3.14.0rc3, Node 25.9.0 and Cargo 1.95.0 were available.
The following commands finished before the final independent-review regressions.
Their ignored local receipts may not exist in another checkout.

| Command/surface | Observed result | Local receipt under reports/checks/ |
| --- | --- | --- |
| Analysis plus new facade tests | 67 passed | check-1vyqlcik |
| New CLI and installed-wheel checks | 7 passed | check-942nv03p |
| New receipt-tool tests | 15 passed | check-8fdhhezn |
| Full pytest, four workers | 3086 passed, 81 skipped, 4 warnings | check-ftb80m6n |
| Web/runtime checker | Passed; RAG index reported stale | check-n2bfxo6u |
| Browser checker with legacy Pyodide | Passed reported default and legacy scenarios; log also contains server BrokenPipeError | check-uzli6o60 |

The browser check covers its existing scenarios, not proof of every new invoice
or checker interaction. Generated manifest and WASM freshness checks had also
passed at that earlier state. These are historical observations, not validation
of the subsequently extended test suite.

The final reviewer added cases only to the new protocol-review test file and
reported **24 failed, 15 passed** for that focused file before stopping.
No fixes for those findings were applied. That result supersedes any impression
of readiness from the earlier green suite. Full-suite execution was not repeated
after those additions. The historical result is reproduced below; no
implementation repairs were made.

## Preservation checks: 2026-10-09

Checks used `python3 -m pytest -o addopts= -q --tb=short` on the exact files below.
These are current bounded observations, not a passing full-suite receipt:

| Surface | Result |
| --- | --- |
| `prototype/tests/unit/analysis/`, `unit/runtime/test_source_check_api.py`, `e2e/test_cli_source_check.py`, `unit/tools/test_check_receipt.py`, `unit/interpreter/python/test_generator_completion_ownership.py` (all under `prototype/tests/`) | 146 passed |
| `prototype/tests/unit/interpreter/python/test_generator_protocol_review.py` | 24 failed, 15 passed; the three blocker families above remain |
| `python3 -m tools.design_passes check` | 5 coherent packets |
| `python3 .codex/scripts/agent_doctor.py` | Checks passed; local RAG index stale warning |
| `python3 scripts/make_web.py --check` | Passed; 127 runtime files and 11 samples |
| `git diff --check` | Passed |

The generated web manifest changed only because it now lists three analysis
modules and `continuation.py`; sample inventory and WASM are unchanged. No
browser or full-suite rerun was performed for this preservation checkpoint.

## Planning retrospective

### Evidence That Changed The Design

Independent review showed that host continuation convenience can hide source
exception boundaries. Strategic review found a separate mistake: the existing
plan let scalar checking and compatibility work dominate the broader authoring
and representation goals. Neither runnable code nor passing counts should choose
the next language contract.

### Workflow Friction

The plan reused milestone names with different meanings in the main roadmap,
retained an outdated mandatory-annotation premise, and mixed future execution
instructions with the user's newer planning-only request.

### Durable Improvement

The revised plan names the active phase first, separates planning checkpoints
from eventual outcomes, schedules human/domain comparisons early and records
partial code as experimental. The handoff and roadmap route to that current
instruction. No additional automation or skill growth is needed for this fix.

### Next Pass

P1: compare exploratory, reusable and checked-boundary forms of the existing
invoice and import/report programs, including one error/repair and one useful
representation challenger. Move resulting decisions to their existing canonical
owners; retain unresolved questions. Remain in planning until the user changes
the current scope.

