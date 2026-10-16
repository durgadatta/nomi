# Project Roadmap

> Status: current delivery priorities and dependency gates.

This file owns delivery order. [Design](../design/README.md) owns meaning;
[research](../research/README.md) owns evidence and competing models. Current
implementation details belong to [Artifacts And Usage](artifacts_and_usage.md).
Project evolution is isolated in [HISTORY.md](../../HISTORY.md).

## Current Support

The public [playground](https://durgadatta.github.io/nomi/web/) and CLI run the
calculation and bounded JSON report journeys. Browser checks cover repair,
current-result JSON download, cells, diagnostics, cancellation/reset, drafts,
startup recovery and desktop/mobile layouts. The default browser uses WASM/JS;
the optional Pyodide route has a narrower inspection interface.

The report uses two manual schemas and structural outcome maps. General target
nominal data, Option/Result, checked public modules and backend-independent
exact-Int transport remain unfinished. Source analysis is scalar/direct-call
and does not certify generic interfaces. Working compatibility behavior must
stay distinct from accepted target guarantees.

## Portable Values And Libraries

Supported compatibility paths enforce declared numeric capacity rather than
silently rounding integers. Prototype text escape/strip, collection order,
call/default binding, hosted cleanup and source/session result boundaries have
focused fixtures. Complete target scalar transport, derived codecs and shared
semantic checking still require integration. Use supported profiles and tests;
reproduce an actual defect before treating a possible gap as a repair task.

## Delivery Order And Dependencies

1. Keep calculation/report repair and export dependable on CLI and public browser.
2. Complete the target scalar, nominal data, failure/match and closed-call contracts
   used by those same journeys.
3. Establish checked local module reuse with independent consumers and honest
   refusal of unknown dependencies.
4. Verify supported installed/deployed artifacts, formatting, repair/recovery and
   actual usability before expanding the release promise.
5. Extend resources/tasks, domains, representations and engines in bounded slices
   whose semantic dependencies and independent expected results are explicit.

Discovery continues alongside delivery. It can challenge architecture and product
assumptions; it need not wait for every implementation milestone. A research
experiment does not automatically become a release prerequisite.

## Report And Target Delivery Gates

| Boundary | Present state | Next closure |
| --- | --- | --- |
| Compatibility calculation/report | Runnable on declared CLI/browser paths | Preserve literal values, field/path errors, repair, encoding, stale controls and refusal behavior. |
| Portable target scalars | Exact Int/Bool/Text meaning accepted | Admit exact tagged producer/consumer transport, canonical source and common measured limits. |
| Owned data and codecs | Manual report descriptors run | Derive named/default fields, nominal identity, atomic constraints and ordered decode from admitted declarations. |
| Failure and structural choice | Compatibility outcomes and Pattern Surface fragment run | Implement real Option/Result, exhaustive transactional match and nearest-function propagation with cleanup. |
| Checked calls | Bounded scalar facts and ordinary callbacks run | Establish closed data-first report signatures, defaults, captures and pure non-retaining callback evidence. |
| Local reuse | Target contracts specified; general module checking incomplete | Produce source-derived closed interfaces and passive independent consumers with dependency invalidation. |
| Public distribution | GitHub Pages serves main at `/nomi/web/` | Keep CI, generated assets and public-browser checks green on each published revision. |
| Wider resources/tasks | Host compatibility and finite model evidence exist | Actual region/completion/cancellation/join contracts and event-controlled conformance. |

## Research And Engineering Frontier

The reasoning direction compares contextual terms, checked composition and
qualified judgments. Scoped pure source, exact polynomial interpretations,
finite premise support, theory bridges and adaptive inquiry have bounded
independent checks. Next extend premise/vocabulary transport and an established
numeric AD adapter while preserving theory, scope, support and actual authority.
General typed/effectful source, scientific/empirical adequacy and human benefit
remain open.

Data/statistics, DW/DT/ML/DC/MSG and interface HX/NL cases stay under existing
owners. The structured comparison case separates raw differences, alignment,
policy acceptance and coverage; tolerance is not equality. A second engine,
incremental update, stream or learned policy must preserve those distinctions.
Current technical recipes live in [action notes](project_action_notes.md), not
another priority queue.

## Priority And Sizing

P0 protects information and support honesty. P1 closes the next useful language
slice. P2 expands usefulness after prerequisites. P3 covers later industrial
profiles. S/M/L describe the next reviewable increment, not calendar promises or
the cost of completing a whole subsystem.

## Whole-Project Work Map


| ID | Aspect | Priority / next size | Main dependency / owner |
| --- | --- | --- | --- |
| A01 | Product scope and milestone contracts | P1 / S | Target design and D4 |
| A02 | Feature, profile and capability honesty | P0 / S | Existing feature/frontend/backend registries; D0 |
| A03 | Scalars, strings, text and portable numbers | P0 / M | Syntax/semantics; D3 and open question 9 |
| A04 | Grammar, CST and parser frontends | P1 / M | A02/A03; parser registry and pattern packet |
| A05 | Name resolution and typed Surface | P1 / L | A03/A08; progressive typing contracts |
| A06 | Core IR, lowering and reduction | P1 / M | A04/A05; Core verifier and feature ownership |
| A07 | Binding, mutation and constraints | P1 / M | A05/A19; accepted binding semantics |
| A08 | Functions, generics, protocols and callbacks | P1 / L | D1; function-contracts packet |
| A09 | Nominal data and generated behavior | P1 / M | A05/A07/A08; data semantics |
| A10 | Patterns and exhaustiveness | P1 / M | Fragment work can start now; full checking needs A05/A09 |
| A11 | Option, Result, panic and cancellation | P1 / M | A05/A06; failure semantics and D2 |
| A12 | Decode, encode and schema projections | P1 / M | A03/A08/A09/A11; boundary contracts |
| A13 | Effects, grants and host capabilities | P1 / M | A08; effects/industrial contracts |
| A14 | Resources, defer and lifetime escape | P1 / L | A08/A11/A13; resource-lifetime packet |
| A15 | Async tasks, cancellation and backpressure | P1 / L | A11/A13/A14; D2 scheduler contract |
| A16 | Collections, streams, tables and arrays | P2 / M | A03/A08/A12/A15; library-first experiments |
| A17 | Prelude and standard library | P2 / M | A09/A11/A12/A13; industrial stdlib contract |
| A18 | Runtime sessions, caches and process transport | P1 / M | Existing facade; A02/A19 |
| A19 | Results, diagnostics, events and explanation | P0 / S | Existing facade/collector; source mapping in A04/A06 |
| A20 | CLI, REPL, check and formatter | P1 / M | A05/A19; bounded syntax support |
| A21 | Browser playground and interaction | P1 / M | A02/A19; A04/A06 for richer execution |
| A22 | Jupyter and notebook experience | P2 / S | A18/A19; current messaging/session contracts |
| A23 | VS Code and language-server path | P1 / M | Harness work now; semantic tooling needs A05/A19 |
| A24 | Tests, differential conformance and fuzzing | P0 / S | Existing test review; capability evidence |
| A25 | Performance and resource budgets | P2 / M | A24; current measured baseline |
| A26 | Modules, packages and reproducible builds | P2 / L | A05/A08/A13; industrial package contract |
| A27 | FFI, execution profiles and future backends | P3 / M | A03/A06/A13/A24; measured engine gate |
| A28 | Distribution, CI, release and Pages | P1 / M | A21/A24; supported revision and owner release choices |
| A29 | Docker and portable notebook delivery | P2 / S | A28/A30; current launcher/container contract |
| A30 | Security, redaction and execution isolation | P0 / S | Concrete token/context fixes now; A13/A18 later |
| A31 | Documentation, research and learning | P1 / S | Existing authority map and bounded experiments |
| A32 | Agent workflows, retrieval and maintenance | P2 / S | Existing doctor/hooks/skills; A31 |
| A33 | Dedicated DSL and string research | P1 / L | Scoped DSL/text contracts; A03/A08/A12/A13 |


## Validation And Progress Reporting

Choose checks appropriate to the changed contract:

```bash
python3 -m tools.design_passes check
python3 scripts/check_doc_links.py
python3 .codex/scripts/agent_doctor.py
python3 scripts/check_web_runtime.py
python3 scripts/check_web_browser.py --legacy-pyodide
python3 scripts/check_web_browser.py --url https://durgadatta.github.io/nomi/web/
python3 -m tools.jupyter.check_nomi_kernel
pytest -n 4
```

Use values, source diagnostics, authority/completion traces, independent replay,
actual host behavior and measured cost as evidence. A test count or document
inventory is not a percentage of language completion. Update present support,
gaps and exact next action in place; keep narrative chronology in HISTORY.md.
