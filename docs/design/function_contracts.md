# Function And Callback Contracts

> Status: designing; conceptual type/effect metadata, not admitted generic syntax.

Packet: `docs/research/features/functions.md`,
`docs/design/function_contracts_target.nomi`,
`docs/review/2026-09-30-function-contracts.md`.

[Syntax](syntax.md) accepts named `func`, explicit expression lambdas, and
ordinary calls. [Semantics](semantics.md) accepts lexical closures, checked
parameters/results, public effects, and cold tasks. It does not yet specify
generic declarations, function-value type spelling, effect variables, protocol
conformance syntax, or region inference. This proposal supplies a precise
comparison before selecting those forms.

## The Design Fork

| Candidate | Collection callback contract | Strength | Cost |
| --- | --- | --- | --- |
| A: pure callbacks first | map/filter/fold/map_error reject world observations and externally observable mutation | Predictable value transformation; simpler hover/error model | Effectful transforms require explicit loops/helpers. |
| B: effect-polymorphic strict callbacks | map/fold propagate a declared callback footprint | One generic combinator and less loop ceremony | Effect variables, capture typing, effect unification, more complex API and errors. |

**Recommendation for the initial library:** A, with effectful loops and dedicated
explicit sequential APIs when earned. Keep B as the challenger. This is not
accepted yet; do not change existing execution or pretend current map APIs
already enforce it. Generic/error/region metadata is required even under A.

Koka provides primary evidence for B; Nomi's separate capability and abnormal
completion model prevents copying its effect system verbatim. See
[redesign frontiers](../research/design_frontiers.md). This proposal extends
[open questions 2/3/4/10](../research/open_questions.md), not a new independent
inference agenda.

## Function Contract Before Its Spelling

Describe a function value with inspectable metadata:

| Field | Required meaning |
| --- | --- |
| Parameters | Ordered names/types/defaults and constraints; named-call mapping. |
| Result | Ordinary payload type, including any Option or Result structure. |
| Calling convention | Sync value call versus async cold-task construction. |
| Required world effects | Declared/conservatively resolved capability categories; not granted handles. |
| Captures | Immutable values, mutable cells, and capabilities/borrowed handles with their regions. |
| Latent task effects | Work required when a returned task starts/runs, separate from construction. |
| Invocation/escape contract | Whether a callback is retained, when/how often called, region restrictions. |
| Evidence | Declaration span, resolved overload/protocol owner, substitutions and unproven obligations. |

Not every field must be a user annotation or runtime object field. Public
interfaces need sufficient versioned metadata for separate checking; local
inference and optimizations may erase proven details. Tooling must not advertise
facts it has not established.

**Purity is not just an empty `uses` set.** A callback updating a captured mutable
cell is observably stateful even without File/Network. A clock read violates
determinism; local scratch mutation may be encapsulated if it cannot escape.
The proof/checking rule for encapsulation is still open. Termination, absence of
panic, and memory bounds are not implied by purity. Do not introduce an implicit
Any or a blanket unchecked "pure" annotation to avoid those questions.

## Abstract Signatures, Not Nomi Source

The notation below is contract metalanguage, not an admitted function-type
grammar. A, B, S, E, and F are quantified type variables; P is a world-effect
footprint; R is a resource region. `Function` is a description, not a stdlib type
that sidesteps compiler support.

```text
map_A:
  values: List[A]
  callback: Function(parameters=[A], result=B, sync, pure, retained=false)
  result: List[B]

fold_A:
  values: List[A], initial: S
  callback: Function(parameters=[S, A], result=S, sync, pure, retained=false)
  result: S

map_error_A:
  value: Result[A, E]
  callback: Function(parameters=[E], result=F, sync, pure, retained=false)
  result: Result[A, F]

map_B:
  values: List[A]
  callback: Function(parameters=[A], result=B, sync, effects=P, retained=false)
  result: List[B], call effects=P

run_scope:
  resource: Resource[Handle@R, E, EnterEffects, ReleaseEffects]
  body: Function(parameters=[Handle@R], result=Result[A, E], sync,
                 effects=P, retained=false, result contains no R)
  result: Result[A, ScopeFailure[E]]
  call effects=EnterEffects union P union ReleaseEffects
```

`@R` is descriptive region metadata, not ownership syntax. General-profile
garbage collection remains accepted. Resource errors and body errors must be
explicitly normalized to the same E or a declared nominal sum; no automatic
heterogeneous error union. The [resource packet](resource_lifetime.md) owns
completion/cleanup policy. Async scope has a separate calling convention and
must join children/cleanup before its completion; this signature does not solve it.

## Operational Obligations

| Operation | Order and invocation | Ordinary failure |
| --- | --- | --- |
| Strict map | Evaluate values/callback once; left-to-right, once per item, no retention | Result-returning callback produces `List[Result[B, E]]`; no automatic propagation. |
| Strict filter | Pure Bool callback, left-to-right; same item order | No truthiness, async test, or hidden decoder call. |
| Strict fold | Start with initial; one callback per item; empty returns initial | Accumulator type stays S; Result accumulator behavior is explicit. |
| map_error | Callback once only for Err; Ok payload unchanged | E to F conversion is explicit; preserve cause through an error wrapper. |
| Explicit effectful loop | Source order, declared uses; `?` can stop subsequent iterations | Partial external effects remain; fail-fast is not rollback. |
| run_scope | Once after successful acquisition; no callback retention | Exactly-once release and cause composition belong to resource contract. |

No callback redirects `return` or `?` to its caller. A named function provides
statement bodies; an expression lambda does not acquire a new block/yield
spelling. Constructor invocation remains ordinary construction; a constructor
as a first-class callback is **open**. Use `(error) => ErrorKind(error)` in
active target examples so the unresolved contract is visible rather than assumed.

## Type Compatibility And Inference Questions

- A callback's argument/result types are checked against the expected signature.
  Proposed world-effect compatibility is subset inclusion; function subtyping,
  parameter variance, and generic bounds still need an explicit rule.
- A pure callback can be used where an effectful callback is permitted; an
  effectful callback cannot be passed to a pure-only API merely because its
  current input branch happens not to perform the effect.
- Escaping aggregates/closures containing a borrowed handle retain its region.
  An immediate invocation may capture a handle if all use ends before its scope
  closes, subject to safe-sharing rules. `retained=false` is an enforceable
  protocol obligation, not a comment the compiler trusts.
- Calling an async function creates a cold task. It does not run/await it. A
  synchronous callback explicitly returning a Task can produce a list of cold
  tasks; latent effects and captured regions still travel with those tasks.
  Constructor-call requirements versus latent effects need separate checking.
- Imported protocol/extension candidates must be locally inspectable. Ambiguity
  is an error naming both owners, not runtime order-dependent dispatch.
- Exported generics quantify variables explicitly in interface artifacts;
  no declaration syntax is chosen here. Recursive/ambiguous private functions
  remain annotated under the existing inference policy.

## Candidate Type Spellings

These are deliberately **unaccepted source candidates** shown as text, not
syntax Nomi currently parses. They compare the common pure map case and a
two-argument fold without changing the callback's call arity.

```text
Candidate 1: explicit parameter-list type constructor
pub func map[A, B](
    values: List[A],
    transform: Fn[[A], B],
) -> List[B]:
    ...

pub func fold[A, S](
    values: List[A],
    initial: S,
    combine: Fn[[S, A], S],
) -> S:
    ...

Candidate 2: function-type literal
pub func map[A, B](
    values: List[A],
    transform: func(A) -> B,
) -> List[B]:
    ...

Candidate 3: named protocol for a domain callback
pub func map[A, B](
    values: List[A],
    transform: Transform[A, B],
) -> List[B]:
    ...
```

| Candidate | Recognition and formatting | Unresolved cost |
| --- | --- | --- |
| 1 | Distinguishes parameter pack `[S, A]` from one tuple input `[(S, A)]`; works within a short multiline signature | Nested brackets and a dedicated parameter-list type grammar; named/default parameter metadata still needs rules. |
| 2 | Makes calling shape visible and keeps `->` a function result marker | Reuses `func` in type context; must distinguish type literals from declarations and anonymous values; formatter/parser need a new contract. |
| 3 | Speaks in a domain concept and can attach invocation/retention rules | Risks many incompatible callback protocols and hides arity/effects behind another definition. |

**Candidate preference, not admission:** compare 1 and 2 with novice/reviewer
tasks; keep 3 for genuine domain contracts rather than naming every arity.
Do not choose a tuple-based function constructor merely to avoid parameter
packs: two parameters and one tuple parameter are different calls.

The concrete pure forms do not solve B's effect polymorphism. Potential extensions
such as `Fn[[A], B, Effects]` or a function-type `uses` clause need declared
effect-kind variables, instantiation/subset rules and meaningful public hover.
An async callable also cannot be conflated with a sync function returning Task;
even when call results look alike their declared convention and latent
requirements differ. Generic protocol bounds, region quantification, defaults,
and named callback arguments must be compared on production code before
accepting any constructor or a reserved `Fn` name.

The scoped resource callback exposes the hardest case: the resource supplies
a fresh region and the result must not contain it. Decide whether a built-in
scope protocol owns that rule or public generics can express it; neither a
`retained=false` comment nor a function's ordinary result type proves it.
The callback itself can return a closure/aggregate containing a capture, so
region tracking must follow results as well as whether the combinator stores
its callback argument.

## Source, Formatting, And Diagnostics

[The target fixture](function_contracts_target.nomi) uses accepted source forms
to contrast pure map, effectful fail-fast looping, and independent row errors.
Types and APIs are still proposals; a typed-artifact producer is not implemented.
Examples show ordinary multiline calls at roughly 80 columns with explicit
callback parameters. No `->` reuse, hole syntax, currying, or equation form.

Expected callback diagnostic: `map needs a pure callback; fetch_name requires
Network.` Relate the callback argument, declaration/capture, and API contract;
suggest an explicit sequential loop, not removal of `uses`. A mutable capture
diagnostic should name the cell and its declaration. A region-escape diagnostic
should name acquisition, capture, and escape spans. A typed hover should show
`List[Result[Int, RowError]]`, not imply automatic Err propagation.

Illustrative diagnostic fields: code, phase=type/effect/region, expected
contract, actual resolved contract, related spans, safe substitutions, repair.
These are requirements for a future schema, not fields already produced by the
current compiler. An empty-list test must still typecheck the callback contract;
zero runtime invocations do not turn an effectful function into a pure one.

## Acceptance And Removal Gates

1. Specify function-value type/generic/protocol notation through a separate
   syntax-first comparison, including formatter and ambiguity diagnostics.
2. Derive complete typed contracts for map/fold, generated decode, and run_scope,
   including mutable capture, constructor values, region retention and latent tasks.
3. Produce positive/negative frontend-neutral typing fixtures; distinguish a
   failed static judgment from a runtime expected Err or abnormal completion.
4. Compare A/B on three full programs and reader repair tasks. Replace A if
   loops introduce more cognitive/control mistakes than B's extra type machinery.
5. Only then implement one gated typed Surface slice, differential CLI/browser
   diagnostics and a supported playground callback sample.

No conformance, benchmark, or typechecker proof was performed. This design step
narrows D1; it does not complete it or justify removing current prototype syntax.
