# Scala

> Status: comparative evidence, deepened 2026-10-10; Scala 3 mechanisms and
> explicitly experimental capture checking, not accepted Nomi additions.

## Scope And Sources

This review studies how Scala combines functional abstraction, object models,
contextual resolution, nominal representations, and staging. The official
reference is a living source; this pass did not run a compiler or establish
cross-version conformance. Capture/separation checking is scoped separately
from the established Scala 3 features below.

## Contextual Abstraction And Selection

Scala 3 `given` definitions supply contextual values, and `using` clauses make
contextual requirements part of a signature. A caller can pass a value explicitly
or let contextual search supply it. Context bounds abbreviate such requirements.
This supports reusable algorithms parameterized by operations without putting
all operations on the data's class.
[Primary references: givens](https://docs.scala-lang.org/scala3/reference/contextual/givens.html),
[using clauses](https://docs.scala-lang.org/scala3/reference/contextual/using-clauses.html).

**Nomi inference:** start with an explicit operation value, then compare a
compiler-selected protocol implementation. The useful idea is separating an
algorithm from its supplied behavior. Automatic search adds another question:
can a reader identify that behavior from the call and its package contract?
Test two orderings for the same nominal type, nested contextual definitions,
and imports that offer competing implementations. Record selection, ambiguity,
search cost, and whether an unrelated dependency changes the answer.

Contextual convenience does not establish an operation's algebraic laws or
permission to access the world. A sorting interface can be well typed while
providing an inconsistent comparison. An automatically supplied filesystem
handle still requires authority and lifetime reasoning.

## Nominal Meaning With A Shared Representation

Opaque type aliases hide representation outside their defining scope while
allowing the implementation to use it within that scope. This can distinguish
concepts without exposing a wrapper representation to clients.
[Primary reference: opaque types](https://docs.scala-lang.org/scala3/reference/other-new-features/opaques.html).

**Nomi inference:** compare a nominal owned product, an opaque library type,
and a checked newtype-like abstraction for identifiers, units, and validated
text. Admission requires a constructor/decoder boundary, equality and hashing
rules, exported operations, and an account of representation inspection and
foreign conversion. Avoid treating equal storage layouts as permission to
exchange domain values. Reduced allocation is a performance hypothesis until
measured on supported backends.

## Patterns And Stages

Extractors let patterns invoke library-defined decomposition through mechanisms
such as `unapply`. They can hide computation behind a representation-like form.
[Primary reference: pattern matching](https://docs.scala-lang.org/scala3/reference/changed-features/pattern-matching.html).

The accepted Nomi alternative remains an ordinary classifier call followed by
an inert structural match. This exposes invocation count and a classifier's
failure result. It costs concise virtual-view composition. A credible extractor
challenger must specify termination, authority, caching, and coverage analysis;
calling an extractor pure would not establish all four.

Scala 3 macros use typed quotations and splices, with staging-level and scope
rules governing which local values can appear in generated code. Its reference
also addresses type evidence across stages and scope extrusion.
[Primary reference: macros](https://docs.scala-lang.org/scala3/reference/metaprogramming/macros.html).

**Nomi inference:** expression data, typed code generation, and compiler
execution need distinct contracts. A quoted expression may refer to a lexical
binding; moving it into another scope must preserve identity or fail. A generated
codec needs inspectable output and source locations. It need not grant arbitrary
compile-time filesystem access. Compare ordinary builders and schema-derived
code before general user macros.

## Capabilities That Travel With Values

Scala's experimental capture checking tracks capabilities reachable through
values; separation checking extends the work toward alias control. The official
overview explicitly labels both extensions experimental.
[Primary reference: tracked capabilities](https://docs.scala-lang.org/scala3/reference/experimental/capture-checking/overview.html).

This is relevant to Nomi's GC-based profile: keeping memory alive does not
justify keeping a scoped resource or permission alive. A callback can hide a
reader, mutable cell, or authority handle. Compare capture tracking, explicit
region parameters, and an escape-rejecting scoped callback contract. Keep
static reachability, effect declarations, and runtime grants separately visible.
Do not import an experimental system as an established resource guarantee.

## Integration Choices And Costs

| Pressure | Nomi alternatives to compare | Cost or conflict |
| --- | --- | --- |
| Reusable operation families | Explicit dictionaries; coherent protocols | Call verbosity versus search and package reasoning |
| Lightweight nominal concepts | Owned wrappers; opaque representation | Allocation/layout versus boundary inspection |
| Domain decomposition | Classifier then match; bounded extractor challenger | Named intermediates versus hidden invocation |
| Generated implementation | Ordinary builders; derived metadata; staged macros | Repetition versus compiler authority and phase complexity |
| Escaping captured handles | Explicit regions; capture tracking; fenced callbacks | Annotation burden versus expressiveness |

## Prepared Discriminators

1. Sort the same identifiers using lexical and numeric ordering. Both behaviors
   must remain nameable; adding an import must not silently select the other.
2. Compose two packages that independently supply the same operation family.
   Require a stable selection or an ambiguity diagnostic with both origins.
3. Pass an unvalidated string into an opaque identifier API. Compare the internal
   constructor and external decoder without allowing representation equality
   to bypass validation.
4. Classify a domain value with a counting/failing function before matching.
   Compare any extractor challenger against that invocation and failure trace.
5. Generate a closure referring to a local identifier, then move the generated
   fragment across a scope boundary. Require preserved binding or a source-located
   rejection, including the generator's provenance.
6. Return a closure capturing a scoped reader and start it in a child task.
   Identify which contract rejects the escape and which owner releases the reader.

These are prepared research cases, not executed Scala/Nomi comparisons. Continue
through [functions](../features/functions.md), [types/data](../features/types_data.md),
[resources](../features/resources.md), [metaprogramming](../features/metaprogramming.md),
and the [maintainer synthesis guide](../synthesis_guide.md).
