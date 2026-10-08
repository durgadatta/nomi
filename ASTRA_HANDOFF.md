# Nomi Frontier Handoff

> Status: temporary, user-requested handoff for the next GPT 6 Astra pass.
> Prepared 2026-10-08 from `8b82d8a` and its linked delivery receipts.
> Expanded 2026-10-08 with the user's broader ecosystem, optional-restriction
> and independently optimized-backend direction below.
> This document selects investigations; it is not language authority, a new
> backlog, target acceptance, implementation evidence or release permission.

## Mission

Push Nomi toward a coherent language and useful product, not a larger collection
of features. Build a coherent, learnable semantic foundation for readable scripts,
checked libraries, data work, effects, failure, resources and rich tools together.
Challenge the current design seriously: rejecting a recommendation, deleting an
abstraction or replacing a bounded mechanism can be the most valuable outcome.

The ambition is substantially larger than repairing the prototype or completing
D1. Synthesize the experience of using computers into a coherent computational
medium: a friendly language, extensible domain layers, useful representations,
inspectable execution and independently improving engines. Pursue that vision
through sustained design/implementation/review iterations. Bounded evidence units
are checkpoints, not a ceiling on the project or a reason to avoid bold redesign.

The completed preparation pass was documentation-only. The next user-authorized
design/implementation pass should produce decisions and executable evidence,
not repeat the global bibliography or implement every unchecked note. The user's
choice of Astra does not change repository permissions or configure any model.

Preserve local reasoning under growth. Python AST, Lark, Rust/WASM, JavaScript,
Pyodide and Core IR are replaceable laboratory substrates, not language laws.
Use [the exploratory doctrine](docs/orientation/exploratory_implementation_doctrine.md)
to keep experiments inspectable and reversible. Larger rewrites are legitimate
when a failed required program demonstrates their need; compare them against a
narrow repair and bounded extraction on the same independent oracles.

Quick route: [user north star](#user-north-star),
[optional restrictions](#freedom-restrictions-and-strict-execution),
[progressive intent](#intent-implicit-first-explicit-as-needed),
[independent engines](#experience-and-engine-independence),
[frontier experiments](#ambition-to-falsifiable-experiments),
[logical conclusion](#what-logical-conclusion-means),
[baseline](#baseline-and-evidence), [first session](#first-session),
[semantic frontier](#lane-one-close-a-semantic-frontier),
[continuation engineering](#lane-two-continuation-engineering),
[domain extension](#extend-without-flattening-domains),
[verification](#verification-and-product-gates),
[next-pass request](#suggested-next-pass-request).

## User North Star

This section records the latest user direction, not an already accepted or
implemented replacement specification. Use it to reopen inadequate assumptions
in existing owners. Do not reduce its ambition to the current prototype's reach.

Nomi already has an executable playground, extensive research, many proposals
and unfinished implementation work. Treat that accumulated experience as material
to synthesize, not as proof the present core, architecture or product is correct.
Audit actual implementation defects as well as design gaps; fix or deliberately
fence them without treating compatibility as the ultimate destination.

The intended ecosystem should absorb, connect and improve experience from shell
scripting, command lines, web programming, spreadsheets/Excel, visual design,
architecture, design patterns, styling, Markdown/HTML, configuration, templates,
notebooks, automation and everyday computer use, alongside data, AI/ML, databases,
scientific work, messaging and the broader human-knowledge domains already studied.
Users should not need to reconstruct incompatible mini-frameworks for each one.
Interoperability with existing tools is part of the ambition, not a concession.

Include ordinary interaction granularity: files and folders, search, clipboard,
keyboard commands/macros, undo/history, repeated actions and repair after failure.
These should compose with programmatic workflows without assuming that gestures,
copied text or a conversational request automatically authorize their effects.

Organize the proposed growth around these responsibilities, not necessarily six
runtime packages or a single mandatory processing pipeline:

| Responsibility | What should compose | What should not be flattened |
| --- | --- | --- |
| Coherent semantic core | Values, identity, naming/binding, calls, composition, change, outcomes, dependencies, effects, authority and observation | An eager call, inert plan, solver relation, reactive dependency and event subscription are different contracts |
| Reusable semantic building blocks | Collections, protocols, constraints, resources, tasks, streams, modules and inspectable reductions | Every object need not support every operation; laws and capability requirements remain conditional |
| Domain libraries and scoped languages | Data plans, shell commands, web/service models, tables, documents, layout/style and workflows | Domain-specific order, escaping, transaction, convergence, timing and persistence guarantees retain owners |
| Human representations and tools | Text, tables, diagrams, forms, command palettes, rendered documents, traces and conversational assistance | A projection or proposed edit is not independent execution authority or automatic inverse editing |
| Restriction and deployment policies | Gradual checking, effect/lifetime restrictions, reproducibility, closed builds and supported host capabilities | Restriction strength, engine selection, runtime permissions and semantic edition are independent dimensions |
| Execution engines | Interpreted, browser, bytecode, native/AOT and specialized candidates | Engine implementation choices must not redefine source meaning or force their machinery into common code |

Reuse foundations wherever that genuinely reduces concepts. Add a missing core
primitive when multiple domains expose the same irreducible semantic gap; compare
it against ordinary calls, protocols and scoped notation before admission. Do not
simulate coherence by putting all domains into one universal DAG, ontology, object
hierarchy, truth algebra or framework. Shared contracts and interoperable artifacts
can unify an ecosystem without universalizing every payload.

Keep the [interaction proposal's representation fork](docs/design/interaction_model.md#thesis-and-a-real-fork)
open: text-primary with useful projections versus structured-document primary
with equally usable text. The existing editor is evidence, not a requirement
that every domain fit bare strings or that every view support inverse editing.

Prefer readable, discoverable and repairable programs over clever compression.
A slower but humane Python-like experience is preferable to a fast design that
requires ugly everyday syntax. Rust-like execution performance is an engineering
aspiration, not an existing result or a promise for arbitrary dynamic programs.
The goal is both: make the experience pleasant now and preserve a credible path
to highly efficient implementations without redesigning users' ordinary programs.

## Freedom, Restrictions And Strict Execution

The user wants a low-friction starting point: write useful programs freely,
without Java-like upfront ceremony, then impose increasingly strong restrictions
when useful, up to rigorous Haskell-/Java-like contracts and a fully strict build
or execution policy. Those comparisons express desired freedom/control, not a
requirement to inherit those languages' syntax, object model or evaluation strategy.

**Explicit design tension:** the current [target typing rules](docs/design/semantics.md#values-and-types),
[public-interface rules](docs/design/industrial.md#modules-and-api-evolution)
and [ledger](docs/design/decisions.md#accepted-foundations) require complete public
types/effects and reject implicit `Any`. The latest direction reopens how much
of that is mandatory, where it applies and whether exploratory/public dynamic
boundaries can be usable without source boilerplate. Do not present the existing
rules as having already fulfilled this request, or quietly replace them in code.
Compare candidates and reconcile the chosen contract in the canonical owners.

Think of the entry experience as an evolved Python or TypeScript, learning from
their successes and limitations and the wider research, not adopting every
existing behavior. Users should be able to grow that same program toward
Rust-/Java-level production rigor and ambitious execution performance through
compiler-enforced policies. Do not make them switch to a different language or
manually expose backend machinery to reach the higher tiers.

Also challenge mandatory mutation/binding notation and other source restrictions
where they obstruct the intended exploratory workflow. For example, compare
simple reassignment with explicit create-versus-change under closures and notebook
re-execution; do not assume either Python behavior or current `var`/`set` wins.
Separate optional source ceremony from the stable binding/transition law it must
still express, and name any true semantic conflict rather than hide it in a mode.

Investigate a progression such as the following; these names are descriptive
stages, not new flags, modes or accepted syntax:

| Stage | User experience | Required explanation |
| --- | --- | --- |
| Explore | Unannotated scripts, cells and functions run with ordinary dynamic feedback | Runtime types, actual effects and unknown static facts remain inspectable; unchecked does not mean fabricated proof |
| Describe | Add chosen types, field constraints, units, schemas and examples locally | Explain what is enforced at runtime, inferred statically, merely tested or still unknown |
| Restrict | Require selected purity/effects, mutation/aliasing, lifetime, exhaustiveness, determinism or dependency policies | State the exact scope, evidence and consequences; do not require every unrelated restriction |
| Close | Publish or deploy a checked boundary, possibly enclosing exploratory components behind adapters | Separate checking, dynamic-boundary checks, authority and versioned interfaces compose across packages |
| Execute/Build Strictly | Demand sufficient closed evidence for the selected production/compiler/host policy | Report unfulfilled obligations and reject, adapt or use an explicitly allowed fallback; optimizers consume evidence independently of assurance strength |

Compare inferred-but-checked exploration against genuinely dynamic exploration
with checked boundaries. Test omitted annotations, heterogeneous values, imported
dynamic APIs and evolving notebook definitions; do not let the proposed starting
mode secretly require a complete static proof. Give users incremental diagnostics
and fixes, not an all-or-nothing rewrite into a second language.

Restrictions need not form one total ladder. A user might demand pure callbacks
but permit dynamic types, or require a schema but permit effects. Explore scoped
policies at expression/function/module/package/build boundaries, with explicit
inheritance, composition, exported evidence and local overrides. Compare that
cost against a smaller set of comprehensible presets. Avoid combinatorial modes
whose interaction requires a new language manual for each combination.

Separate three ideas: choosing to declare a restriction, choosing static versus
runtime enforcement, and disabling an already promised check. Optimization may
erase a redundant check only with adequate evidence; it must not quietly stop
enforcing a user contract. Arbitrary user predicates may remain runtime-only,
unknown or outside a strict compiler profile; user intent is not a universal
decision procedure or authorization to assume an unproved property.

Optional restrictions must not silently change evaluation order, values, default
timing, cleanup, external authority or failure meaning. For programs satisfying
the same declared contracts, compare all relevant observables across policies.
An intentionally different numeric, unsafe or deployment semantics needs a named
contract, not a hidden strict-mode switch. Relaxed checking does not create
capabilities or bypass host-enforced limits. If the intended freedom actually
requires semantic differences, expose that fork honestly instead of asserting
that every progression is automatically meaning-preserving.

## Intent: Implicit First, Explicit As Needed

The language should take the user's intent and direction from ordinary code and
context early, then let them express it explicitly as precision, guarantees or
performance matter. Types are one form of direction, not the whole system.
Inference should reduce initial ceremony; explicit intent should strengthen and
clarify the existing program rather than force a parallel implementation.

| Direction | Early low-ceremony candidate | Later explicit candidate |
| --- | --- | --- |
| Shape and meaning | Infer usable types/shapes from definitions, literals and operations where justified | Public types, nominal/domain models, schema, units and refinements |
| Effects and mutation | Infer actual calls, captures and local state transitions; show unresolved dependencies | Pure/effect contracts, mutation/aliasing policies and capability requirements |
| Lifetime and time | Track lexical use and visible suspension/dependencies where analysis supports it | Resource/region, task ownership, stream demand, observation and cleanup policies |
| Architectural intent | Discover a computation, plan, adapter or component's actual relationships | Protocols, module boundaries, dependency rules and versioned domain descriptions |
| Correctness and evidence | Use examples/checks and observed failures as evidence, not universal proofs | Invariants, pre/postconditions, laws and declared proof/runtime-check obligations |
| Deployment and performance | Run with a friendly managed profile and report measured costs | Strict compiler policy, target capabilities, reproducibility and explicitly scoped budgets or specialization directions |

These are candidate sources of intent, not syntax or inference features already
implemented. Separate inferred facts supported by analysis, declared promises,
runtime enforcement, observed examples and heuristic suggestions. A compiler may
specialize using soundly established facts without making the user restate them;
patterns, variable names, tests or conversational hints alone do not prove a law.
Model-assisted suggestions must not make program meaning depend on a model's
guess, invent external authority or silently commit a proposed change.

When intent is genuinely ambiguous, preserve ordinary meaning and expose the
unknown or request a targeted clarification rather than guessing a new evaluator.
An exploratory run may proceed with defined runtime checks and honest unknown
static facts. A strict policy must explain the exact blocking obligation, related
source/dependency and the smallest explicit direction or boundary that resolves
it. Compiler inference is allowed to eliminate ceremony; unknown evidence must
not be relabelled inferred simply to admit a strict build.

Make tier transitions ergonomic in text, CLI and the playground: explain current
guarantees, preview the additional obligations, show local fixes and preserve the
working source. Compare source annotations, ordinary declarations, module/project
policy and structured-tool projections for expressing direction. Keep one owned
contract rather than inconsistent tool-only flags. Allow tightening one useful
dimension at a time and undoing policy/source changes without undoing unrelated
work. No particular tier UI or compiler flag is accepted by this handoff.

Production readiness is broader than a compiler accepting the file: supported
dependencies/hosts, boundary checks, lifecycle, diagnostics, observability,
packaging and actual operational evidence still matter. Strict assurance and
speed are independent: checked code can be slow, and optimized dynamic code can
retain runtime checks. Aim to make them reinforce each other, not advertise that
a mode switch proves reliability or guarantees optimal speed for every program.

## Experience And Engine Independence

Keep the user-facing language, tools and policy distinct from execution strategy.
Build on [existing engine boundaries](docs/orientation/implementation_layers.md)
without treating their current artifact shapes as permanent. Define versioned
interfaces for source identity, resolved/type/restriction facts, normal forms,
runtime values, outcomes, capabilities, sessions and diagnostics. Establish a
small executable producer/consumer contract before a broad architectural split.

Make frontends independently replaceable too: text and structured producers must
negotiate artifact versions, preserve source/referent identity and invalid-draft
recovery, and agree with downstream consumers on the supported semantic slice.
A faster parser or richer editor must not dictate backend selection or change
the meaning of the same accepted program.

Demand strong internal engineering too: memory-safe implementations, exhaustive
state/outcome representations, explicit ownership at host boundaries, bounded
resources and auditable transitions. Internal rigor should support freedom at
the surface, not require ordinary users to manage backend memory or prove every
property. Do not trade implementation safety for benchmark numbers.

Ask whether one program can be interpreted immediately, checked progressively,
then specialized/compiled behind the same source-level contracts. Make partial
optimization useful: checked hot paths can coexist with dynamic orchestration
where boundary checks and fallback are explicit. Compare AOT, JIT, bytecode,
specialization, bulk/vectorized domain operations and other engines only where
their measured workload warrants them; Rust is a candidate substrate, not a
source-language requirement or automatic speed guarantee.

Compiler-friendly restrictions can supply type/layout, effect, aliasing, escape,
dispatch, dependency and numeric-law evidence. Track the provenance/scope of
each assumption and reject invalid or stale evidence. Code from an unchecked
dependency cannot inherit caller guarantees merely because the build is strict.
If speculative specialization or fallback is used, preserve completed effects,
resource ownership and once-only evaluation; restarting from an earlier phase
must not duplicate real work. Strict policies must say whether fallback is allowed.

Use independent semantic fixtures for engine equivalence, not the current
interpreter as an unquestioned oracle. Preserve source-linked debugging, useful
diagnostics, redaction, cancellation/cleanup and meaningful traces under optimized
execution; an optimization may change instrumentation availability only under
an explicit inspection contract. Runtime internals may become sophisticated;
do not export allocation, ownership or scheduling ceremony into ordinary code
merely because the backend would be easier to implement that way.

Measure startup, interactive feedback, steady-state throughput, tail latency,
allocation/peak memory, boundary/transport cost and inspection overhead. Use
scripts, tabular pipelines, service/CLI work and composed workloads, cold and
warm. Compare implementations doing the same job under stated contracts; a fast
arithmetic loop is not evidence of Rust-like ecosystem performance. Record the
case where a proposed speedup harms explanation or edit/run usability and reject
it when the experience cost outweighs the benefit.

## Ambition To Falsifiable Experiments

Start with a broad experience-to-semantics synthesis, then execute a portfolio
of discriminating experiments rather than another survey. Extend the existing
packets and A/D owners; this table is a challenge set, not a second work queue.

| Experiment | Pressure program | What would falsify the approach |
| --- | --- | --- |
| Freedom-to-strictness continuity | Grow one unannotated script/cell workflow into a checked reusable module and strict compiled component, retaining recognizable code | Strictness requires unrelated ceremony, changes successful behavior, assumes missing evidence or conceals a dynamic boundary |
| Independent restriction composition | Apply type, effect, mutation, lifetime and deterministic-build restrictions separately and together | A policy silently grants authority, changes an unrelated policy or cannot explain a conflict locally |
| Strict-build admission | Introduce a dynamic dependency, unresolved callback, unchecked FFI edge and effectful initializer; compare project policy with explicit run/build overrides | Strict execution begins external work before required admission, silently trusts unknown evidence or lets an override bypass a promised boundary |
| Dynamic/checked interoperability | Move heterogeneous data, mutable captures and host callbacks through exploratory and checked modules, comparing runtime contracts and refusal policies | A boundary loses obligations, assigns misleading blame, invents proof or makes source-level explicit `Any` the only unexamined route |
| Implicit-to-explicit intent | Run the evolved Python/TypeScript-like workflow with inferred facts, then add types, effects, invariants and project policy incrementally | Explicit direction requires a new language, overrides successful ordinary meaning, creates unsupported proof or causes nonlocal annotation cascades without an explanation |
| Engine substitution | Execute the same closed slice through the reference and an independently optimized candidate, including failure-heavy cases | Value/order/cause/cleanup differences, lost source explanations or backend-specific source machinery |
| Frontend substitution | Use independent text/structured producers with version changes, unknown extensions and malformed/recovered drafts | Source identity or comments disappear, consumers guess unsupported versions, or recovery guesses become executable meaning |
| Shell-to-service composition | Start with a file/process pipeline, then expose a web/CLI job with events, config/templates, failures and deployment policy | Strings become hidden execution, quoting/grants leak across stages or framework adapters invent incompatible failure/lifetime rules |
| Spreadsheet-to-data/ML composition | Edit a table, inspect dependencies/time, validate rows, construct a learning description and publish a result | Cell coordinates masquerade as durable identity, edits replay effects, graph reuse erases domain laws or confidence substitutes for evidence |
| Document/design-to-application composition | Connect Markdown/HTML, styling/layout, structured form data, revisions and reviewable changes | Rendering changes meaning or authority, an inverse edit loses source/comments, or presentation becomes an alternate truth/execution model |
| Architecture/pattern compression | Express strategy, observer/pub-sub, state transitions, resource scopes and workflow composition using the shared mechanisms | Every pattern needs a new core keyword, or a generic abstraction hides invocation, retention, order, state or failure facts |
| Domain admission without evaluator surgery | Add a genuinely new domain package/scoped tool through published extension contracts | Each domain requires global engine branches, incompatible identities or a privileged escape from shared diagnostics/security |

These are proposed programs/experiments, not current supported examples. Retain
beginner, ordinary production and adversarial/failure-heavy variants. Review
annotation burden, concept count, explanation quality and repair steps as well
as correctness/performance. Automated measurements are not human usability proof.

## What Logical Conclusion Means

Do not stop after the two existing continuation repairs or a polished roadmap.
Drive repeated synthesis, candidate comparison, implementation, independent
review, correction and verification until the chosen milestone is coherent from
user intent to installed/hosted execution. Carry the wider vision forward even
when only one vertical contract can be implemented in a given checkpoint.

The frontier pass should aim to leave:

- A reconciled product/language thesis and an explicit accounting of what belongs
  in core, reusable composition, domain libraries, scoped languages, projections,
  policy and engines; every inclusion earns its cognitive/semantic cost.
- A defensible freedom-to-strictness design, including its conflicts with current
  target assumptions, implicit-to-explicit intent, dynamic/checked package
  boundaries, ergonomic tier transitions and strict-build meaning.
- A credible experience/engine separation demonstrated by a versioned executable
  slice, plus measured optimization evidence where feasible, not a directory-only
  reorganization or a promise that rewriting in Rust solves performance.
- At least one complete, useful composed workflow in the CLI/playground, expanded
  into additional domain slices as their contracts close; no fictional research
  APIs presented as implemented functionality.
- A disposition for consequential research and implementation gaps: adopted,
  rejected, bounded experimental, repairable or deferred with a real trigger.
  Research should change mechanisms, not merely become more navigation links.
- Consistent source, typing/restriction, lowering, runtime, diagnostic, tool,
  packaging and conformance owners, with explicit migration/rollback evidence.
- Honest onboarding, supported profiles, performance/host evidence, remaining
  release gates and the next precise checkpoint for sustained development.

No finite pass completes all human knowledge or proves every optimization. A
logical conclusion is a coherent, extensible foundation and demonstrated growth
path, with unresolved obligations visible and removable. Seek the strongest
feasible progress, not exhaustive feature accumulation or premature claims of
completion. Plan boldly, implement deeply, revise honestly and keep going through
the useful iterations authorized by the user.

## Start Here

Read this route, then only the packet and code required for the chosen slice:

1. [AGENTS.md](AGENTS.md), [README](README.md), [docs authority](docs/README.md)
   and `opencode.json`; inspect the worktree before editing.
2. [Target design](docs/design/README.md), [syntax](docs/design/syntax.md),
   [semantics](docs/design/semantics.md), [industrial contracts](docs/design/industrial.md)
   and [decision ledger](docs/design/decisions.md).
3. [Synthesis](docs/design/synthesis.md), [D0-D7 agenda](docs/design/redesign_agenda.md),
   [active target suite](docs/design/targets/README.md) and
   [overall program](docs/design/targets/overall.nomi). `docs/design/target.nomi`
   is superseded, even where older entrypoints still mention it.
4. [Latest runtime receipt](docs/orientation/project_roadmap.md#scoped-runtime-continuation-receipt),
   [roadmap queue](docs/orientation/project_roadmap.md#first-reviewable-work-queue)
   and [detailed A01-A33 notes](docs/orientation/project_action_notes.md).
5. [Registered packets](config/design_passes.json),
   [packet workflow](docs/orientation/design_pass_workflow.md),
   [convergences](docs/research/convergences.md) and
   [bounded open questions](docs/research/open_questions.md).

Use [.agents/skills/nomi-language-design](.agents/skills/nomi-language-design/SKILL.md)
for semantic work and [nomi-ai-native](.agents/skills/nomi-ai-native/SKILL.md)
for handoff/process changes. Before implementation, read the applicable
`nomi-interp`, `nomi-parse`, `nomi-rust-parser`, `nomi-reduce`, `nomi-test` or
`nomi-web` skill rather than infer the local workflow. Local RAG is source
discovery, not authority; reconcile every useful hit with the active owner.

Do not restore the old corpus at `08f2aad` as parallel authority. Retrieve a
historical detail only when a selected open question needs it.

## Baseline And Evidence

| Checkpoint | What it establishes | What it does not establish |
| --- | --- | --- |
| `8b82d8a` | Comprehensive notes, A01-A33 decomposition, domain recipes, eleven research units, rewrite/evidence gates; repaired Q02-Q04 queue entries distinguished from residuals | Execution of proposed tasks or acceptance of any new contract |
| `3184ef3` | Detailed research-gap and bounded experiment contracts | Execution of new comparisons, foreign adapters or human studies |
| `f8209ea` | Once-only native displayed values and historical binding-name maps | Deep-owned snapshots of mutable values/handles; Pyodide displayed-value support |
| `e949551` / receipt `000ad54` | Hosted hook binding, synchronous scope/try cleanup and child-before-parent normal resumption | General operand/phase continuations, failed-child unwind, close/throw, async cleanup or D2 conformance |

The last runtime receipt reports **2,931 passed / 81 skipped**, **1,177 web/runtime
passed / 1 skipped**, actual default/Pyodide Chromium workflows and native-hosted
completion comparisons. These are historical October 4 local observations, not
checks run for this handoff or proof against a future revision. Local tools were
Python 3.14.0rc3, Node 25.9.0 and Cargo 1.95.0; refresh actual versions.

The notes preparation reran 127 documentation/packet/target-fixture checks,
validated all five packet structures and checked 253 local links/anchors.
Documentation checks do not parse/typecheck the whole target. The four affected
design packets remain `designing`; pattern matching remains `implementing`.

Current behavior to retain or label explicitly:

- The default browser is Rust/WASM parsing, structured JS lowering and the JS
  Core runtime. Legacy Pyodide is a separate bootstrap/execution path.
- Hosted ordinary calls/defaults and synchronous context hooks have bounded
  repairs. Portable lowering refuses named/unpacked calls and hosted scope
  intrinsics before effects; richer hosted support is not portable support.
- JS rejects integers outside +/-9007199254740991; Python admits wider integers.
  This repair is not the final scalar/wire contract.
- Browser text length, iteration, indexing and slicing use code points, not
  graphemes. Browser slices work; Python-AST-to-Core slice lowering remains fenced.
- Native session results retain values and historical names without rerunning
  effects; contained mutable values/handles remain references. Pyodide is output-only.
- Worker termination is a host stop, not proof of language cancellation or cleanup.
- Root licensing, actual minimum-version/hosted CI, exact Pages revision,
  container/digest evidence and human accessibility studies remain distinct gates.

## First Session

1. Record `git status --short`, `git log -8 --oneline`, actual tool versions and
   any user changes. Never revert unrelated work. Refresh the baseline if HEAD
   moved after this handoff.
2. Validate packet structure and generated freshness using the startup commands
   below. Check capabilities/dispositions; refresh D0's census rather than assume
   its historical count of three unreviewed directions still holds.
3. Map the updated north star onto the existing agenda/owners, explicitly reopening
   the freedom/public-contract tension. Then select a primary semantic question
   and bounded engineering discriminator for the first checkpoint. D1 and the
   continuation failures are high-leverage starting points, not the whole mission
   or a veto over the latest user direction. State deliverables and stop gates.
4. Delegate independent review/oracle preparation on disjoint files. Give each
   reviewer its exact contract, evidence limits and no-edit boundary as needed.
   A second implementation sharing assumptions is not an independent oracle.
5. Write candidate judgments/traces before choosing or repairing a producer.
   Implement only after identifying the accepted contract or compatibility lane.
   Leave the existing owner with the exact next step if evidence is insufficient.

```bash
python3 -m tools.design_passes list
python3 -m tools.design_passes show function-contracts
python3 -m tools.design_passes check
python3 scripts/make_web.py --check
scripts/build_wasm.sh --check
python3 .codex/scripts/agent_doctor.py
```

Freshness failure is a finding to explain, not permission to regenerate files
indiscriminately. The two lanes below can proceed independently. Accepted
pattern-fragment migration, source mapping and harness maintenance may also
advance where their own prerequisites are ready; D1-D7 do not freeze all work.

## Lane One: Close A Semantic Frontier

### D1: Callable Contracts

Use the [function packet](docs/design/function_contracts.md),
[callback target](docs/design/function_contracts_target.nomi) and
[current-to-target bridge](docs/review/2026-09-30-function-contracts.md).
The agenda makes D1 the next gate; synthesis starts its admission route with
cleanup. Resolve callback/resource metadata together in paper derivations, then
carry unclosed region/completion obligations into D2. Do not create a circular
requirement to implement every resource/task facility before comparing callbacks.

Type ordered map/fold, derived decode and `run_scope` together under:

- Pure-only strict callbacks versus effect-polymorphic strict callbacks. The
  pure-only recommendation is not accepted or a functional-paradigm mandate.
- Explicit parameter-list type constructor versus function-type literal;
  genuine domain protocols are a challenger, not one protocol per arity.
- Exact positional callback shape versus compatible defaulted/labelled shape.
  Two parameters differ from one tuple parameter; defaults obey accepted call-time
  laws, not whichever host representation is easiest.

Prepare positive/negative judgments for Clock/Random, captured mutation, empty
input, ordinary Err elements, abnormal callback failure, cold tasks and borrowed
handles inside results, causes, diagnostics and returned closures. Purity is not
an empty `uses` set; a cold task can retain effects/authority/regions. A
`retained=false` comment is not a proof of non-escape.

Challenge conservative, relaxed and effect/region-aware generalization with
delayed identity, a captured shared outer slot and independent fresh factories.
Every candidate excludes variables fixed by the surrounding monomorphic
environment. Reject inconsistent sharing without changing allocation to make
the judgment convenient.

Include two equally applicable imported protocol extensions as a required
negative judgment. The diagnostic must identify both declaration/package owners
and an explicit disambiguation route; convenience dispatch must not select by
import order or privately inspect an implementation.

**Output:** coherent call/type/effect/region/interface facts for three program
levels; 80/100-column signatures; hover and conflicting-call/capture diagnostics;
an explicit choice, rejection or sharply bounded unresolved obligation. Encode
accepted once-only evaluation/default laws instead of reopening them implicitly.
If an actual type-inference slice is feasible, compare inferred output against
independently supplied judgments. A supplied-fact validator is not a typechecker.

### Follow-On Frontiers

Select the next row only when its required contracts are sufficiently closed.
Do not build all of them in a single pass.

| Frontier / owner | Exact comparison | Independent discriminator | Completion / refusal gate |
| --- | --- | --- | --- |
| D2 completion/resources/tasks; A11/A14/A15 | Typed recoverable scope failure plus distinct abnormal completion; static non-escape plus revocation versus runtime-only checks; cancel-siblings versus collect-all abnormal task failure | Body/release Err, panic and cancellation; binding failure after enter; LIFO release/join; ordinary returned Err distinct from abnormal failure; independent active/queue/evidence bounds | One slice retains causes, transfer targets and declared observation order, not timestamp order; deadlines/worker termination are not completed cleanup |
| D3 portable values; A03/A12 | Display/inspection/encoding; strict UTF-8 decode versus evidenced repair; scalar/UTF-8/UTF-16/grapheme coordinates; exact numeric transport | Fixed bytes, values, paths, spans and sensitive-value negatives prepared independently of adapters | One versioned golden contract on declared hosts; reject host-default coercion, replacement or display-as-wire semantics |
| Interface/nominal ownership; A05/A26 | Passive separately checked interfaces across diamonds/re-exports/stores | Declaration/package identity, public dependency and runtime owner/brand facts | Import execution/private-source coincidence cannot create type identity; instance ownership need not make every declaration generative |
| D4 whole-program coherence; A01/A17 | Beginner invoice, boundary-heavy import/report and failure-heavy resource job | Explain every call, expected error, authority, suspension and cleanup; list proposed APIs explicitly | One vertical contract fits locally without fictional support; revise a decision when composition fails |
| D5 representations; A21/A31 | Text plus read-only projection versus structured-document primary | Same supplied facts; invalid drafts, stale revisions, denied grants, changed referents and missing checks | Preserve identity/comments/fallback/accessibility; actual human observations remain separate from fixture answers and screenshots |
| D6/D7 migration; A04/A06/A20/A28 | One admitted source/artifact/runtime/diagnostic family through two frontend paths | Independent accepted/rejected/corrupt artifacts, spans, values and order | Gated profile, rollback and an honest runnable sample; no whole-target conformance from parsing or stdout alone |

Task bounds must separately name active work, queued item count/bytes and retained
result/evidence storage. A running-task limit alone does not bound memory.

Prototype a checked typed interface when host AST/dictionaries cannot retain
required symbol/type/effect/region ownership. Start with one producer and one
downstream consumer, not a universal checker or whole IR replacement. Keep
supplied, inferred and observed facts distinguishable in inspection output.

## Lane Two: Continuation Engineering

Start with [the exact runtime next step](docs/orientation/project_roadmap.md#iterative-runtime-continuation-plan).
Relevant owners are `prototype/interpreter/python/generator_state.py`,
`expressions.py`, `function_call.py`, `control.py`, `exceptions.py`,
`context_managers.py` and their Nomi/reduced overrides. Read current code before
selecting the owner; these are starting locations, not a prescribed architecture.

Prepare two minimal native/hosted reproductions:

1. An effectful completed left operand plus a yielding right operand in a compound
   expression. Preserve the left value, exactly one left effect, the sent value
   including `None`, the resume phase and final result.
2. A failing paused child under nested `try`/`with`. Deliver failure to the waiting
   ancestor so handlers and every required exit observe the right error/completion;
   no ancestor disappears merely because a child resumed first.

Use declared native Python values, event order, active error/context facts and
cleanup traces as compatibility oracles across `python`, `nomi` and `reduced`.
Record operand, phase, child and pending completion together. Compare a narrow
repair, bounded continuation extraction and explicit pre-effect unsupported-shape
fence. Choose one coherent boundary rather than repeated operator-specific patches.

The existing focused anchors are
[generator frame boundaries](prototype/tests/unit/interpreter/python/test_generator_frame_boundaries.py),
[context boundaries](prototype/tests/unit/interpreter/python/test_context_scope_boundaries.py)
and [exception completion](prototype/tests/unit/interpreter/python/test_exception_completion_boundaries.py).
The reduced failed-child skip is intentional evidence, not permission to remove
it or weaken assertions. Add new reproductions; obtain required approval before
editing existing tests. Close/throw, async cleanup and target generator admission
remain separately gated unless the selected contract and actual fixtures cover them.

**Output:** explicit supported/unsupported shapes, one bounded mechanism or fence,
once-only/cause/order fixtures, relevant neighboring/full tests and an updated
receipt. Hosted Python suppression/context parity must not silently become Nomi's
typed all-cause completion contract. Keep target design and compatibility repair
in separately reviewable commits.

## Extend Without Flattening Domains

Use [A33](docs/orientation/project_action_notes.md#a33-text-interfaces-strings-and-scoped-dsls),
[domain recipes](docs/orientation/project_action_notes.md#domain-extension-recipes)
and their research owners, not another new domain catalog. Choose one inert
description before an executor. Ordinary calls/protocols come first; new global
grammar is not justified merely by repeated composition failure. Scoped notation
needs demonstrated ordinary-call pressure plus hygiene, budgets, source maps,
formatting and removal gates. A further core primitive additionally needs a
missing semantic contract and an independent conformance slice.

| Pressure | Small reusable foundation | Domain law that must remain owned |
| --- | --- | --- |
| Data/DAG/time/database | Typed identity, dependency/plan, snapshot basis, revision and commit boundary | Scheduling order, cyclic/fixed-point rules, predicate consistency, history and crash durability are not one graph law |
| AI/ML/science | Shape/unit/clock, numeric profile, randomness, evidence/provenance, budget | Differentiability, convergence, adaptive evaluation, correlation and learned removal require separate assumptions/oracles |
| Queues/pub-sub/events | Message identity, position, owned delivery/settlement, bounded demand | Partition order, lease, replay, local atomicity and broker durability are profile-specific; no universal exactly-once promise |
| Text/config/web/CLI | Text/Bytes, versioned decode/encode, source maps, contextual escaping and command plan | Display, inspection, serialization, shell arguments and template stages differ; quoting at one stage does not secure all sinks |
| Visual/support/documentary domains | Referent/revision, reviewable change, explanation/evidence, explicit executor authority | Approval covers the exact proposed action under current authority, not truth, repair safety, a changed revision or new executor capabilities |

For generic operations use [GA1-GA8](docs/research/generic_operations.md#bounded-experiments)
to expose order, demand, retention, cache context, failure prefix and algebraic
side conditions. Do not create universal Object/Function methods or assume hash,
encoding, serialization, parallel reduce and fixed-point convergence are total.

For natural language use [its research owner](docs/research/interfaces/natural_language.md)
for naming/semantic roles, quantifier scope, audience, localization and changed
referents. Compare discoverable aliases/labels without giving prose execution
authority. An English-friendly surface must not impose English-only identifiers
or hide binding/scope behind grammatical intuition.

Translate [philosophical inspiration](docs/research/cognition.md) into falsifiable
obligations: Leibniz-style
composable representation suggests explicit identities, operators and interpreters,
not a universal knowledge engine; Boole-style calculation suggests named logical
laws without confusing unknown, contradiction, failure and False; Dijkstra-style
reasoning suggests local invariants and inspectable reductions that still account
for effects, cleanup and concurrency. Judge these proposed translations by actual
programs, not by claims about what historical thinkers would endorse.

The [eleven research units](docs/orientation/project_action_notes.md#eleven-research-units-to-turn-into-evidence)
have prepared discriminators. Existing countermodels can falsify naive policies;
they do not prove adapters, weak-memory behavior, numeric convergence, durable
recovery or human comprehension. Execute a selected comparison or eliminate a
candidate instead of merely expanding its prose.

## Verification And Product Gates

Scale checks to the changed contract. Do not use large green counts as a
substitute for independent outcomes, or claim a listed command was executed.

| Changed surface | Required evidence |
| --- | --- |
| Design/docs | Selected packet validations, target positives/negatives, local links/anchors and authority review; no runtime claim from doc checks |
| Parser/Surface/Core | Two declared frontend paths, acceptance/rejection, corrupt/versioned artifacts and span/order parity; `prototype/syntax/core_json.py` currently needs a versioned span-carrier decision |
| Hosted runtime | New failing reproductions, three hosted modes, independent value/effect/cause order, neighboring suites then relevant broader suite |
| Browser/runtime assets | Manifest generation when inputs change, `--check`, WASM rebuild only for its changed inputs, actual default and affected Pyodide workflows with desktop/mobile screenshots |
| User-facing sample | Supported profile, normal regressions, intentional snapshot policy, fresh artifacts and actual CLI/browser execution; target-only source stays outside `samples/` |
| Distribution/editor/notebook | Installed outside-checkout artifact or actual declared editor/kernel/container host; mocked/helper tests are not client/host evidence |
| Human claims | Reviewed stimulus facts, consent/accessibility/expertise/confounds and observed task results; no population or longitudinal benefit from a pilot |

Useful focused and promotion commands, conditional on the work selected:

```bash
python3 -m pytest -q -n 4 prototype/tests/unit/tools/test_docs_lifecycle.py prototype/tests/unit/tools/test_design_passes.py prototype/tests/unit/tools/test_design_packet_boundaries.py prototype/tests/unit/tools/test_target_fixture_coherence.py --tb=short
python3 -m pytest -q -n 0 prototype/tests/unit/interpreter/python/test_generator_frame_boundaries.py prototype/tests/unit/interpreter/python/test_context_scope_boundaries.py prototype/tests/unit/interpreter/python/test_exception_completion_boundaries.py
python3 scripts/check_web_runtime.py
python3 scripts/check_web_browser.py --legacy-pyodide
python3 -m pytest -q -n 4 --tb=short
git diff --check
```

Preserve existing tests unless the user explicitly requests or approves the
specific edit, as required by [nomi-test's rules](.agents/skills/nomi-test/SKILL.md#rules).
Reuse recorded authorization for the same scoped work; do not request it again
or generalize it to unrelated edits. Independent evidence must justify changes;
follow `nomi-test` for new test placement and snapshot policy. Keep generated
caches/reports/browser captures out of commits.
Stop servers/processes used for verification; retain a requested usable dev
server with its URL when the future task changes the web experience.

Public release still needs owner decisions on root license, support versions,
artifact identity and authentication/deployment policy, plus actual hosted
evidence and rollback. No push, publication, deployment, license selection,
credentials, privileged services or unsafe native/device probes are authorized
by this handoff. Ask for the specific missing approval rather than broaden claims.

## Completion And Continuity

Commit logical slices: comparison/decision, bounded implementation, then verified
integration/receipt as warranted. Do not manufacture checkpoints or mix target
acceptance, test reorganization, snapshots and backend replacement together.
Update existing packet owners, registry next actions, bridge retrospective and
roadmap receipt; do not make this temporary file permanent parallel authority.

A successful frontier pass advances the broad ecosystem thesis and leaves fewer
unexplained contracts, one or more
credible alternatives eliminated by evidence, and a demonstrably more useful or
more honest supported path. An explicit rejection or narrowed unsupported fence
counts; a bibliography-only expansion or broad rewrite without a pressure oracle
does not. Broad domain coherence is a project goal; implemented breadth still
needs staged evidence and is not automatically the next release obligation.

At each checkpoint record:

```text
Baseline and changed paths:
Selected pressure / A-D-packet owner:
Candidates, hypothesis and independent oracle:
Decision or remaining exact obligation:
Implemented / accepted / speculative boundaries:
Actual commands, host/profile, results and skips:
Preserved behavior, migration/fallback and removal trigger:
Unresolved approval/security/human/host gates:
Next exact task and first fixture/command:
```

When this handoff is consumed, move durable conclusions into their existing
owners and remove or mark this file consumed with the final checkpoint. Do not
leave both its baseline and a newer receipt competing as live instructions.
Update its links in the docs index, roadmap and action notes if retiring the file.

## Suggested Next-Pass Request

> Read `ASTRA_HANDOFF.md`, especially the updated user north star, and the named
> owners. Take Nomi toward its logical conclusion as a coherent computational
> ecosystem: an evolved Python/TypeScript-like starting experience, implicit intent
> and inference first, progressively explicit types and other directions, optional
> composable restrictions up to compiler-enforced production policies, broad domain
> layers and representations, and independently evolving frontends/engines aiming
> for Rust-/Java-level rigor and speed without harming experience.
> Challenge current target assumptions where this direction conflicts with them.
> Synthesize the research into decisions and executable mechanisms; do not stop
> at a new plan or the existing two runtime fixes. Use D1 and continuation failures
> as initial discriminators where appropriate, then pursue the composed workflows
> and frontier experiments through sustained design/implementation/review/fix
> iterations and coherent commits. Keep runnable CLI/browser surfaces useful,
> preserve meaningful debugging and distinguish accepted target, supported
> prototype and unperformed evidence. Respect approval boundaries for existing
> tests and external operations. End each checkpoint with actual results, remaining
> obligations and the exact next step; keep ambitious scope and honest evidence.
