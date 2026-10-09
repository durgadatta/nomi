# Frontier checkpoint: 2026-10-08

> Status: active iterative execution checkpoint, refreshed 2026-10-09. This supersedes the earlier
> documentation-only checkpoint at 22c7bbd; that historical record remains in Git.
> It preserves context, not a claim that unfinished code is ready.

## Latest instruction and next step

The latest 2026-10-09 instruction requests more depth on plans and gaps and a
commit of that work. This pass ends at a documentation checkpoint. The wider
iterative implementation mandate remains the context, with current delivery
order in the roadmap; no new runtime work is included in this pass.

Planning preparation P1-P5 is historical planning context, not semantic
acceptance or independent review. The current product-first handoff narrows the
first release to calculation, local JSON report/repair and local reuse. Continue
through [FRONTIER_PLAN.md](../../FRONTIER_PLAN.md), whose
[fresh-session sequence](../../FRONTIER_PLAN.md#fresh-implementation-session-sequence)
is the execution handoff. Strategy `bc8f0c8` and calculation `9d2f87d` are already
committed. Resume with the report admission gaps and its library comparison,
then target migration and checked reuse. The latest gap-review receipt below
supersedes historical “next pass” instructions; earlier counts remain historical.
Committing the experiments preserves them; it does not accept their architecture
or mark their milestones complete.

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
| 6aec9f3 | All previously pending experiments and planning state; known failures preserved with current focused checks |

The canonical direction has advanced beyond mandatory public annotations.
General inference, public generic contracts, dynamic adapters and policy syntax
remain unresolved. The first product profile is deliberately narrower: local
calculation/report/reuse closes only the scalar, codec, callable and host-run
contracts it needs. Explicit mutation remains the current target. Interpreter
modes are implementation/test choices, not user assurance tiers.

The frontier plan uses the roadmap's M0-M5 milestones, with M1/M2 interleaved
by journey. Earlier P/F labels are historical planning organization; S0-S3 identify
older experimental implementation slices. Existing A and D owners remain
authoritative.

## Preserved experimental inventory

All rows below are **experimental work included in the preservation checkpoint**,
including their related documentation and tests. They remain unfinished at the
start of this continuation; retain the failing expectations while repairing them.

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

## Planning outcome: 2026-10-09

Canonical additions stay with the four existing designing packets:

- [Synthesis](../design/synthesis.md#growth-journeys-and-boundary-evidence):
  invoice/import/job growth, policy scope, error/repair and evidence identity.
- [Function contracts](../design/function_contracts.md#bounded-contract-comparison-for-implementation):
  monomorphic public boundary, exact/default call shapes, shared-storage
  generalization witnesses and producer/consumer separation.
- [Resource completion](../design/resource_lifetime.md#remaining-completion-experiments):
  missing schedules, heterogeneous causes, argument capture and async gates.
- [Interaction model](../design/interaction_model.md#paired-representation-and-revision-trial):
  matched text/structured tasks, notebook binding/epoch comparison and domain
  challengers. No UI or human study was produced.
- [Implementation map](implementation_layers.md#planned-assurance-and-representation-boundaries):
  proposed artifacts, invalidation, refusal, extraction and continuation lane.

The frontier plan contains ordered future work, exact first experiment,
verification/removal gates and remaining evidence requirements. The registry,
decision ledger, target-only fixtures and four bridges route to the same plan.
No new grammar, type-system rule, schema, runtime behavior, test implementation
or runnable sample was introduced after 6aec9f3. All four packets remain
`designing`; pattern-matching keeps its independent implementing status.

Planning verification: **127 passed** across the existing documentation
lifecycle, design-pass, target-fixture coherence and malformed-packet suites.
`python3 -m tools.design_passes check` passed all five packets. A read-only link
and heading audit passed 554 local links across 17 changed Markdown files.
Agent checks passed, initially warning that the local RAG index was stale;
the ignored index is refreshed after the final prose edits. These checks validate
document integrity, not the proposed typing, cleanup or representation contracts.
No runtime, browser or research-capture rerun is attributed to these planning
edits. The preservation results above remain the implementation evidence.

## Planning retrospective

### Evidence That Changed The Design

Earlier independent review exposed host continuation exception boundaries.
This session reproduced the findings and used adversarial self-review for the
new plan. The growth journeys separated a successful scalar call from a public
contract, and a stable API from fresh implementation verification. Shared
storage, default timing and unknown external outcome remain concrete negative
cases rather than assurances inferred from attractive source.

### Workflow Friction

The handoff still said code was uncommitted, packet routes requested an already
preserved scalar experiment, and broad P1-P5 titles did not identify exact
inputs, observations, files or stop conditions. The prior milestone/annotation
corrections are retained; no new parallel backlog or study inventory was needed.

### Durable Improvement

Prepared comparisons now live with their canonical owners and link to bounded
implementation work orders. The checkpoint is reconstructible from Git and
distinguishes actual checks from proposed evidence. No additional automation,
skill growth or runtime implementation was justified in this planning phase.

### Next Pass

Commit the reconciled plan, then establish independent calculation vectors and
repair the reproduced JS mixed-type arithmetic mismatch. Reconcile the 24
known continuation failures in a separate bounded maintenance lane. Close and
deliver calculation, report and local reuse in that order; closed public evidence
belongs to reuse, not the first outcome. Unknown dependencies refuse checked
export; supplied facts are never reported as inference. The roadmap ledger
retains the wider generic/resource/representation/domain frontier and its real
experimental, human and external gates. No further global survey is required.

## Iterative strategy receipt: 2026-10-09

Start revision `40c365e` was clean. Independent read-only reviews reproduced
the 146 passing analysis/API/CLI/completion cases and 24 failing / 15 passing
protocol-review cases, and probed the invoice through three public backends.
3850 and edited 5050 agree. Text quantity exposed JS coercion; Bool arithmetic,
wide Int capacity, Unicode ordering and whitespace normalization remain named
target/prototype mismatches. These observations do not establish the complete
first-product profile.

The committed strategy reconciles the current phase, interleaves M1/M2 by
journey, and accounts for A01-A33 in eleven owned closure lanes. Reviews changed
the order and gates rather than adding a new backlog. The existing documentation,
packet and target-fixture selection passes **127 tests**, with all **five**
design packets coherent and whitespace clean. These are planning-integrity
checks; the actual browser baseline is a separate check in progress.

## Report plan handoff: 2026-10-09

The next reviewed plan closes the bounded report laws in
[semantics](../design/semantics.md#first-report-boundary-contract), records the
decision in [the ledger](../design/decisions.md#first-report-boundary-october-9-planning-decision),
and specifies the proposed library/value/outcome bridge in
[synthesis](../design/synthesis.md#report-library-experiment). Commit these
owners before report code; use the
[frontier work order](../../FRONTIER_PLAN.md#report-boundary-work-order).

Read-only probes reproduced missing `pub`/variant/`?` source support, unsupported
Core imports/named data calls, absent Ok/Err/map_error/trim owners and divergent
host stripping. Passive DecodeError records are not a decoder. The selected
bridge therefore uses finite ordinary-call Python/JS libraries, a closed
structural JSON tree with exact Number tokens, two declarative batch/options schemas and
source-owned report transformations. Compatibility outcome/record adapters do
not implement target nominal data/Result, checked modules or derived codecs.

Independent fixtures must distinguish duplicate keys from duplicate IDs, retain
both malformed name/age paths, enforce 128/129 rows before filtering, reject
Bool/Text/fraction/exponent Int fields, and preserve/refuse wide Int explicitly.
Options default to `13` only through their separate descriptor, recording actual
application; no default fills a missing row field or hides invalid options.
Finite ASCII trim retains U+0085/U+FEFF; deterministic structural encoding is
separate from display. The five configured limits remain provisional until
measured limit/limit-plus-one evidence exists. No report code, measured support,
user trial or target sample promotion is attributed to this planning addition.

Next exact step: after the plan commit, close the remaining admission gaps and
add literal boundary vectors before the replaceable parser/closed decoder
libraries, then integrate ordinary providers
and source report logic. Validate CLI and committed WASM/JS before promoting a
compatibility sample. Keep general schema, Result/data/module/checker migration,
runner work bounds and target-format support visible as later obligations.

## Calculation delivery receipt: 2026-10-09

The strategy was committed first at `bc8f0c8`. Independent calculation vectors
then exposed and removed JS operand coercion at `a1813f6`: wrong text operands
now fail, compatible Text/List operations retain their meaning and evaluation
occurs once in source order. `02de067` accepts bounded target exact-Int,
Bool/Text distinctions and Unicode scalar rules; it does not claim those laws
are completely implemented by the compatibility runtimes.

`e0c2102` gives the public Node adapter a validated `nomi.eval-result` v1
success/failure contract. Completed output survives a source failure, semantic
codes are preserved and malformed transport cannot manufacture success.
Source positions remain unavailable. `200ee98` repairs the legacy equation
wildcard's Core reduction after strict arithmetic revealed that a fallback
had incorrectly returned None. Existing expectations were retained.

The promoted `samples/calculate.nomi` delivers run (3850), edit (5050), wrong
quantity, inspect error and repair (3850). Saving source downloads the actual
current source. Editing labels the prior result stale; failure does not retain
5050 as current output. This is an executable compatibility journey; full
target Int capacity, strict Bool control, checked calls and source maps remain
separate obligations.

| Capability | Current evidence | Limit |
| --- | --- | --- |
| Parse/lower | Python frontend and committed Rust/WASM producer lower the calculation | No new target source spelling admitted. |
| Check | Existing independent `known-types` experiment refuses the invoice's wrong argument without execution | Not a verified public contract or full type checker. |
| Run | Public Python/Core/Node and browser agree on 3850/5050 and wrong-argument refusal | JS explicitly refuses wide Int; Python Bool arithmetic remains compatibility behavior. |
| Diagnose | JS preserves `NOMI-OPERAND-TYPE`, readable kinds and completed stdout | No invented source span; Python diagnostics retain their existing shape. |
| Format/save | Browser exports current source and preserves edits/drafts | No canonical whole-language formatter or separate input editor claimed. |

Checks for this increment:

- Public JS backend, session, numeric and collection selection: **217 passed**.
- Independent scalar, wildcard and WASM pipeline/parity selection: **68 passed**.
- New sample regressions: **4 passed, 2 existing skips**. Only
  `test_eval_loop_nomi_sample_calculate_nomi_.txt` and
  `test_eval_loop_reduced_sample_calculate_nomi_.txt` were generated, because
  sample promotion requires snapshots. Existing snapshots were unchanged.
- Actual CLI `--output program`: **3850**.
- Actual browser: calculation/edit/error/repair/source download plus existing
  sample, notebook, diagnostics, cancellation, draft and desktop/mobile checks
  passed. The repaired calculation screenshot was inspected. Artifacts are
  ignored under `reports/web-browser-calculation/`.
- The pre-change browser baseline also passed with the optional legacy Pyodide
  route under `reports/web-browser-frontier-baseline/`. This is local evidence,
  not a deployed artifact or a human usability trial.
- `scripts/make_web.py` regenerated the manifests solely to add the calculation
  sample: **127 runtime files, 12 samples**. `--check` passed. The manifest-list
  digest is `a988067f012cf841409cca63a840bf35609690826bbdc120b22966ce2fe3ce7f`;
  it identifies inventory, not runtime file contents. WASM was not rebuilt.
- Changed-file Ruff and whitespace checks passed.

An exploratory full-suite run during concurrent backend edits found transient
envelope failures and the real wildcard defect. It is not a passing receipt;
rerun the full suite after the continuation candidate and adapters settle.
The next action recorded at calculation delivery was continuation review and
report-contract planning. The gap-review receipt below now owns the next step.
Target-only report and reuse fixtures are not yet runnable product claims.

## Plans And Gaps Receipt: 2026-10-09

Planning starts at `52deae4`. This documentation checkpoint includes the pending
report contract, deepens its admission gaps and replaces stale active-queue
instructions. It leaves five modified continuation/interpreter files and the
untracked `test_generator_source_transport.py` outside the commit; those changes
are not validated or accepted by document tests.

The [synthesis gaps](../design/synthesis.md#report-admission-gaps) name eight
concrete decision/integration boundaries, their owners and discriminating cases.
Independent report oracles now include exact encoded output. The
[roadmap gates](project_roadmap.md#report-and-target-delivery-gates) order library
comparison, ordinary providers, real report repair, target scalars, nominal data,
Result/match, checked callbacks and local reuse. The compatibility report cannot
close the target release; a third manual schema triggers target extraction work.
The target fixture uses explicit finite trim, and the registry/research route
agree with the selected report laws and remaining work.

Next exact step: settle library failure classification/completeness, path/code
rendering, JSON lexical/escape rules and local budget accounting, then materialize
literal fixtures. Implement no unresolved envelope by guessing inside a host.
Options-versus-input identity and the outer report outcome must close before
source integration. Continuation review stays separate; full-suite health,
capacity measurements, human trials and hosted distribution remain unverified.

Validation for this planning checkpoint:

- Documentation lifecycle, design-pass, target-fixture coherence and malformed
  packet suites: **127 passed** (`python3 -m pytest -o addopts= -q` on their
  four existing test files). These checks do not execute target programs.
- `python3 -m tools.design_passes check`: all **five** packets coherent.
- Read-only Markdown scan: **205** local links/anchors resolve across the
  **eight** changed Markdown files.
- `python3 .codex/scripts/agent_doctor.py`: setup checks pass; the ignored local
  RAG index is stale after documentation changes. Rebuild it before relying on
  retrieval in the next session; no index content is committed.
- `git diff --check`: passes. No runtime, browser, benchmark, generated-asset,
  hosted or human-study check was run in this planning pass.

