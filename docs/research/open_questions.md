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

**Current direction (October 8):** exploration permits unresolved static facts;
selected restrictions demand evidence. Checked exported contracts may be inferred
locally or declared; inference cannot depend on clients' private calls. An
unknown is not an inferred `Any` or proof. Constraint predicates retain runtime
meaning. See the revised [assurance contract](../design/semantics.md#progressive-assurance).

**First executable discriminator:** the scalar/direct-call experiment is
preserved at 6aec9f3; see the [checkpoint](../orientation/frontier_checkpoint_2026-10-08.md)
for current checks and separate continuation failures. It infers bounded
invoice call results, checks independent type/purity obligations and keeps
uncalled function effects latent. Rebinding and unknown operations must not
retain stale proofs. This does not close public generic inference.

**Next discriminator:** the [growth journeys](../design/synthesis.md#growth-journeys-and-boundary-evidence)
and [bounded contract trial](../design/function_contracts.md#bounded-contract-comparison-for-implementation)
prepare a closed monomorphic export, a consumer without private source, unknown
dependency rejection and source/contract/verification invalidation. Unknown
dynamic dependencies block the first checked trial; a runtime adapter remains
a later challenger whose type/effect/lifetime guarantees must be named. Policy
scope distinguishes module execution from complete exported callable evidence.

**Test:** separate compilation, recursive local functions, generic collection
helpers, dynamic host interop, editor latency, and public API diffing.

**Sharing pressure:** [polymorphic sharing and generalization](features/functions.md#polymorphic-sharing-and-generalization)
adds a stateful delayed-identity counterexample. Use unrestricted generalization
as a negative baseline; compare conservative restriction with justified
relaxed/effect-aware rules, excluding variables fixed by the environment;
an apparently identity-shaped callable can retain values across invocations.
Challenge private mutable captures, independent factory calls and immutable
covariant results before choosing annotation or generalization policy. These
are unperformed D1/D3 subexperiments, not a selected type-system rule.

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

Resolved protocol ownership must distinguish
[package/declaration identity from runtime instance ownership](features/modules_tooling.md#nominal-identity-across-package-instances),
not just use the displayed type name. Follow question 13 for duplicate-version,
re-export and explicit conversion cases; a structural resemblance is not
evidence that two nominal declarations share constraints or conformance.

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

**Foreign-boundary pressure:** [callbacks and re-entry](features/resources.md#foreign-callbacks-and-re-entry)
extend capture/escape and in-flight use with synchronous foreign callbacks,
foreign-thread entry, deregistration races and incompatible unwinding.
Compare restricted non-reentrant entry, explicit re-entry contexts and queued
handoff, preserving current authority and distinct body/cleanup causes.
The existing lease model does not establish an ABI, thread safety or quiescence;
use deterministic callback schedules before any unsafe adapter is admitted.

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

**Commit-consistency pressure:** [DT4 predicate consistency](data_workflows/dependencies_and_time.md#predicate-consistency-beyond-snapshots-and-row-guards)
adds write skew and absent-row predicates. Compare whole-owner revision guards,
precise dependency/predicate validation, and a named serializable adapter profile.
Revalidate at the publication owner and preserve atomic participant boundaries;
per-row freshness is not cross-row invariant preservation. The designed schedules
are unperformed and do not replace the existing owner-enforced publication law.

## 9. Numeric And Scientific Model

**October 9 bounded closure:** default mathematical Int, distinct Bool and the
initial scalar operations are accepted in
[semantics](../design/semantics.md#first-product-scalar-contract). Fixed width
is not default Int meaning. Exact transport/execution and shared measured
capacity remain admission work. The
[first-report boundary](../design/semantics.md#first-report-boundary-contract)
selects integer-form JSON tokens and finite ASCII trim; its
[synthesis closure](../design/synthesis.md#report-admission-gaps) selects concrete
failure records and budget accounting; library/target implementation and measured
capacity remain open. General
numeric conversion and Unicode trimming remain open, as do Float,
Decimal, units, arrays and the richer numeric operations below.

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

**Uncertainty pressure:** [DW4 shared origins and covariance](notation_atlas.md#correlated-uncertainty-shared-origin-is-part-of-the-model)
compares independent summaries, named uncertainty sources and explicit joint
models. Under the stated exact scalar theory, one uncertain X minus itself
cancels; separately measured equal-valued inputs need not. Challenge shared
calibration, nonlinear propagation and missing covariance without treating zero
covariance as independence. No uncertainty notation or engine is selected.

**Evaluation and removal pressure:** [ML1 adaptive feedback](data_workflows/ai_ml.md#adaptive-evaluation-feedback-is-also-a-dependency)
treats selection and optional stopping as evaluation dependencies, not only
training-code reads. Compare declared exposure histories, governed held-out
evaluation and method-qualified adaptive reuse. [ML4 learned removal](data_workflows/ai_ml.md#data-erasure-and-learned-influence-are-different-operations)
separates source erasure, current access, descendant invalidation, retraining and
supported influence-removal claims. Scope each guarantee to its model, retained
state and threat/measurement profile; neither a provenance graph nor a delete
acknowledgment certifies it. Both are unperformed continuations, and privacy
accounting remains explicitly outside the existing selected ML scope.

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

**Nominal identity pressure:** [the package-instance comparison](features/modules_tooling.md#nominal-identity-across-package-instances)
separates registry location, resolved package identity, declaration identity and
runtime module instance. Compare revision-qualified declarations with stable
public identities and checked compatibility, including a diamond
dependency, an identity-preserving re-export and fresh module instances.
Compatibility claims need their own evidence; neither equal source spelling nor
equal fields establishes substitutability. The comparison is unperformed.

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

**Memory-model pressure:** [visibility and publication](features/concurrency.md#memory-visibility-and-publication)
separate task lifetime/scheduling from what another worker may observe.
Compare isolation/transfer, synchronized sharing and qualified atomics using
publication, stale reads and compound updates. Require named happens-before
edges, race policy and host profile; sleep/yield is not a publication contract.
No weak-memory model or atomic API has been accepted or exercised by this pass.

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

The [paired trial](../design/interaction_model.md#paired-representation-and-revision-trial)
now fixes inputs, repair tasks, unsupported-source obligations and comparison
costs for both candidates. It also separates binding/capture syntax from notebook
re-execution policy. This is prepared protocol, not performed usability evidence.

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

**Natural-language pressure:** [the linguistic dossier](interfaces/natural_language.md)
adds NL1-NL6 under existing questions 4/5/7/11/15/17: optional domain vocabulary,
named/nominal argument roles, quantifier/evidence views, context clarification,
localized discovery aliases and scoped controlled-language tools. Start with
NL2 role swaps and NL4 changed referents using the prepared N01-N10 facts and
HX8 protocol. Maintain ordinary Bool and call meaning, distinguish query/request
from permission, and treat fluent interpretations as drafts. No NLP engine,
universal English grammar or compiler naming restriction is selected.

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

**Reliance and team pressure:** C12/HX8 now includes
[repeated advisory reliability](interfaces/composition_cases.md#c12-advisory-reliability-and-calibrated-reliance)
and [split-information handoff](interfaces/composition_cases.md#c12-team-handoff-and-distributed-understanding).
Compare prediction and repair over a reliability sequence, and distinguish
artifact completeness from who checked each obligation. These are additional
unperformed protocols, not participants, outcomes or additions to the prepared
U01-U07/N01-N10 inventories. Natural-language grounding alone does not establish
calibrated reliance or shared task knowledge.

**Diagnostic pressure:** [contrastive explanation and diagnosis](interfaces/query_search.md#contrastive-explanation-and-diagnosis)
extend C09/HX2/HX8 with why/why-not, false-premise and multiple-blocker cases.
Compare passive traces, contrastive dependency slices and separately authorized
hypothetical repair. Showing one failed condition does not prove that changing
it will enable the expected action; incomplete evidence must remain visible.

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
