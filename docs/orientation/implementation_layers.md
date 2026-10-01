# Implementation Layers

> Status: current boundary map and incremental engineering plan.
>
> Scope: preserve runnable prototype behavior while making engines replaceable.
> This is not a new language specification or a promise of Rust speedups.

The first maintainer-facing layers should explain *what is requested*, which
capabilities are allowed, and which artifacts/results cross a boundary. Keep
that orchestration readable Python, with plain JavaScript where the host is
an editor or browser. Optimized engines may be complex internally, but must
not own hidden frontend policy or silently change semantics.

This operationalizes the [Exploratory Implementation Doctrine](exploratory_implementation_doctrine.md).
The existing [artifact map](artifacts_and_usage.md) owns pipeline details;
the [performance notes](performance_notes.md) own measurements. Do not duplicate
their feature/status inventories here.

## Existing Owners

| Layer | Owner | Boundary rule | User-facing consequence |
| --- | --- | --- | --- |
| Commands and editor interaction | `scripts/cli.py`, `tools/jupyter/`, `tools/vscode/nomi/src/`, `web/app.js` | Prefer the public runtime/worker API; do not select grammar implementations directly. | Running the same file should not depend on where an editor was launched. |
| Runtime policy and orchestration | `prototype/runtime/api.py`, `modes.py`, `pipeline.py`, `session.py` | Own defaults, sessions, inspection, capability selection, and result assembly. | A backend change must not silently reset sessions or remove diagnostics. |
| Language artifacts | `prototype/syntax/`, especially `core.py` and `core_json.py` | Passive artifacts and validation separate meaning from engine mechanics. Python AST remains a transitional artifact. | Inspect reductions and compare implementations without guessing from output alone. |
| Parser/evaluator adapters | `prototype/parser/nomi/frontend.py`, `prototype/runtime/backends/` | Existing specs/registries own support and promotion; adapters translate engine-specific responses. | Unsupported paths remain explicitly opt-in rather than surprising defaults. |
| Transport and resource mechanics | `prototype/runtime/backends/json_process.py`, extension `src/runner.js` and `src/run_commands.js` | Transport owns argv, process failures, lifecycle, and framing, not language rules. | Paths with spaces work; failed launches are distinguishable from language errors. |
| Replaceable engines | Lark/lowering, layered Python interpreters, Rust/WASM parser, JS Core runtime | Engines implement declared contracts; internal optimization must not leak into command code. | Playground and CLI stay useful while alternative engines are evaluated. |

These are ownership boundaries, not six new packages. Existing cross-layer
imports and registry initialization are not fully isolated yet. A directory
rename or a wrapper around every function would not establish isolation.

## Current Changes

- The CLI imports the public runtime only when execution is requested. The
  runtime owns the parser default; `--parser-frontend` remains an explicit
  override. Source execution works without installing the checkout, and help
  needs neither the parser nor its dependencies.
- Wheels include grammar, host data, JS/WASM assets, and the default demo, but
  not the Python test package. Default demo lookup is package-relative.
- The Node evaluator delegates one-shot JSON process mechanics to
  `run_json_process`; verification, Core serialization, argv selection, and
  result interpretation remain in its adapter. Existing backend defaults and
  capabilities are unchanged.
- Editor runner resolution returns `{executable, args, cwd}`. VS Code task
  integration owns trust, document saving, resource-scoped settings, and
  selection cleanup. Execution requires an opened, trusted workspace; navigation
  is still a separate regex-based prototype.
- Jupyter creates sessions through the facade, inspects AST/completeness through
  runtime inspection, and reads public session bindings. Silent requests keep
  state but suppress streams, command output, and displayed results.
- `tools.syntax.inspect` delegates supported artifacts/tables to runtime
  inspection. Raw/transformed trees and Surface debug output remain an explicit
  parser-specific branch. CLI `passes`/`expansions` retain the legacy full
  reduction inventory through reduced-mode inspection, not copied lowering code.
- The playground launcher owns server startup/readiness and reaping; browser
  opening cannot race ahead of its listener. This probes TCP listener availability,
  not worker/WASM readiness, which the browser check verifies separately.
- RAG resource listing/reads reuse source discovery selection and enforce
  resolved-path boundaries. Resource URIs are source-relative, including for
  declared book sources outside the repository. Stdio framing reports bad
  requests without terminating subsequent valid requests.
- CI now declares the full Python 3.14 suite and a separate minimum-Python
  installed-wheel/CLI job, alongside the existing smoke/runtime/browser jobs.
  Local validation is not evidence that those hosted jobs have run.

The process helper accepts an already serialized request and requires a JSON
object response. Request/stdout bytes are explicitly UTF-8; invalid request
encoding is rejected before launch. Invalid stdout encoding and non-JSON
`NaN`/`Infinity` tokens become labeled transport errors. Failure logs use
replacement decoding; successful logs cannot corrupt the protocol response.
This is a transport rule, not a Nomi floating-point policy. It follows the
[JSON interchange standard](https://www.rfc-editor.org/rfc/rfc8259), rather than
[Python's permissive numeric-token default](https://docs.python.org/3/library/json.html#infinite-and-nan-number-values).
Duplicate-key handling, numeric representation limits and payload schemas are
not settled by this change. The adapter owns version/schema validation.
There is one request and response per process; stdout is protocol data and
stderr is failure detail/logging. Successful stderr is not merged into the
language result. Timeout is optional and remains unset for the existing Node
backend. This is **not** a sandbox, a memory/output limit, a persistent worker,
or a guarantee of descendant-process termination.

The helper currently lives under the runtime backend package, whose parent
imports initialize runtime metadata. Do not import it into parser registration
and introduce a cycle. Extract a transport owner below both packages before
sharing it with Rust parser runners; keep their parse-error distinctions intact.

## Admitting An Optimized Engine

An opaque implementation is acceptable only behind an inspectable contract:

1. Name a measured bottleneck and a bounded artifact it consumes/produces.
   Benchmark the current implementation before selecting Rust, native code,
   caching, parallelism, or any other optimization.
2. Reuse the parser/backend registry and capability declarations. Keep the
   existing engine as the oracle/fallback and the candidate opt-in.
3. Specify payload version, source spans, diagnostics, value conversion,
   host permissions, session lifetime, and cancellation. Transport alone
   does not answer these questions.
4. Compare artifacts and behavior using existing parity/fixture ladders.
   Include failure, cleanup, malformed payloads, and unsupported features,
   not just a successful arithmetic program.
5. Verify installed packaging and CLI, then the actual playground worker if
   the engine is used there. A Python-side Node check is not a browser check.
6. Promote only after measured benefit and unchanged supported behavior.
   Document a removal/fallback gate; keep engine details out of commands.

There is no new Rust dependency or replacement engine in this pass. The shared
transport is an extraction point, not evidence that arbitrary native engines
can already execute Nomi or preserve its session semantics.

## Next Bounded Steps

The [Project Enhancement Roadmap](project_roadmap.md) now owns the shared
delivery sequence. Its A18 covers facade/session/transport boundaries, A23
editor host behavior, A04/A06 structured parser/Core payloads, A25 measured
optimization, and A28 distribution/CI/release metadata. Each retains the
acceptance gates described here; the roadmap adds dependencies on language,
diagnostic, conformance and product work rather than another engine framework.

Do not batch these into a rewrite. Discovery should produce a small fix or a
specific unresolved contract, followed by focused checks and a checkpoint.
Suspected test defects belong in the [separate test review](../review/2026-09-30-test-issues.md),
not in implementation changes that merely make the suite appear green.

## Verification Loop

```bash
python3 -m pytest -q -n 0
python3 tools/vscode/nomi/scripts/nomi-vscode.py test
python3 tools/vscode/nomi/scripts/nomi-vscode.py package
python3 scripts/make_web.py --check
scripts/build_wasm.sh --check
python3 scripts/check_web_runtime.py
python3 scripts/check_web_browser.py
python3 -m tools.design_passes check
```

Install `.[dev]` for the Python checks, Node.js for cross-backend/editor checks,
and `.[web-test]` plus Playwright Chromium for browser smoke. Desktop extension
tests require a graphical host. The new distribution test builds an actual
wheel from a clean temporary source copy without build isolation/network and
imports it outside the checkout; it needs setuptools in the test environment.
It isolates source paths, not dependencies: Lark is supplied by that environment.

Packaging declarations follow setuptools' official
[data-file guidance](https://setuptools.pypa.io/en/latest/userguide/datafiles.html).
