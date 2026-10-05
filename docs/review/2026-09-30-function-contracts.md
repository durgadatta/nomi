# Function Contract Design Checkpoint

> Status: dated design evidence; no typechecking/conformance claim or live backlog.

Packet: `docs/research/features/functions.md`,
`docs/design/function_contracts.md`,
`docs/design/function_contracts_target.nomi`.

## What Changed

The broader research makes callback/effect typing a prerequisite for richer
interfaces rather than a detail to leave to implementation. The proposal now
compares pure-only strict callbacks with effect-polymorphic callbacks using
abstract signatures and explicit order/retention contracts. It recommends the
former initially but keeps the latter open pending full-program evidence.

Purity cannot be defined solely by an empty world-effect set: captured mutation,
clock/random observations, termination, panic, and cost require separate facts.
Cold-task construction and execution similarly need separate footprints, with
captured resource regions retained. These facts are not all represented by the
current function interface model.

## Documentation Gap And Correction

The feature comparison already says constructor values remain open, but two
canonical syntax snippets and the new interaction target passed constructors
directly to `map_error`. Replace them with explicit lambdas. The historical
`target.nomi` is superseded and is not rewritten into an apparent active fixture.
This corrects a source example assumption, not the semantics of constructors.

Generic declarations, function type syntax, protocol coherence, effect subtyping,
encapsulated mutation checks, and region inference remain open. Abstract
signatures are marked metalanguage. A new packet does not silently turn any
of these recommendations into an accepted contract.

## Current Implementation Boundary

Current callable/runtime layers execute callbacks but do not establish this
proposal's static purity, retention, region, or effect-variable guarantees.
Python class/function behavior and host exceptions cannot serve as their oracle.
Use the existing typed Surface/schema boundary for a future gated producer,
then test independently of parser and host. Do not add runtime flags claiming
static guarantees based solely on these docs.

Three unaccepted type-spelling candidates are now compared: a parameter-list
constructor, a function-type literal, and a domain protocol. None yet settles
named/default parameters, effect-kind variables, or generative resource regions.

## Paper Audit Follow-Up

Manual substitutions now cover the invoice's map/fold, explicit submission error
conversions, and List[Result] row assessment. They remain conditional on proposed
scalar/collection/decoder contracts; no typed producer executed them. A trace
distinguishes independent ordinary row errors from a fail-fast effectful loop.

The resource derivation deliberately stops at generative regions, retained
captures and completion payloads. It exposes a substantive gap: Err(E), nested
causes and diagnostics can retain a handle just as Ok(A) can. The resource
proposal now includes this whole-completion export gate. Cold tasks additionally
need a construction/start authorization rule; no-body-execution alone does
not establish pure factory eligibility.

Named/default callback arguments expose another fork: exact positional contracts
with explicit adapters versus compatible call-shape subtyping. This is recorded
beside the source candidates instead of pretending punctuation settles arity.
The audit also removes an accidental expected `InvalidIdentity` edit error:
duplicate IDs in raw input belong to decode, while duplicates in an owned
Invoice violate its invariant and take the abnormal panic path. No target
program was executed to claim this policy is implemented.

Live steps belong to [function acceptance](../design/function_contracts.md)
and D1-D4 in [the redesign agenda](../design/redesign_agenda.md). This packet
remains `designing`; the next step is a source/formatter comparison for generic
and function-value type declarations followed by positive/negative typed facts.

## Validation Scope

Validation: ten documentation lifecycle/packet tests passed, five registered
packets passed coherence checks, and local links across 134 Markdown/target
files resolved. `git diff --check` passed. They establish discoverability, not
callback inference, typeability,
source conformance, effect propagation, or region safety. No actual typed
artifact, solver, partial-program evaluator, or UI experiment is produced here.
The paper-audit follow-up also passed 63 resource/docs/packet tests and agent
doctor checks; local links were checked outside fenced code and the ignored
RAG index was refreshed. The source counterexamples remain design fixtures.

## Original September Retrospective

### September Evidence

Koka supplies a concrete higher-order effect alternative. Typed holes and
projection laws show why an editor cannot simply guess missing type facts.
The invoice and import programs make retained captures and expected errors
observable even without a new source notation.

### September Friction

Examples can settle open API questions by accident. A constructor passed as a
callback looks innocent while assuming a first-class callable contract. Keep
abstract signatures separate from accepted source and use explicit long forms.

### September Improvement

Register the function contract packet using the existing function evidence page,
correct constructor-callback examples, and route the agenda to its admission
gates instead of duplicating generic/effect research in every interface thread.

### September Next Step

Select a call-shape rule and compare the explicit function-value/generic candidates
at 80/100 columns. Close construction/latent authority and whole-completion
region rules, then produce checked map/fold, decode and run_scope facts.
No interpreter migration is justified for this still-open contract.

The generic-operation continuation below extends this same packet; the original
September observations and validation above remain historical evidence.

## Generic-Operation Continuation 2026-10-04

### Pass 1: Source Mechanisms And Property Hierarchy

The user requested pragmatic functional abstractions across paradigms, including
map/reduce/filter, pipe, object methods, hash/serialization, caching, tap,
accumulation, repeat and fixed points. The
[cross-cutting chapter](../research/generic_operations.md) develops a capability
graph from small value/callable/structure/state/law/policy facts. Selected primary
sources cover Wolfram, Haskell, Common Lisp, Python, ECMAScript, pandas, Clojure,
Rust, Java, Kotlin, Lodash, RxJS and Serde, with pinned/rolling/fetch limits.

Important corrections: Java Object methods are broadly present but Serializable
is opt-in; hash is not a persistent identity; Haskell fix is not operational
numerical iteration; pandas pipe passes the whole frame rather than its cells.
Higher-order functions and generic object protocols share useful design pressure
without becoming one universal Function/Object superclass.

The [canonical contract continuation](../design/function_contracts.md#generic-operation-continuation)
and [three-program challenger](../design/targets/research/generic_operations.nomi)
keep existing call/pipeline shapes. Their cache/codec/observer/iteration facades
are fictional, not public APIs or a static capability checker. No notation,
generic spelling, core IR, callback-effect choice or production library was
accepted. GA1-GA8 refine existing D1-D3 and open questions.

### Pass 2: Counterexamples And Evidence Checks

Twelve [local probes](../research/features/probe_generic_operations.py) record
strict/fused call and failure order, reduction direction/seed/history,
nonassociativity, row outcomes, tap mutation/failure, demand, repetition,
bounded stopping, stale captured cache state and wrapper order, hash eligibility,
encoding profiles and aliased accumulator histories. Their
[capture](../research/features/generic_probe_results.json) retains per-case
limits and explicit unperformed execution flags. Forty focused tests passed.
These are Python-host and original finite-model evidence, not Nomi or foreign
library conformance; concurrency, authority, numerical proofs and human trials
remain unperformed.

The repository matrix check caught a real topology mismatch: a supplemental
chapter placed in the feature-category directory appeared to require another
matrix row. Moving it to cross-cutting research preserved the thirteen category
reviews without weakening the coverage test or copying a new comparison axis.
The repaired focused/docs/packet/matrix run passed 53 tests. The maintained
capture checker rejects ambiguous metadata, wrong JSON types and scope/outcome
drift, preserves historical version differences and never rewrites evidence.

### Pass 3: Integration Audit

Registry routing, research indexes, function/collection evidence, text/domain/ML
continuations and the target index now route to the same owner. All five design
packets and target-direction inspection passed. Parser, runtime, samples and
generated web assets were not changed. Integration checks also caught the
required research-target header marker and duplicate historical retrospective
headings that confused the existing registry's first-heading lookup. The target
marker and historical heading names were corrected without weakening validators.
The repaired target/probe run passed 44 tests and the packet/docs run passed ten.
A changed-document audit resolved 466 local links/anchors. The final full Python
suite passed 1,573 tests with 76 skipped and four existing Jupyter path
deprecation warnings. All agent-doctor checks passed after refreshing the ignored
RAG index; the agent/docs/packet regression slice passed 17 tests. Lint,
formatting, capture reproduction and whitespace checks passed. No browser trial
or Nomi/foreign generic-operation conformance was performed.

## Pass Retrospective

### Evidence That Changed The Design

Equal output values do not establish identical execution order or failure
prefixes. Receiver identity does not include changing receiver state; returning
the same value does not make tap an identity operation. Bounded stopping needs
reason/evidence, while reusable caches need explicit context and ownership.
Keep the hierarchy conditional and the pure/effectful callback fork open.

### Workflow Friction

Some primary documentation is rolling, redirects between editions or lacks
extractable content. Pinned/fetch limits remain explicit. The category-directory
check additionally distinguished a useful cross-cutting research chapter from
another feature row; research breadth must not silently expand target taxonomy.

### Durable Improvement

The existing function packet now routes generic-operation prompts and validates
the twelve-probe capture and forty focused tests. The existing matrix invariant
remains intact. No new packet, agent instruction, universal metadata framework
or runtime flags were justified by these bounded observations.

### Next Pass

Use GA2/GA3/GA8 to produce D1-D3 positive/negative typed facts for strict map,
seeded scan and conditional Eq/Hash/codec support. Then challenge the context-
bound cache and fallible observer long forms under region/effect contracts.
Retain explicit statements/loops when they make control clearer. Compare one
settled adapter on CLI/browser before adding shorthand or runnable samples;
the hierarchy is not a mandate to implement every cataloged combinator.

## Research Gap Continuation, 2026-10-04

This continuation documents the accepted audit finding, not an accepted language
feature. [Polymorphic sharing](../research/features/functions.md#polymorphic-sharing-and-generalization)
owns the detailed counterexamples, alternative generalization policies and
unperformed D1/D3 subexperiment. Existing GA1-GA8 and the current call contract
retain their scope; no generic notation, checker or new probe was added.

**Evidence That Changed The Design:** the selected OCaml 5.5 evidence exposes
state retained between apparently identity-shaped calls. Callable shape and
per-invocation purity are insufficient reasons to generalize shared storage.
The research now compares conservative restriction with justified relaxation
and explicit state ownership; no alternative has been selected.

**Workflow Friction:** callback effects, local mutation and inference are already
open, but their prior coverage did not preserve a sharp soundness discriminator.
A named subexperiment prevents that obligation from becoming either a second
generic backlog or a premature prohibition on all useful local inference.

**Durable Improvement:** the existing function owner, research indexes, question
2/3 and registry now expose the delayed-identity and factory-isolation cases.
The dossier records normal-form/inspection requirements and three program
levels while retaining the unperformed boundary. No framework, agent instruction
or maintained runtime abstraction was justified by this documentation pass.

**Next Pass:** compare frontend-neutral positive/negative generalization facts
under D1/D3, including shared mutable captures, independent factories and
immutable covariant results. Record rejection location and any lost useful
inference. Only evidence that distinguishes the alternatives can select a rule;
documentation checks or host-language examples do not prove Nomi soundness.
