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

## Pass Retrospective

### Evidence That Changed The Design

Koka supplies a concrete higher-order effect alternative. Typed holes and
projection laws show why an editor cannot simply guess missing type facts.
The invoice and import programs make retained captures and expected errors
observable even without a new source notation.

### Workflow Friction

Examples can settle open API questions by accident. A constructor passed as a
callback looks innocent while assuming a first-class callable contract. Keep
abstract signatures separate from accepted source and use explicit long forms.

### Durable Improvement

Register the function contract packet using the existing function evidence page,
correct constructor-callback examples, and route the agenda to its admission
gates instead of duplicating generic/effect research in every interface thread.

### Next Pass

Select a call-shape rule and compare the explicit function-value/generic candidates
at 80/100 columns. Close construction/latent authority and whole-completion
region rules, then produce checked map/fold, decode and run_scope facts.
No interpreter migration is justified for this still-open contract.
