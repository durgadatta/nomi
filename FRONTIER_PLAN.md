# Nomi frontier execution plan

> Active, user-requested implementation plan, started 2026-10-08 from
> `7db4ed5`. This consumes the direction in [ASTRA_HANDOFF.md](ASTRA_HANDOFF.md).
> It records execution order and evidence; canonical language decisions remain
> in `docs/design/`, and the [roadmap](docs/orientation/project_roadmap.md) owns
> project-wide delivery. This is not a second language specification.

## Big picture

Build a humane computational language that starts with useful ordinary code,
admits progressively stronger contracts, and can grow through domain libraries,
tools and independently replaceable engines. Optimize for coherent complete
workflows rather than feature count. Preserve an operational CLI and playground
while changing their foundations deliberately.

The current design mandates annotated public APIs and explicit mutation. The
latest user direction reopens those choices. Resolve annotation requirements
first: compare checked inference, dynamic exploration with checked boundaries,
and mandatory annotations against the same programs. Keep simple reassignment
versus `var`/`set` as a separate experiment; a checking switch must not change
capture, evaluation or mutation meaning.

Keep four dimensions independent: source semantics, selected checking policy,
runtime authority, and execution engine. A strict check must neither invent
proof nor grant permissions; choosing an engine must not change source meaning.
An unknown fact is useful diagnostic information, not `Any` inferred as proof.

## Delivery waves

| Wave | Outcome and owners | Completion evidence / next dependency |
| --- | --- | --- |
| 1. Establish the direction | Reconcile exploratory code, inferred interfaces and selected restrictions in syntax/semantics/industrial/decisions; reuse language-coherence and function-contracts packets (A01/A02/A05/A09, D0/D1). | Beginner, reusable and adversarial source examples; independent judgments; all unsupported inference explicitly identified. |
| 2. Make checking useful | A bounded source-analysis producer and versioned inspection result; composable restrictions; CLI preview that executes no user code. Reuse runtime facade and diagnostics (A18/A19). | Same source runs as before; adding a policy reports precise obligations; unknown calls/imports/captures cannot pass as pure or checked. |
| 3. Make execution trustworthy | Repair the reproduced generator operand/phase and failed-child completion boundary in the hosted compatibility lane (A08/A11). Audit backend refusal before effects (A02/A06). | New native/hosted value and event oracles across three modes; neighboring tests; unsupported shapes remain explicit. This does not accept target generators or D2 cleanup semantics. |
| 4. Demonstrate a whole workflow | Grow a small invoice/report computation from unannotated execution to inspectable checks, and demonstrate refusal of an unresolved dependency. Verify actual CLI, installed artifact and affected browser surfaces (A17/A20/A28). | Runnable source, documented commands/output and honest limits; generated assets fresh; no fictional APIs. |
| 5. Close composed contracts | Use map/fold, decode and resource programs to decide generic callbacks, capture/generalization and lifetime/completion (D1/D2). | Independent positive/negative type and trace judgments before a wider checker; retain existing packet status until the whole contract closes. |
| 6. Extend engines and domains | Admit versioned producer/consumer contracts, portable scalar boundaries, then measured specialization and owned domain layers (D3-D7, A25/A33). | Equivalence including failure/order/cleanup; cold/warm cost measurements; a new domain composes without global evaluator surgery. |

Waves are dependency-guided rather than a requirement to settle the entire
language before improving one supported slice. Each iteration can reject a
candidate or replace a mechanism when its pressure program demands it.

## First milestone

Deliver waves 1-4 as a bounded local frontier checkpoint: a reconciled target
direction, actual conservative source analysis with useful CLI output, a
complete small checking/execution workflow, and verified continuation repairs
where a coherent mechanism can support them. Document later obligations with
their exact experiment and trigger. Do not claim a complete compiler, general
type/effect inference, permission sandbox, native optimization, or target-wide
conformance from this milestone.

Before implementing each slice, append its granular plan here and commit it.
Each plan must identify pressure, owner, competing mechanisms, independent
expected judgments/traces, changed files, tests, and removal/rollback gate.
Then implement, independently review, repair, verify, commit, and record actual
results. Keep target decisions separate from compatibility fixes in Git.

## Investigation baseline

- Working tree was clean on `main`; HEAD is `7db4ed5`.
- Available tools: Python 3.14.0rc3, Node 25.9.0, Cargo 1.95.0.
- All five registered design packets validate; four remain `designing` and
  pattern matching remains `implementing`.
- No existing general typechecker or public-interface inference producer was
  found. Runtime host metadata is not proof that an arbitrary source operation
  is pure: overloaded operators, conversion and iteration can call user code.
- Independent probes reproduced lost binary operands and lost failed-child
  unwinding across all hosted modes. `close()` is currently a no-op; its full
  semantics require separate evidence rather than an incidental promise.
- The default web path and legacy Pyodide are distinct verification surfaces.
  Earlier test counts in the handoff are historical, not current receipts.

## Verification and checkpoint discipline

1. Prepare independent expected outcomes before implementing a producer.
2. Add new focused tests; preserve existing tests and snapshots for these
   slices. Run relevant focused and neighboring suites before full promotion.
3. Validate registered packets and documentation boundaries after design edits.
4. Regenerate the web manifest when its runtime inventory changes, explain the
   reason, and run `--check`. Rebuild WASM only when its inputs change.
5. Run the full Python suite, web/runtime checks, actual affected browser
   workflows, and installed CLI evidence before recording milestone completion.
6. Keep generated reports, caches and screenshots out of commits. Check the
   staged diff and whitespace before each coherent local commit.
7. Record failed checks and evidence limits; do not silently weaken an oracle.

## Deferred obligations and activation triggers

- General callback/type/effect/region inference: activate on the three D1
  composed programs after call shapes, generalization and capture laws settle.
- Mutation surface: compare reassignments, explicit change and notebook edits
  with closure/cell traces before changing syntax or binding meaning.
- Dynamic package boundaries: specify exported evidence, runtime adapters,
  separate checking and stale dependency invalidation before package strictness.
- Resource/task completion: use D2 body/release/panic/cancel and escape cases;
  Python exception compatibility does not choose the target cause algebra.
- Native/AOT/JIT performance: measure a supported workload and versioned engine
  contract first; do not equate Rust parsing with native Nomi compilation.
- Shell, tables, documents, styling and AI/ML: select one complete workflow and
  ordinary inert descriptions before adding an executor or scoped syntax.
- Publishing, licensing and release policy remain owner decisions; local
  implementation and Git commits do not require a public release.

## Checkpoints

- Plan 1: big-picture plan prepared before implementation. Next: commit this
  plan, refine the checking and continuation slices with independent review,
  and commit those detailed plans before editing their implementation.
