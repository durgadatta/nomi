# Haskell

> Status: comparative evidence, deepened 2026-10-10; 2010 baseline and scoped GHC extensions.

The Haskell 2010 report defines the baseline. Extension observations below use
GHC **9.12.2** documentation, a pinned comparison version rather than a claim
about the latest compiler. No GHC execution, proof or reader study ran here.

## Demand And Function Composition

Haskell 2010 has non-strict semantics, curried application, sections and pattern
bindings. Demand determines whether a subexpression is needed; non-strictness
is a semantic property, not a promise about one implementation's allocation.
[Expressions](https://www.haskell.org/onlinereport/haskell2010/haskellch3.html).

**Nomi judgment:** keep pure composition and explicit algebraic alternatives;
retain eager ordinary calls and explicit adapters. Default currying or laziness
would change failure timing, callback counts and retention throughout the target.
An explicit Stream can offer demand-driven work without turning List into a lazy
value through pipeline syntax. Losing convenient infinite structures and terse
composition is a deliberate cost, still open to challenge through whole programs.

GHC bang patterns force an expression to weak head normal form; strictness
extensions have stated scope. This is not necessarily deep evaluation of every
field or an assurance of constant memory.
[Strictness](https://downloads.haskell.org/ghc/9.12.2/docs/users_guide/exts/strict.html).

## Abstraction, Dictionaries And Coherence

The report combines polymorphic inference with type classes, instances and kinds.
A class describes required operations for instances; a higher-kinded abstraction
can describe a type constructor, not just an element type.
[Types and classes](https://www.haskell.org/onlinereport/haskell2010/haskellch4.html).

GHC supplies explicit policies for overlapping/incoherent instances and restrictions
on instance resolution; relaxing termination restrictions can permit typechecking
loops. These are extension choices, not properties of every Haskell program.
[Instance resolution](https://downloads.haskell.org/ghc/9.12.2/docs/users_guide/exts/instances.html).

**Nomi hypothesis:** compare explicit operation dictionaries with imported,
compiler-resolved protocols. A protocol signature alone does not prove its laws.
An inferred operation must expose the selected implementation and why it won.
Higher-kinded abstractions may reduce repeated carrier-specific code, but their
inference and learning cost must be compared with concrete List/Stream/Result
APIs. Do not import global instance selection, overlapping resolution or monad
vocabulary as the price of ordinary function use.

## Effects Are Values, But Values Are Not Total Proofs

The 2010 library specifies mapping and sequential composition through Functor
and Monad, with identity/composition and sequencing laws. These abstractions
describe reusable operation shapes across carriers. The report's `return` method
injects a value into a carrier; it is unrelated to Nomi's function-exit keyword.
[Control.Monad](https://www.haskell.org/onlinereport/haskell2010/haskellch13.html).

**Nomi hypothesis:** compare carrier-specific `map`/fallible composition with a
shared operation dictionary. A single name must not imply that List, Option,
Result, Stream, and a cold task have identical execution meaning. State how each
carrier handles missing input, first failure, accumulation, repeated consumption,
and cancellation. Lawful abstraction can reduce duplication; its learning and
inference cost needs the same whole-program evidence as any new syntax.

The report models I/O actions through `IO`; constructing/composing an action and
performing it are distinct. Sequencing provides an account of effect order.
[Basic I/O](https://www.haskell.org/onlinereport/haskell2010/haskellch7.html).

**Nomi implication:** public effect information and explicit starting of cold work
can preserve similar distinctions in Nomi's direct call model. An `IO`-inspired
carrier is not itself a capability grant. Pure code may diverge or encounter a
partial operation; an algebraic result type does not enumerate every abnormal
exit. Laws need side conditions for demand, failure and observational equivalence.

## Representation And Resource Use

GHC roles distinguish nominal, representational and phantom dependencies,
constraining when a representational coercion is sound.
[Roles](https://downloads.haskell.org/ghc/9.12.2/docs/users_guide/exts/roles.html).

GHC linear arrows describe consumption multiplicity: when a result is consumed
once, a linear argument is consumed once. This is a function/type discipline,
not simply "run a destructor at lexical exit."
[Linear types](https://downloads.haskell.org/ghc/9.12.2/docs/users_guide/exts/linear_types.html).

**Nomi implication:** representation sharing must not erase nominal identity or
protocol selection. Borrowed regions, copyability, callback retention, use counts
and cleanup outcomes are separate facts. Linear, affine, region-based and dynamic
revocation candidates should be compared on the same escape cases. A declaration
of purity cannot establish either multiplicity or timely release.

## Integration Choices

| Pressure | Candidates | Cost or conflict |
| --- | --- | --- |
| Reuse operations across carriers | Concrete APIs; first-order protocols; higher-kinded dictionaries | Generic power versus readable inferred signatures and decidable resolution |
| Select a numeric/codec behavior | Explicit dictionary; coherent imported instance | Local choice versus plumbing; imports must not silently change meaning |
| Avoid unnecessary work | Eager values; explicit demand-bearing Stream/plan | Callback count, retained thunks, partial results and resource ownership |
| Wrap a concept efficiently | Nominal data with optimized representation | Representation equivalence must not imply domain substitutability |
| Prevent resource misuse | Region/non-escape rules; affine/linear uses; checked runtime handles | Each protects different cases; none alone establishes fallible cleanup composition |

These candidates do not accept Haskell syntax or reopen Nomi's rejected sections,
equation functions and automatic partial application by resemblance.

## Discriminating Cases

1. Consume two transformed items from three, with a supplied error in the third.
   State the List versus Stream callback count, error timing and remaining owner.
2. Sort one domain using ascending and descending order dictionaries. Record the
   selected evidence and whether an unrelated import changes a previously checked call.
3. Apply an allegedly associative operation to exact integers, floating values
   and a callback that can fail. Compare the admitted law and observable order.
4. Generalize a stateless factory result and a closure retaining one mutable slot
   at Int and Text. A universal scheme must not erase shared storage.
5. Coerce between same-representation domain wrappers with different validation or
   protocol behavior. Preserve the published nominal boundary.
6. Retain a scoped handle in a returned closure/task and in an error payload.
   Compare consumption, escape and release evidence through whole completion.

The expectations are prepared, not Haskell/Nomi conformance. Existing owners:
[functions](../features/functions.md), [effects](../features/effects.md),
[collections](../features/collections.md), [resources](../features/resources.md)
and [types/data](../features/types_data.md). The
[maintainer guide](../synthesis_guide.md) supplies the integration loop.
