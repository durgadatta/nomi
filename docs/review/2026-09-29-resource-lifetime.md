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

## Pass Retrospective

### Evidence That Changed The Design

Both candidate carriers preserve cause lists, so "no lost errors" alone cannot
choose one. The distinction is whether expected close failure is inspectable
through a declared Result or adds another public control channel. Returning
copied data differs from returning an alias, and repeated cancellation differs
from repeated release. These distinctions changed the recommendation and fixtures.

### Workflow Friction

The current implementations use several host-control models, none a complete
target scope contract. A symbolic lease check can be mistaken for a lifetime
checker, so its inputs and evidence limits are named explicitly. The accepted
function-value/generic surface is not yet sufficient to type the proposed APIs.

### Durable Improvement

A registered resource packet and declarative fixtures now preserve exact traces,
channel distinctions, and cause order. The experiment reuses passive diagnostic
records and has focused tests; it is explicitly removable when conformance owns
the fixtures. No additional agent instructions or production abstractions were
justified by this single pass.

### Next Pass

For the resource thread, begin with callback/generic/region metadata and the
binding-failure fixture, not more source-language surveys. The user also requested
a separate maximal cognitive/interface exploration after this checkpoint: connect
human acts, historical principles, and modern interfaces to explicit Nomi forms
and bounded interface experiments without admitting borrowed notation prematurely.
