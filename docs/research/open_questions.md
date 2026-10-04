# Open Research Questions

> Status: active, bounded research agenda.
>
> These are genuine design forks. They should be answered with focused
> prototypes and representative programs, not by reopening the full language
> survey.

## Experiment Protocol

Every experiment should produce:

- at least three programs: beginner, ordinary production, and failure-heavy;
- two or more syntax/semantic candidates;
- formatted source at realistic widths;
- diagnostics and explanation output;
- interactions with types, patterns, Result, effects, async, and modules;
- a removal criterion;
- a recommendation recorded in the decision ledger.

An experiment can conclude that no syntax is needed.

## 1. Constraint Surface

**Question:** Does `name: Type where predicate note "message" = value` remain
readable across local bindings, parameters, fields, and cross-field rules?

**Current hypothesis:** one `where` vocabulary is better than tuple-like
annotations, decorators, contract blocks, or refinement-type punctuation.

**Test:** format constrained signatures and nested data from finance, API input,
configuration, and scientific domains. Measure whether readers can distinguish
type, predicate, value, and diagnostic note without rereading.

## 2. Progressive Type Boundary

**Question:** Which declarations require annotations, and how much local
inference remains predictable?

**Current hypothesis:** exported package APIs are explicit; scripts and private
locals infer; no implicit `Any`; constraint predicates retain runtime meaning.

**Test:** separate compilation, recursive local functions, generic collection
helpers, dynamic host interop, editor latency, and public API diffing.

## 3. Protocol And Method Model

**Question:** How do generic behavior, owned methods, and third-party extension
methods coexist without invisible dispatch?

**Current hypothesis:** nominal protocols, explicit conformance, owned methods,
and imported extensions only. Free functions remain canonical for many
algorithms.

**Test:** numeric types, collection iteration, display/redaction, decoding,
HTTP adapters, and two libraries that define colliding extensions.

**September pressure:** the target suite assumes map/map_error and typed task
handles but cannot yet declare their full generic/function-value contracts.
Compare pure-only collection callbacks with explicit effect-polymorphic types;
inspect resolved dispatch and errors at the callback argument. See
[functions](features/functions.md) and [effects](features/effects.md).

**Generic-operation pressure:** [GA1-GA8](generic_operations.md#bounded-experiments)
compare carrier-specific versus shared protocols, pure/effectful callbacks,
seeded history, lawful merge, fallible observation, context-bound caches,
bounded iteration and conditional value capabilities. Start with GA2/GA3/GA8
under D1-D3. Host/model counterexamples do not select type notation or close
effect/region checking. No universal Object/Function methods are assumed.

## 4. Effect Taxonomy

**Question:** What belongs in a public `uses` set, and at what granularity?

**Current hypothesis:** stable categories such as `ConsoleWrite`, `FileRead`,
`FileWrite`, `Network`, `Clock`, `Random`, `Process`, `Database`, and
`UnsafeHost`; handles carry narrower runtime authority.

**Test:** CLI, web service, notebook, browser/Wasm, deterministic test, and
embedded host. Avoid path/URL-level types in function signatures unless the
complexity pays for itself.

## 5. Resource Scope And Async Cleanup

**Question:** Can exactly-once `with`, `async with`, and `defer` cover resource
lifetime without hidden control or duplicate cleanup mechanisms?

**Current hypothesis:** yes, if cleanup outcomes, cancellation, suppressed
errors, return, and break semantics are specified before implementation.

**Test:** nested files, transaction commit/rollback, async stream, cancellation
during enter/body/exit, and simultaneous body/cleanup failure.

**September pressure:** settle handle escape and the typed outcome carrier
together. Compare static non-escape checking with runtime closed-handle checks
for return, callback capture, and child-task transfer. Compare a domain-visible
cleanup Result with a separate composed abnormal envelope. Require body and
release causes to survive cancellation. See [resources](features/resources.md).

**Executed:** [the focused resource comparison](resource_lifetime.md) preserves
causes under both carriers. Prefer typed recoverable completion and static scoped
use with revocation, subject to callback/error/region typing. Next test binding
failure after successful enter, in-flight operations, and actual async cleanup
with deadlines; supplied lifetime facts are not checker evidence.

## 6. Error Conversion

**Question:** Is explicit `.map_error(...)` too repetitive in layered services?

**Current hypothesis:** keep conversion explicit until real programs prove a
small, locally discoverable protocol is worthwhile.

**Test:** a five-layer CLI/service with IO, decode, database, and domain errors.
Compare explicit mapping, declared conversion protocols, open error sets, and
exception-like propagation.

## 7. Generator And Stream Semantics

**Question:** Do synchronous and asynchronous generators need `yield` syntax,
or are explicit iterator/stream builders clearer?

**Current hypothesis:** reserve `yield`; do not reuse it for resource policy or
concurrency. Admit it only with defined final values, errors, cancellation,
cleanup, reentrancy, and typing.

**Test:** file lines, parser tokens, tree traversal, infinite sequences,
bidirectional coroutines, and async events.

## 8. Tables And Query Plans

**Question:** When do `map`/`filter`/`group_by` stop being adequate for tables?

**Current hypothesis:** typed table values and ordinary verbs first; explicit
lazy plan type; syntax only if joins, windows, projections, and row scopes stay
materially awkward.

**Test:** in-memory CSV cleanup, SQL pushdown, dataframe analysis, distributed
aggregation, null policy, and `explain` output. Compare ordinary calls, named
expression objects, and a scoped query form.

The [data dossier](data_workflows/README.md) supplies literal comparisons and a
reconciliation oracle. [DW1-DW3](data_workflows/nomi_candidates.md) first close
expression/callback contracts, then compare eager rows, schema-bound expression
data and scoped notation under duplicate keys, missing values and name collisions.
The [dependency/time continuation](data_workflows/dependencies_and_time.md)
adds DT1-DT5: checked DAG owners, partial ordering, snapshot versus bitemporal
basis, domain-specific change algebra and cache/backfill authority. Acyclicity
does not prove safe ordering, consistent snapshots or lawful incrementality.

## 9. Numeric And Scientific Model

**Question:** What are the default integer, decimal, float, overflow, unit,
shape, and broadcasting rules?

**Current hypothesis:** ordinary numeric protocols with explicit array/shape
types; checked or well-specified overflow; units and rank library-first; dense
notation scoped later.

**Test:** finance, statistics, image kernels, linear algebra, physical units,
automatic differentiation, and native/Wasm performance.

Use [notation cases 2/3](notation_atlas.md) and
[DW4/DW5](data_workflows/nomi_candidates.md) for explicit contraction binders,
axis/unit/frame identity and learned-state boundaries. Equal array lengths must
not silently establish coordinate compatibility or prevent training leakage.

The [orthogonal models](dsls/orthogonal_models.md) add E20/E21: arithmetic
rewrite theories, density versus sampling, derivative callback staging and
simulation evidence. The host float and finite-posterior probes illustrate
differences; no numeric API or inference engine is selected.
The [AI/ML continuation](data_workflows/ai_ml.md) adds ML1-ML6: train-only
preprocessing, supported differentiation/staging, exact/tolerance/profile
vectors, training-state completeness, pinned serving/agent requests and checked
export. [Local probes](data_workflows/composition_experiments.md) cover selected
arithmetic/metadata counterexamples, not engine execution or model quality.

## 10. Generic Dispatch

**Question:** Are protocols and ordinary functions enough, or does scientific
and data code need explainable multiple dispatch?

**Current hypothesis:** do not add multiple dispatch until conflicting library
extensions and numeric algorithms demonstrate a clear need.

**Test:** arithmetic across user numeric types, serialization formats, table
backends, and geometry. Require deterministic ambiguity diagnostics and a
locally inspectable candidate set.

## 11. Structural Openness And Versioned Data

**Question:** How does strict closed decode coexist with forward-compatible APIs
and stored-data evolution?

**Current hypothesis:** closed by default, explicit rest/unknown-field policy,
versioned decoders, and migrations as ordinary functions with provenance.

**Test:** rolling service deployment, config typo detection, event replay,
client/server skew, and schema export limitations.

## 12. Metaprogramming Boundary

**Question:** Which capabilities justify syntax generation, and what is the
smallest safe mechanism?

**Current hypothesis:** typed hygienic Surface transformations in a sandbox,
scoped invocation, full source maps, no ambient authority, and expansion visible
through tooling. Many use cases should remain code generation or protocols.

**Test:** deriving equality/codec, route tables, parser declarations, symbolic
math, and eliminating boilerplate in data APIs.

**DSL/string pressure:** [the dedicated dossier](dsls/README.md) compares typed
libraries, explicitly parsed foreign DSL values and scoped notation. E1-E3/E7
test literal preservation, typed construction and named checking guarantees
before grammar extensibility. A foreign keyword or raw string is not evidence
that a macro facility is needed; the existing scope/hygiene gate still applies.

The [expanded atlas](dsls/domain_atlas.md) covers 50 families. E20/E22 distinguish
directed rewrite strategy, equivalence exploration and a source/evidence
envelope from a universal DSL AST. Parsed foreign binders and environment
identity must not be reduced to raw interpolation or implicit host capture.

## 13. Package Identity And Federation

**Question:** How should organization/domain identity, mirrors, offline use,
signatures, and transparency logs combine?

**Current hypothesis:** scoped identity plus content hash; registry location is
not identity; exact lockfile; immutable releases; pure fetch.

**Test:** domain loss, package transfer, private registries, air-gapped builds,
forks, compromised signing keys, and dependency confusion.

## 14. Edition And Migration Model

**Question:** How can source syntax evolve after stability without splitting
runtime semantics or ecosystem tooling?

**Current hypothesis:** package-scoped editions normalize to versioned Surface
and Core artifacts; formatter/compiler provide automated migration and semantic
diffs.

**Test:** one deliberately breaking syntax change and one semantic-default
change across a multi-package dependency graph.

## 15. Backend-Neutral Determinism

**Question:** Which observable behaviors must be fixed across interpreter,
native, JavaScript, and Wasm profiles?

**Current hypothesis:** evaluation order, integer behavior, text encoding,
collection ordering, diagnostics, decode, effects, and task outcomes are fixed;
platform differences require explicit APIs.

**Test:** differential execution of randomized conformance programs and
failure/cancellation/resource scenarios across every backend.

## 16. Pattern Ergonomics After The Core Decision

**Question:** Does real Nomi code validate the accepted positional nominal
patterns, exact-by-default maps, missing-witness detail, and left-biased
or-pattern captures?

**Current hypothesis:** keep the closed transactional core in
[Pattern Matching](../design/pattern_matching.md). Permit only local syntax or
diagnostic refinements; do not reopen choice aliases or user extractors.

**Test:** format and compare domain variants, evolving protocol maps, nested
missing cases, and overlapping capture alternatives from
`docs/design/pattern_matching_target.nomi`. Record comprehension errors and
compiler-complexity pressure in `docs/research/pattern_matching.md` before
changing the focused target.

## 17. Computational Representations And Change

**Question:** Should source text remain primary with derived views, or should
a structured document own equally editable textual/spatial projections?

**Current hypothesis:** test text-primary, read-only views first; retain the
structured-document alternative if inverse source edits repeatedly fail.

**Test:** the [invoice target](../design/interaction_model_target.nomi) across
text, table, dependency diagram, form and semantic commands. Include stale edits,
invalid drafts, row reordering, unsupported constructs, comments, denied effects,
and keyboard/screen-reader workflows. The [registered interaction proposal](../design/interaction_model.md)
owns laws and experiments; the [redesign agenda](../design/redesign_agenda.md)
owns closure order. No usability study or target execution is claimed.

[Cross-disciplinary notation](notation_atlas.md) broadens the pressure beyond
invoices: finite-set/Venn membership, tensor binders, chemical graphs,
reference-coordinate variants and aligned annotation/evidence. DW7 owns the
local comparison; [workflow evidence](data_workflows/execution_models.md)
adds partition/attempt/observation identities. This does not turn every diagram
into the same executable graph or reopen core punctuation by analogy.

The [orthogonal DSL comparison](dsls/orthogonal_models.md) adds live bindings,
solver/proof evidence, token traces, circuits, scenes and localized documents.
E15/E17/E22 ask which inspection/source envelope can be shared while semantic
payloads retain domain owners; [composition fixtures](dsls/composition_boundaries.md)
include mapped errors and draft/checked separation. No universal editable IR
or evaluator is selected.

**DSL/string pressure:** [source provenance research](dsls/strings_and_embedding.md)
adds escapes, folding, indentation removal, included files and repeated
expansion to the source/view problem. E6/E11 compare mapped inner diagnostics
and incomplete drafts with the existing committed-value model; no new editable
projection or exact inverse source mapping is claimed.

**Text-interface pressure:** [the focused extension](dsls/text_as_interface.md)
distinguishes display, inspection, formatting, rendering, encoding, parsing and
execution while retaining text as the universal authored/fallback form. T1-T10
test representation intent, strict decode, offset units, structured encoding,
template trust, argv, framing, lossless versus semantic formatting,
localization, and the text/structured-primary fork. Before promoting a text API,
close the scalar/index/rendering contract and reject implicit second evaluation.

**Domain-layer pressure:** [the domain-family map](domain_composition.md)
adds DC1-DC6: domain-owned payloads versus a universal IR, ordinary package
composition versus scoped tools, versioned vocabulary/catalog references,
controlled clauses versus interpreted prose, a composed report/train/review/
publication fixture, and a new-domain admission trial. These extend questions
4/7/8/9/11/12/15/17; the [canonical synthesis](../design/synthesis.md#domain-layer-proposal)
owns the recommendation. No natural-language evaluator or universal knowledge
ontology is selected.

**Architecture pressure:** [messaging and events](data_workflows/messaging_and_events.md)
adds MSG1-MSG6 beneath questions 4/5/7/11/15/17: carrier-specific delivery,
partition frontiers, local versus remote atomic participants, handler versus
explicit loops, replay versus effectful workflow, and verified adapter profiles.
Lost acknowledgments, stale ownership, payload conflicts, retention and bounded
feedback challenge the shared primitives. Finite models motivate the forks;
they do not settle distributed guarantees. D1-D3 precede a pinned broker slice,
and no new global architecture keywords or implementation backlog is selected.

**Human interaction edges:** the [96-case atlas](interfaces/edge_cases.md) and
[twelve composition cases](interfaces/composition_cases.md) sharpen this same
question. HX1-HX8 compare proposal invalidation/repreparation, passive/refreshed
inspection, draft/commit controls, bounded inverse edits, Stop evidence, source
mapping, frame/control context, and interrupted-task comprehension. The
[local probes](interfaces/experiments.md) exhibit counterexamples; they do
not close those Nomi candidates or perform a human study. Keep ordinary APIs,
library models, and view adapters ahead of notation; D1-D3 dependencies remain.

The gap review adds two HX1 obligations: publication must enforce freshness at
the actual owner boundary, and application-required review must name its scope
separately from current capability grants. P19/P20 are finite supplied-policy
counterexamples, not production enforcement. HX8 now has a
[seven-task protocol and answer facts](interfaces/composition_cases.md#hx8-minimal-study-protocol);
execution, authentic approval, and human comprehension remain open evidence work.

## Research Stop Rule

The [September synthesis](../design/synthesis.md) orders these gates against
[the overall program](../design/targets/overall.nomi). Task-group policy is a
specific additional fork exposed there: cancel siblings versus collect all on
abnormal failure, with ordinary child Err remaining data unless explicitly
promoted. Use controlled scheduler events and record active/queued bounds,
cause ordering, parent cancellation, and no children after lexical exit. See
[concurrency](features/concurrency.md). This does not reopen cold tasks or
structured lifetime; it closes their currently underspecified library policy.

Do not add another open question merely because a language has an interesting
feature. Add one only when:

1. a target program exposes a concrete deficiency;
2. two credible Nomi-compatible answers remain;
3. the choice would alter source, semantics, or an industrial contract;
4. a bounded experiment can distinguish them.
