# Generic Operations And Compositional Properties

> Status: comparative research and library/protocol hypotheses, not new syntax
> or implemented Nomi APIs. Selected primary sources checked 2026-10-04.

Owned by the existing [function evidence](features/functions.md),
[function contract proposal](../design/function_contracts.md),
[callback target](../design/function_contracts_target.nomi) and
[bridge](../review/2026-09-30-function-contracts.md). This continuation also
connects [collections](features/collections.md), [text boundaries](dsls/text_as_interface.md)
and [domain composition](domain_composition.md). No additional design packet.

## Practical Meaning, Not A Paradigm Test

The user pressure is to reuse an operation across many functions or objects
without repeatedly rebuilding the plumbing. "Functional abstraction" here is
a pragmatic umbrella. It includes higher-order functions, collection algorithms,
object protocols, wrappers, state transitions and execution policies. Hashing
and encoding are generic value operations, not necessarily higher-order ones.
Python, JavaScript and Common Lisp support functional techniques alongside other
styles; they do not inherit Haskell's evaluation/effect model from having `map`.

Three programs distinguish useful candidates:

1. Beginner: select positive amounts, double them, total them, and retain running
   totals. Predict empty-input and callback behavior without learning a taxonomy.
2. Production: transform a pinned dataset, reuse a bounded cached report, encode
   it under an explicit schema, and observe a redacted summary. A method chain
   must not obscure cache dependencies or world effects.
3. Failure-heavy: assess every row versus stop at the first failure; tap may fail;
   iteration may oscillate; a publication timeout has an unknown remote outcome.
   None of these is solved by replacing a loop with `reduce`.

[The source challenger](../design/targets/research/generic_operations.nomi)
uses ordinary calls and explicit long forms. [Local probes](features/probe_generic_operations.py)
execute only small Python-host/library and original finite-model distinctions.
They do not typecheck the challenger or run the compared foreign libraries.

## Cross-Language Mechanisms

These are selected mechanisms, not an exhaustive feature survey. Pinned Java SE
25, Haskell 2010/base 4.21.0.0 and RxJS 7.8.2 pages are edition evidence. Python,
pandas, Rust, Kotlin, Serde and Wolfram links are rolling documentation. Lodash's
4.17.21 URL redirected to 4.18.1 when checked; no runtime was installed here.

| Evidence | Useful abstraction | Difference that must remain visible |
| --- | --- | --- |
| [Wolfram Map](https://reference.wolfram.com/language/ref/Map.html) | Transform selected levels of general expressions; operator form | Expression parts/heads and subsequent evaluation are not just List elements. |
| [Wolfram Listable](https://reference.wolfram.com/language/ref/Listable.html) | Attribute-driven threading over list arguments | Scalar replication and matching list arguments are an evaluator policy, not universal function lifting. |
| [Wolfram iteration](https://reference.wolfram.com/language/guide/FunctionalIteration.html), [FoldList](https://reference.wolfram.com/language/ref/FoldList.html) | Nest, fold, state history and iteration predicates | Repeated state transformation differs from consuming a sequence and from repeating an action. |
| [Wolfram FixedPoint](https://reference.wolfram.com/language/ref/FixedPoint.html) | Iterate until successive values satisfy an equality/test policy | Test and iteration limit determine operational stopping; convergence is not implied. |
| [Haskell Prelude](https://www.haskell.org/onlinereport/haskell2010/haskellch9.html), [classes](https://www.haskell.org/onlinereport/haskell2010/haskellch6.html) | map, left/right folds, scans, id, composition and class-directed behavior | Non-strict evaluation and typed classes differ from eager callbacks; callable arity is not Nomi's automatic currying policy. |
| [Haskell Traversable](https://hackage.haskell.org/package/base-4.21.0.0/docs/Data-Traversable.html) | Traverse/sequence preserve structure while combining an effect carrier; mapAccum threads state | Applicative/Monad instance determines combination, short-circuiting and multiplicity. A name is not a universal execution schedule. |
| [Haskell Data.Function](https://hackage.haskell.org/package/base-4.21.0.0/docs/Data-Function.html) | id, const, argument adaptation, on and fix | `fix` denotes a least-defined fixed point, not a tolerance-based numerical iteration loop. |
| [Clojure transducers](https://clojure.org/reference/transducers) | Compose reducing-function transformations independently of a chosen source/sink | Init/step/completion and early termination are a process contract; stateful transducers need per-process state. |
| [Common Lisp mapping](https://www.lispworks.com/documentation/HyperSpec/Body/f_mapc_.htm), [reduce](https://www.lispworks.com/documentation/HyperSpec/Body/f_reduce.htm) | Element/tail traversal, side-effect traversal and reduction | mapc returns the first list; mapcar collects results; mapcan destructively concatenates callback lists. Reduce's empty unseeded case calls the function with zero arguments. |
| [Python functools](https://docs.python.org/3/library/functools.html) | Callable wrappers, reduce, partial, singledispatch and cache | Hashable keys, retained arguments/results and observable state constrain wrappers; explicit partial is not a change to ordinary call syntax. |
| [Python itertools](https://docs.python.org/3/library/itertools.html) | accumulate, chain, product, repeat and tee | Iterators consume on demand; initial affects scan length; tee can buffer a large consumer lag. |
| [ECMAScript arrays](https://tc39.es/ecma262/multipage/indexed-collections.html#sec-array.prototype.map) | Method-based map/filter/reduce and predicate short-circuiting | Array callbacks receive value/index/array; holes are skipped by map/filter; filter uses Boolean coercion. This is not Nomi's unary/Bool callback contract. |
| [pandas pipe](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pipe.html) | Feed the whole frame to an ordinary function, including named data-argument selection | Not elementwise map or axis-wise apply. The function can return any supported result, not necessarily another frame. |
| [Rust Iterator](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.inspect) | Lazy adapter methods, fold, try_fold and inspect | Callbacks may be stateful; borrowing/consumption matters; inspect runs as items are consumed. |
| [Java Stream](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Stream.html) | Intermediate/terminal stages, reduction and peek | Optimizers may omit result-irrelevant stages/callbacks. A peek stage is not a reliable audit receipt. |
| [Kotlin scope functions](https://kotlinlang.org/docs/scope-functions.html) | also/apply return receiver; let/run return callback result | Implicit receiver/parameter and returned value are independent choices; the receiver can be mutable. |
| [Lodash tap/thru](https://lodash.com/docs/4.18.1#tap) | Preserve the supplied value versus replace it with an interceptor result | Tap can mutate the supplied object. Preserving a reference does not mean preserving state or effects. |
| [RxJS tap source, 7.8.2](https://github.com/ReactiveX/rxjs/blob/7.8.2/src/internal/operators/tap.ts) | Observe notifications while forwarding them | A synchronous observer error becomes an output error; subscription/completion/unsubscription have separate hooks. |
| [Java Object](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html), [Serializable](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/Serializable.html) | Common equality/hash/display methods; opt-in persistence marker | All objects have Object methods; not all objects are serializable. Hash codes need not survive another process. |
| [Python data model](https://docs.python.org/3/reference/datamodel.html#object.__hash__), [Serde Serialize](https://docs.rs/serde/latest/serde/trait.Serialize.html) | Conditional protocols and format-selected serializers | Python equality/hash eligibility and Rust trait implementation are not one universal object superclass. |

Nomi inference: take the reusable semantic distinction, not each ecosystem's
entire vocabulary. Familiar verbs should identify related acts while carrier,
schedule, law, failure and authority remain explicit in types and interfaces.

## A Hierarchy Of Requirements, Not One Inheritance Tree

Small properties combine in several directions. A value may be encodable but
not ordered; a callback may be pure but nonterminating; a stream may be mappable
but single-pass; a state update may be repeatable but not safe to retry remotely.
Use a capability graph rather than making every object implement everything.
The levels below are a reading order, not new compiler categories or keywords.

| Level | Small fact available | Derived operation families | Extra fact needed before the next composition |
| --- | --- | --- | --- |
| 0: value and invocation | A typed value; a known call shape; an ordinary call | identity, constant, explicit adapters, one value through a function | Input/output compatibility, captures, defaults and invocation convention |
| 1: observational capability | Equality, ordering, display, inspection or a selected codec | distinct, sort_by, formatting, encoding, comparison-based stopping | Owner/profile and laws; not every capability follows from another |
| 2: structure and traversal | Elements/positions plus traversal and rebuilding policy | map, filter, flat_map, zip, enumerate, find, partition | Shape/cardinality, input exhaustion, order, retention and demand |
| 3: state threading | A seed and a transition over inputs | fold, scan, map_accum, unfold, batching/windows | Transition law, emission/termination and buffer/resource limits |
| 4: lawful combination | Declared associative combine and possibly an identity | fold_map, chunk summaries, mergeable aggregates, parallel reduction | Reassociation law for the actual numeric/carrier profile; commutativity if reordered |
| 5: temporal and contextual policy | A repeated transition or callable plus context/policy | iterate_n, bounded convergence, memoization, once, retry, debounce | State/version/dependency identity, clock, failures, concurrency and current authority |
| 6: domain execution | Typed descriptions and checked adapters | TablePlan optimization, workflow retries, differentiable transforms, reviewed actions | Domain-specific algebra, effects, host profile, provenance and completion |

Two separate branches make the object/function distinction concrete:

```text
value + lawful equality + compatible hash -> hash lookup / distinct
value + codec profile + supported schema -> encode/decode
callable + key policy + explicit dependency basis + reuse-safe result -> cache
callable + compatible inputs/results -> explicit composition
sequence + transition + initial state -> fold / scan / map_accum
endomorphism + stopping rule + budget -> operational iteration
```

Hashability alone does not imply encodability or cache eligibility. Codec
round-trip support does not imply canonical bytes. Determinism does not imply
termination, bounded cost, idempotence or permission. A finite property test is
a counterexample finder, not an inferred proof for arbitrary user functions.

## Operation Families And Minimal Contracts

Names in this table are research vocabulary, not a proposed prelude inventory.
Nomi already prefers map/filter/flat_map/fold/group_by/sort_by/take/collect;
foreign reduce/scan/accumulate names help discover the corresponding contracts.

| Family | Representative operations | Minimum useful property | Frequent hidden cost or ambiguity |
| --- | --- | --- | --- |
| Preserve/select a value | identity, constant, projection, noop | Explicit call/result shape | Identity returns its input; noop returns Unit; constant ignores inputs but argument evaluation still occurs. |
| Adapt a call | compose, argument reorder, tuple unpack, explicit partial, curry/uncurry, predicate negation, on/key adaptation | Compatible parameters/results; visible captured values | Default/label/receiver differences; retained handles; composition direction. No implicit Nomi currying. |
| Lift over a carrier | List map, Option map, Result map/map_error, Task transform | Carrier-owned structure and result rule | Zero/one/many invocations and work-start timing differ. Mapping Err is not raising it. |
| Select/search | filter, partition, find, any, all, take_while | Typed Bool predicate and declared traversal | Truthiness, empty any/all, early stop and discarded evidence |
| Expand/combine structure | flat_map, flatten, concat, zip, product, chunk, window | Element/rebuilding policy | Zip truncation versus exact length; output explosion; bounded buffering |
| Summarize inputs | fold, reduce_nonempty, count, sum, fold_map | Seed/accumulator transition or lawful algebra | Unseeded empty failure, operand direction and reassociation |
| Expose state history | scan, accumulate, map_accum | State transition; explicit output at each step | Include seed or not; snapshot aliasing; state type versus emitted type |
| Generate/repeat | repeat_value, repeat_call, iterate_n, unfold | Value duplication versus callable or state transition | Same mutable reference versus fresh values; infinite sources; work duplication |
| Reach a stopping condition | iterate_until, fixed_point, cycle check | Endomorphism, comparison/test, budget | Approximate stability is not mathematical proof; cycles/divergence/NaN |
| Pass through and observe | pipe, apply_to, tap, inspect_each, tee/fanout | Whole-value input or traversal plus observer contract | Returned object versus state; observer error; lazy demand; lag buffering |
| Preserve context and errors | and_then, traverse, sequence, recover, validate_all | Explicit carrier and combination/selection policy | Fail-fast versus accumulated errors, deterministic error order and partial effects |
| Reuse computations | memoize, bounded cache, single_flight, once, invalidate | Defined key/equality, dependency basis, retention and outcome policy | Cache mutation, stale captures, sensitive data, shared mutable results, duplicate concurrent misses |
| Control invocation | retry, backoff, timeout, rate_limit, debounce, throttle, circuit_breaker | Explicit callable, clock/scheduler, cancellation and failure classification | Remote outcome unknown; timeout may not stop work; pending debounce needs an owner |
| Encode or identify | display, inspect, encode, decode, canonicalize, hash, digest | Selected relation/codec/schema/profile | Human text versus persistence, collisions, mutable identity, version portability |
| Own resources | bracket/run_scope, acquire-use-release, transaction, defer | Resource protocol, nonescape and all-completion contract | Release/cancellation error composition; rollback cannot undo arbitrary external effects |
| Transform a program | differentiate, vectorize, compile, trace, specialize | Inspectable supported program subset and host profile | Arbitrary closures/effects are not automatically transformable or serializable. |
| Focus/update a structure | projection, getter, setter, update, lenses/traversals | Selected focus, rebuilding and declared round-trip/update laws | Validation, read-only/redacted fields and revision-bound changes may prevent a total setter. |

Not every abstraction should be user-facing initially. Start with explicit
long forms and one canonical verb per common act. A collection reduction does
not make that verb the implementation of every algorithm; a direct loop may
explain early exits, mutation, resources or diagnostics much better.

## Important Distinctions And Laws

### Related Algebraic Families Without Mandatory Jargon

The names can help library designers find reusable laws; they need not become
concepts a beginner must master before using `map` or an explicit loop.

| Family | Small reusable idea | Concrete ordinary form | Boundary |
| --- | --- | --- | --- |
| Functor-style mapping | Transform a selected output while retaining its declared context | List/Option/Result-specific map; postcompose a callable | Identity/composition laws do not supply filtering, effect scheduling or arbitrary container rebuilding. |
| Applicative-style combination | Combine independently described contextual inputs | Assemble independently checked fields under a declared validation carrier | Error accumulation and execution order come from the selected carrier, not universal parallelism. |
| Monad-style sequencing | Choose the next contextual computation from a previous result | Explicit Result and_then or a fail-fast function with `?` | No new Nomi do-notation or universal control/effect algebra is proposed. |
| Foldable/Traversable-style structure | Summarize elements or distribute a chosen context across a structure | fold versus a typed traverse/sequence | Shared generic support needs richer type/instance contracts; these capabilities are not every object's defaults. |
| Input adaptation / profunctor-style adaptation | Preprocess input and/or postprocess output | `(value) => after(operation(before(value)))` | Direction, receiver/captures and effects remain explicit. |
| Optic-style focus | Compose access/update paths into larger structures | Read a named field, rebuild an owned value, or compose a checked edit | Getter, setter, traversal and source/view projection are different capabilities. |

The [Haskell traversal interface](https://hackage.haskell.org/package/base-4.21.0.0/docs/Data-Traversable.html)
provides an explicit class/law comparison, and
[profunctor documentation](https://hackage.haskell.org/package/profunctors/docs/Data-Profunctor.html)
provides input/output adaptation laws. The
[lens maintainer's repository](https://github.com/ekmett/lens) identifies distinct
getter/setter/fold/traversal families; its implementation was not reviewed here.
The ordinary forms and Nomi costs in the table are our proposed translations.
Some additional pinned Hackage entrypoints were inaccessible; no detailed
claims about their current implementations are made.

For a proposed total field lens, useful candidate laws are read-after-write,
writing back the read value leaves the value unchanged, and the last write wins.
A checked edit can reject invalid values, so its law must include rejection and
base revision instead. A redacted or derived projection may not have a setter.
See [interaction projection boundaries](../design/interaction_model.md).

The [Clojure process contract](https://clojure.org/reference/transducers) offers
a separate abstraction direction: transform a reducer's init/step/finish behavior
rather than allocate a new collection at every stage. Early stopping, final
flush and state ownership matter. This is a library/tool challenger for GA2/GA3,
not permission to fuse eager Nomi callbacks while changing their observations.

### Map, Filter And Context

For finite strict Lists and total pure deterministic callbacks, value laws include:

```text
map(xs, identity) == xs
map(map(xs, f), g) == map(xs, lambda(x): g(f(x)))
filter(filter(xs, p), q) == filter(xs, lambda(x): p(x) and q(x))
map(xs, f) has length len(xs)
filter(xs, p) preserves the relative order of survivors
```

These are not automatic operational optimization licenses. Two strict maps
evaluate all f calls before any g call. Fusing them interleaves f/g, changes
failure timing, and can perform an observer before a later f fails. Even a pure
callback may panic or diverge; "no world effects" alone does not justify the
rewrite. Source maps, error location, resource bounds and observable tracing
need their own preservation rule. Query/numeric engines may have a different,
explicitly scoped contract; Nomi's pipeline does not secretly grant it.

Mapping a Set can collapse distinct inputs. Filtering a fixed-size tensor changes
shape or produces a mask/ragged result. Mapping a function means postcomposition,
not enumeration. Mapping a task need not run it immediately. Therefore "all
objects have map" is weaker and less honest than a selected lawful protocol.
Do not infer filter from a shape-preserving map capability.

For independently parsed rows, `List[Result[A,E]]` retains every outcome.
An explicit fail-fast traversal produces `Result[List[A],E]`; an accumulating
validator produces a declared error collection and runs only valid independent
checks. General Applicative/Monad vocabulary can explain these mechanisms, but
Nomi need not expose that vocabulary before the actual programs require it.

### Fold, Reduce, Scan And Merge

Contract metalanguage, not admitted generic declarations:

```text
fold:       (sequence A, seed S, step(S,A): S) gives S
scan:       (sequence A, seed S, step(S,A): S) gives sequence S
map_accum:  (sequence A, seed S, step(S,A): (S,B)) gives (S, sequence B)
unfold:     (seed S, step(S): Option[(B,S)]) gives an explicit sequence/stream B
```

For a seeded finite scan including the initial state, empty returns `[seed]`
and nonempty length is input length plus one. An alternative excludes the seed.
Choose one public contract or an explicit policy; do not leave it to the host.
Plain fold allows state S to differ from element A and needs no associativity.
An unseeded nonempty reduction needs a nonempty witness or typed absence/error.
It must not manufacture a seed by silently calling a binary callback with zero
arguments because Common Lisp's reduce permits that separate contract.

Semigroup/monoid terminology identifies additional laws: associativity permits
reparenthesizing combinations; an identity makes an empty summary meaningful.
Commutativity is needed to reorder terms, not merely to reparenthesize them.
An arbitrary seeded step is not a merge function. Distributed reduction needs
an explicit summary/merge relationship plus a declared numeric profile. IEEE
floating addition is not associative; subtraction is not associative either.
Neither concurrency nor deterministic error order follows from these laws.
Inverse updates/deletions need another law; see
[data change algebra](data_workflows/dependencies_and_time.md).

### Repeat And Several Fixed Points

| Operation | What repeats | Ordinary zero/stop case | Additional outcome needed |
| --- | --- | --- | --- |
| repeat_value | Supplied value/reference | Zero yields no elements | Duplication/sharing policy; infinite demand bound |
| repeat_call | Call producing a value | Zero invokes nothing | Effects, freshness, failure and invocation count |
| iterate_n | Updated state through an endomorphism | Zero returns the seed | Nonnegative count and abnormal completion |
| iterate_until | Transition plus stopping predicate | Whether seed is tested first is explicit | Limit reached, predicate/step failure, cancellation |
| Operational fixed point | Successive states compared under a named test | First equality can stop | Cycle, budget exhaustion, approximate/nonfinite numeric state |
| Recursive fixed point | Self-reference in a function/evaluator | No generic numeric seed meaning | Recursion/evaluation/termination contract |
| Least relational fixed point | Repeated rule application under an ordered domain | Start at a declared bottom | Monotonicity, ascending-chain/convergence and domain evidence |

Haskell's `fix` and Wolfram's `FixedPoint` belong to different rows. The
[SICP primary text](https://web.mit.edu/6.001/6.037/sicp.pdf) demonstrates an
oscillating square-root iteration and average damping in section 1.3.3; this
supports checking convergence assumptions, not promising every iteration stops.
Our proposed operational API returns evidence about why it stopped. A tolerance
test is a domain criterion, not a transitive Eq relation suitable for hash keys.
Cycle detection needs an equality/key policy and a memory budget of its own.
A finite seen-state table is not a general symbolic termination solver.

### Pipe, Passthrough, Tap And Object Methods

The existing Nomi `x |> f(a)` lowers to `f(x, a)`. It neither maps x's elements nor
wraps a new function. pandas `.pipe` supplies a whole frame and can select a
named input slot; Nomi can adapt non-data-first APIs using a named helper or
explicit lambda. Do not add a second pipe operator or automatic argument holes.

`identity(x)` returns x without invoking an observer. A one-value tap calls an
observer then returns x on ordinary completion; a thru/apply operation returns
the callback's result instead. A stream tap observes only demanded/emitted
items. An observation failure, retained reference, mutation or extra subscription
changes behavior even when the returned reference is the same. Fanout/tee is
another operation: slower consumers require buffering/backpressure/drop policy.

The long form remains clear:

```nomi
result = transform(input)
observe_summary(result)?
return Ok(result)
```

Whether an earned tap API has a Unit observer, a Result observer or a separately
owned best-effort sink must be explicit. It is not pure identity and not a
reliable audit trail merely because a library names it inspect/peek/tap.
Observation of a redacted copied summary avoids exporting a whole resource-
bearing value, but redaction itself still needs its owner and policy.

OOP adds receiver binding, dispatch, discoverability, mutation and ownership,
not a different mathematical status for every operation. A bound method captures
its receiver; caching can retain it or ignore later mutations if its key omits
state. `value.method(args)`, a resolved extension and `algorithm(value,args)`
may offer related ergonomics without identical overload/dispatch semantics.
Nomi's protocol/import owner must make the selected implementation inspectable;
do not declare every method call equivalent to free-function insertion.

### Equality, Hash, Encoding And Function Identity

Java's Object evidence corrects two tempting universal claims: hash codes can
collide and need not be stable across processes; Serializable is a separate
opt-in interface. `toString` is not its serialization protocol. Python also
permits unhashable objects; mutable value equality is dangerous for hashed keys.
Nomi's accepted product-data hashing is conditional on all fields being
hashable, but its portable algorithm/profile still belongs to D3.

Keep separate candidate capabilities:

| Capability | Intended law or boundary | Does not provide |
| --- | --- | --- |
| Eq | Declared equivalence appropriate to the value domain | Approximate similarity or all partial orders |
| Hash | Equal values have equal hashes within a declared profile | Converse, globally unique ID, cryptographic strength |
| Order | Declared comparison and incomparability/NaN policy | Equality/hash/encoding by implication |
| Display/Inspect | Human-facing bounded/redacted view | Round trip, stable key or wire schema |
| Encode/Decode | Specified schema/profile and representable domain | Canonical bytes, safe authority reconstruction |
| Canonical encoding | One declared representation for supported equivalent values | Cross-schema equivalence or freedom from every collision |
| Content digest | Named digest over explicit bytes/profile | Semantic equality, authenticity or current authorization |

`decode(encode(x))` can equal x only within the declared supported domain and
equivalence. Schema migrations, lossy Float formatting, omitted private fields,
cycles, reference sharing and resource handles change that obligation. Runtime
functions/closures need code edition and capture/environment rules; source text
alone is not a portable callable. Prefer explicit inert operation descriptions
for remote/cache artifacts, not automatically serialized executable closures.
[Python pickle](https://docs.python.org/3/library/pickle.html) warns that untrusted
payloads can execute code during loading. Generic convenience cannot erase that
trust boundary; inspectable Nomi decoders must not deserialize authority.

### Cache, Once And Retry Are Different State Machines

A candidate cache contract must specify key extraction and equality; operation
edition; input/schema/numeric/backend and ambient dependency basis; result
ownership; bounded retention/eviction; error/negative-cache policy; invalidation;
and in-flight concurrency/cancellation. A closure's code/name alone does not
include its captured state. A private key may itself leak input data. Reading
retained results requires current policy, not just a matching content hash.

Caching an otherwise pure computation still gives the wrapper state, retention
and cost behavior. It may be observationally value-equivalent under a restricted
contract, but tooling cannot infer universal purity from the wrapped callback.
Python's cache documentation explicitly permits duplicated concurrent misses;
threadsafe storage is not single-flight. A single-flight API additionally owns
leader/waiter cancellation, recursive same-key calls, error fanout and cleanup.
Do not cache a single-use iterator/task/reader as a reusable immutable result.

Wrapper order is a semantic decision:

```text
tap(cache(f)): observe every lookup result, including hits
cache(tap(f)): observe only recomputations under that cache policy
retry(cache(f)): cached transient errors may defeat recomputation
cache(retry(f)): final outcomes may be retained under a separate policy
```

`once` may mean once per wrapper instance, once on successful completion, or one
in-flight call; none guarantees exactly-once external execution across crashes.
Retry classifies failures and repeats an explicit callable; an unknown remote
outcome needs reconciliation/idempotency evidence, not blind repetition.
Timeout, debounce and throttle own clocks and retained pending work. Resource
cleanup, transactions and cancellation keep their existing semantic owners.

## Candidate Nomi Layers And Admission

This is our design inference, not a conclusion dictated by the sources:

| Layer | Candidate responsibility | Admission boundary |
| --- | --- | --- |
| Core | Existing typed calls, closure capture, failure, effects, lifetimes, tasks and modules | D1-D3 must explain callable shape, captures, region escape and scalar equality. No new generic-operation keyword. |
| Reducible convenience | Existing first-argument pipeline and explicit lambdas | One inspectable ordinary-call long form; no currying/hole/composition punctuation. |
| Library/protocol | Small carrier-specific map/fold families, conditional Eq/Hash/codecs, explicit state/policy combinators | Full public callback/multiplicity/order/retention/outcome contract, locally resolved owner and independent examples |
| Scoped language tool | Earned query/numeric/relational transformation | Supported program subset, lawful rewrites and source maps; never arbitrary-call translation |

The current pure-only collection recommendation remains a candidate, with
effect-polymorphic strict APIs as challenger. This broader map does not settle
that fork. Candidate generic-operation metadata adds invocation phase, demand,
failure/error combination, result sharing and wrapper dependency context to the
existing callable contract only where needed. Not every function gets a giant
runtime metadata object.

Diagnostics must identify the failed obligation, for example:

```text
callback expects one value; supplied method also requires an unbound receiver
parallel reduction needs a declared merge law; this is only a sequential step
cached result retains Reader from region R; copy owned data before returning
iteration stopped at budget 8; no convergence witness was produced
tap observer failed before returning the value; downstream stage did not run
```

Source/call/adapter spans and the resolved protocol owner belong in machine
diagnostics and hover. These are future requirements, not existing outputs.
Formatting uses ordinary multiline calls at 80/100 columns. Domain effectful
loops remain a valid explicit implementation, not a failure of abstraction.

## Bounded Experiments

These extend open questions 2/3/4/5/8/9/10/17 rather than create a new backlog.
Each full comparison uses the three programs above, diagnostics, reader repair,
80/100-column formatting and frontend-neutral positive/negative facts.

| ID | Genuine fork | Discriminator/deliverable | Stop/removal rule |
| --- | --- | --- | --- |
| GA1 | Specific List/Option/Result operations versus one higher-kinded map protocol | Type/inspect each call, include Set collisions and tensor filtering; compare imported method/free-function ambiguity | Keep specific APIs if shared protocol obscures carrier laws or needs unexplained inference. |
| GA2 | Pure-only strict callbacks versus effect-polymorphic strict callbacks | Invoke/count/trace/error facts, captured mutation and defaulted/bound receiver adapters | No fusion based on purity alone; no admission without typed callback evidence. |
| GA3 | Seed-including scan versus separate seed/history result | Empty input, input length, heterogeneous state, map_accum and mutable-state snapshots | Choose one comprehensible initial contract; no synonymous prelude families. |
| GA4 | Sequential fold only versus a separate lawful summary/merge protocol | Nonassociative and floating cases, ordered errors, chunk merges and capability limits | Reject reassociation when declared laws/profile cannot preserve the required observations. |
| GA5 | Explicit statements versus effectful tap and demand-aware observation | Returned value, observer failure, mutation, skipped demand, cache/tap order, audit evidence | Keep statements when tap conceals outcome, mutation or retention. |
| GA6 | Generic callable memoization versus explicit context-bound operation cache | Capture changes, operation/schema/profile keys, mutable results, error TTL and single-flight/cancellation | No caching of live authority or silent inference of completeness from a function hash. |
| GA7 | General fix combinator versus domain-owned bounded iteration | Finite stabilization, cycles, approximate tests, budget, nonfinite states and effectful steps | No universal convergence claim; keep mathematical/recursive/operational fixed points distinct. |
| GA8 | Universal object methods versus conditional protocols and explicit codecs | Eq/hash coherence, mutable keys, unsupported fields, round trips, editions, untrusted input | Reject universal serialization/hash/copy/ordering when supported domains or authority cannot be stated. |

## Executed Local Evidence

Reproduce without writing the historical capture:

```bash
python3 docs/research/features/probe_generic_operations.py --check docs/research/features/generic_probe_results.json
pytest -n 0 prototype/tests/unit/tools/test_generic_operations_research.py
```

The [capture](features/generic_probe_results.json) records twelve discriminators, with a
limit on each. Python host versions are provenance, not required to equal the
current version. The checker rejects outcome/scope drift, duplicate fields and
wrong JSON types without rewriting evidence. Generation requires an explicit
`--output` argument; `--check` never regenerates expected results.

| Probe | Executed distinction | Experiment | Limit |
| --- | --- | --- | --- |
| GP01 | Strict two-phase map versus fused callback traces and failure prefix | GA2 | Original finite Python model; not Nomi optimizer execution |
| GP02 | Seeded fold, unseeded empty reduction, left/right operand direction, seeded scan | GA3/GA4 | functools/itertools plus explicit finite right fold; not foreign reduce conformance |
| GP03 | Subtraction and finite binary floating reassociation | GA4 | Chosen Python arithmetic examples, not all numeric profiles |
| GP04 | All-row outcomes versus fail-fast invocation prefix | GA1/GA2 | Original tagged-result model; not Nomi Result typing |
| GP05 | Passthrough object identity despite mutation, and observer failure | GA5 | Original immediate tap; no logging service or lazy library |
| GP06 | Lazy map has no construction calls; partial demand invokes only a prefix | GA2/GA5 | Python map iterator, not Nomi Stream or foreign schedule |
| GP07 | Same repeat reference versus fresh calls versus iterated state | GA7 | Python repeat and original finite models; no remote retries |
| GP08 | Stabilization, oscillation, budget and supplied comparison policy | GA7 | Bounded integer-state iteration; no numerical solver or termination proof |
| GP09 | Cached mutable capture stays stale; tap/cache wrapper order changes observation count | GA5/GA6 | Sequential functools cache, no concurrency/single-flight enforcement |
| GP10 | Hash collisions remain unequal; a mutable List cannot be a hash key | GA8 | Python host objects; no Java VM or portable Nomi Hash implementation |
| GP11 | Equal mappings can encode to different bytes; JSON List round trip differs from tuple | GA8 | Python JSON subset and sorted-key example, not a general canonical encoder |
| GP12 | Mutable scan history aliases versus copied states; map_accum emits a different type | GA3 | Original state models, no compiler encapsulated-mutation proof |

Still unperformed: a generic/effect/region checker, protocol coherence,
parallel reductions, actual stream cancellation/backpressure, authenticated
cache policy, clock/scheduler combinators, numerical convergence proofs,
framework execution and human repair trials. These probes sharpen admission;
they do not close GA1-GA8 or justify production APIs by their count.
