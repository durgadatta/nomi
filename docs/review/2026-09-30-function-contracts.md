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

Compare explicit function-value and generic declaration spellings without
overloading existing punctuation, then type map/fold, decode, and run_scope.
No interpreter migration is justified for this still-open contract.
