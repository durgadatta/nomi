# Coherent Domain Layers

> Status: research synthesis and extensibility hypotheses, not new grammar,
> accepted public APIs, a universal ontology or formalization of all knowledge.
>
> Selected primary documentation checked 2026-10-04. Coverage below distinguishes
> reviewed mechanisms, existing research and deliberately shallow discovery.

[Data dependencies/time](data_workflows/dependencies_and_time.md) and
[AI/ML](data_workflows/ai_ml.md) supply the first substantial domain pressures.
This chapter extends [the DSL atlas](dsls/domain_atlas.md),
[notation](notation_atlas.md) and [cognitive foundations](cognition.md).
The canonical [language synthesis](../design/synthesis.md#domain-layer-proposal)
owns the current proposal; D1-D7 remain the admission order.

## Ambition With A Compositional Boundary

The useful version of "a language for all human knowledge" is a medium in which
new domains can name their concepts, state their assumptions, compose operations,
retain evidence and expose understandable views. It is not one evaluator that
settles every legal interpretation, scientific controversy, social intention or
natural-language ambiguity.

The user's atom-to-civilization analogy is a helpful design exercise:

```text
small semantic foundations
-> reusable types/protocols and laws
-> domain models and transformations
-> stateful systems and evidence
-> institutions, collaboration and human interpretation
```

This is an analogy, not a scientific reduction or mandatory inheritance tree.
Domains overlap, evolve and disagree. A model can preserve a document or an
unresolved claim without turning it into executable truth. Coherence means
explicit composition and boundaries, not identical semantics at every level.

## Foundations Before New Primitives

Already accepted Nomi foundations include names, immutable values, nominal
`data`, calls, structural choice, typed absence/failure, constraints, effects,
resources, tasks and modules. These are the first primitives to reuse.

The candidates below are semantic building blocks for shared libraries and
tooling. They are not eight additional keywords or universal wrapper types.

| Candidate building block | Fact it makes explicit | Example composition | Must not imply |
| --- | --- | --- | --- |
| Contextual identity/reference | Owner, entity, schema/edition and resolution basis | Asset version, bibliography item, legal provision, named tensor axis | A display label, path or unqualified integer is globally unique |
| Description/operation value | Inputs, outputs, binders and declared operation meaning | Query operator, workflow step, numeric expression, design constraint | Any closure is automatically serializable/translatable |
| Relation/composition | Typed edge role and lawful connection | Data dependency, derivation, attribution, membership, reference | All edges are execution prerequisites or all relations are DAGs |
| State/version/change | Base context, proposed update and domain transition law | Snapshot correction, parameter update, document patch | Every change is invertible or every value needs history |
| Interpretation boundary | Grammar/schema/unit/time/numeric/evidence profile | Codec, theorem checker, scientific-name resolver, clause importer | Parse success proves truth, suitability or authorization |
| Execution boundary | Explicit effects, resources, suspension, limits and current authority | Collect, fit, publish, apply, measure | Check/preview/cache lookup grants permission to run |
| Evidence/observation | Origin, assumptions, context, scope and completeness | Metric, test, proof reference, diagnostic, provenance receipt | A universal confidence score or authenticity from a hash |
| Projection/command | Readable view and checked revision-bound action | Text/table/diagram/form/palette | A rendered view is another authoritative evaluator |

Keep context proportional: a simple integer sum does not need a tenant, lineage
graph and approval record. Attach metadata at boundaries or artifacts that need
it; optional facets must carry a declared schema/owner. Avoid a giant
`UniversalObject` with nullable fields for every discipline.

The [generic-operation hierarchy](generic_operations.md) supplies the
horizontal library vocabulary: carrier-specific traversal, state accumulation,
lawful merge, explicit observation, context-bound reuse and bounded iteration.
These combine the foundations without assuming every domain value supports
hashing, serialization, filtering, differentiation or the same executor.

## One Source Language, Multiple Domain Models

The existing four [surface layers](../design/README.md#surface-layers) are enough:

| Nomi layer | Role in domain growth | Examples / admission pressure |
| --- | --- | --- |
| Core | Meaning shared by ordinary programs | Typed values/calls, binders, failure, effects, lifetimes, concurrency; fix D1-D3 gaps here |
| Standard reducible conveniences | Repeated ordinary acts with one explicit long form | Pipeline inserts an argument; interpolation renders text under a specified conversion |
| Libraries/protocols | Domain semantics, lawful composition, engines and interoperability | Tables, snapshots, tensors, learning, HTTP, commands, catalog records, unit systems |
| Scoped language tools | Domain notation whose parser/checker is explicitly selected | Query, numeric expression, proof, policy or document tool after ordinary calls are challenged |

Web, data and ML should be packages/profiles within these layers, not new global
modes that change what `=`, `where`, `->`, `?` or `|>` means. A domain profile
names required package editions, supported operations, codecs and host
capabilities. It is not implicit evaluator selection by file extension or UI.

A common envelope can route source maps, errors, revisions and observations.
Each domain owns its payload, algebra and execution semantics. Domain IR may be
relational, numeric, logical, documentary or spatial; adapters lower a checked
subset to an engine. Nomi Core must not pretend all such meanings have one
universal optimizer or equality law.

### Hierarchies Built From Those Foundations

These are candidate compositions, not a requirement that every domain use all
levels or that one level compile mechanically into the next:

| Domain | Small forms -> composed forms | New contract at composition |
| --- | --- | --- |
| Data | Entity/reference -> schema/snapshot -> partitioned asset -> typed dependency description -> checked workflow -> run/materialization/history | Keys/cardinality, consistency, edge roles, progress and publication |
| ML | Scalar/axis -> tensor/numeric program -> transformed program -> model specification/state -> training/evaluation -> serving or agent workflow | Derivative/shape laws, state, randomness, dataset basis and authority |
| Documents/knowledge | Source/reference -> term/concept/provision -> typed relation/rule -> interpreted model -> evidence/review -> institution-specific action | Edition, scope, ambiguity, assumptions and responsible authority |

The vertical program can compose horizontally: an ML split refers to a data
snapshot; its report cites a documentary source; a reviewed action uses a cloud
capability. Those adapters must preserve the newly required contracts rather
than inherit them by analogy. This is how a few foundations support many
domains without a new global grammar for each one.

## Domain Scan And Primitive Extraction

Rows marked **reviewed** have selected primary mechanism evidence linked here;
**existing** reuses a bounded repository review; **discovery** is an orientation
source, not full specification analysis. No adoption/popularity ranking is
claimed. Every initial layer is library/protocol, with scoped tools conditional.

| Domain / depth | Primitive candidates | Primary evidence / present route | First discriminator |
| --- | --- | --- | --- |
| Data / reviewed | Schema-bound plan, key/cardinality, snapshot/partition, typed dependency, change law | [Data/time survey](data_workflows/dependencies_and_time.md) | Duplicate keys, independent snapshots, deleted history, late correction |
| AI/ML / reviewed | Numeric program, shape/axis, specification/state, split, randomness, evaluation | [AI/ML survey](data_workflows/ai_ml.md) | Held-out leakage, impure tracing, mutable model alias, weights-only resume |
| Web/service / reviewed | Request/response, media/schema, route, conditional update, streaming completion | [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html), [OpenAPI](https://spec.openapis.org/oas/latest.html) | A retry or stale precondition does not imply exactly-once business effect |
| Command line / existing | Typed command/argument, stream codec, process invocation/outcome | [Text boundaries](dsls/text_as_interface.md), [PowerShell](languages/powershell.md) | Shell source versus argv, stdout data versus stderr diagnostics, partial stream |
| Visual tools / reviewed | Model/view, selection identity, coordinate frame, semantic command | [Vega-Lite view specification](https://vega.github.io/vega-lite/docs/spec.html), [interface packet](interfaces/README.md) | Sorted selection, unsupported inverse, stale source map, accessible textual projection |
| Tech support / reviewed | Observation, hypothesis, diagnostic step, bounded runbook action | [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/), [planning evidence](interfaces/planning_optimization.md) | Partial trace or missing telemetry cannot establish absence of an incident |
| DevOps / reviewed | Desired/observed state, plan, dependency, reconciliation, rollout receipt | [Kubernetes controllers](https://kubernetes.io/docs/concepts/architecture/controller/), [Terraform dependencies](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on) | Plan freshness, hidden dependency, partial apply, unjoined child task |
| Cloud/security / reviewed | Identity/principal, capability, resource scope, policy decision, lease | [AWS evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html), [effects](features/effects.md) | Explicit deny/revocation cannot be replaced by yesterday's allow result |
| Design systems / reviewed | Typed token, alias/reference, constraint, theme/profile and export artifact | [DTCG 2025.10 format](https://www.designtokens.org/tr/2025.10/format/) | Cyclic alias, wrong token type, incompatible export; not a W3C Standard |
| Database / reviewed | Relation/schema, transaction basis, query plan, migration, constraint/conflict | [Temporal database comparison](data_workflows/dependencies_and_time.md), [table evidence](data_workflows/source_forms.md) | Textual merge succeeds while uniqueness fails; SQL null/bag laws differ from lists |
| Scientific research / reviewed | Protocol, measurement/context, uncertainty, dataset/software version and provenance | [PROV-DM](https://www.w3.org/TR/prov-dm/), [RO-Crate 1.2](https://www.researchobject.org/ro-crate/specification/1.2/introduction.html) | A complete manifest is not an independent replication or valid experiment |
| Mathematics / discovery + existing | Typed expression, binder, assumptions, proof/witness, solver/search result | [Lean reference](https://lean-lang.org/doc/reference/latest/), [formal DSL evidence](dsls/orthogonal_models.md) | Timeout is not false; proof depends on assumptions; Float does not inherit ring laws |
| Legal/documentary / reviewed + existing | Provision/version/reference, rule/exception, jurisdiction/context, interpretation/evidence | [Akoma Ntoso 1.0](https://docs.oasis-open.org/legaldocml/akn-core/v1.0/os/part1-vocabulary/akn-core-v1.0-os-part1-vocabulary.html), [Catala comparison](dsls/domain_atlas.md#c-logic-knowledge-policy-and-law) | Correct structure/formal rule is not a legally authoritative interpretation |
| Scientific naming / reviewed + discovery | Reference sequence/version, coordinate system, controlled terminology and resolver | [HGVS references](https://hgvs-nomenclature.org/stable/background/refseq/), [IUPAC orientation](https://iupac.org/what-we-do/nomenclature/) | Same coordinate/name under another reference can denote another object |
| Library/cataloging / reviewed | Work/instance/item, authority reference, edition, preferred/alternative labels | [BIBFRAME 2.0](https://www.loc.gov/bibframe/docs/bibframe2-model.html), [SKOS](https://www.w3.org/TR/skos-reference/) | Shared title is not shared identity; translation label is not exact concept equivalence |
| English/communication / reviewed | Message/audience, glossary, term role, obligation strength, locale/style profile | [BCP 14 clarification](https://www.rfc-editor.org/rfc/rfc8174.html), [GOV.UK style guide](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/) | Stylistic conformity does not establish meaning, truth, assent or executable intent |
| Knowledge organization / reviewed | Concept/scheme, typed relationship, imported vocabulary, entailment/validation result | [OWL 2 primer](https://www.w3.org/TR/owl2-primer/), [SHACL](https://www.w3.org/TR/shacl/), [SKOS](https://www.w3.org/TR/skos-reference/) | Open-world lack of fact is not closed-world false; validation is not entailment |
| Finance/accounting / existing | Quantity/currency, posting/ledger, balancing law, settlement evidence | [Accounting atlas](dsls/domain_atlas.md#h-scientific-notation-clinical-queries-and-accounting) | Conversion/rounding/settlement cannot be inferred from displayed money |
| Chemistry/biology / existing | Molecular graph, reaction/stoichiometry, sequence/annotation and reference | [Notation research](notation_atlas.md#4-chemistry-composition-structure-and-process) | A balanced drawing is not physical feasibility, simulation or clinical evidence |
| Spatial/engineering/music / existing | Coordinate frame, geometry/constraint, signal/clock, event/score | [DSL atlas](dsls/domain_atlas.md), [timing research](interfaces/music_timing.md) | Same coordinate or tick is meaningless without frame/time-domain context |

The scan is broad, not exhaustive. ASD-STE100 and clap entrypoint fetches failed
in this pass; no detailed controlled-English or new CLI-framework claims are
derived from them. Lean and IUPAC remain discovery-level here. Standards and
domain-specific adapters need their own conformance profiles before execution.

## Knowledge Is Not One Tree Or One Truth Value

SKOS distinguishes concepts, labels, semantic relations and mapping relations.
BIBFRAME distinguishes Work, Instance and Item. OWL's open-world entailment and
SHACL's shape validation answer different questions. PROV distinguishes
entities, activities and agents, with extensibility and provenance of provenance.
[SKOS](https://www.w3.org/TR/skos-reference/),
[BIBFRAME](https://www.loc.gov/bibframe/docs/bibframe2-model.html),
[OWL](https://www.w3.org/TR/owl2-primer/), [SHACL](https://www.w3.org/TR/shacl/),
[PROV](https://www.w3.org/TR/prov-dm/).

**Nomi inference:** keep typed relations and ontology edition/context explicit.
Avoid equating `same_title`, `same_label`, `same_content`, `same_entity`,
`equivalent_under_model` and `authorized_for_use`. Mappings may be approximate,
directional, contested or time-limited. Contradictory imported records should
remain inspectable rather than silently collapse through name matching.

Preserve domain evidence states such as unknown, unsupported, conflicting,
refuted, expired and incomplete where meaningful. Do not replace core Bool with
a universal epistemic lattice; finite checks can still return Bool under stated
assumptions. Prediction confidence, measurement uncertainty, legal authority
and theorem proof status are not interchangeable numbers.

## Structured English And Documentary Domains

There are at least four separate operations:

1. Preserve authored prose and document structure, references and edition.
2. Lint against a declared audience/glossary/style profile.
3. Parse a deliberately controlled grammar into candidate domain structure.
4. Interpret/check that structure under a domain model, with human review when
   needed, before any authorized execution.

Akoma Ntoso provides legal-document vocabulary and structural interchange, not
a universal adjudicator. The existing Catala research studies executable rules
and exceptions under an authored formalization, not automatic legal validity.
BCP 14 gives particular meanings to uppercase requirement keywords within its
declared context; lowercase English is not automatically the same protocol.
[Akoma Ntoso](https://docs.oasis-open.org/legaldocml/akn-core/v1.0/os/part1-vocabulary/akn-core-v1.0-os-part1-vocabulary.html),
[Catala evidence](dsls/domain_atlas.md#c-logic-knowledge-policy-and-law),
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174.html).

Candidate `Clause`, `Obligation`, `Exception`, `DefinedTerm` and `Interpretation`
are library-owned values, with source provision, version, responsible author
and applicable context. Natural English never silently becomes Nomi control
flow. Ambiguity can be a typed collection of alternatives or unresolved draft;
it is not a reason to choose a parse and grant it execution authority.

Communication profiles should declare language, audience and purpose rather
than impose one English style on every domain or person. Retain original text
and translation/alignment evidence. A grammar/style checker can improve
consistency while leaving contested interpretation and social intent unresolved.
No legal advice, clinical interpretation or jurisdictional correctness is
claimed by these computational boundaries.

## A Domain Package Must Supply More Than A Pretty Surface

Candidate package contract, extending existing industrial/package rules:

| Boundary | Deliverable | Rejection example |
| --- | --- | --- |
| Meaning | Named domain, edition, values/operations, identity and equality laws | Unqualified name denotes different reference systems |
| Composition | Typed entry/exit, edge role, absence/failure and translation rules | Tensor output is wired to a table port by similar labels |
| State/time | Version/transition/retention/progress/consistency policy where relevant | Past version unavailable; latest fallback would change the question |
| Execution | Effect/capability/resource/task contracts and budgets | A plan captures a live file or serializes an authorization grant |
| Evidence | Assumptions, provenance, authenticity limits, completeness and redaction | A supplied hash is presented as verified approval |
| Tooling | Formatter, source maps, diagnostics and readable accessible fallback | Domain error exposes only backend coordinates |
| Interchange | Versioned codec/profile, loss policy and unknown-field behavior | Unsupported predicate erased by schema export |
| Evolution | Explicit migration/extension conflicts, tests, removal and unsupported-profile policy | Importing a package changes global punctuation or unrelated dispatch |

This is initially admission metadata and test evidence, not a proposed package
manifest schema. Existing registries/schemas can host a settled slice; avoid
building a new parallel framework before three packages demonstrate a shared
contract. A third-party package is an extension of the ecosystem, not authority
to redefine the evaluator or install execution hooks.

## Composition Must Preserve Meaning Across Boundaries

The vertical challenger combines domains deliberately:

```text
versioned catalog document
-> decoded source/evidence references
-> historical table/features under explicit temporal basis
-> train-only model artifact and evaluation
-> report/view with source and evidence context
-> revision/payload-specific review
-> separately authorized publication with uncertain-outcome handling
```

Every arrow is an explicit adapter. The catalog cannot prove the legal source;
temporal correctness cannot prove the learning objective; good metrics cannot
grant publication permission; rendering a report cannot send it. This tests
cohesion more usefully than separate features with no composed failure path.

The [target-only program](../design/targets/research/domain_layers.nomi) uses
ordinary data/functions/Result/match and fictional APIs. The
[local composition probes](data_workflows/composition_experiments.md) challenge
selected identity/time/update/state/review laws. Neither typechecks or executes
the target or establishes usability across disciplines.

## Philosophy To Implementable Obligations

The prior [primary philosophical readings](cognition.md#actionable-translation-map)
remain the historical evidence. The translations below are **our engineering
inferences**, not an assertion that past thinkers endorse this design.

| Lens | Concrete domain obligation | Falsifying program / destination |
| --- | --- | --- |
| Leibniz: explicit representations and calculi | Inspect definitions, relation meanings, edition and translation assumptions | Catalog title conflates two works; source/reference metadata and resolver diagnostics |
| Boole: operations with domains and laws | State algebra and side conditions before rewriting or incrementality | Deleted minimum or nonassociative Float; domain-law fixtures and optimizer admission |
| Dijkstra: all-path reasoning and progress | Declare state transitions, invariant, failure/cleanup and progress/budget obligations | Acyclic job starves or send outcome unknown; runner/transaction/effect protocols |
| Iverson: notation as thought tool | Compare explicit calls with domain notation and accessible equivalent views | Tensor binder clearer only to experts; formatter/diagnostic and reader trial |
| Hoare/Turing: assumptions and formalization limits | Keep model-relative proof separate from truth/purpose and incomplete search | Solver timeout or wrong objective; typed evidence payload, not Boolean success |
| Engelbart/Suchman: situated augmentation | Let people inspect, revise and repair the model with bounded authority | Support runbook's assumptions fail; observed state, checked proposal and human escalation |

Modern programming-language mechanisms are compared through the existing
[44-language matrix](language_feature_matrix.md) and
[cross-language convergences](convergences.md): algebraic data, explicit effects,
structured concurrency, protocol composition, staged descriptions and domain
notation. Borrow laws and pressure-test interactions; fame is not admission
evidence, and no claim of historical novelty is made here.

## Experiments And A Finite Next Step

| ID | Candidate comparison | Stop or promotion gate |
| --- | --- | --- |
| DC1 | Domain-owned payload plus shared diagnostic envelope versus one universal graph/object IR | Data, numeric and documentary example; reject erased identity/edge/time laws |
| DC2 | Ordinary package/protocol composition versus scoped tool for one representative domain | Beginner, production and failure-heavy forms; no grammar without comprehension/error-locality evidence |
| DC3 | Versioned vocabulary mappings and catalog work/instance/item references | Conflicting labels/editions and partial mapping; preserve disagreement rather than assert exact equivalence |
| DC4 | Controlled clause parsing versus authored structured rule, with original prose/alignment | Ambiguity/version/jurisdiction visible; no unsupervised legal interpretation or prose execution |
| DC5 | Cross-domain report/train/review/publish fixture | Every type/effect/region resolves, source-local errors and independent value/authority/evidence vectors |
| DC6 | Add a new domain package using only existing foundations and documented adapters | No edits to global grammar/evaluator for the baseline; record actual missing core contracts and remove redundant abstraction |

First close a typed descriptor/snapshot/lifecycle slice against D1-D3. Then
compare one data package, one numerical package and one documentary package
under DC1/DC5. Keep the broader map as a discovery frontier, not hundreds of
simultaneous implementation commitments. New evidence should change a candidate,
close a fork, or expose a missing contract; otherwise stop collecting examples.
