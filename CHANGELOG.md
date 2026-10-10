# Changelog

## Unreleased: Experimental Preview

This checkout remains pre-alpha. Runnable prototype behavior is separate from
the target language; no stable syntax, type/effect checker or production
data/ML engine is promised.

- Added a hierarchical user guide for first use, language basics, complete
  examples, tool workflows, troubleshooting, current support, and gradual growth.
- Made the local playground start with the calculation task on a first visit,
  preserve returning selections, group examples by learning path, label older
  experiments, and link the user guide from the sidebar.
- Added repeatable exact-output checks for the introductory guide on hosted
  Nomi/reduced and WASM/JS, package project/guide/issue links, CLI version/help
  discovery, and an issue form for installation, CLI, editor, notebook, and docs.
- Made installed RAG developer tools explain their explicit configuration
  requirement, reject malformed setup before indexing, and keep startup errors
  on stderr without traceback or MCP stdout pollution.
- Repaired prototype `strip` on Python Core and JavaScript: character sets,
  Unicode whitespace compatibility, and argument failures now agree with the
  hosted path. Escaped all C0 controls in Rust parser JSON and rebuilt WASM
  artifacts after text vectors exposed invalid transport. Target Unicode
  trimming and Python-style source escape parity remain separate work.
- Aligned the local Jupyter launcher and editor activation with the beginner
  calculation task. Added a clean calculation notebook, labeled older notebook
  tours as experiments, and added actual-kernel notebook checking without
  saving execution outputs into the lesson.
- Audited current local browser, CLI, package, notebook, and editor boundaries;
  routed current walkthroughs to the checkout after detecting an older published
  playground. The [readiness audit](docs/orientation/project_roadmap.md#user-facing-readiness-audit)
  records implementation/distribution findings for the next fixing pass.
- Completed the bounded JSON report's validation, two-field repair, encoding,
  and current-result browser download, as recorded in the
  [report receipt](docs/orientation/frontier_checkpoint_2026-10-08.md#report-compatibility-completion-receipt-2026-10-10).
- Added data-first ordered `fold` and seed-including `scan` library experiments
  across Nomi/reduced and Python/JavaScript Core runtimes, with explicit empty,
  failure, order and mutable-history contracts.
- Added runnable data and text notebooks; simplified the quick tour to explicit
  named functions without changing its output.
- Rejected silent JavaScript integer loss; repaired bounded integer division,
  remainder and bitwise behavior. Python retains wider integers.
- Added structured fallback diagnostics and selectable CLI program/JSON output.
- Repaired Rust multiline collection continuation and pipeline argument insertion,
  browser boolean lowering, text iteration/length and per-execution stdout.
- Made browser indexing and slicing code-point consistent, with explicit invalid
  access failures, clipped/reverse bounds and shallow type-preserving copies;
  expanded the text notebook with bounded windows.
- Preserved special JavaScript property names as ordinary binding/map/data keys;
  excluded inherited host methods from nominal field lookup.
- Propagated portable-runtime abnormal failures before later eager work; prevented
  failed bindings, continuing map/filter callbacks and ignored finalizer errors.
- Ran portable Python-compatible `for ... else` after normal exhaustion, not
  only empty input; `break` and abnormal completion still bypass it.
- Rejected unrepresentable portable call/parameter/mapping shapes before effects
  instead of silently erasing named arguments or parameter kinds.
- Repaired portable function fall-through and lexical call-time defaults;
  rejected invalid positional arity before defaults or body execution.
- Preserved Python-hosted cleanup across nested, repeated and recursive calls;
  kept legacy lambda defaults in their lexical call frame.
- Rejected invalid Python-hosted argument shapes before defaults, parameter
  checks or body execution; preserved positional-only keyword collisions in
  ordered `**kwargs` without letting missing formals resolve outer names.
- Rejected duplicate/non-text unpacked keywords, accepted mapping-protocol
  calls and preserved argument values across direct yield pauses, including
  resumed `None` and starred expansion.
- Repaired hosted context-hook binding, partial acquisition, assignment failure
  and synchronous LIFO unwind; reduced scopes now always enter and use guarded
  cleanup. Python suppression remains separate from target resource semantics.
- Kept re-yielding child frames ahead of waiting ancestors and propagated state
  through expression statements and while bodies; subsequent continuation
  repairs are recorded in the [current checkpoint](docs/orientation/frontier_checkpoint_2026-10-08.md).
- Displayed single-expression native session values exactly once and retained
  historical binding-name maps without deep-copying mutable values or handles.
- Preserved notebook source framing; added local UTF-8 open/download, source-linked
  diagnostics, stale-result labels, run-generation protection and keyboard controls.
- Distinguished unavailable inspection evidence from captured empty bindings or
  measured zero timings; stopped guessing pipeline stages for unknown results.
- Expanded release gates to real desktop/mobile browser scenarios, alongside
  backend, sample, wheel and generated-asset checks.
- Repaired the optional Pyodide bootstrap by registering required runtime data
  in the web manifest; added an isolated-manifest test and opt-in browser gate.
- Rejected malformed legacy runtime manifests and stopped initialization after
  missing required assets or failed bridge/manifest HTTP responses.
- Bounded editor/sample startup failures and exposed explicit recovery rather
  than leaving the loading screen pending indefinitely.
- Disabled automatic occurrence highlighting to avoid the pinned editor's
  uncaught cancellation on disposal; explicit Find and selection remain usable.
- Corrected active target examples and strengthened design-packet integrity
  checks without claiming a target parser or typechecker.
- Kept JSON CLI failures structured before execution; redacted launcher-owned
  Docker token logs and excluded common local credential/state files from the
  build context. The development image is not a hardened service.
- Replaced the fixed notebook credential with generated tokens; rejected blank
  credentials and incompatible container reuse; required JSON readiness evidence
  and redacted configured credentials in timeout log excerpts.

The [project roadmap](docs/orientation/project_roadmap.md) owns observed
verification and remaining gates. Root licensing, hosted deployment, supported
version evidence and target semantic admission must be resolved before a public
release claim. Nothing in this log implies those gates have passed.
