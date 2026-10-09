# Nomi product synthesis and handoff

> Active planning handoff, refreshed 2026-10-09 after the user's product-first
> synthesis request. Implementation belongs in a fresh session.
> This replaces the earlier contract-first execution order at `915aea1`.
> Canonical selection: [synthesis](docs/design/synthesis.md#first-product-contract).
> Project-wide delivery: [roadmap](docs/orientation/project_roadmap.md#delivery-order-and-dependencies).
> Preserved code and actual checks: [checkpoint](docs/orientation/frontier_checkpoint_2026-10-08.md).

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
| M1: close only the blocking contracts | Resolve scalar/text, strict codecs, closed callable/module evidence and host entry/run rules for these programs | Independent positive/negative vectors and canonical decisions; every proposed API in the selected path is explained. General D1/D2 can remain open outside this profile. |
| M2: implement complete vertical slices | First calculate/edit/error/repair, then decode/report/repair, then local reuse; each crosses source, checking, lowering, runtime and diagnostics as required | A user can perform the slice; expected values and errors agree across declared routes. A parser, schema or analyzer alone is not completion. |
| M3: make the product comfortable | Curate three examples; format, input editing, error navigation, result inspection, save/export, stop/restart and draft recovery | Real browser and CLI journeys, keyboard/focus checks, installed execution, stale-result tests and fresh generated artifacts. Observe unfamiliar users attempting the tasks; record remaining confusion. |
| M4: release a traceable artifact | Verify actual hosted/installed artifacts, support profile, version/source identity, documented limits and rollback | Reproducible build inputs, deployment smoke, release notes and recoverable previous artifact. No invented benchmark or hosted result. |
| M5: expand from observed need | Choose one new workflow, starting with ordinary libraries | A concrete missing capability, its owner and extension tests; new syntax only after ordinary code fails the task. |

### M1 Work Orders

These are planning candidates, not newly accepted semantic laws. Update the
canonical owner when independent evidence settles each rule.

| Decision / owner | Exact comparison | Failure or removal condition |
| --- | --- | --- |
| Portable values, A03/D3 | Exact Int versus checked fixed width; literal/arithmetic/JSON round trips, huge/negative/fractional numbers, Bool distinction, Unicode supplementary characters and source offsets | Any accepted number silently rounds, hosts disagree or display units are confused with source offsets. Narrow unsupported operations explicitly instead of inventing host-specific semantics. |
| Strict data, A09/A12/D3 | Declared fields and supported codec shapes; missing/extra/duplicate keys, multiple errors, explicit normalization, empty/128/129 rows and repeated IDs | Malformed rows disappear during filtering, errors lose original paths, constraints silently coerce, or encoding uses human display. |
| Closed calls and reuse, A05/A08/D1 | Directed subtotal and inferable constant; map/filter/fold/map_error instances; default/capture/effect behavior; two passive consumers plus unknown and changed-dependency cases | Supplied metadata is called inference, client arguments determine a public promise, checking executes user code, or unresolved effects become purity. |
| Host/run experience, A19-A23/D4/D5 | Explicit entry/input/options; source/input/run identity; host read/save failures; bounded input/depth/work/output; stop/restart/draft recovery | New source displays old results as current, inspection runs effects, save falsely claims publication, or worker termination is claimed as language cleanup. |

Prefer exact Int and strict codecs as starting candidates, but do not implement
a numeric tower or general schema system before accepting the bounded rules.
Runner budgets need documented values and a pinned measurement environment
during M1/M2; 128 rows alone is not a resource bound. General callback, resource
and representation comparisons already live in
[function contracts](docs/design/function_contracts.md#bounded-contract-comparison-for-implementation),
[resource completion](docs/design/resource_lifetime.md#remaining-completion-experiments)
and [the paired interface trial](docs/design/interaction_model.md#paired-representation-and-revision-trial).

### First Actual Implementation Slice

After M0/M1 select and accept the calculation's needed rules, make
calculate → edit → wrong argument → repair work through the public runner and
the browser path. Reuse the invoice source and independent expected values.
Keep an explicit capability table for parse/check/lower/run/diagnose/format;
unsupported target constructs must refuse clearly.

Likely owners are `prototype/analysis/`, `prototype/runtime/api.py`,
`prototype/parser/`, `prototype/runtime/js/`, `scripts/cli.py` and
`web/app.js`/`web/editor.js`; choose files from the accepted missing contract,
not an assumption that every layer needs a rewrite. Use the existing module
check report only within its actual scope. Add public-contract evidence when
the reuse slice needs it; it is no longer the first product outcome by default.

Then add the report's decode/repair path and finally local reuse of both.
For each increment, provide expected values/errors, source maps, formatting,
refusal cases and appropriate differential checks. Avoid a long sequence of
disconnected infrastructure milestones before a person can complete a task.

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
No examples, web code or generated assets changed in this planning pass.

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

Continuation reconciliation is bounded maintenance when its hosted path is
relied upon. Compare explicit source-exception transport, explicit continuation
frames and a pre-effect support fence using the same existing oracle. Do not
let Python compatibility absorb the main product work or claim target resource
completion from a host-generator fix.

## What Is Ready And What Remains

Ready for handoff: product promise, selected core, explicit deferrals and
extension boundaries, a narrowed target, screen/storyboard, milestone gates,
first work orders and playground migration policy. The selection is
self-reviewed planning; no independent user study or new implementation exists.

Still required: four bounded contract decisions, executable cross-host evidence,
actual product trials and distribution checks. These are specific evidence
tasks, not a reason to reopen all research or add more planning layers.

Start a fresh session with this instruction:

> Read this plan, canonical first-product synthesis and the checkpoint. Keep
> the playground working, but adapt examples freely. Confirm the selected
> profile and actual baseline, close the calculation's scalar/call rules with
> independent cases, then implement its complete browser/CLI edit-error-repair
> slice. Continue toward the local report and reuse journeys. Consult broader
> research only for a concrete blocker. Do not silently accept proposed APIs,
> change tests to hide failures or restart a general redesign.
