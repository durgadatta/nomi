# Remaining Language Feature Gap Survey

> Status: source research for unresolved Nomi feature families.
>
> Scope: documentation-only synthesis of language features that remain thin,
> scattered, or future-layered in the current Nomi corpus. This is not an
> active syntax spec. Fold stable decisions into focused feature docs,
> convenience notes, or `../language/language_spec.md`.
>
> Purpose: convert "remaining language features" into Nomi design packets:
> extension/protocol dispatch, context parameters, capabilities/effects,
> state/mutation, contracts, macros, module values, structured concurrency, and
> transducer-style flow.

## Why This Pass Exists

The existing corpus covers many language families, but the remaining design
pressure is no longer "which languages have interesting syntax?" It is:

```text
Which feature families can make Nomi grow without splitting the language?
```

The highest-risk remaining features are powerful because they solve real
problems, but each can become a second language if admitted too early:

- traits/protocols/typeclasses can become a hidden dispatch system;
- context parameters can hide dependencies;
- capabilities/effects can become academic overhead;
- macros can destroy local readability;
- state tools can weaken local reasoning;
- contracts can duplicate types, tests, and constraints;
- structured concurrency can add a second function color;
- module values can create a parallel type/value world;
- transducers can make flow extremely reusable but hard to teach.

The synthesis target is:

```text
source feature -> durable user need -> Nomi normal form -> admission posture
```

## Source Scan

Primary and near-primary references used for this pass:

- Rust Book, traits:
  <https://doc.rust-lang.org/stable/book/ch10-02-traits.html>
- Rust Reference, traits and dyn compatibility:
  <https://doc.rust-lang.org/stable/reference/items/traits.html>
- Rust Reference, procedural macros:
  <https://doc.rust-lang.org/reference/procedural-macros.html>
- Rust Book, ownership and borrowing:
  <https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html>
  and <https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html>
- Swift Book, macros:
  <https://docs.swift.org/swift-book/documentation/the-swift-programming-language/macros/>
- Swift Book, property wrappers:
  <https://docs.swift.org/swift-book/documentation/the-swift-programming-language/properties/>
- Kotlin documentation, context parameters:
  <https://kotlinlang.org/docs/context-parameters.html>
- Scala 3 Reference, extension methods, context functions, and opaque types:
  <https://docs.scala-lang.org/scala3/reference/contextual/extension-methods.html>,
  <https://docs.scala-lang.org/scala3/reference/contextual/context-functions.html>,
  and <https://docs.scala-lang.org/scala3/reference/other-new-features/opaques-details.html>
- OCaml manual, modules and first-class modules:
  <https://ocaml.org/manual/modules.html>
  and <https://ocaml.org/manual/firstclassmodules.html>
- Racket Reference, contracts:
  <https://docs.racket-lang.org/reference/contracts.html>
- Clojure Reference, transducers:
  <https://clojure.org/reference/transducers>
- Clojure Reference, refs/transactions and agents:
  <https://clojure.org/refs>
  and <https://clojure.org/reference/agents>
- Koka book, effect types and handlers:
  <https://koka-lang.github.io/koka/doc/book.html>
- Go package `context`:
  <https://go.dev/pkg/context/>
- OpenJDK JEP 525, Structured Concurrency (Sixth Preview, JDK 26):
  <https://openjdk.org/jeps/8366891>
- Pony reference capabilities:
  <https://www.ponylang.io/learn/reference-capabilities/>

## Cross-Cutting Thesis

The remaining features mostly orbit four design problems:

1. **How does behavior attach to data?**
   Traits, protocols, extension methods, typeclasses, active patterns, and
   property wrappers all answer this.
2. **How does context travel without clutter?**
   Context parameters, scoped values, Go contexts, capability systems, and
   effect types all answer this.
3. **How does controlled power stay inspectable?**
   Macros, module values, compile-time derivation, and contracts all answer
   this.
4. **How does a program do more work while preserving local reasoning?**
   state cells, transactions, structured concurrency, transducers, and
   cancellation all answer this.

Nomi should not import these as independent feature families. It should reduce
them through existing normal forms:

```text
binding
data
function/call
pattern
flow
block policy
absence/result
explanation
module/package
capability/world
```

## 1. Traits, Protocols, Typeclasses, And Extension Methods

### User Need

Users need to say:

```text
values of different concrete shapes support this shared operation
```

Rust traits, Swift protocols, Scala extension methods, Haskell typeclasses,
and Kotlin extensions all provide ways to define shared behavior without
forcing inheritance.

### What Works

Rust traits make behavior explicit and reusable through bounds. Scala 3 makes
extension methods a named mechanism rather than an implicit-class trick. Swift
protocols and extensions support a familiar "this type conforms to this
behavior" model.

The durable lesson is that behavior attachment has two distinct jobs:

- **surface ergonomics:** call `x.method()` instead of `method(x)`;
- **semantic constraint:** accept only values that satisfy a named behavior.

### What Fails

The danger is hidden dispatch complexity:

- method lookup can become non-local;
- extension methods can make APIs look owned by a type when they are imported;
- typeclass/given resolution can produce surprising ambiguity;
- dynamic dispatch and static dispatch have different performance and
  capability implications;
- protocol/trait associated types can quickly require advanced static typing.

### Nomi Implication

Nomi should separate method-call spelling from behavioral constraints.

Nomi normal form:

```text
x.method(a) -> method(x, a) unless owned method dispatch is explicitly known
behavior constraint -> named capability/protocol requirement
extension method -> module-exported function with receiver-first call sugar
trait/protocol -> future data/function contract, not first-layer dispatch
```

Admission posture:

- receiver-first call sugar can be ordinary surface syntax;
- extension functions belong with modules and imports;
- protocol/trait constraints are future typed-layer work;
- no hidden global extension lookup in the first everyday layer.

## 2. Context Parameters, Scoped Values, And Dependency Context

### User Need

Programs often need services that are not business arguments:

```text
logger
clock
locale
database/session
request id
auth capability
tracing context
deadline/cancellation token
```

Passing these everywhere is noisy. Hiding them completely is dangerous.
Kotlin context parameters and Scala contextual abstractions make required
context visible in function declarations while resolving values from the call
site. Go's `context.Context` keeps cancellation and request-scoped values
explicit as a first argument. Java scoped values are designed to cooperate with
structured concurrency.

### What Works

The best designs make requirements visible:

```text
this function requires Clock and Logger
this block provides Clock and Logger
```

Kotlin's newer context parameters are especially useful evidence because they
replace context receivers and avoid making context values implicit receivers in
the function body. That is a readability improvement: dependencies are still
named values.

### What Fails

Context mechanisms fail when:

- dependency resolution becomes magical;
- ambiguous context values produce confusing errors;
- capabilities are available too broadly;
- request-scoped values become untyped key/value bags;
- hidden context makes tests and examples non-local.

### Nomi Implication

Nomi should grow context through block policies and explicit capability values
before adding implicit context parameters.

Nomi normal form:

```text
context requirement -> function metadata + capability requirement
context provider -> block policy that extends an evaluation context
context lookup -> explicit name unless feature profile allows scoped lookup
Go Context -> ordinary value carrying deadline/cancellation/provenance
```

Possible future shape:

```nomi
with clock, logger:
    report = build_report(input)
```

Do not promote implicit context resolution until `explain` can show:

```text
required capability -> provider -> scope -> value used -> redaction policy
```

## 3. Capabilities, Effects, And World Contact

### User Need

Users need to touch the world safely:

```text
read files
write files
make HTTP calls
spawn processes
read time
generate randomness
open transactions
access secrets
```

Koka shows the typed-effect version: function types track effects. Pony shows
reference capabilities for safe sharing. Rust ownership and borrowing show
compile-time control over aliasing and mutation. Nomi needs the practical
version before the theoretical version.

### What Works

Capability and effect systems make authority visible. They allow tools to ask:

```text
Can this function read the network?
Can this value be shared across tasks?
Can this block mutate this store?
What cleanup runs if it fails?
```

### What Fails

Effect systems can become too academic for everyday code. Capability systems
can expose too much type machinery. Ownership-like rules are powerful but
would distort Nomi's high-level daily layer if copied directly.

### Nomi Implication

Nomi should start with practical world-contact values:

```text
FileSystem
Network
Clock
Random
ProcessHost
SecretStore
Transaction
```

Nomi normal form:

```text
world contact -> effectful host operation requiring capability
capability -> value whose use is visible in explain/event traces
effect -> metadata on a call/block, not a required first-hour type concept
ownership/borrowing -> future optimization/safety layer, not daily syntax
```

Admit this as a feature packet before any effect syntax:

```text
state_and_capability_model.md
```

It should specify capabilities, redaction, event traces, host permissions,
and test fixtures.

## 4. State, Mutation, Transactions, And Property Wrappers

### User Need

Everyday programs mutate:

- variables are rebound;
- collections are updated;
- caches are filled;
- files are written;
- transactions commit or roll back;
- UI state changes;
- a field needs validation or persistence behavior.

Clojure separates state tools: atoms, refs/transactions, agents, and vars.
Swift property wrappers bundle reusable get/set behavior around fields. Rust
uses ownership/borrowing to statically constrain mutation.

### What Works

Clojure is a useful warning and inspiration: mutable state is not one thing.
Independent atomic state, coordinated transactional state, asynchronous state,
and dynamic vars have different semantics.

Swift property wrappers reveal a user need Nomi already has pressure for:
attach reusable behavior to a binding or field without repeating getter/setter
boilerplate.

### What Fails

Mutation becomes hard when:

- rebinding and storage mutation look identical;
- field wrappers hide effects;
- transactional retry is invisible;
- aliases make local reasoning impossible;
- validation lives in setters, constructors, decode, and tests separately.

### Nomi Implication

Nomi should define state as a feature packet with a small taxonomy:

```text
rebind name
mutate container
derive updated value
transactional update
field policy
external side effect
```

Nomi normal form:

```text
assignment -> binding or store update, depending on target
field policy -> constraint/binding wrapper with explicit read/write behavior
transaction -> block policy with commit/rollback events
agent/async state -> future library over block/concurrency
```

Property-wrapper-like behavior should be adapted as **binding policy**, not
annotation magic:

```nomi
data Account:
    balance: Money, non_negative(balance)
```

A future field policy could be accepted only if `explain` shows what happened
on read, write, decode, display, and serialization.

## 5. Contracts, Assertions, And Executable Invariants

### User Need

Users need lightweight ways to state:

```text
this function expects X
this function returns Y
this module exports values satisfying this contract
this boundary validates external input
```

Racket contracts show a mature higher-order contract system. Kotlin contracts
show compiler-facing assertions about call behavior. Eiffel-style design by
contract and runtime assertions show the same pressure from another direction.

### What Works

Contracts are valuable because they sit at boundaries:

- module exports;
- function arguments/results;
- external data decode;
- callback protocols;
- generated code;
- tests and examples.

They communicate blame: if a boundary contract fails, the diagnostic can name
which side violated the promise.

### What Fails

Contracts fail when they duplicate types, constraints, tests, and runtime
checks without a single explanation model. Higher-order contracts can also
introduce runtime wrappers that surprise performance and identity semantics.

### Nomi Implication

Nomi already has the seed: binding constraints.

Nomi normal form:

```text
argument contract -> parameter binding constraint
return contract -> result binding constraint
data invariant -> data field/constructor constraint
module contract -> export boundary constraint
decode contract -> external boundary validation with provenance
```

Adopt contracts as a **constraint and explanation story**, not a separate
contract DSL. The next packet should explain:

```text
where is the constraint checked?
what value failed?
who supplied the value?
what source path/provenance is attached?
can all failures be accumulated?
```

## 6. Macros, Derivation, And Compile-Time Generation

### User Need

Users need to avoid boilerplate:

- deriving equality/display/serialization;
- generating API clients;
- building DSLs;
- adding repetitive members;
- checking domain-specific syntax;
- producing compile-time diagnostics.

Rust procedural macros, Swift macros, Scala inline/macros, Racket macros, and
OCaml PPX all demonstrate the value.

### What Works

Swift's macro model is especially instructive for Nomi because it fences macro
power:

- macro declaration and implementation are separated;
- macro roles declare where expansion can happen;
- generated names can be declared;
- input and output are syntax-checked;
- macro expansion is an additive operation;
- macro implementations can be tested as syntax transforms.

Rust procedural macros show the ecosystem power of derive and attribute
macros, but also the hygiene and diagnostics burden.

### What Fails

Macros can destroy local reasoning:

- generated names are hidden;
- imports change syntax;
- error spans point into generated code;
- build-time execution becomes a security surface;
- tooling cannot understand unexpanded code;
- macro-heavy ecosystems become hard for beginners and AI tools.

### Nomi Implication

Nomi should keep macros future-fenced behind explicit `quote`/`use`/expansion
boundaries.

Nomi normal form:

```text
quote -> SyntaxValue with source spans
macro -> SyntaxValue -> SyntaxValue transform
derive -> declared expansion recipe over data shape
expansion -> inspectable event with generated spans and names
```

Admission posture:

- built-in derivations may arrive before user macros;
- user macros require expansion display, source maps, feature profiles,
  capability restrictions, and tests;
- no global syntax-changing imports in the everyday layer.

## 7. Module Values, Functors, And Package-Scale Abstraction

### User Need

Programs eventually need:

```text
hide implementation
expose a signature
parameterize a module by another module
choose an implementation at runtime
organize package boundaries
```

OCaml modules and first-class modules are the strongest evidence here.
They distinguish module-level abstraction from ordinary values while allowing
modules to be packed as values when needed.

### What Works

Module signatures make boundaries explicit. Functors support reusable
module-level construction. First-class modules allow dynamic choice of
implementations without losing the abstraction boundary.

### What Fails

The cost is a second language of modules:

- module expressions and value expressions differ;
- packing/unpacking syntax is heavy;
- type components can escape if the rules are wrong;
- beginners often do not know when a record of functions is enough.

### Nomi Implication

Nomi should begin with simple modules:

```text
file/module -> explicit exports/imports
package -> manifest + capabilities + dependencies
interop -> visible boundary
```

Nomi normal form:

```text
module -> namespace + export bindings + metadata
module signature -> export constraints
functor -> function from module-like record to module-like record
first-class module -> package of bindings as ordinary value, future layer
```

Do not add module functors until ordinary packages, imports, re-exports,
capability identity, and Python interop have one coherent story.

## 8. Structured Concurrency, Cancellation, And Scoped Work

### User Need

Users need to do concurrent work without leaks:

```text
start related tasks
wait for them together
cancel unfinished work on failure
propagate deadlines
observe concurrent failures
clean up resources
```

Java's structured concurrency preview is useful current evidence: as of JDK 26,
OpenJDK is still previewing and refining the API. Virtual threads are already
part of Java's Loom story, but the structured API has gone through multiple
preview rounds because completion policy, cancellation, and observability are
hard to get right.

Go's `context.Context` shows another side: cancellation and deadlines are
ordinary values passed across API boundaries, but value bags and cancellation
causes can become convention-heavy.

### What Works

Structured concurrency is a near-perfect match for Nomi's block-policy design:

```text
concurrent subtasks live within one lexical block
the parent owns joining and cancellation
failure is aggregated or policy-selected
observability follows the block tree
```

### What Fails

Concurrency designs fail when:

- async creates a second function color;
- child tasks outlive their parent scope;
- cancellation has no reason/provenance;
- errors race and become nondeterministic;
- task trees are invisible to diagnostics.

### Nomi Implication

Nomi should preserve the current design stance:

```text
no async/await as Nomi's core control model
structured concurrency as block policy
cancellation at yield/checkpoints
Result for expected concurrent failures
explainable task tree
```

Nomi normal form:

```text
parallel/retry/timeout -> block policy
child task -> value with lifecycle and result
cancellation -> block event with cause and source
join policy -> function/block deciding aggregate result
```

The important next artifact is a block-policy prelude packet, not a standalone
concurrency syntax proposal.

## 9. Transducers, Reducers, And Reusable Flow Plans

### User Need

Users want transformation logic independent of where values come from:

```text
same map/filter pipeline over list
same transform over stream
same transform over channel
same transform into vector/table/file
```

Clojure transducers are composable transformations independent of input and
output context. Reducers show eager/parallel reduction and deferred
transformation without intermediate collections.

### What Works

The key insight is decoupling transformation from source and sink:

```text
transform recipe
input process
accumulation process
output materialization
```

This maps well to Nomi's future collection/table vocabulary and plan values.

### What Fails

Transducers are hard to teach because the simple surface hides a higher-order
reduction protocol. Multi-result transforms, early termination, buffering, and
stateful transformations can surprise users.

### Nomi Implication

Nomi should adapt the idea as **flow plans**:

```text
where/select/derive pipeline -> executable now over collection
flow plan -> reusable transformation value
materialize -> choose list/table/stream/sink
explain -> show stages, cardinality, laziness, early termination
```

Nomi normal form:

```text
transducer -> function transforming a reducer
flow plan -> Nomi-owned stage list with cardinality/failure policy
reducer -> fold policy with accumulator binding
```

This belongs after ordinary flow verbs are stable.

## Nomi Adopt / Refuse / Adapt

| Feature family | Decision | Nomi reason |
| --- | --- | --- |
| Receiver-first method sugar | Adapt | Useful readability; reduce to function calls when possible. |
| Full trait/protocol/typeclass system | Future | Needs typed dispatch, module coherence, and diagnostics. |
| Extension methods | Adapt | Module-owned functions with receiver-first call sugar; no global magic. |
| Kotlin/Scala context parameters | Adapt later | Real need, but must grow from capability scopes and explain. |
| Go context values | Adapt | Deadlines/cancellation as values are practical; avoid untyped value bags. |
| Koka-style effect types | Research-only for now | Strong model, too heavy for first everyday layer. |
| Pony/Rust capability/ownership rigor | Research-only for daily layer | Valuable safety pressure; not Nomi's high-level starting point. |
| Swift property wrappers | Adapt | Recast as binding/field policies with visible read/write behavior. |
| Clojure refs/agents | Adapt | Useful state taxonomy; first specify Nomi state and transactions. |
| Racket contracts | Adapt | Use constraints plus explanation, not a separate contract language. |
| Swift macro fences | Adopt as future macro gate | Role-limited, additive, testable expansion is the right discipline. |
| Rust procedural macros | Adapt cautiously | Powerful derivation model; requires hygiene, spans, and security. |
| OCaml module functors | Future | Valuable for library authors; too much before simple package story. |
| First-class modules | Future/library | Prefer records of functions until module signatures matter. |
| Structured concurrency | Adopt approach | Fits block policy; no function coloring. |
| Clojure transducers | Adapt | Flow-plan inspiration after ordinary pipeline verbs settle. |

## Feature Packet Recommendations

The remaining research should become concrete packets in this order:

1. **State and capability model**
   - capabilities for file/network/time/process/secret;
   - rebinding vs storage mutation;
   - transaction block policy;
   - redaction and explain events.
2. **Extension and receiver-call story**
   - method-call sugar;
   - module-owned extension functions;
   - import visibility;
   - no hidden global dispatch.
3. **Contracts and binding policy**
   - parameter/result/data/module constraints;
   - blame/provenance;
   - accumulated failure reporting.
4. **Block policy prelude**
   - `using`, `retry`, `timeout`, `parallel`, `transaction`, `trace`;
   - yield/cancellation/result behavior;
   - event schema.
5. **Macro and derivation gate**
   - built-in derivations;
   - source spans and generated names;
   - expansion display;
   - capability restrictions for macro execution.
6. **Flow plan model**
   - transform values;
   - materialization;
   - cardinality and laziness;
   - explainable pipeline execution.
7. **Simple module/package story**
   - import/export;
   - package manifest;
   - Python interop boundary;
   - future module signatures.

## Bottom Line

The remaining language features should not be treated as a checklist to add.
They should be treated as stress tests for Nomi's normal forms.

The strongest direction is:

```text
ordinary explicit core first
library/block/capability experiments second
syntax only after explainable normal forms
advanced power fenced by feature profiles and expansion traces
```

Nomi can learn from advanced languages without becoming an advanced-language
museum. The feature families that survive should make everyday programs more
local, inspectable, and reliable.

