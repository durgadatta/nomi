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

## Experimental Source Analysis

Owner: `prototype/analysis/`; public facade: `prototype.runtime.check`; CLI:
`--check` with repeatable `--require known-types` / `--require pure`. This is
the first S1 producer for progressive assurance, not a whole-target checker or
a runtime/backend mode. The source analyzer uses passive Python AST; replacing
that input adapter does not change the obligation/report contract.

`AnalysisPolicy` validates restriction names and version 1. `AnalysisResult`
records a source SHA256, producer identity/version, module-execution scope,
facts, known effects, latent function summaries, unresolved obligations and each
selected restriction's blockers. `CheckResult.to_record()` wraps this as
`nomi.check` v1 with parse diagnostics. Unknown policy versions/names and
unsupported frontend selection fail instead of silently falling back. Reports
are descriptive local evidence, not transferable admission or execution tokens.

The supported primitive rules are owned in `prototype/analysis/source.py`:
scalar literals, simple assignments, selected arithmetic/comparisons, direct
known-scalar calls and scalar `print`. Calls are analyzed in their argument
context; the report explicitly leaves public/polymorphic contracts unproved.
Unused function bodies stay latent. Unknown operations invalidate environmental
knowledge, so a later call cannot reuse a proof that a dependency may have
changed. Work, input and call-depth limits produce obligations, not guessed
results. No user function, import or annotation is executed while analyzing.

Annotations are currently fenced, including scalar-looking ones: the hosted
Nomi prototype can interpret them as executable constraints. Wrong scalar
declarations additionally report a contradiction. Captures, containers,
branches, recursive/generator functions and richer argument conventions need
their own analysis contracts. Optional restrictions have identical inferred
facts and differ only in which obligations block admission. `known-types`
concerns analyzed execution, not complete latent callable signatures; `pure`
does not prove termination or freedom from panic. A preview with no selected
restrictions can succeed while listing unknowns.

The Nomi adapter uses the default Lark frontend. Its lowered AST currently loses
accurate source positions, so analysis spans are unavailable rather than guessed
from synthetic line-1 fields; filename, source digest and binding/call context
remain. Python checking uses CPython's syntax AST and converts UTF-8 offsets to
one-based Unicode code-point columns. That parser is independent of the hosted
Python execution parser. Other parser routes are not yet accepted for checking.
The checker is CLI/API only; the invoice itself uses existing runnable syntax.

Extraction/promotion gate: a shared resolved symbol/type/effect artifact and
independent frontend fixtures before admitting public generic contracts or
browser checking. Removing this optional analysis package and CLI route leaves
execution semantics unchanged. Strict build/run admission and dynamic package
adapters remain target work.

## Hosted Generator Continuations

Owner: `prototype/interpreter/python/continuation.py` and `generator_state.py`;
Nomi/reduced inherit this compatibility adapter. Host generator frames preserve
AST child values and errors, without compiling or executing source as Python.
Suspension-free subtrees still use the existing interpreter. Admitted suspended
paths are declared in the adapter handler table: yield/from, expression,
assignment, return, binary operator, call, if/for/while, try and with. Other
suspended shapes fail before generator-body effects. Scope traversal includes
definition-time defaults, decorators and class bases while excluding nested
function bodies. This is a bounded compatibility adapter; reduced desugaring
guards remain active and raw `With` cannot bypass its reduction.

The adapter owns `send`, `throw`, `close` and child completion. A private
`SourceException` carrier preserves actual `StopIteration`/`GeneratorExit`
objects through implementation frames. Source handlers and context protocols
receive the original active error; only an unhandled StopIteration crossing the
public generator boundary becomes RuntimeError. Native child RuntimeErrors
are never guessed back into source errors. Delegation lookup failure and ignored
close warnings have separate transport records. Nested context cleanup clears
a suppressed error before the outer protocol runs. Finalization restores the
source environment. Independent tests compare operand order, `None`,
child failures, handlers, cleanup replacement/suppression, active exceptions,
delegation, ignored close and attached Nomi blocks against native Python.

This does not accept target generators, arbitrary suspended AST shapes, async
cleanup or D2's typed all-cause completion contract. The old resumable evaluator
methods remain a migration surface, but `CoroutineState` no longer drives their
flattened paused-frame queue. A future Core continuation representation should
consume the same independent traces before replacing this hosted adapter.

## Planned Assurance And Representation Boundaries

Status: October 9 implementation handoff, **not implemented interfaces or
accepted JSON schemas**. The canonical questions are in the
[growth journeys](../design/synthesis.md#growth-journeys-and-boundary-evidence),
[function trial](../design/function_contracts.md#bounded-contract-comparison-for-implementation)
and [interaction trial](../design/interaction_model.md#paired-representation-and-revision-trial).
This map selects replaceable owners rather than a mandatory compiler framework.

| Boundary | Producer / consumer | Minimum proposed contents | Refusal and extraction rule |
| --- | --- | --- | --- |
| Source document | Parser adapter / source analysis and tools | Exact revision, edition, text, real coordinate unit, recoverable unsupported regions | Do not fabricate spans from lowered host nodes; retain lossless source outside Core. |
| Resolved facts | Bounded analysis producer / policy and explanation | Symbol/operation owner, type/effect/capture facts, scope, provenance, dependencies, unresolved obligations | Unsupported is explicit; facts do not depend on which restrictions were selected. |
| Public interface | Owning-module checker / independent client checker | Complete exported contract, quantification if supported, call shape, nominal owners, version | No private client observations or execution to fill missing fields. Start monomorphic. |
| Verification basis | Producer / evidence validator | Source, producer/rules, dependency interfaces, semantic/profile assumptions and verified contract identity | A declaration or well-formed record is not verification; stale/unknown versions refuse. |
| Policy verdict | Obligation selector / CLI and eventual build/run admission | Normalized requirement set, scope, per-obligation evidence or blocker | Preview is not execution admission; a restriction cannot grant authority or change meaning. |
| Execution | Runtime facade and host / result and observation tools | Exact selected source/build, input/run epoch, current grants, completion and events | Use-time authority, supported capabilities and cleanup belong to execution, not a cached verdict. |
| Projection or change | Tool/domain adapter / reader or commit owner | Source/value identity, completeness, target and base context, explicit edit kind | Rendering never runs code; stale changes are rejected by the owner at publication. |

One record need not contain every row. Separate source evidence, public contract
compatibility and exact executable identity. Do not introduce a universal graph,
shared mutable facts service or a mandatory sidecar file for a one-line script.
Use in-memory passive records first; persist only when separate consumers expose
a concrete cache or interchange need. A second independent consumer justifies
extracting a shared schema; it does not justify generalizing unsupported types.

### Invalidation And Failure Protocol

The first trial may conservatively reanalyze an entire owning module. Selective
dependency invalidation is later work and must earn its complexity.

| Change or malformed input | Required first-trial behavior |
| --- | --- |
| Source changes while displayed name stays the same | Old report remains historical; fresh analysis before a current verdict. |
| Private edit preserves the public contract | Reverify implementation; public compatibility may remain unchanged. |
| Dependency changes result/effects or nominal owner | Reverify dependent facts; unchanged importer text is insufficient. |
| Numeric profile or analysis rule version changes | Invalidate facts using that basis; never silently reuse host assumptions. |
| Requirement order changes | Same facts and normalized verdict; unknown/duplicate policy handling is explicit. |
| Runtime grant revoked | Existing static fact can remain true; subsequent effect authorization is independently refused. |
| Missing spans or truncated trace | Retain filename/revision/context and completeness; no invented positions or implied full explanation. |
| Malformed artifact, unsupported major version or unresolved contract field | Structured refusal; no fallback to execution to discover the answer. |
| Budget exhausted or analysis cancelled | Incomplete obligations; never a successful strict verdict. |

Distinguish violated contracts from insufficient evidence and from invalid
requests. An eventual strict runner must bind its admitted source/build to the
one executed; the existing `check()` result does not perform that binding.
Checks and supplied fixtures are local evidence, not authenticated remote
attestation. Do not add trust machinery before a package/host boundary needs it.

### First Extraction And Migration Order

Candidate file locations are deliberately tentative:

1. Add a small passive contract model beside `prototype/analysis/model.py`,
   for example `prototype/analysis/contracts.py`, plus new tests under
   `prototype/tests/unit/analysis/`. Cover the canonical monomorphic cases,
   evidence source and refusal boundaries before changing the scalar producer.
2. Supply two independently specified consumers: call/obligation judgments and
   human/machine inspection. Hand-authored facts stay labeled supplied. Do not
   report this as a source checker or general type inference.
3. Only after that comparison agrees, add one source adapter that establishes
   the constant-return/explicit-scalar contract. Target `pub` and annotation
   behavior need an explicit frontend profile; the current hosted annotation
   evaluator is not that profile. Keep unsupported frontend claims false.
4. Reuse `prototype.runtime.check` and the CLI for a bounded explanation only
   after report scope and version compatibility are explicit. Preserve the
   existing module-execution report; use a new scoped/versioned record if its
   meaning changes rather than silently upgrading `ok`.
5. Introduce browser checking or a projection only after its actual source/fact
   producer is supported. A rendered supplied-fact study remains a study artifact.
   Use existing runtime result/diagnostic boundaries; keep layout out of Core.

Removal: an optional analysis experiment can be withdrawn without changing
ordinary execution. A failed source adapter can be replaced while retaining
the independent contract cases. An unsupported projection falls back to source.
Do not migrate every frontend, implement generic syntax or write a universal
policy engine just to preserve one candidate's internal data structures.

### Hosted Continuation Maintenance Is A Separate Lane

The carrier repair closes the existing protocol counterexamples and adds
independent native/hosted source-transport cases. It retains the handler-table
support fence. An explicit-frame rewrite remains an alternative if supported
source shapes cannot be represented without more host-protocol leakage; no such
rewrite was needed for these cases. Withdrawing previously supported handlers
would avoid rather than repair their relied-upon behavior. Error provenance is
never inferred from a RuntimeError's message or cause.

Use the existing new regression files as the independent compatibility oracle;
do not weaken them to approve the committed mechanism. Keep protocol transport
in the continuation/public adapter; ordinary evaluator operators only preserve
the original source error. New carrier-aware branches elsewhere or new supported
suspension families trigger the frame-versus-fence comparison again. Document
any reduced support before effects.
The hosted choice does not settle target generators, typed resource completion
or the architecture of a future scheduler.

## Closed Report Compatibility Boundary

Owners: `prototype/runtime/report_boundary.py` and
`prototype/runtime/js/report_boundary.js`. These replaceable libraries implement
the selected [report laws](../design/synthesis.md#report-admission-gaps): exact
JSON number tokens, strict versioned trees, two closed schema descriptors,
ordered accumulated decode errors, explicit finite trim, deterministic encode
and shared input/work/output accounting. They own no report transformation.

Hosted Nomi/reduced interpreters use a run-reset provider. Core uses the strict
`report_boundary_adapter.py` whitelist; JS uses its corresponding tagged seam.
The adapters preserve aliases/cycles for library validation and refuse implicit
nominal, Float, callable or foreign projections. Caller contract errors precede
budget consumption. Each evaluator/session run has its own allowance; a fork
retains custom calls while creating fresh default-provider closures.
`host_capabilities.json` records ordinary call shape and supported routes, not
source-derived purity evidence or target typechecking.

`samples/report.nomi` owns options-first validation, full batch decode before
filtering, normalization, counts and separate `report_json` encoding. Its
structural outcomes and callback-first `map`/`filter` with explicit `list`
materialization are compatibility forms. The default browser renders result
bindings and offers an explicit download for an exact `{ok: true, text: Text}`
outcome. That shape is a host presentation convention, not authenticity or JSON
validation; the library-produced bytes have independent encoding fixtures.
Download cannot start from stale/busy results, and initiation failure preserves
the report. The browser cannot attest a durable filesystem save. Legacy Pyodide
executes the source but keeps Bindings/download unavailable.

Removal gates: derive the two descriptors from admitted Data declarations,
replace outcome maps with nominal Result, justify closed checked callbacks and
local imports, then compare the same independent values/errors/bytes before
removing adapters. A third schema or general schema syntax requires returning
to the target owner. Separate input/options editing and persistence, source
locations/formatting, browser peak memory and supported release capacity remain
open. The current runtime/report fixtures establish only their declared
compatibility boundaries; broader target conformance is not inferred.

## Next Bounded Steps

The [Project Enhancement Roadmap](project_roadmap.md) now owns the shared
delivery sequence. Its A18 covers facade/session/transport boundaries, A23
editor host behavior, A04/A06 structured parser/Core payloads, A25 measured
optimization, and A28 distribution/CI/release metadata. Each retains the
acceptance gates described here; the roadmap adds dependencies on language,
diagnostic, conformance and product work rather than another engine framework.

Do not batch these into a rewrite. Discovery should produce a small fix or a
specific unresolved contract, followed by focused checks and a checkpoint.
Reproduce suspected test defects independently and preserve their oracle; do
not mix assertion weakening into implementation changes to make a suite green.

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
