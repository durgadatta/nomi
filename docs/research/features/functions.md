# Functions And Calls

> Status: comparative evidence; core accepted, generic callback contracts open.

Packet: `docs/design/function_contracts.md`,
`docs/design/function_contracts_target.nomi`,
`docs/review/2026-09-30-function-contracts.md`.

The [generic-operation continuation](../generic_operations.md) researches a
pragmatic hierarchy beyond FP doctrine: call adapters, carrier-specific
map/filter/fold/scan, method/pipe/tap interfaces, bounded repetition/fixed points,
stateful caching, and conditional equality/hash/codec capabilities. Its GA1-GA8
comparisons and bounded probes belong to this same packet. No universal object
methods, generic type syntax or new runtime API is admitted.

User pressure: know which arguments a transformation receives and where it
returns without reconstructing shorthand rules.

| Evidence | Mechanism | Nomi judgment |
| --- | --- | --- |
| [Ruby](../languages/ruby.md) | Callable variants differ in return and arity | One anonymous expression form. |
| [Haskell](../languages/haskell.md), [OCaml](../languages/ocaml.md) | Curried composition | Explicit lambdas instead of implicit partial application. |
| [Scheme](../languages/scheme.md) | Lexical first-class functions | Preserve lexical environments with explicit calls. |
| [Julia](../languages/julia.md) | Library-defined execution of callbacks | Admit callback contracts before optimizing their calls. |
| [Koka evidence](../design_frontiers.md#2-higher-order-effects-need-a-real-type-model) | Row-polymorphic callback effects | Compare effect propagation with pure-only strict transforms. |

```nomi
func add_tax(amount: Int, tax: Int) -> Int:
    return amount + tax

with_tax = (amount) => add_tax(amount, 2)
```

The long form gives behavior a name. The lambda only maps explicit inputs to
one expression; multi-step logic moves to a function. The pipeline inserts its
left value into an ordinary first argument and does not manufacture parameters.

Costs include extra lambdas and helpers, especially in builders. The accepted
surface does not yet settle generic declarations, function-value effect types,
statement callbacks, constructor values, or protocol resolution. Target demos
must not conceal these by passing a variant constructor directly to `map_error`.
Use `(error) => ErrorKind(error)` until that contract is admitted.

**Experiment:** format a beginner callback, a report builder, and an effectful
callback at 80/100 columns. Require input types, resolved effects, and return
targets to be inspectable. Compare a pure-only collection API with an explicitly
effect-propagating proposal. Keep signatures open rather than force fake purity.
The [focused proposal](../../design/function_contracts.md) now owns abstract
signatures, purity/capture distinctions, order, retention and admission gates.
Its initial pure-only recommendation remains unaccepted.
The manual derivation of invoice, submission and row-result calls is conditional
on proposed APIs. The resource and cold-task derivations deliberately stop at
region/error payload and authorization-timing gaps; no typechecker ran.

**User-facing gate:** hover and diagnostics must agree with actual calls and
show callback effects before supported playground promotion.
[Target](../../design/targets/functions.nomi).

## Polymorphic Sharing And Generalization

> Research extension checked 2026-10-04. These are competing type contracts,
> not admitted generic syntax, inferred compiler facts, or runtime changes.

### Existing Coverage And New Pressure

The function packet already separates callback arity, effects, capture regions,
retention, and ordinary versus abnormal completion. The
[type compatibility questions](../../design/function_contracts.md#type-compatibility-and-inference-questions)
explicitly leave function subtyping, variance, and generic bounds open.
[Bindings](binding.md) distinguish immutable names from captured mutable cells.
What is not yet compared is **when one computed value can be generalized and
reused at several types**, especially when it hides persistent state.

This is a soundness pressure within open questions 2/3/4/10 and the registered
`function-contracts` packet, not a new notation proposal. An immutable binding
to a closure is not proof that the closure's captured state is immutable. An
empty world-effect set is not proof that independent type instantiations use
independent storage. Conversely, rejecting every locally stateful computation
may unnecessarily restrict a function whose scratch state never escapes.

### Checked Primary Evidence

The [OCaml 5.5 manual, polymorphism and its limitations](https://ocaml.org/manual/5.5/polymorphism.html)
was checked on 2026-10-04. Its weak-polymorphism/value-restriction discussion
uses functions hiding persistent references to explain unsafe generalization.
Its relaxed value restriction uses covariance to recover some safe
generalizations; abstract types must expose sufficient variance information.
These are OCaml-specific rules and costs, not a proof that Nomi needs the same
restriction, subtyping model, or annotation syntax.

The [Koka evidence](../design_frontiers.md#2-higher-order-effects-need-a-real-type-model)
remains relevant to the challenger effect model. Effect polymorphism alone
does not select Nomi's generalization, state encapsulation, region, or public
interface rule. No new theorem about Koka is claimed here.

### A Sharp Counterexample

Original contract metalanguage, not executable Nomi source:

```text
create_delay():
    create one mutable saved slot, initially absent
    return a closure that, for argument x:
        remembers the previous saved value
        saves x
        returns the previous value, or x when initially absent

delay = create_delay()
first = delay(1)
second = delay("next")
```

If one shared `delay` is independently treated as `A -> A` at both calls, the
second call can return an Int where its instantiation predicts Text. This is
a counterexample to that hypothetical generalization rule, not a bug report
about the current prototype. Giving the shared slot one monomorphic element
type prevents the mismatch. Calling a suitably generic factory separately for
each element type can create separate slots; that is a different program.

The test must include a genuinely stateless identity obtained through an
ordinary call. A syntactic restriction may reject this harmless computed value
too. The design question is both soundness and the cost of conservative repair.

All candidates also need the ordinary generalization boundary: do not quantify
type variables fixed by the surrounding monomorphic typing environment. A
declared function or lambda can capture a slot allocated outside its invocation;
being an eligible value form does not give that slot a fresh element type at
each call. A wrapper around the shared delayed-identity slot must preserve the
same monomorphic obligation, unlike a factory that allocates a fresh slot.

### Competing Contracts

| Candidate | Generalization boundary | Strength | Cost or unclosed obligation |
| --- | --- | --- | --- |
| Conservative value restriction | Generalize eligible variables in declared functions/value forms, excluding those fixed by the environment; computed state-bearing values remain monomorphic | Small local rule; hidden storage cannot silently acquire independent element types | Safe computed identities may need an explicit wrapper; determine which Nomi forms are eligible |
| Relaxed generalization | Admit additional generalization using proven variance and absence of writable shared positions | Recovers useful immutable collection/factory results | Requires constructor variance, abstract-interface metadata, and a sound interaction with captures/regions |
| Effect/region-aware generalization | Generalize when typed state and escape facts establish safe instantiation | Can distinguish encapsulated scratch state from persistent shared state | Empty world effects are insufficient; inference, separate compilation, and diagnostic complexity need evidence |

These are challengers, not three features to add. The first two also need a
rule for explicit public generics; a declaration cannot assert a universal
result type inconsistent with storage allocated once outside its invocation.
Generic factories, polymorphic values, and one monomorphic factory result must
remain distinguishable in hover and interface artifacts.

### Edge Matrix

| Case | Fact that must remain visible | Discriminator |
| --- | --- | --- |
| Declared stateless identity at Int and Text | Each call's type substitution | Do not reject ordinary generic reuse solely because there are two calls |
| Computed stateless identity returned by a factory | No persistent writable state, if established | Record safe acceptance versus conservative rejection and repair cost |
| Delayed identity with one captured slot | Both calls share the same storage | Reject incompatible instantiations or provide a declared monomorphic type |
| Declared function/lambda wraps an outer shared slot | Its element type is fixed in the surrounding monomorphic environment | Value eligibility cannot freshly quantify the captured slot at each use |
| Two fresh stateful factory results | Distinct allocation/capture identities | Do not conflate separate state with independent instantiation of shared state |
| Empty immutable collection with unknown element type | No writable alias into its elements | Compare safe generalization with an explicit element annotation |
| Mutable cell containing a function | Writes can change the callable stored for all aliases | Covariant reading alone cannot justify accepting incompatible writes |
| Opaque imported collection | Variance and mutation facts available through its public interface | Separate checking must not inspect private implementation to guess safety |
| Closure/task result retaining a borrowed handle | Region travels through the result | Generalization must not erase the existing whole-completion escape obligation |
| Generic cache retains results or arguments | Storage and key/result types are shared across calls | Generalize the factory or cache operation only under a stated storage contract |
| Recursive or polymorphically recursive helper | Instantiation at recursive uses | Require a stated annotation/decidability policy; do not imply local inference solves every case |

Parameter contravariance/result covariance are comparison vocabulary, not an
accepted Nomi subtyping rule. An initially invariant generic model is also a
credible restriction to compare. Mutable host values cannot be made safe by
describing only their immutable wrapper names.

### Nomi Normal Form And Inspection

Placement: core type/binding contract plus versioned module-interface metadata;
cache/collection protocols remain library contracts. No new source token is
needed to state the question. Proposed analysis normal form:

```text
evaluate initializer once
-> identify shared allocations and captured cells/regions
-> infer one provisional monomorphic contract
-> exclude variables fixed by the surrounding monomorphic environment
-> decide which variables may be universally quantified
-> publish the scheme and any remaining monomorphic obligations
-> instantiate permitted variables at each use
-> check calls, writes, effects, and escapes against that contract
```

An inspector should distinguish a quantified type variable from an unresolved
or fixed monomorphic variable, relate the storage/capture origin to a failed
use, and show why a computed value was not generalized. Do not expose an
implicit Any as a repair. Compare an element annotation, a fresh factory call,
and an explicit adapter; do not suggest eta-expansion without checking whether
it changes allocation frequency, timing, default evaluation, or identity.

### Named Subexperiment Under Questions 2 And 3

**Subexperiment: shared-state generalization.** Compare the candidates above
under the existing function packet and its D1 typed-contract gate.

| Program level | Prepared inputs | Required observations |
| --- | --- | --- |
| Beginner | Stateless identity used at Int/Text; computed identity; empty immutable list | Inferred contract, call substitutions, acceptance/rejection, formatted annotation or wrapper repair |
| Production | Generic decoder/cache factory; opaque immutable collection imported through an interface; two independently allocated caches | Public quantified variables, storage ownership, variance facts and separate-checking result |
| Failure-heavy | One delayed-identity slot used at incompatible types; declared wrapper capturing an outer slot; mutable function cell; escaping resource closure/task; recursive helper | Negative judgment at the conflicting use/capture, no erased region, no hidden shared-type mutation |

Start with paper judgments and explicit allocation diagrams, then a removable
type-model spike if the judgments distinguish viable candidates. Include the
same public interface without implementation source. A successful experiment
records sound rejection *and* the recognition/repair cost of benign rejection;
it does not merely count accepted snippets.

Falsifiers: a claimed safe rule admits the shared-slot mismatch; an imported
opaque type needs private inspection; a region disappears during instantiation;
or a recommended repair silently changes storage multiplicity. Remove a more
permissive candidate if its necessary facts cannot be supplied locally or its
diagnostics routinely require reconstructing hidden allocation history. Retain
the explicit conservative rule as a challenger, not as accepted semantics.

**Unperformed:** no Nomi typechecker, soundness proof, foreign inference engine,
public-interface producer, or reader study executed these cases. The original
counterexample is a proposed oracle obligation. Existing generic-operation
probes do not establish this generalization rule.

## Dispatch Coherence And Operation Values

> Research continuation 2026-10-10: questions 3/10 with package identity from
> question 13; candidates below are unselected and unexecuted.

The expanded [Haskell](../languages/haskell.md), [Scala](../languages/scala.md),
[Rust](../languages/rust.md), [Julia](../languages/julia.md),
[Kotlin](../languages/kotlin.md), and [Mojo](../languages/mojo.md) reviews expose
several distinct mechanisms often grouped under “methods.” Contextual argument
selection, trait conformance, static receiver extensions, and runtime multiple
dispatch solve different problems. Receiver spelling does not identify which
one is in force. The reviews carry the primary evidence; this section owns the
Nomi comparison.

Begin with an ordinary function receiving an operation value. In contract
metalanguage, an ordering supplies `compare(T, T) -> Ordering`, and a decoder
supplies `decode(Value) -> Result[T, DecodeErrors]`. Explicitly passing two
orderings for the same T establishes the need for more than one meaningful
behavior without requiring ambient implementation search. These are proposed
interfaces, not accepted Nomi protocol syntax.

| Candidate | What chooses behavior | Benefit | Price |
| --- | --- | --- | --- |
| Explicit operation value | Caller's lexical value | Multiple behaviors are locally nameable | Plumbing through helpers and public contracts |
| Globally coherent nominal protocol | Declared conformance plus ownership/overlap rules | Separate package reasoning and conventional defaults | Limits independent foreign-type retrofits |
| Scoped implementation selection | Explicit scope/import plus checked search | Convenient alternate interpretations | Search complexity and import-sensitive review |
| Open multiple dispatch | Applicable argument-type tuple and specificity | Extensible cross-type algorithms | Intersection ambiguity and dependency/version interactions |

Do not collapse this choice into higher-kinded inference or method notation.
Those are additional axes. A program can use explicit operation values with
ordinary generics; a protocol can be coherent without being an algebraic proof.
An operation value can capture state, fail, or carry a resource region. Its
contract must preserve those facts across generic instantiation, including the
shared-state counterexample above.

**Prepared comparison:** two independent adapter packages provide decoding for
one foreign concept; two orderings intentionally coexist; two numeric methods
specialize opposite positions of a pair. Add and reorder imports, introduce a
third package, and inspect a consumer without private implementation source.
Compare selection/rejection at the declared checking/linking/runtime stage.
No candidate may use source order as an unexplained ambiguity tie-breaker.

Required inspection identifies the operation declaration, supplying package or
lexical value, applicable candidates, selected implementation, relevant type
substitutions, and expected failure/effect/capture contract. A useful diagnostic
names both origins and a repair: explicitly pass a behavior, qualify a function,
remove an overlap, or define the intended intersection where the candidate
permits it. It must not suggest changing nominal identity to make search succeed.

Remove a candidate if adding an unrelated dependency silently changes a checked
call, if selection needs clients' private source, or if preserving region/effect
facts requires unchecked erasure. Keep the explicit-value baseline unless its
measured whole-program cost is outweighed by a challenger that passes these
cases. Continue under the existing function-contract D1-D3 work and
[maintainer guide](../synthesis_guide.md); no protocol implementation was added.
