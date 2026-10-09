# Resource Lifetime Design Experiment

> Status: dated evidence; bounded experiment complete, packet still designing.

Keep this file as evidence, not as a second backlog. Packet:
`docs/research/resource_lifetime.md`, `docs/design/resource_lifetime.md`,
`docs/design/resource_lifetime_target.nomi`.

## Result

The first synthesis action was advanced through two completion candidates,
two escape policies, three source pressure programs, deterministic fixtures,
and a standalone experiment. Recommend typed completion through an ordinary
library Result carrier and static scoped use backed by runtime revocation.
No new syntax, production resource runtime, or lifetime checker was implemented.
The packet remains `designing`, not `design-accepted`.

Run `python3 -m tools.resource_scope_experiment --json` to inspect the 32
candidate traces and diagnostic records. The seven escape cases compare 14
policy predictions from supplied lifetime facts; these are not compiler proofs.
The 28 body/cleanup pair tests check preservation and channel separation.

## Current-To-Target Audit

| Surface | Observed mechanism | Required migration |
| --- | --- | --- |
| Python context manager mixin | Python enter/exit suppression; successful-exit exceptions can pass through exception cleanup again | Structured scope state, no suppression boolean, never double-release, continue after release failure. |
| Python function evaluator | Function-local defer stack; first failing deferred action can abort remaining actions | Lexical action stack; aggregate failures; do not redirect pending control. |
| Python async mixin | Calls enter/exit synchronously and manually advances awaitables | Actual cold task/executor protocol and cooperative release join. |
| Reduced with desugaring | Python Try with except/else, no finalbody; host return/control semantics govern cleanup | Target-neutral outcome-carrying scope reduction, not host-exception imitation. |
| Python Core evaluator | Function defer stack returns immediately on deferred control/error | Preserve original destination; attempt remaining actions; typed cause composition. |
| JS Core evaluator | Similar function-stack defer and immediate signal/error exits | Same target-neutral scope/lease contract and conformance fixtures. |
| Passive diagnostics | Existing Diagnostic/RuntimeEvent records | Reuse source maps and redaction; resource event owner/schema still needed. |

Evidence paths: `prototype/interpreter/python/context_managers.py`,
`prototype/interpreter/python/function.py`, `prototype/interpreter/python/others.py`,
`prototype/parser/nomi/desugar/with_.py`,
`prototype/runtime/backends/core_runtime.py`,
`prototype/runtime/js/core_runtime.js`, `prototype/runtime/diagnostics.py`.
These are code-read findings, not new failing interpreter tests. Preserve supported
surfaces while migrating; the lab does not patch their behavior.

## Ordered Continuation

1. Specify Resource/callback/error/region metadata and type all three programs;
   resolve heterogeneous nested errors without implicit conversion or Any.
2. Add successful-enter/binding-failure, nested lexical defer scopes, capture
   timing, concurrent in-flight use, and cleanup timeout to the contract fixtures.
3. Run event-controlled actual async cleanup: cancellation latches, cleanup
   joins, timeout reports incompletion, and no external operation uses a revoked lease.
4. Admit a narrow frontend-neutral scope/lease contract and one backend slice;
   differential CLI/browser tests must precede runnable sample promotion.
5. Add a supported read/error example to the playground only after conformance,
   with visible enter/read/release/observe and both causes on failure.

Validation uses the registered checks. Passing the symbolic tests does not
complete any production migration or settle usability.

Checkpoint checks: 63 focused experiment/docs/registry tests passed; the
standalone experiment passed all 32 traces and 14 escape comparisons; all three
design packets validated. Ruff and the agent doctor are also required before
committing this checkpoint. No target runtime or browser conformance was run.

## 2026-10-04 Hosted Compatibility Follow-Up

The September audit above remains dated evidence. The user-approved runtime
continuation repairs a bounded Python-hosted compatibility surface, not the
proposed Resource/Result/region contract. Interpreted hooks use ordinary callable
binding; captured type-level exit is registered after enter, before handle
assignment/checking. Successful acquisitions unwind once in LIFO order on later
acquisition/binding failure, normal completion, real BaseException and
return/break/continue. Cleanup replacement and Python suppression retain their
legacy meaning, including abandonment of a transfer when its replacement error
is suppressed. No-error hook results are ignored. Private control signals are
not active cleanup exceptions or user-visible context-chain entries.

Reduced hosted `with` always enters and uses captured hooks with guarded
`try/finally`; generated names and private intrinsic loads survive source
shadowing. Core rejects these intrinsics instead of inventing a portable scope
operation. Synchronous host `try` retains real exception context and validates
handlers; pending transfers run finalizers without an active private signal.
This adapter is removable when a versioned completion/scope contract owns it.

New native-oracle scope/exception tests, inspectable reduction tests and real
Pyodide scope/resumption programs cover this slice. Direct AST assignment-shape
tests do not imply source parser acceptance. Snapshots and WASM outputs are
unchanged; observed verification and commits belong to the
[continuation receipt](../orientation/project_roadmap.md#scoped-runtime-continuation-receipt).

Normal generator suspension retains scopes, but a failing paused child can
bypass waiting ancestor cleanup in the old engine; a precise reduced-mode skip
records this gap. Arbitrary expression resumption, generator close/throw, async
cleanup, retained causes, non-escape and cancellation/timeout joining remain
gates. The packet stays `designing`; no syntax or target conformance is promoted.

## Pass Retrospective

### Evidence That Changed The Design

Both candidate carriers preserve cause lists, so "no lost errors" alone cannot
choose one. The distinction is whether expected close failure is inspectable
through a declared Result or adds another public control channel. Returning
copied data differs from returning an alias, and repeated cancellation differs
from repeated release. These distinctions changed the recommendation and fixtures.

October 4: real hosted binding-failure and cleanup-transfer tests sharpen the
migration obligations without changing the target recommendation. Host exception
suppression and context chains are compatibility evidence, not typed causes.

### Workflow Friction

The current implementations use several host-control models, none a complete
target scope contract. A symbolic lease check can be mistaken for a lifetime
checker, so its inputs and evidence limits are named explicitly. The accepted
function-value/generic surface is not yet sufficient to type the proposed APIs.

October 4: reduced AST helper hygiene, host active-exception state and child-frame
ordering required separate tests. A direct AST fixture is not evidence of source
grammar acceptance, and a passing normal resume is not abnormal unwind evidence.

### Durable Improvement

A registered resource packet and declarative fixtures now preserve exact traces,
channel distinctions, and cause order. The experiment reuses passive diagnostic
records and has focused tests; it is explicitly removable when conformance owns
the fixtures. No additional agent instructions or production abstractions were
justified by this single pass.

October 4: the new scope, exception and reduction suites join the maintained
web/runtime gate; two actual Pyodide programs cover scopes and nested resumption.
A precise known-gap skip prevents normal suspension coverage from hiding failed
child unwind. No additional agent instructions are justified by this repair.

### Next Pass

October 4: the [live runtime plan](../orientation/project_roadmap.md#iterative-runtime-continuation-plan)
owns operand/phase/completion reproductions and the next continuation boundary.
The resource packet's target typing/region gate below is unchanged.

For the resource thread, begin with callback/generic/region metadata and the
binding-failure fixture, not more source-language surveys. The user also requested
a separate maximal cognitive/interface exploration after this checkpoint: connect
human acts, historical principles, and modern interfaces to explicit Nomi forms
and bounded interface experiments without admitting borrowed notation prematurely.

## Research Gap Continuation, 2026-10-04

The later research-only audit deepens
[foreign callbacks and re-entry](../research/features/resources.md#foreign-callbacks-and-re-entry)
inside the existing lifetime question. It does not expand the preceding hosted
compatibility repair or claim that the symbolic lease experiment models foreign
threads, callback quiescence, a target ABI or supported cross-language unwinding.

**Evidence That Changed The Design:** selected Rustonomicon mechanisms distinguish
synchronous re-entry, asynchronous foreign callback lifetime and unwind
compatibility. Admission closure, draining in-flight callbacks and releasing
captured state are different obligations. The dossier compares restricted entry,
explicit re-entry contexts and queued handoff without choosing a Nomi contract.

**Workflow Friction:** a callback whose registration remains live can outlive a
nominally closed resource scope. Rejecting new callbacks is not enough when a
foreign caller can reach freed gate memory; deterministic schedule proposals
must name the still-live entry boundary and final quiescence evidence. Hosted
`with` tests do not settle those obligations.

**Durable Improvement:** question 5, feature navigation and the existing resource
registry now route to the detailed edge matrix, long form, inspection facts,
three program levels and unperformed experiment. This preserves the original
completion/lease recommendation and all existing test evidence. No unsafe
adapter, callback runtime, source syntax or new maintained probe was added.

**Next Pass:** compare event-controlled callback admission, synchronous re-entry,
foreign-thread attachment, late/in-flight callbacks, deregistration and abnormal
completion under two explicit contracts. Establish authority and thread/region
ownership before invoking user code, and prove quiescence before freeing state.
Only then consider one pinned host adapter; even that cannot justify a portable
cross-language unwind guarantee without a declared ABI profile.

## Frontier Planning Continuation, 2026-10-09

### Evidence That Changed The Design

The committed hosted continuation candidate still fails source exception and
pre-effect suspension-boundary cases. That evidence concerns compatibility,
not target resource completion. The target plan must separately close binding
failure after acquisition, in-flight use, repeated cancellation, heterogeneous
causes and the observation of incomplete cleanup.

### Workflow Friction

"Exactly once" can conceal an unsupported host guarantee, and body-only error
mapping can conceal a different cleanup error type. Defer timing also remained
an unspecified implementation choice despite changing which resource closes.

### Durable Improvement

The [remaining completion experiments](../design/resource_lifetime.md#remaining-completion-experiments)
now give event schedules, expected observations, heterogeneous adapter/compound
alternatives and a registration-versus-exit capture discriminator. Target
comments and registry routes preserve their unperformed status. No new traces,
runtime semantics or cleanup precedence were accepted.

### Next Pass

Jointly with D1, prepare typed phase/callback/region facts for these schedules,
then run an event-controlled implementation comparison. Keep the existing
foreign-callback/quiescence work with its explicit ABI owner. This planning
self-review does not validate actual async cleanup, escape checking or source
`defer` timing.
