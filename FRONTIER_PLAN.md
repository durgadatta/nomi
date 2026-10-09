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

## Completed high-level delivery strategy

This section completes the high-level plan requested on resumption. It is a
dependency and acceptance map, not a promise that all milestones fit one turn.
The existing roadmap A01-A33 and design agenda D0-D7 retain detailed ownership.
This plan is complete enough to execute; later evidence may revise its sequence.

| Priority / milestone | Deliverable | Depends on | Completion gate |
| --- | --- | --- | --- |
| M0: trustworthy feedback | Reusable experiment/review/repair/check loop; command receipts; concise durable retrospectives | Existing agent and design-pass owners | A real failure is reproduced, repaired and rechecked; receipt failures survive; stale/dirty evidence is identifiable. |
| M1: exploratory checking | Bounded actual inference, honest unknowns, independent restrictions, CLI/API, one installed invoice workflow | Reconciled exploration/checked-contract direction | Independent policy matrix; no user-code execution while checking; no stale fact or annotation treated as proof; supported/unsupported source documented. |
| M2: reliable hosted execution | Operand/phase continuation and child completion delivered through lexical cleanup | Fixed native/hosted compatibility oracles | Once-only effects, sent values, handler/finally/with traces in all hosted modes; unsupported paths fenced; old and new tests agree. |
| M3: composed typed foundation | Function/generic/protocol/effect contracts, checked interface producer/consumer, resource/task completion and escape | M1 evidence plus D1/D2 candidate comparisons | Map/fold, decode and scoped-resource programs type consistently; failure/capture negatives reject for the right reason; interfaces do not execute dependencies. |
| M4: portable product slice | Versioned source/fact/Core/value/diagnostic boundaries, CLI and browser parity, inspectable repair | One closed M3 slice; D3 numeric/Text/Bytes decisions for its values | Two frontend/engine routes agree on independent values, order, failures and spans; malformed/unsupported versions refuse; actual installed and browser workflows pass. |
| M5: domain composition | One ordinary library workflow at a time: file/process/report, table/data, document/style, then AI/ML where justified | Shared identity, outcomes, authority, lifetime and domain-specific laws | A complete useful workflow, inert description before execution, bounded resources, explicit external effects and repair; no evaluator surgery for each domain. |
| M6: performance and deployment | Measured specialization/bytecode/native candidates, package closure and supported release profiles | Stable bounded artifacts, workload evidence, dependency/host contracts | Equivalent semantics and explainability; measured end-to-end benefit; declared host/version evidence, exact artifact identity and rollback. |

M1 and M2 can advance independently; M0 supports every milestone. M3 is not a
reason to postpone useful bounded M1/M2 repairs, and no milestone requires
implementing every domain. Optimize a measured workload only after its semantic
contract is stable enough to compare engines honestly.

### Architecture decisions and unresolved forks

- Keep user-facing orchestration in the public runtime facade. Frontends produce
  owned versioned artifacts; analyzers supply facts with scope/provenance;
  policies select obligations; engines consume admitted operations. Retain
  current backends as migration surfaces while validating replacements.
- Prefer registries/spec data for restrictions, operations and capability
  selection. Imperative code implements those contracts; avoid a universal
  framework before two real consumers expose a shared need.
- Inference lowers ceremony. Public generic inference, callbacks, dynamic
  package adapters and policy inheritance require their own counterexamples.
  A concrete scalar call is never promoted to a generic public proof.
- Binding syntax, representation choice (text or structured document primary),
  resource completion, task policy and numeric portability remain explicit
  forks with existing owners. Implement neither side merely because it is
  easier in Python, JavaScript or Rust.
- Shared identity, revisions, outcomes and capability boundaries connect domain
  layers. Scheduling, transactions, styling, solver laws, timing and learning
  semantics stay with their domain; a single graph does not unify those laws.

### The self-improving cycle used at every milestone

1. Select one user pressure and the smallest discriminating expected outcome.
2. Commit a granular plan before widening implementation scope.
3. Preserve a failing reproduction or explicit negative judgment, then implement.
4. Review against adversarial cases independently of the implementation's tests.
5. Correct substantive findings and retain a focused regression where useful.
6. Run the checks appropriate to changed owners, retaining actual receipts and
   source identity; broaden only for promotion or unresolved risk.
7. Commit a coherent result and update its existing owner with what changed,
   what remains, and the next exact fixture. Promote repeated reasoning to a
   prompt/skill, deterministic gaps to tests, and one-off facts to the receipt.
8. Reassess the next milestone using evidence. Delete a weak approach, narrow an
   unsupported boundary or change architecture when the pressure proves it.

A green test count cannot close an untested contract. A process change earns
its place by reducing repeated mistakes or making evidence more reliable.
Automatic tools record/check facts; they do not accept semantics, rewrite tests
to hide failures, grant authority or publish releases.

### Current execution state

High-level/granular plan commits: `581b549`, `903aa97`, `6f97222`.
Canonical exploration/checked-contract direction: `fcc0b2d`, validated by 127
documentation/packet/target-fixture checks. The initial lifecycle failure was
repaired by indexing the previously committed checkpoint.

M0/M1/M2 implementations are work in progress in the shared tree, not promoted
results. Initial analyzer, facade and continuation tests have passed, but
independent review, full integration, generated manifest updates, browser checks
and final receipts remain. Preserve these edits; do not reset to the earlier
documentation-only checkpoint. Next: finish adversarial review and concrete
CLI/installed checks, then commit M0, M1 and M2 in separately verified slices.

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
- Checkpoint 2026-10-08: plan commits are `581b549` and `903aa97`; see
  [the durable session note](docs/orientation/frontier_checkpoint_2026-10-08.md)
  for evidence, reproductions, clean-state confirmation, and the exact next
  implementation commands. S1/S2 implementation remains incomplete.

## Slice plans, committed before implementation

### S0 — execute and retain the feedback cycle

The resumed user request explicitly asks for a self-improving development loop.
Use the existing design-pass retrospective and checkpoint owners; avoid a
parallel backlog. Each cycle starts with a falsifiable expectation, implements
one owned change, seeks adversarial review, repairs the findings, runs relevant
checks and records the smallest durable improvement and next exact fixture.

Add a reusable feedback-cycle prompt and a small local check-receipt command
under `.codex/`/`tools/`. The command runs explicitly supplied argv without a
shell, records command/exit status/time/current Git identity plus dirty-state
information, and stores logs/JSON under ignored `reports/`. Failed commands and
interrupted runs must remain distinguishable from success. It does not choose
tests, accept designs, change policy, claim attestation or automatically commit.
Reuse receipt evidence in existing bridge/roadmap notes. Test real successful
and failing subprocesses, invalid input and receipt preservation; integrate
discovery through the existing agent docs/prompts rather than longer hooks.

Apply the cycle immediately to S1/S2: independent expected values/judgments,
implementation, separate review, targeted regression for each substantive
finding, verification and commit. A repeated reasoning failure becomes a
prompt/skill improvement; a deterministic failure becomes a test. No new rule
is required when a one-off note suffices. Completion is measured by corrected
behavior and honest evidence, not the volume of process artifacts.

### S1 — source facts and independent restrictions

Pressure: a user writes an unannotated invoice calculation, inspects what is
known, then demands known values or absence of observable effects without
rewriting it. An imported/dynamic call must remain an explained unknown.

Owner: language-coherence / D0-D1; target laws in semantics/industrial and
ledger; experimental producer under `prototype/analysis/`; public entry through
`prototype/runtime/api.py`. This is source analysis, not an evaluator/backend
mode or a whole-target checker. Transitional Python AST is a replaceable input
adapter. No grammar or binding-law change is needed.

Compare mandatory annotations (reject as universal entry requirement), static
inference over all programs (reject unsupported proof), and dynamic exploration
with conservative checked facts (selected bounded experiment). Accept the
direction that interfaces may be inferred when sound and independently
inspectable; leave generalization, dynamic package adapters and policy syntax
open. Exported inferred contracts must not depend on callers' private code.

Implement an actual AST analysis over a declared closed scalar/straight-line
slice: literals, bindings, supported primitive operators and ordinary direct
function calls where arguments/body can be analyzed safely. Keep annotations
as declared information until checked. Unsupported nodes, dynamic imports,
unknown calls, overloadable operations on unknown operands, recursion and
captures outside the supported scope generate source-linked obligations.
Never execute source, import its dependencies, or call host functions while
checking. Keep module execution effects distinct from uncalled function effects.

Use a versioned result with source digest, analyzer identity, fact provenance,
inferred bindings/call results, known effects and unresolved obligations.
Represent each independently selected restriction as data. Initially compare
`known-types` and `pure` for the analyzed module execution, separately and
together; neither claims complete public-interface or lifetime checking.
Unknown evidence must block the restriction it could invalidate. No selected
restrictions means an honest preview, not a claim of production readiness.

Independent expectations prepared before producer implementation:

- `price = 1200; quantity = 3; total = price * quantity`: Int facts; no effects;
  both restrictions satisfied without annotations.
- A directly called scalar invoice function: same result type; argument/body
  analysis must not run the function or generalize one call into a public proof.
- `print(total)`: ConsoleWrite known; purity fails, type restriction need not.
- An unused function containing output: latent effect is not module output.
- Unknown imported call or operator on an unknown operand: unresolved type and
  effect obligations; no permission gained; strict selection fails before work.
- Wrong annotation: a declaration is not proof; report a contradiction.
- Reassignment, shadowing, recursion, closures and unsupported control: either
  prove the supported semantics or report the precise unknown; never reuse a
  stale fact from an earlier binding.
- Same source under four policy combinations: identical facts, only obligation
  selection/admission changes. Malformed policies/unknown versions fail closed.

Tests: new analysis unit contracts and independent adversarial review; public
API/CLI subprocess fixtures in S3. Rollback: remove this optional checker and
CLI route without changing execution. Broader admission waits for a resolved
symbol/type/effect contract; do not grow ad hoc inference to make a demo pass.

### S2 — resumable operand and completion ownership

Pressure: `mark('left', 10) + (yield 'ready')` must retain the left value/effect
and combine with `send(5)` to produce 15. Nested `try`/`with` around a paused
failing call must unwind inner/outer exits in order, reach the handler, run
finally, and continue. `None` sent to a yield is a real value.

Owner: hosted Python compatibility in generator_state/expressions and existing
resumable statement owners; inherited Nomi/reduced behavior is verified without
claiming target generators or D2 cause composition. Compare a narrow binary
patch, a bounded child-result/completion mechanism, and a pre-effect fence for
unsupported expression shapes. Prefer shared explicit state over operator-only
replay logic. Record where support ends.

Independent oracle: fixed expected native Python values and event sequences,
then the same program in python/nomi/reduced. Include completed left effects,
nested operands, child exceptions, suppression/handler/finally, return and
repeated yields. Preserve existing documented skips; add new test files.
Close/throw may be included only when the same mechanism supports explicit
GeneratorExit/throw/replacement/cleanup fixtures; otherwise report the exact
remaining limitation.

Tests: new failing reproductions first, existing generator/context/exception
neighbors, all hosted modes, full suite and affected legacy Pyodide workflow.
Rollback: revert the coherent compatibility slice if order/cause/once-only
behavior regresses; do not weaken existing expectations or silently re-evaluate
already completed effects.

### S3 — useful CLI, packaging and integration

Pressure: inspect the invoice's inferred facts and selected obligations from an
installed CLI, repair an unresolved dependency, and execute the same source.
Add `--check` with repeatable `--require` restrictions and text/JSON rendering,
using the public API; reject restriction flags without checking. Preserve the
default runner and avoid implying an integrated sandbox or strict compiler.
Use new fixture/example paths without changing existing regression snapshots.
Document exact supported syntax and reproducible check/run commands in README
and implementation orientation. Add new subprocess and installed-wheel checks.

Independently review checker soundness, diagnostic provenance and continuation
unwinding. Then run focused checks, full suite, packet/doc validation,
manifest/WASM freshness, web/runtime and actual default/Pyodide browser checks.
Explain any generated manifest inventory changes and record `--check` result.
Commit implementations in separate slices and finish with a verified receipt,
remaining obligations and the next exact source fixture.
