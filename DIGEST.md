# Nomi: Repository Digest

> Status: repository snapshot, 2026-10-16. A compact orientation story, not a
> specification, release declaration or independent roadmap.

Nomi is an early language-design project with runnable prototypes. Its purpose
is to make computational work easier to create, understand, revise and share:
start with a readable script, then add dependable boundaries as it grows. The
ambition includes scientific models, learning and alternative representations.
A few understandable mechanisms should compose into richer activities while
keeping meaning, assumptions and authority visible.

The repository contains three different kinds of progress: **working prototype
behavior**, **accepted target-language contracts**, and **research hypotheses
with bounded experiments**. They overlap but are not interchangeable.
Compatibility features can run while being rejected from the target; an accepted
design can still lack an implementation. Nomi is versioned `0.1.0`, marked
pre-alpha, and has no source-compatibility promise yet.

## The Core Being Preserved

The target favors local reasoning. Ordinary evaluation is eager, lexical,
left to right and once per argument. Bindings are immutable by default;
`var` and `set` expose mutation. Functions use `func` or explicit anonymous
parameters; `|>` only inserts a first argument. Equation definitions,
placeholder lambdas and implicit partial application are excluded from the target.

Owned concepts use immutable nominal `data`; received JSON, rows and host values
remain structural until explicit decoding succeeds. Binding and construction
check constraints atomically. Exhaustive `match` performs inert structural
choice with tentative captures; guards, constraints and external decode failures
have distinct roles. `Option`, expected `Result` failures, panic and cancellation
also remain distinct. Public contracts may be inferred locally or declared;
exploration can retain honest unknowns, but unknowns cannot serve as proofs.

Effects describe possible world interaction; actual capability handles grant
authority. Resource scopes own cleanup, and structured tasks own child lifetime
with explicit suspension. Exact mathematical Int, distinct Bool and Unicode
scalar-value Text are accepted initial scalar laws; limited backend capacity
must refuse rather than change successful meaning. Source provenance and
structured diagnostics survive reductions. Detailed effect typing, resource
completion and broader numeric contracts remain open. [Syntax](docs/design/syntax.md),
[semantics](docs/design/semantics.md) and the
[decision ledger](docs/design/decisions.md) own these distinctions.

## What Actually Runs

The first product boundary is **small calculations, trustworthy local JSON
reports, and eventually checked local reuse**. Calculations and a bounded
report/repair/export journey already run as compatibility prototypes. The report
uses two manual schemas and structural outcome maps, not the complete target
nominal-data/Result system. Limited scalar/direct-function analysis can report
facts and enforce selected `known-types` or `pure` requirements; general checked
module interfaces are still work ahead.

| Surface | Current implementation and limit |
| --- | --- |
| CLI and Jupyter | Python 3.12+ host, Lark parsing, transitional Python AST and layered `python`/`nomi`/`reduced` interpreters. These are implementation modes, not language strictness levels. |
| Runtime architecture | `prototype.runtime` exposes execution, inspection and sessions. Nomi-owned Surface/Core artifacts, verification, registries and alternate backend paths exist; complete target execution is unfinished. |
| Browser playground | Rust/WASM parser feeding a JavaScript runtime, with examples, cells, diagnostics and report download. An optional legacy route uses Pyodide. Their supported subsets and limits differ. |
| Editor and containers | A local VS Code extension provides highlighting/run support and bounded navigation; notebook and Docker helpers exist. A mature shared language service, debugging and portable deployment remain incomplete. |

Parser/runtime substrates are replaceable; a Rust parser is not a native Nomi
compiler. Capability metadata, asset freshness and artifact parity bound support.
The [public playground](https://durgadatta.github.io/nomi/web/) serves main and
passes the same calculation/report, inspection, recovery and mobile browser
checks as the local checkout.

From the repository root:

```bash
python3 -m pip install -e .
python3 scripts/cli.py samples/calculate.nomi --output program
python3 scripts/launch_web.py --no-wasm
```

The calculation prints `3850`. The browser editor still uses CDN assets.
[Getting started](docs/guide/getting_started.md) explains the report journey;
[current support](docs/guide/status.md) names prototype/target differences and
host limits. Runnable product examples live in `samples/`; aspirational
programs stay under `docs/design/targets/`.

## Research Has Its Own Executable Frontier

Comparative research spans language semantics, notation/DSLs, data/workflows,
cognition and industrial contracts. It asks whether programming, domain models
and intelligent work can share naming, composition, inspection and revision
while retaining different laws. **Contextual terms, checked composition and
qualified judgments** are the current foundational candidate, not an accepted
replacement Core or universal knowledge graph.

Python checkout laboratories already exercise engine-free object/document
descriptions, schema-only statistical plans, exact polynomial maps, scoped
binders, premise support and finite theory interpretations. Other tools capture
bounded pure Nomi functions, construct example-fitting programs, form prediction
kernels and choose finite questions. Observation journals retain endorsements,
withdrawals and model-relative support. Selected paths have independent replay;
optional SymPy checks are pinned to `1.14.0`.

For an accessible example, run `python3 -m tools.intelligence_loop --observe 4`.
The lab distinguishes `x` from `x*x` using supplied observations. It does not
measure the world, prove an induced program universally correct or establish
general intelligence. The [reasoning guide](docs/guide/reasoning_lab.md) tells
the complete example; the [artifact map](docs/orientation/artifacts_and_usage.md)
names each tool and its evidence limits.

Scientific validity, broad inference, general effectful/recursive source capture,
richer theory/evidence transport and numerical AD remain open. Text-primary,
structured and mixed authoring still compete. Comprehension, accessibility,
reliance and handoff have prepared comparisons and finite probes; human benefit
still needs observation.

## Open Gaps And The Next Boundary

The current composition proposal connects binding, carrier operations,
descriptions and evidence through shared mechanisms with explicit policies.
A data-comparison showcase is prepared: raw change, key identity, tolerance and
coverage stay distinct. Accepting `200 -> 250` under a tolerance does not make
the numbers equal. Portable, incremental, streaming and learned extensions have
counterexamples and admission limits. See the
[synthesis](docs/design/synthesis.md#composition-while-preserving-the-core) and
[comparison case](docs/research/data_workflows/nomi_candidates.md#structured-data-comparison-showcase).

Delivery now needs the intended calculation/report semantics to work together:
portable exact scalar transport, nominal construction and derived decode,
real Option/Result and transactional match, checked closed callbacks, then
source-derived local module reuse. Compatibility success does not close these
gates. Distribution additionally needs clean installed-host evidence and a
verified published artifact. Broader resources/tasks, packages, FFI and domain
engines retain their own prerequisites.

Discovery continues alongside delivery and may challenge the architecture.
The research continuation includes richer premise/vocabulary transport and
independent numeric adapters; it does not make every research topic a release
requirement. The five registered packets are pattern matching (`implementing`)
and functions, resource lifetime, cognitive interfaces and language coherence
(`designing`). Their registry routes work; the
[roadmap](docs/orientation/project_roadmap.md) owns delivery order.

## How To Read And Trust The Repository

| Artifact | What it contributes |
| --- | --- |
| [Vision](docs/design/vision.md) | Purpose, whole human activity, competing directions and the gap to the ambition. |
| [Target design](docs/design/README.md) and [industrial model](docs/design/industrial.md) | Intended language, package/effect/security/tooling contracts; acceptance does not imply implementation. |
| [Research guide](docs/research/synthesis_guide.md) and [open questions](docs/research/open_questions.md) | Evidence, alternatives, counterexamples and bounded next discriminators. |
| [Implementation map](docs/orientation/artifacts_and_usage.md) and [development guide](docs/orientation/development.md) | Runtime paths, tool ownership, setup and checks. |
| [Design-pass registry](config/design_passes.json) and [workflow](docs/orientation/design_pass_workflow.md) | Linked research/design/target/bridge packets, status, validation commands and continuation. |
| [Agent map](AGENTS.md) and [AI collaboration](docs/orientation/ai_collaboration.md) | Repo-local skills, advisory hooks and cited RAG/MCP discovery; retrieved material must be read and reconciled with current authority. |
| [Documentation index](docs/README.md) | Complete routes through guides, design, research, implementation and current bridges. |

Tests describe supported prototype behavior; canonical design owns intended
meaning, and current user decisions can revise it. Current bridges record
implementation evidence and gaps; project evolution
belongs only in [HISTORY.md](HISTORY.md). `local/` and `PLAY/` are scratch/reference
areas; generated caches, reports and build products are not project authority.

Verification separates implementation tests, documentation/packet integrity,
generated-asset freshness and actual-host behavior. Current checks are
reproducible commands, not release certification or a
percentage of progress. The [roadmap](docs/orientation/project_roadmap.md) and
[development guide](docs/orientation/development.md) name those gates.

Update this digest when the accepted design, supported paths, research frontier
or next product boundary changes. Keep detailed laws and current evidence in
their linked owners so this remains a short, self-contained map of the story.
