# Nomi product synthesis and handoff

> Historical implementation plan, closed as a handoff 2026-10-10. Planning
> reached synthesis at `7684950`; bounded compatibility report implementation
> reached `8081e93`, with its completion recorded at `2338bdd`.
> The next pass starts from user-facing documentation and explanation; follow
> the [current pass direction](docs/orientation/project_roadmap.md#user-facing-documentation-pass).
> The target and reuse gates below remain future engineering dependencies,
> not the active task or a claim that the full frontier is complete.
> This replaces the earlier contract-first execution order at `915aea1`.
> Canonical selection: [synthesis](docs/design/synthesis.md#first-product-contract).
> Project-wide delivery: [roadmap](docs/orientation/project_roadmap.md#delivery-order-and-dependencies).
> Preserved code and actual checks: [checkpoint](docs/orientation/frontier_checkpoint_2026-10-08.md).

## Completed Checkpoint And Remaining Engineering Gates

Implementation checkpoint: `8081e93`, superseding the incomplete library slice
`1d218ff`. The overall strategy is committed at `bc8f0c8`;
the compatibility calculation journey shipped at `9d2f87d`, followed by the
Unicode scalar-order repair. Those results do not complete the first-product
target profile. The plans/gaps checkpoint is `5728c96`; the separately completed
continuation repair is `e4209c8`, with 3,392 passing full-suite cases and actual
default/legacy browser checks. The latest checkpoint records skips, warnings
and the limits of that evidence.

The report's [admission choices](docs/design/synthesis.md#report-admission-gaps)
are selected and their literal oracles now execute through the closed libraries
and ordinary source. `samples/report.nomi` works through hosted Python, Core,
both JS producers, CLI and real default/legacy browser repair. The default
browser also downloads exact encoded JSON and blocks stale publication.
The [latest receipt](docs/orientation/frontier_checkpoint_2026-10-08.md#report-compatibility-completion-receipt-2026-10-10)
supersedes the incomplete library checkpoint. Future implementation must close
target scalar/data/Result/callback contracts and prepare source-derived closed
reuse evidence; do not expand the two manual schemas or add a whole-report builtin.
Reopen a selected rule only for a concrete failed discriminator.
The roadmap's [active queue](docs/orientation/project_roadmap.md#first-reviewable-work-queue)
owns ordering. Keep three outcomes distinct: a working compatibility report,
the target report with checked nominal contracts, and reusable local modules.
The first cannot silently substitute for the other two.

## End Goal

Nomi should let a person start with a short readable script, turn imperfect
input into a useful result, and grow that logic into a dependable program
without switching languages. The wider destination includes services, jobs,
data tools and domain packages. The first product earns that ambition through
**small scripts and trustworthy local data reports**.

The primary user can read simple code and wants an immediate useful result.
Local library reuse is the first growth step. General-purpose breadth, all
research topics, every existing feature and compatibility with all prototype
examples are not first-release obligations. Keep the playground usable while
changing examples and language support deliberately.

Four things remain separate: source meaning, selected checking restrictions,
runtime authority and engine choice. A checking switch never changes evaluation
or grants authority. Unknown evidence cannot become proof. A replacement engine
must conform to the same supported semantics.

## The Product In Sight

The default experience is a source editor with explicit input and understandable
results. This is a proposed screen/storyboard, not a UI implemented in this pass.

```text
Nomi    Calculate | Validate a report | Reuse a function
        Run   Stop   Format   Save source

Source                         Input / Result / Problems
build_report(text, options)     Input: editable JSON
...                            Result: received 2 | eligible 1 | skipped 1
                               Customer: c-1 | Ada | 20
                               Export JSON
                               Run belongs to source + input revision

Problem: $.customers[0].age
Expected a non-negative Int; received -1.
Also repair $.customers[0].name: the name must not be blank.
```

The first minute: open Calculate, press Run, change quantity 3 to 4, see integer
cents change from 3850 to 5050. Under a minute is a usability target, not a
measured result. The next task: paste the report's two-row input, inspect the
counts, break name and age, repair both errors and rerun. Finally save the source
and deliberately selected input, import the function locally, and reproduce
the same report from the CLI.

Source remains authoritative. Tables and diagnostics are read-only projections
of a particular run. No silent effectful rerun, hidden input binding or second
evaluator is permitted. The entry function, input/options and any host operation
must be inspectable. Advanced engine/capability detail belongs in inspection,
not the beginner's main route. Save source, encode result and save output remain
distinct actions; a failed save does not erase an inspectable successful report.

## What We Are Selecting

Use the canonical [core selection](docs/design/synthesis.md#selected-core-and-library-boundary),
rather than growing another feature checklist here.

- Include ordinary lexical names, visible mutation, functions, nominal data,
  strict lists, Bool choice, patterns, loops, Option/Result and explicit decode.
- Build the report from pure synchronous calls and a small checked collection
  library. Public reuse begins with closed contracts, inferred where supported
  or declared where needed.
- Keep console/input/save in explicit host adapters. Match browser and CLI values,
  failures and source explanations; transport UI may differ.
- Defer network jobs, general fallible resources, public generic/protocol syntax,
  effect polymorphism, editable graphs, broad package distribution, optimizing
  native engines and advanced domain libraries from the first release.
- Retain their extension seams: ordinary modules, owned data, explicit codecs,
  effects, resource/task owners and replaceable producers/consumers. Do not
  implement a universal framework merely to reserve future room.

The active [overall target](docs/design/targets/overall.nomi) is now a pure local
report. It validates the complete batch before filtering, preserves error paths,
retains duplicate IDs and row order, and returns a typed Result. The old combined
network/concurrency target is preserved at `915aea1`; existing resource and
concurrency fixtures continue to challenge the larger design. No target fixture
has been promoted into runnable samples.

Existing accepted syntax remains in its canonical owners. This release can
support a smaller explicit subset. A removed prototype spelling gets an honest
diagnostic or migration note, not a hidden alternative meaning. Research is
consulted for a concrete unresolved fork, not replayed as a comprehensive survey.

## Fresh Implementation Session Sequence

Use the roadmap's existing M0-M5 labels. The older P/F labels were planning
organization, not additional milestones; detailed comparisons remain in their
focused owners and Git history. Completion is based on evidence, not a date or
number of features implemented.

| Milestone | Concrete work | Exit evidence |
| --- | --- | --- |
| M0: fix the promise and baseline | Confirm the three journeys and first-product profile; inventory selected feature support and the last known working playground artifact; classify existing failures | Source examples, expected outputs/errors, explicit unsupported areas, baseline revision and a practical rollback path. No claim that current target source runs. |
| M1: close the next journey's blocking contracts | First scalar/direct-call/run rules; next strict codec/data rules; finally closed callable/module evidence | Independent positive/negative vectors and canonical decisions explain every API in the next slice. Repeat before each M2 increment; general D1/D2 can remain open outside this profile. |
| M2: implement complete vertical slices | First calculate/edit/error/repair, then decode/report/repair, then local reuse; each crosses source, checking, lowering, runtime and diagnostics as required | A user can perform the slice; expected values and errors agree across declared routes. A parser, schema or analyzer alone is not completion. |
| M3: make the product comfortable | Curate three examples; format, input editing, error navigation, result inspection, save/export, stop/restart and draft recovery | Real browser and CLI journeys, keyboard/focus checks, installed execution, stale-result tests and fresh generated artifacts. Observe unfamiliar users attempting the tasks; record remaining confusion. |
| M4: release a traceable artifact | Verify actual hosted/installed artifacts, support profile, version/source identity, documented limits and rollback | Reproducible build inputs, deployment smoke, release notes and recoverable previous artifact. No invented benchmark or hosted result. |
| M5: close the owned frontier | Execute the roadmap's owned comparisons in dependency order; use observed need to select product expansion | Every lane has verified support, evidence-based rejection or a bounded alternative/deferral with an exact trigger; new syntax only after ordinary code fails a concrete task. |

M1 and M2 interleave by journey. Close calculation's scalar/call/run rules, then
deliver calculation; close report's codec/data rules, then deliver report;
close reusable boundary rules, then deliver reuse. Every journey has a plan
before code, but calculation does not wait for unrelated report or generic
contracts. M3/M4 collect evidence from these increments rather than arriving as
an end-of-project testing phase.

### Iterative Commit Strategy

The roadmap's [active work queue](docs/orientation/project_roadmap.md#first-reviewable-work-queue)
owns scheduling; its whole-frontier ledger keeps the wider mandate visible.
The following work orders make the first increments concrete. Each row is one
or more independently reviewable commits, not a promise of a single giant patch.

| Order | Preparation and implementation boundary | Acceptance and next decision |
| --- | --- | --- |
| 1. Reconcile the plan | Remove superseded phase restrictions, record the baseline and three journeys, connect all frontier lanes to owners and closure gates | Commit documentation only after packet/fixture integrity checks. No runtime or target-conformance claim follows from this commit. |
| 2. Establish executable calculation evidence | Use `scripts/check_invoice.nomi`; independently pin 3850, edited 5050, wrong argument, repair, negative/zero/huge Int, Bool, Unicode text and mixed-operation cases | Exercise the public Python runner, Node Core and committed WASM producer. Classify value disagreement, explicit unsupported range and checking obligations separately. Fix reproduced host coercion without teaching a new source spelling. |
| 3. Reconcile relied-upon continuation | Compare an explicit exception carrier, explicit frames and a support fence against existing native/hosted protocol traces | Preserve exception identity/active state and fence unsupported definition-time suspension before effects. All 24 known failures must pass without weakened tests; no target-resource guarantee follows. This maintenance lane can run beside calculation work. |
| 4. Close the calculation profile | Decide exact Int versus fixed width with independent vectors; document Bool/Text distinctions, range refusals, error/source units and run limits in existing canonical owners | Accept only the bounded laws actually tested. Inventory parse/check/lower/run/diagnose/format separately; unsupported or unavailable evidence stays explicit. General inference is not a dependency. |
| 5. Deliver calculate/edit/error/repair | Repair the accepted missing runner/runtime/diagnostic behavior, then expose the same supported source in the playground | Values and failures agree in CLI and actual browser; a stale result is labeled, repair succeeds, check does not execute. Promote the sample with regression, manifest and browser evidence in the same increment. |
| 6. Close and deliver report | Specify strict JSON/declared data wire shapes, error order/path/truncation, constraints and byte/depth/work/output budgets; implement decode before filter and explicit encode | Empty/128/129 rows, duplicate IDs/keys, missing/extra fields, Bool/fraction/huge Int, two malformed fields and round trips. Inspect success independently of save; never construct a success report on decode error. |
| 7. Close and deliver reuse | Specify closed exports, local module/private identity, dependencies and source/contract/verification invalidation; add a bounded source producer and two passive consumers | Identical calculation/report results without consumers executing or reading private bodies. Unknown, modified dependency, forged supplied facts and unsupported versions refuse checked evidence. |
| 8. Complete product and distribution evidence | Curate the three journeys, formatting/error navigation, explicit input/save, stop/restart and recovery; verify wheel and actual hosted artifact when authorized | Record exact tested revisions and budgets; keyboard and fresh-asset checks pass. Human trials, publication and owner metadata remain separately named gates until actually performed. |
| 9. Carry the frontier through closure | Follow the roadmap ledger through callbacks/effects, resource/task completion, representation trials, domains, packaging and engine substitution | Each lane reaches accepted-and-verified, rejected with evidence, or a bounded experiment/deferment with a concrete trigger. An unimplemented research API or a passing host model is never reported as a shipped capability. |

Before each implementation commit, name the semantic owner, normal form,
affected capability axes, expected independent cases, inspection surface and
removal criterion. Keep producers and consumers replaceable; extract a shared
mechanism only when a second actual consumer demonstrates the need. Finish
focused checks first, then broaden for changed semantics and unresolved risks.
Record actual evidence and the next exact step in the existing checkpoint;
do not create another live backlog or treat historical check counts as current.

### Historical Baseline And Recovery

The strategy pass started at `40c365e`, with a clean working tree. Its read-only
calculation probe gives 3850 and 5050 on Python/Core/JS, but text quantity
`"three"` fails in Python/Core and produces concatenated text in JS. Bool
quantity executes as 1450 in the compatibility runtimes while the scalar
checker refuses it; this is an explicit target/prototype mismatch to settle,
not a reason to advertise typed Int calls. A huge integer is exact on Python
and refused on JS. The selected analysis/API/CLI/completion selection again
gives 146 passed; protocol review again gives 24 failed and 15 passed.

The later [calculation receipt](docs/orientation/frontier_checkpoint_2026-10-08.md#calculation-delivery-receipt-2026-10-09)
records actual local browser checks and 12 samples. Keep `40c365e` as the
historical source recovery point and `9d2f87d` as the calculation delivery
checkpoint. Neither identifies a verified hosted deployment. Rebuild and verify
the chosen recovery revision before serving it; retain source/draft export
during migration. This planning pass performs no new browser or deployment run.

### M1 Work Orders

These work orders retain the comparisons behind M1. The scalar and bounded
report decisions are now recorded in their canonical owners; their implemented
support still needs the evidence below. Callable, module and run gaps stay open.

| Decision / owner | Exact comparison | Failure or removal condition |
| --- | --- | --- |
| Portable values, A03/D3 | Exact Int versus checked fixed width; literal/arithmetic/JSON round trips, huge/negative/fractional numbers, Bool distinction, Unicode supplementary characters and source offsets | Any accepted number silently rounds, hosts disagree or display units are confused with source offsets. Narrow unsupported operations explicitly instead of inventing host-specific semantics. |
| Strict data, A09/A12/D3 | Declared fields and supported codec shapes; missing/extra/duplicate keys, multiple errors, explicit normalization, empty/128/129 rows and repeated IDs | Malformed rows disappear during filtering, errors lose original paths, constraints silently coerce, or encoding uses human display. |
| Closed calls and reuse, A05/A08/D1 | Directed subtotal and inferable constant; map/filter/fold/map_error instances; default/capture/effect behavior; two passive consumers plus unknown and changed-dependency cases | Supplied metadata is called inference, client arguments determine a public promise, checking executes user code, or unresolved effects become purity. |
| Host/run experience, A19-A23/D4/D5 | Explicit entry/input/options; source/input/run identity; host read/save failures; bounded input/depth/work/output; stop/restart/draft recovery | New source displays old results as current, inspection runs effects, save falsely claims publication, or worker termination is claimed as language cleanup. |

Use the selected exact Int and strict report laws; do not infer acceptance of a
numeric tower or general schema system from those bounded decisions.
Runner budgets need documented values and a pinned measurement environment
during M1/M2; 128 rows alone is not a resource bound. General callback, resource
and representation comparisons already live in
[function contracts](docs/design/function_contracts.md#bounded-contract-comparison-for-implementation),
[resource completion](docs/design/resource_lifetime.md#remaining-completion-experiments)
and [the paired interface trial](docs/design/interaction_model.md#paired-representation-and-revision-trial).

### Calculation Slice And Its Remaining Target Gap

The compatibility calculate → edit → wrong argument → repair journey is
delivered. Its checkpoint table records parse/check/lower/run/diagnose/format
evidence separately. Exact portable Int execution, Bool-only boundaries,
verified public calls, real source spans and canonical formatting remain open.
Use the same independent invoice vectors when closing those target gaps.

Likely owners are `prototype/analysis/`, `prototype/runtime/api.py`,
`prototype/parser/`, `prototype/runtime/js/`, `scripts/cli.py` and
`web/app.js`/`web/editor.js`; choose files from the accepted missing contract,
not an assumption that every layer needs a rewrite. Use the existing module
check report only within its actual scope. Add public-contract evidence when
the reuse slice needs it; it is no longer the first product outcome by default.

The compatibility report decode/repair path is delivered. Next replace its
manual data/outcome adapters in target order and establish checked local reuse.
For each increment, provide expected values/errors, source maps, formatting,
refusal cases and appropriate differential checks. Avoid a long sequence of
disconnected infrastructure milestones before a person can complete a task.

### Report Boundary Work Order

Commit the selected [boundary laws](docs/design/semantics.md#first-report-boundary-contract)
and [library proposal](docs/design/synthesis.md#report-library-experiment) before
report code. The first library APIs are ordinary `parse_json`,
`decode_data(value, schema_name)`, `encode_json`, `trim_text` calls. Source
`build_report` owns normalization, eligibility and counts; there is no native
whole-report builtin or general schema language.

The parser emits a validated versioned structural Value tree whose Number nodes
retain exact token Text; no Float conversion occurs. Decode accepts integer-form
tokens, rejecting Bool/Text/`1.0`/`1e0`, with explicit per-host numeric capacity.
The two declarative schemas are strict batch/row and separate options; options
alone apply the recorded default `minimum_age=13`. The compatibility entry is
`build_report(text, options_text="{}")`; it parses/decodes both explicit inputs.
Trim removes only
U+0009..U+000D and U+0020; U+0085/U+FEFF remain intact. Errors carry exact ordered
paths and no raw input echo. Encoding accepts the bounded structural family,
sorts map keys by scalar-value order and emits minimal UTF-8 JSON with required
escapes. Target Result/nominal data/derived codec/import obligations remain open.

| Increment | Concrete owner and independent evidence | Gate / next step |
| --- | --- | --- |
| Boundary fixtures and libraries | Small replaceable Python/JS library owners under `prototype/runtime/`, a closed declarative schema registry and new contract fixtures; reuse `decode.py` through an explicit record adapter | Exact tokens, duplicate/escape-equivalent keys with original paths, supplied-tree schema/version/tag rejection, surrogate refusal and deterministic encoding. No general evaluator/schema rewrite. |
| Closed batch/options decode | Only `report-batch`/`report-options`; original Text retained, fresh detached records, 128-row cardinality before children, field/error ordering and independent predicates | Two errors for blank name plus age -1; malformed ineligible row still fails; empty/128 succeeds, 129 fails; repeated IDs/order retained. Omitted versus supplied `13` records different default provenance; invalid options remain separate. Observe the 65th error before returning first 64 with `complete=false`. |
| Public source report | Register ordinary pure provider calls through existing metadata/adapters; implement readable Nomi transformation and explicit encode | Facade/CLI/committed WASM/JS agree on supported cases and explicit wide-Int refusals. Compatibility outcome records and current source syntax are labeled; `overall.nomi` stays target-only. |
| User repair and target handoff | Explicit input/options and structured error navigation; sample/regression/assets/browser promotion after the whole path works | Repair/rerun/export and stale-run cases are real. Source checker unknowns stay unknown. Replace manual schema/outcome adapters when admitted DataDecl/Result/module contracts and independent consumers supply the same evidence. |

Provisional per-call experiment configuration is 256 KiB input UTF-8 bytes, 32 simultaneous
map/list containers, 8,192 Value scalar/container nodes (keys excluded), 64
retained errors and 64 KiB encoded UTF-8 bytes. The selected synthesis additionally
defines shared input/work/output accounting and a diagnostic-byte ceiling.
These remain candidate support settings. The reproducible
`scripts/measure_report_boundary.py --browser` probes local Python, Node and
Chromium workers; the checkpoint distinguishes traced allocations, process RSS
and unavailable browser memory. Broader deployment/capacity claims still need
representative pinned hosts. Source/evaluation work and worker Stop remain
separate gates. Failed encode/save preserves an inspectable success.

### Commit Boundaries And Stop Rules

1. **Planning closure (this pass):** selected laws, adapters, decision rationale,
   literal records, target pressure and delivery gates are ready. Commit them
   with document/packet/fixture-integrity evidence. The pending continuation
   repair is already verified and committed separately.
2. **Materialize executable boundary checks:** consume the prepared literal
   cases and add limit, graph, boxing and error-category vectors from the same
   contract. Do not generate expected records with either implementation under
   test. A fixture-integrity check alone is not report conformance.
3. **Library comparison:** implement exact-token parse, supplied-tree validation,
   closed decode, trim and encode in replaceable Python/JS modules. Review
   library results before provider wiring. An unresolved failure envelope or
   budget rule returns this increment to its canonical owner with the exact
   failing vector; it does not justify a new global planning pass.
4. **Public report integration:** wire ordinary providers, source-owned
   transformation and explicit inputs; establish facade/CLI/committed-WASM
   agreement, then real browser repair/export/recovery. Promote a compatibility
   sample only with its profile, regressions and generated assets.
5. **Target migration and reuse:** follow the roadmap's target gates. Replace
   manual schemas and outcome maps as nominal data, Result and checked calls
   become available. Do not add a third report schema or second ad hoc module
   loader to extend the bridge; that need triggers the corresponding target
   contract comparison first.

Each implementation receipt names the exact revision plus dirty-file scope,
host/toolchain, input vectors, declared route, results/refusals and unresolved
capabilities. Historical counts and manifest path digests cannot establish
current runtime or hosted-artifact identity. Revert an unsuccessful experiment
as its own reviewed change; do not erase unrelated continuation work.

## Keeping The Playground Working

1. Record and retain the last known working artifact before implementation.
   A clean Git tree alone is not browser validation.
2. Keep new target fixtures outside the sample selector until the whole supported
   path runs. Integrate sample, runtime, diagnostics, capability metadata and
   generated assets together.
3. Curate examples around Calculate, Validate and Reuse. Existing examples may
   be adapted, replaced or retired; annotate meaningful syntax migrations.
   Preserve user drafts and offer source export before incompatible changes.
4. Keep experimental capabilities accurately labeled. Do not make the default
   experience require knowing Python, Core IR, WASM or interpreter modes.
5. Run sample regressions, runtime artifact checks and actual browser checks
   for promoted changes; verify the exact deployed artifact when publishing.
   Roll back to the retained working artifact if the main journeys regress.

The current JS/WASM route and hosted compatibility routes are implementation
assets, not the language definition. A prototype feature is not worth preserving
solely because tests exist, but retiring it must be explicit and reviewable.
Planning changed only target fixtures. The subsequent compatibility increment
promotes `samples/report.nomi`, providers, browser JSON download and generated
assets together, with independent source/runtime and real browser evidence.

## Verification And Release Gates

| Change | Required evidence | Limit |
| --- | --- | --- |
| This plan and target-only fixture | Existing documentation/packet/target integrity suites, links and whitespace | Does not parse, typecheck or execute the target. |
| New source semantics | Independent accepted/refused vectors, focused parser/checker/runtime tests, relevant differential/regression checks | Do not weaken an existing expectation simply to make migration pass. |
| Public contract | Two independent consumers, source-derived evidence, identity/invalidation and no-user-execution negatives | No general polymorphism, secure package verifier or lifetime proof implied. |
| Playground/sample | Runtime freshness/contracts, sample regression and actual browser workflow, then deployed artifact when released | A browser smoke is not usability/accessibility evidence. |
| Product readiness | All three journeys, malformed-input repair, local reuse, recovery and keyboard operation observed | Targets such as first success under a minute require measurement, not assertion. |

The known continuation experiment at `6aec9f3` has **24 failing / 15 passing**
protocol-review cases; a separate focused analysis/API/CLI/receipt/completion
selection has **146 passing**. These are recorded earlier checks, not freshly
rerun by this synthesis. The last planning integrity suite had **127 passing**.
Current-pass results belong in the checkpoint below.

The later continuation completion is recorded at `e4209c8`; the counts above
are historical. New host-protocol leakage or a newly required suspension family
reopens the carrier/frame/fence comparison. This compatibility repair does not
select target generator semantics or typed resource completion.

## What Is Ready And What Remains

Delivered: compatibility calculation and continuation repair, planning
synthesis, closed report libraries and source-owned report/repair/encode,
default-browser JSON download, independent oracles and local capacity probes.
The eight planning gaps have explicit dispositions and implementation evidence.

Still required: target scalar/data/Result/call migration, source-derived checked
local reuse, representative capacity support, separate input/options editing
and persistence controls, product trials and distribution checks. The current
sample edits JSON inside source; changing it changes the source revision.
Existing owners contain these tasks; another global planning layer is unnecessary.

Continue this session or start a fresh one with this instruction:

> Read this plan, canonical first-product synthesis and the checkpoint. Keep
> the playground working, but adapt examples freely. Confirm the selected
> profile and actual baseline. The strategy and compatibility calculation are
> already committed, and continuation compatibility is repaired. The bounded
> compatibility report and default-browser repair/export are delivered. Close
> target scalar/data/Result/checked calls in the roadmap order and prepare the
> source-derived closed reuse comparison with two passive consumers. Consult broader
> research only for a concrete blocker. Do not silently accept proposed APIs,
> change tests to hide failures or restart a general redesign. Continue through
> the ordered commits and the whole-frontier closure ledger; report incomplete
> evidence as incomplete rather than declaring the entire frontier finished.
