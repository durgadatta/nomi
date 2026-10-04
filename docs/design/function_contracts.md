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
                 effects=P, retained=false, completion contains no R)
  result: Result[A, ScopeFailure[E]]
  call effects=EnterEffects union P union ReleaseEffects
```

`@R` is descriptive region metadata, not ownership syntax. General-profile
garbage collection remains accepted. Resource errors and body errors must be
explicitly normalized to the same E or a declared nominal sum; no automatic
heterogeneous error union. The [resource packet](resource_lifetime.md) owns
completion/cleanup policy. Async scope has a separate calling convention and
must join children/cleanup before its completion; this signature does not solve it.
The no-region condition covers **A, E, every nested cause, and exported diagnostic
or trace payload**, not only the successful result. Returning `Err` containing
a reader is still an escape. Stable resource IDs and owned redacted observations
can survive a scope; a raw handle or closure/task retaining it cannot.

## Operational Obligations

| Operation | Order and invocation | Ordinary failure |
| --- | --- | --- |
| Strict map | Evaluate values/callback once; left-to-right, once per item on ordinary completion, no retention | Result-returning callback produces `List[Result[B, E]]`; no automatic propagation. |
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
Panic or cancellation stops ordinary iteration and follows the enclosing unwind
contract; it does not promise calls for remaining items. Purity is not totality.

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

### Names, Defaults, And Call Shape

Neither the parameter-list constructor nor the function-type literal above
specifies named/default argument behavior by itself. Compare two rules before
choosing syntax:

| Rule | Example | Cost |
| --- | --- | --- |
| Exact positional contract initially | A unary callback has exactly one exposed positional parameter; adapt `add(value, tax=2)` with `(value) => add(value, tax=2)` | More explicit adapters; simple separate checking and no implicit partial application. |
| Compatible callable shape | A function with optional extra parameters can satisfy a smaller required call shape | Arity/default/label subtyping and default evaluation must be preserved in interfaces. |

Named calls through an abstract function value require labels in that contract;
they cannot rely on the original declaration being discoverable at runtime.
Parameter defaults still obey call-time evaluation under accepted semantics.
The initial exact-contract rule is a candidate, not a retroactive restriction
on ordinary named function calls. A formatter comparison without this rule
would merely compare typography while leaving the actual call ambiguous.

## Paper Derivations And Unclosed Obligations

These are manual deductions **conditional on proposed library contracts**,
not output from a typechecker. They expose the remaining proof obligations
without introducing fake runtime capability flags. `Function` notation below
is contract metalanguage; no Fn spelling is admitted.

### Invoice: A Closed Local Transformation

For [the invoice fixture](interaction_model_target.nomi), assume ordinary scalar
operators have the displayed scalar result types, and Text operations used here
are deterministic. Arithmetic overflow/precision remains a separate profile gate.

| Expression | Substitution/resolved fact | Remaining obligation |
| --- | --- | --- |
| `line_total` | Function([Line], Int), sync, no world observations or captured cells | Int multiplication may still fail under an eventual bounded numeric profile. |
| `map(invoice.lines, line_total)` | A=Line, B=Int; result List[Int] | Specify generic declaration and pure callback eligibility. |
| `fold(amounts, 0, combine)` | A=Int, S=Int; combine([Int, Int]) produces Int; result Int | Decide accumulator/error law and arithmetic policy. |
| `unique_line_ids(lines)` | map produces List[Text]; all_unique produces Bool | Resolve equality/Hash protocol and cost policy; do not silently add arbitrary user effects to constraints. |
| `apply_edit(model, edit)` | Every ordinary return is Result[Model, ChangeError]; impossible duplicate owned IDs panic | Nominal constructor, match coverage and constraint metadata need a real typed producer. |

No callback captures a mutable cell or resource, so region absence is locally
plausible for this example. That does not prove generic map/fold safe for every
element/result type. The model change is pure application state; it does not
grant the ability to edit source or execute external operations. Row identity
uses an explicit ID, not display order; Text normalization/equality still needs
its portable scalar contract.
Duplicate IDs in raw input are expected decode errors. Duplicate IDs inside an
already-owned Invoice violate its constructor constraint and cannot be quietly
reclassified as an ordinary edit error. The target's fallback now names that
broken invariant as panic; structural coverage still requires the fallback
because arbitrary predicates are not assumed proven by pattern analysis.

### Submission: Typed Conversion, Not A Universal Error Union

Under the proposed generated decoder contract:

```text
Edit.decode(raw) : Result[Edit, DecodeErrors]
lambda(errors) = SubmissionError.Decode(errors)
  : Function([DecodeErrors], SubmissionError), pure
map_error(decoded, lambda) : Result[Edit, SubmissionError]
postfix ? : unwrap Edit or return Err(SubmissionError) from submit

apply_edit(model, edit) : Result[Model, ChangeError]
lambda(error) = SubmissionError.Change(error)
  : Function([ChangeError], SubmissionError), pure
map_error(changed, lambda) : Result[Model, SubmissionError]
```

This conditional derivation is compatible with `submit`'s declared result.
It needs no first-class constructor value, automatic error coercion, or lambda
control transfer to a caller. **Unclosed:** generated decoder/protocol signature,
variant wire representation, accumulated constraint evaluation on partially
invalid input, and method resolution. Do not run declaration constraints on
raw malformed fields just to collect another error; the predicate expects
tentatively decoded field values, not arbitrary transport objects.

### Independent Row Errors: Result Is The Mapped Element

For [the callback fixture](function_contracts_target.nomi), checked_double has
result Result[Int, RowError]. Explicit map_error changes RowError to ReportError.
Therefore A=Int and **B=Result[Int, ReportError]** for the enclosing map, yielding
List[Result[Int, ReportError]]. It does not yield Result[List[Int], ReportError].

The ordinary trace for `[1, -1, 3]` is:

```text
invoke 1  -> Ok(2)
invoke -1 -> Err(ReportError.Row(RowError.Negative(-1)))
invoke 3  -> Ok(6)
return the three outcomes in input order
```

By contrast, `publish_names`' loop uses `?` on each request, so a failure ends
later iteration after required cleanup. Earlier publication is not rolled back.
An abnormal callback panic would stop map as well; this trace assumes ordinary
completion. This distinction is a real user-facing diagnostic/hover requirement.

### Resource Callback: Where The Derivation Must Stop

For [the reader program](resource_lifetime_target.nomi), suppose the resource
supplies Reader in a fresh R, enter/release report IoError, and read_body returns
Result[Text, IoError] while requiring FileRead. Text and the IoError payloads
must be region-free. Then A=Text, E=IoError, and the expected ordinary result
is Result[Text, ScopeFailure[IoError]]. Enter/body/release requirements compose
under the proposed protocol; an explicit carrier can be mapped by the caller.

**This is not a completed derivation.** Reader's hidden region propagation,
generation of R, protocol retention, the no-R condition on errors/causes,
actual release effect requirements, and abnormal unwind policy remain unproven.
If a resource has a different release error, an ordinary map_error on the body
does not magically convert it. Compare an explicit resource-error adapter with
a compound resource protocol; type both against a declared nominal error sum.
Do not hide this mismatch in Any, an untagged union, or an alleged compiler fact.

### Cold Tasks: Call Requirements Versus Latent Work

A synchronous wrapper returning Task does not automatically qualify for pure map.
The result type carries latent effects/captures, but construction may also need
authority or introduce observable temporal identity. Compare a plan-like cold
description whose authority is checked at start with a task that captures/checks
authority at construction. The accepted cold-task rule only says no task body
runs until start/await; it does not decide all authorization timing.

Until that rule is closed, a table must label task-builder purity conditional,
and an inferred empty execution footprint must not erase declared call
requirements. Empty input does not bypass a callback's static contract. This
is a task/callback interface gap, not a reason to make map silently start tasks.

### Negative Contract Facts To Validate Later

| Supplied program fact | Candidate A expectation | Required explanation |
| --- | --- | --- |
| Callback reads Clock or Random | Reject pure eligibility | Name observation and declaration/capture span. |
| Callback updates a captured outer cell | Reject pure eligibility | Name the cell, not a misleading missing Network grant. |
| Callback returns ordinary Err | Permit pure result if its computation is otherwise pure | Show List[Result], not automatic propagation. |
| Callback returns Task with borrowed R | Track R through result; reject escape beyond its scope | Relate task capture, acquisition and escape. |
| Scope returns Err containing a Reader | Reject whole-completion escape | Failure payload is not exempt from lifetime checks. |
| Diagnostic or cause stores a closure retaining Reader | Reject checked export; revoke at unsafe boundary | Preserve owned explanation without retaining live authority. |
| Two imported extensions resolve equally | Reject ambiguity | Show both owners and explicit disambiguation route. |
| Callback has a defaulted extra parameter | Undecided pending call-shape rule | Show adapter versus compatible-shape alternatives. |

These are future positive/negative typing fixtures. Supplied facts are not
inferred proofs, and doc validation is not a conformance oracle.

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

## Generic-Operation Continuation

The [property hierarchy](../research/generic_operations.md) and
[ordinary-call challenger](targets/research/generic_operations.nomi) extend
this packet with GA1-GA8. Status: designing hypotheses, not additional accepted
core semantics or public stdlib APIs. Keep the A/B callback-effect fork open.

Recommendation: build a capability graph from specific callable/value facts,
not a universal Object/Function toolbox. Identity/composition need compatible
call shapes; map/filter need carrier-specific structure; fold/scan thread state;
parallel merge needs additional laws; cache/iteration/tap need explicit policy
and outcomes. Hash/encoding/display belong to conditional value protocols and
selected profiles, not eligibility automatically shared by every object.

For each proposed combinator, supplement the existing callback metadata with
only the facts its interface needs:

| Contract dimension | Required distinction |
| --- | --- |
| Input/result shape | Element versus whole value, state versus emitted output, receiver binding, labels/defaults and carrier |
| Invocation phase | Construction, immediate traversal, consumer demand, task start or subscription |
| Multiplicity/order | Zero/one/many calls, prefix short-circuiting, no hidden repetition or optimizer elision |
| Retention/sharing | Callback/capture/result region; immutable owned result versus aliased mutable or single-use state |
| Completion | Ordinary Result policy, observer failure, budget/cycle/stopping evidence, abnormal cancellation/panic |
| Context/dependencies | Explicit operation/key/schema/profile basis for reusable artifacts; current authority remains separate |
| Laws/rewrite scope | Value equality alone versus declared operational observations; sequential step versus associative merge |

These are abstract interface obligations, not annotations chosen for source or
facts the current compiler infers. Pure callbacks can still panic/diverge;
strict map fusion and reassociation need a separate preservation argument.
Tap is not pure identity; cache state and captured mutable dependencies do not
disappear behind a decorator; approximate stopping is not Eq/hash coherence.
Normal statements/loops are valid long forms, not missing FP sophistication.

The challenger supplies beginner, production and failure-heavy forms without
new punctuation or an automatic method-to-free-function equivalence. Preserve
local protocol/import resolution and whole-completion region checks. Extend
D1-D3 typed facts with seeded scan, context-bound caching and fallible observation
before considering shared higher-kinded protocols or shorthand.

The [local capture](../research/features/generic_probe_results.json) contains
bounded Python-host/original models only. It does not establish Nomi typing,
foreign library conformance, concurrent caches, numerical convergence or human
repair. GA1-GA8 remain open; removal is limited to proposed library contracts,
their research metadata and target-only challenger, not current runtime behavior.

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
