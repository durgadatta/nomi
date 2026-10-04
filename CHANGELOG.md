# Changelog

## Unreleased: Experimental Preview

This checkout remains pre-alpha. Runnable prototype behavior is separate from
the target language; no stable syntax, type/effect checker or production
data/ML engine is promised.

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
