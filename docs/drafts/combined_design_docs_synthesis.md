# Nomi Design Synthesis

> Status: deduplicated draft.
>
> This file consolidates the essential ideas from the active design docs,
> adjacent design notes, and archived design-review material. It is organized
> by concept rather than by source file. When older notes conflict with the
> current active foundation and draft language spec, this synthesis follows the
> active foundation/spec and records the older idea only as background.

## Purpose

Nomi is an experimental general-purpose programming language for ordinary,
medium-level programming: scripts, command-line tools, notebooks, data cleanup,
API and configuration boundaries, small services, application logic, teaching
examples, and readable glue between libraries.

The design target is not feature accumulation. Nomi should grow by making a
small set of semantic primitives combine into richer forms while preserving
local reasoning, readable syntax, and inspectable reduction.

The one-line product promise is:

```text
few remembered operations, many composable uses
```

The everyday experience should be:

```text
small script
-> clearer script
-> reusable functions
-> named data
-> checked boundaries
-> readable transformations
-> explainable failures
```

## Design Thesis

Programming is the act of externalizing intention into executable structure.
A language should help a person form, inspect, revise, trust, and explain that
structure.

Nomi should feel locally readable like Python, but it should not become
"Python plus features." It can learn from Python, ML/Haskell, Lisp/Scheme,
ALGOL, Ruby, Kotlin, Rust, Swift, R, APL, SQL, Mathematica, Pydantic, JSON
Schema, Racket contracts, and capability systems. The source languages are
reference experiments, not ingredients.

The design process is:

```text
primitive programming need
-> existing language references
-> extracted durable idea
-> Nomi semantic role
-> Nomi syntax
```

The anti-pattern is:

```text
admired syntax
-> copied into Nomi
-> explanation after the fact
```

## First-Principles Ladder

Nomi's design starts from primitive cognitive acts rather than from a syntax
catalog.

| Act | Language role | Typical surface |
| --- | --- | --- |
| Distinguish | value, literal, identity, equality, variant | `42`, `"Ada"`, `Ok(user)` |
| Name | binding, scope, context | `email = raw.email` |
| Judge | constraint, predicate, type, diagnostic | `age:int, age >= 13 = raw_age` |
| Transform | function, call, expression, pipeline | `normalize(email)`, `raw |> strip` |
| Choose | condition, pattern, match, guard | `match result: case Ok(user): ...` |
| Group | data, collection, table, module | `data User(id:UserId, email:Email)` |
| Repeat | loop, map, where, fold, query | `users |> where(_.active)` |
| Sequence in time | block, yield, policy, resource | `retry(3): send(request)` |
| Touch the world | effect, world, capability | `world(fs, network): ...` |
| Explain | example, trace, diagnostic | `examples: " A@B.COM " => "a@b.com"` |
| Reflect and rewrite | quote, syntax value, rule, notation | `quote: x + 0` |

The conceptual dependency order is:

```text
source/context/spans
-> values
-> bindings/scope
-> constraints/diagnostics
-> functions/calls
-> data and external boundaries
-> patterns/match
-> collections/repetition
-> blocks/yield
-> effects/worlds/capabilities
-> examples/traces/explanation
-> quote/rewrite/scoped notation
```

This is not a strict implementation order. It is a design discipline: higher
features must reduce back to lower concepts.

## Small Core

The first everyday core is:

```text
Source
Value
Binding
Constraint
Function
Call
Data
Pattern
Match
Collection
Block
Example
Trace
Diagnostic
Module
```

Future layers may add:

```text
Effect
World
Capability
Quote
Rewrite
Notation
```

The core is not minimal for a machine. It is minimal for a programmer's memory.
Each feature should reduce to these ideas in a way that diagnostics can explain.

## Construction And Elimination Lens

One useful idea from the type-theory draft is that many sophisticated features
can be understood as construction and elimination.

Construction means providing enough information to make a value:

```python
User(id=id, email=email)
Ok(user)
(x, y)
```

Elimination means using a value by exposing the structure it guarantees:

```python
match result:
    case Ok(user):
        user.email
    case Err(error):
        explain(error)
```

This lens keeps data, variants, pattern matching, guarded constraints,
decoding, and future dependent/refinement-style ideas connected:

```text
constructor -> asserts a structured fact
pattern     -> asks whether that fact is present and binds what follows
constraint  -> judges whether the constructed or eliminated value is acceptable
diagnostic  -> explains which fact or judgement failed
```

Nomi should use this idea pragmatically. It does not need to expose a formal
proof system in the first language, but it should preserve the continuity
between creating values, inspecting values, and explaining why inspection or
validation failed.

## Coherence Contract

### One Binding Story

Names are introduced through binding. Assignment, parameters, block parameters,
loop variables, pattern captures, imports, exception aliases, and eventual
external structural contracts should all be understandable as:

```text
receive a value
-> optionally check it
-> bind it in a scope
```

Examples:

```python
age:int, age >= 0 = raw_age

func signup(age:(int, age >= 13)):
    ...

each(users) -> user:User:
    send(user.email)

match payload:
    case {"age": age:(int, age >= 13)}:
        signup(age)
```

If these require separate validation engines, the language is drifting.

### One Function And Call Story

Functions transform values. Calls evaluate a callee, map arguments to parameter
bindings, validate those bindings, run the body, and produce a value.

Pipelines, collection transforms, method-call sugar, and composition must reduce
to ordinary function/call semantics. They may improve readability, but they
must not become separate execution models.

### One Data Story

Program-owned domain values are declared with `data`. A data declaration creates
constructors, fields, equality/display rules, and pattern forms.

Fields reuse binding and constraints. Data does not get a private validation
language.

### One External Boundary Story

Older notes explored a `shape` keyword as a peer to `data`. The current design
demotes that for the first everyday layer.

Current decision:

```text
Do not introduce a separate shape keyword in the first everyday layer.
```

Use:

```text
data declaration      -> construct an owned program value
structural pattern    -> recognize/project part of an external value
constraint            -> judge whether a received value is acceptable
decoder/parser        -> convert external structure into owned data
```

External data should cross a visible boundary:

```python
signup_input = SignupInput.decode(request.json)
```

or through an explicit pattern:

```python
match request.json:
    case {"email": email:(str, contains(email, "@")), "age": age:(int, age >= 13)}:
        signup_input = SignupInput(email=email, age=age)
```

The word "shape" remains useful as an ordinary design term. If a future
`shape` keyword is admitted, it must mean a named structural pattern/constraint,
not a second data declaration system.

### One Pattern Story

Patterns test structure and bind names. Destructuring, `match`, data variants,
mapping patterns, and block parameters should reuse one pattern model.

Pattern failure and constraint failure are related but distinct:

```text
pattern failure: this structure did not fit
constraint failure: this structure fit, but a value was unacceptable
```

### One Block Story

A block is caller-side code attached to a call. The callee may invoke it with
`yield`.

```python
retry(3, on=NetworkError):
    send(request)

using(open(path)) -> file:
    text = file.read()
```

This is the shared basis for resource handling, retries, transactions, tests,
tracing, fixtures, and other time-shaped policies. A new keyword should not be
needed for every policy.

### One Expression Flow Story

Nested calls, pipelines, collection transforms, table queries, and composition
are different views of value flow.

```python
clean =
    raw
    |> strip
    |> lower
    |> normalize_space
```

Pipeline applies a value now. Composition builds a function for later.
Collection and table operations should remain traceable transformations, not a
separate string language.

### One Explanation Story

Diagnostics are part of the language, not decoration.

Each semantic event should be able to explain itself:

- binding explains failed constraints;
- calls explain argument mapping;
- data construction explains field failures;
- decoding explains external field paths;
- patterns explain why they did or did not match;
- pipelines explain intermediate values;
- blocks explain yield, retry, cleanup, and cancellation;
- examples explain intended behavior;
- future rewrite systems explain which rule fired;
- future capability systems explain what authority was used.

## Everyday Language Surface

This section consolidates the intended concrete surface. It describes the
target language, not necessarily the current Python-hosted prototype.

### Program And Layout

A Nomi file is a module. Top-level statements execute in module order when the
file is run as a program. Top-level declarations bind names in module scope.

```python
module app.signup

import csv

data Person:
    name:str
    email:str, contains(email, "@")

func load(path:str) -> list[Person]:
    rows = csv.read(path)
    return rows |> map(Person.decode)
```

Source files are UTF-8 text. Newlines separate logical lines except inside open
delimiters or explicit continuation positions. Indentation is significant. A
line ending in `:` begins an indented block. Mixed tabs and spaces should be
rejected by conforming tools.

Comments begin with `#`. Documentation comments are ordinary comments
immediately preceding a declaration; tooling may attach them to that
declaration.

Reference naming style:

```text
lower_snake_case      values, functions, modules, fields
UpperCamelCase       data types, variant constructors, type parameters
_leading_underscore  private or intentionally local convention
_                   wildcard pattern or placeholder
```

In patterns, bare lowercase identifiers bind new names. Uppercase identifiers
are resolved as constructors or named constants.

### Values And Truth

Every expression evaluates to a value or raises an error.

Core value categories:

- numbers;
- booleans;
- strings;
- absence;
- tuples;
- lists;
- dictionaries;
- functions;
- data values;
- modules;
- errors.

Canonical literals:

```python
42
3.14
true
false
none
"hello"
[1, 2, 3]
(1, 2)
{"name": "Ada", "age": 36}
```

Compatibility layers may accept Python spellings such as `True`, `False`, and
`None`, but the Nomi spec uses lowercase.

Conditions require boolean values. Nomi should not use Python-style broad
truthiness for ordinary conditions:

```python
if len(items) > 0:
    ...
```

This avoids accidental branching on numbers, strings, lists, or `none`.

### Bindings And Scope

A binding connects a value to a name or pattern target in a scope.

```python
name = "Ada"
age:int = raw_age
email:str, contains(email, "@") = raw_email
```

Scopes include:

- module scope;
- function scope;
- block scope;
- match-case scope;
- comprehension or collection-transform scope.

Names are resolved lexically. Inner scopes may shadow outer bindings.

Rebinding without a new annotation keeps the active constraints for that
binding:

```python
count:int, count >= 0 = 0
count = count + 1
```

Rebinding with a new annotation replaces the constraint set in the current
scope:

```python
value:int = 1
value = 2
value:str = "2"
```

`const` introduces a binding that may not be rebound in the same scope:

```python
const pi:float = 3.14159
```

### Constraints

A constraint is an executable judgement over a tentative binding.

```python
age:int, age >= 13 else "Must be at least 13" = raw_age
```

Binding proceeds as:

```text
evaluate right side once
-> tentatively bind target names
-> check constraints in the tentative environment
-> commit bindings if all checks pass
-> raise BindingError if any check fails
```

Constraint forms:

```python
age:int = value
email:str, contains(email, "@") = value
amount:int, amount > 0 = value
age:int, age >= 13 else "Must be at least 13" = value
```

Multiple constraints are evaluated from left to right.

Parameterized constraints are part of the target language:

```python
list[int]
dict[str, int]
Result[User, SignupError]
```

The language treats type annotations as runtime constraints first. Static tools
may use them for analysis, but core runtime semantics must not depend on a full
static type checker.

Constraint failure raises `BindingError` with structured context:

```text
name
value
constraint
message
source_span
binding_kind
```

Example diagnostic:

```text
BindingError: age failed constraint age >= 13
  value: 12
  binding: parameter age in signup(...)
  note: Must be at least 13
```

### Functions And Calls

Named functions use `func`:

```python
func add(x:int, y:int) -> int:
    return x + y
```

`func` is preferred over `def` because it names the construct directly: a
function definition. It preserves Python-like block readability while giving
Nomi its own semantic vocabulary.

Arrow functions are expression-level function values:

```python
double = (x:int) => x * 2
is_adult = (age:(int, age >= 18)) => true
```

Arrow functions contain one expression. Use `func` for named or block-bodied
functions.

Parameters are bindings. Parameter constraints are checked after
Python-compatible argument mapping:

```python
func signup(
    email:(str, contains(email, "@")),
    age:(int, age >= 13),
    plan:Plan = Plan.Free,
) -> SignupInput:
    return SignupInput(email=email, age=age, plan=plan)
```

Calls evaluate the callee, evaluate arguments left to right, map arguments to
parameters, validate parameter constraints, execute the body, and return the
result. Unknown arguments, duplicate arguments, missing required arguments, and
wrong arity raise `CallError`.

### Data

`data` defines program-owned values.

Product data:

```python
data User(id:UserId, email:Email, plan:Plan)
```

Block form:

```python
data SignupInput:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"
    plan:Plan = Plan.Free
```

Fields are bindings checked by the constructor. Data fields are read-only in
the everyday language.

Sum data:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)
```

Constructors also serve as patterns:

```python
match fetch_user(id):
    case Ok(user):
        user.name
    case Err(error):
        explain(error)
```

Raw external structure does not silently become domain data. `DataName.decode`
is the standard explicit conversion boundary:

```python
signup_input = SignupInput.decode(raw)
```

Default decoder policy:

- mapping keys correspond to field names;
- missing required fields fail;
- unknown fields fail;
- defaults are applied after required fields are checked;
- field constraints are checked exactly as constructor constraints;
- errors include field paths.

Lenient decoding is a library concern and must be explicit.

### Patterns And Match

Patterns inspect structure and bind names.

Pattern forms include:

```python
_
42
"ok"
true
none
name
name:int
name:(int, name >= 0)
(x, y)
[first, *rest]
{"email": email:str, "age": age:(int, age >= 13)}
User(id=id, email=email)
Ok(value)
Err(error)
Ok(value) | Err(value)
```

`match` tries cases in order:

```python
match value:
    case pattern:
        body
    case pattern if guard:
        body
    else:
        body
```

If no case matches and no `else` exists, `MatchError` is raised.

`match` may produce a value:

```python
message =
    match result:
        case Ok(user):
            "hello " + user.name
        case Err(error):
            explain(error)
```

In `match`, pattern failure skips the case. Constraint failure during tentative
case binding also skips the case before the body starts. In direct
destructuring assignment, failure raises `PatternError` or `BindingError`.

### Collections, Pipelines, And Repetition

Loops are ordinary statements:

```python
for item in items:
    print(item)

while remaining > 0:
    remaining = remaining - 1
```

The standard transform vocabulary includes:

```text
map
where
select
fold
group
sort
take
drop
count
any
all
```

Pipelines express readable value flow:

```python
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Reduction:

```text
raw |> f      == f(raw)
raw |> f(a)   == f(raw, a)
```

If the right side contains `_`, the piped value replaces `_`:

```python
numbers |> map(_ * 2)
```

Collection operations are library functions with ordinary call semantics. The
pipeline is syntax for readable flow, not a separate query language.

### Blocks And Yield

A block is caller-side code attached to a call:

```python
retry(3, on=NetworkError):
    send(request)
```

Block with yielded value:

```python
using(open(path)) -> file:
    text = file.read()
```

Block parameters are binding targets:

```python
each(users) -> user:User:
    send(user.email)
```

The callee invokes the attached block with `yield`:

```python
func each(items):
    for item in items:
        yield item
```

Conceptual reduction:

```text
block call
-> ordinary call plus attached Block value

yield value
-> invoke attached Block with yielded value
-> bind yielded value to block binding target
-> execute block body in caller lexical environment
-> return block result to callee
```

The block call expression returns the callee's return value. If the callee wants
the block body's value, it receives it as the result of `yield` and may return
it.

Failure model:

- if the block body raises, the exception resumes at the callee's `yield`;
- the callee may catch, retry, translate, or re-raise it;
- `finally` in the callee must run on success, failure, or cancellation;
- diagnostics should show both the callee policy frame and caller block frame.

Open block-scope questions remain:

- Do new names created inside a block escape to the surrounding scope?
- Should there be a `scope:` or `let:` wrapper for block-local names?
- How do `global` and `nonlocal` interact with block execution?
- Can `return`, `break`, and `continue` cross block/callee boundaries?

Default direction:

- existing caller bindings may be read and rebound;
- yielded parameters are scoped to the block invocation;
- new names should be local to the block unless explicitly exported;
- nonlocal control needs explicit rules and diagnostics.

### Errors, Absence, And Expected Failure

Expected alternatives should usually be modeled with data:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)
```

Unexpected or exceptional failures use errors:

```python
try:
    user = load_user(id)
except NotFound as error:
    return Err(error)
finally:
    cleanup()
```

Standard error categories:

```text
Error
BindingError
CallError
ConstructionError
DecodeError
FieldError
IndexError
MatchError
ModuleError
PatternError
```

`none` is the ambient absence value. When absence should be modeled explicitly,
use option data:

```python
data Option[T]:
    Some(value:T)
    NoneValue()
```

### Examples, Tests, And Explanation

`examples:` attaches executable examples to a declaration.

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

Examples are:

- documentation;
- runnable tests;
- diagnostic anchors;
- optional runtime metadata.

Example failure must report the example span, evaluated input, expected output,
and actual output.

The long-term explanation goal is that a programmer can ask:

- why did this constraint fail?
- why did this match case win?
- which values flowed through this pipeline?
- where did this block yield, retry, or cancel?
- which examples define intended behavior?

### Modules, Imports, Exports, And Members

A file is a module. Optional module declaration:

```python
module app.signup
```

Imports bind module values or exported names in the current module scope:

```python
import csv
import app.users as users
from app.email import normalize_email, Email
```

Top-level names are exported unless they begin with `_`. An explicit export
list may restrict exports:

```python
export User, signup
```

The everyday core does not include class inheritance. Data plus functions is
the primary modeling style:

```python
data User:
    name:str
    email:Email

func display_name(user:User) -> str:
    return user.name
```

Member calls are permitted only when a function is explicitly exported as a
member by the data declaration or standard library:

```python
data User:
    name:str
    email:Email

    func display_name(self) -> str:
        return self.name

user.display_name()
```

This is sugar for a function whose first parameter is `self`. There is no
implicit inheritance, hidden receiver scope, monkey patching, or global method
mutation in the core language.

## Advanced Layers

The first everyday language should deliberately postpone advanced layers until
the core is stable. Postponed does not mean rejected.

### Effects, Worlds, And Capabilities

Effects should be understandable as scoped capabilities rather than ambient
global permission.

Possible direction:

```python
world(fs, network) -> w:
    page = w.network.get(url)
    w.fs.write(path, page)
```

This should start as a runtime convention or block policy and only later become
a stronger effect system if experience justifies it. The cognitive question is:
what can this code touch, and under which policy?

### Quote, Rewrite, And Symbolic Code

Ordinary code runs. Code becomes data only at an explicit boundary.

```python
expr = quote:
    x + 0

simplified = rewrite(expr, rule(a + 0, a))
```

The archived notes discuss Mathematica-style rewrite syntax, unification,
normal forms, e-graphs, and macro systems. The current synthesis keeps the
principle and postpones the syntax:

```text
quoted syntax -> SyntaxValue
pattern -> Pattern over SyntaxValue or Value
rewrite -> Pattern + replacement + strategy
normalization -> repeated rewrite with trace
```

Do not make ordinary runtime code implicitly symbolic.

### Scoped Notation

Domain notation may be useful later, but only inside explicit scopes with
inspectable desugaring.

Possible direction:

```python
use units:
    speed = 30 km / hour
```

Guardrails:

- no global syntax mutation;
- every notation extension must provide a desugaring;
- tooling must be able to show the expanded form;
- notation must compose with binding, patterns, diagnostics, and examples.

### Concurrency And Async

Blocks and yield create a foundation for time-shaped control. They may later
support async, structured concurrency, cancellation, timeouts, and scheduling.

The first language should not be designed around advanced concurrency. It should
define ordinary block policies well enough that concurrency can build on them
without changing their meaning.

## Implementation Roadmap

The prototype is a laboratory, not the final semantic boundary. Python AST may
remain a bootstrap substrate, but Nomi should move toward Nomi-owned nodes with
source spans and semantic vocabulary.

### Milestone 0: Source, Context, Spans

Goals:

- parse source into Nomi-owned nodes with spans;
- preserve source locations through lowering/evaluation;
- represent module context and lexical scopes explicitly;
- produce at least one diagnostic with exact source location.

### Milestone 1: Binding, Constraints, Functions

Target:

```python
func signup(age:(int, age >= 13), email:(str, contains(email, "@"))):
    return email

payload_age:int, payload_age >= 13 = 18
payload_email:str, contains(payload_email, "@") = "a@b.com"
result = signup(payload_age, payload_email)
```

Acceptance:

- assignment constraints work;
- parameter constraints use the same binding engine;
- failed checks produce `BindingError`;
- source spans survive into diagnostics;
- tests cover success and failure.

### Milestone 2: Product Data And Explicit Decode

Target:

```python
data SignupInput:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"

func signup(raw:dict) -> SignupInput:
    return SignupInput.decode(raw)
```

Acceptance:

- data constructors route fields through binding constraints;
- field access, equality, and display are defined;
- `decode` conversion is explicit and diagnostic-rich;
- extra and missing external fields have documented policy.

### Milestone 3: Variants And Match

Target:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)

func display_name(result:Result[User, Error]) -> str:
    match result:
        case Ok(user):
            return user.name
        case Err(error):
            return explain(error)
```

Acceptance:

- variants construct values;
- match reuses pattern binding;
- match failure and constraint failure are distinguishable;
- diagnostics can explain why a case did not match.

### Milestone 4: Collections And Pipelines

Target:

```python
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Acceptance:

- pipeline lowers to ordinary calls;
- each stage can be traced;
- collection operations bind each element in a normal context;
- library equivalents exist before syntax becomes mandatory.

### Milestone 5: Blocks As Policy

Target:

```python
retry(3, on=NetworkError):
    send(request)

using(open(path)) -> file:
    file.read()
```

Acceptance:

- block calls parse as calls with attached blocks;
- `yield` invokes caller-side code;
- block parameters use the shared binding engine;
- exceptions move through `yield` coherently;
- diagnostics show policy frame, yield location, block binding, and failure.

### Milestone 6: Examples And Trace

Target:

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

Acceptance:

- examples attach to declarations;
- examples can run as tests;
- example failure reports source span, input, expected output, and actual
  output;
- trace records exist for constraints, calls, matches, pipelines, and blocks.

### Later Milestones

Research-only until the everyday core is stable:

- effects/worlds/capabilities;
- quote/syntax values/rewrite rules;
- scoped notation;
- async/concurrency;
- static type inference and proof-like systems;
- custom syntax plugins;
- advanced array/table/rank semantics.

## Syntax Admission Tests

Admit syntax only when it passes all of these:

1. It supports a primitive cognitive act.
2. It reduces to a small Nomi semantic primitive.
3. It makes a common pattern clearer at the call site.
4. It composes with binding, functions, data, patterns, blocks, examples, and
   diagnostics.
5. It has a clear failure model.
6. It has an inspectable desugaring.
7. It does not introduce a second unrelated story for an existing concept.

Reject or redesign a feature when:

- it exists only because another language has it;
- it imports visual clutter or implicit magic;
- it competes with an existing Nomi spelling for the same operation;
- it cannot produce a meaningful diagnostic;
- it requires global magic to be useful;
- it makes common code read like expert-only notation;
- it cannot be scoped, desugared, or inspected.

## Key Resolved Decisions

- Use `func` for named function definitions.
- Use arrow functions for expression-level function values.
- Treat annotations as executable constraints first.
- Reuse binding semantics for assignment, parameters, block parameters,
  destructuring, and pattern captures.
- Rebinding without annotation keeps constraints; rebinding with annotation
  replaces the local constraint set.
- Use lowercase `true`, `false`, and `none` in the Nomi spec.
- Require boolean conditions; do not inherit Python's broad truthiness.
- Use `data` for program-owned values.
- Do not introduce `shape` as a first-layer peer to `data`.
- Use explicit `DataName.decode(value)` or structural patterns at external
  boundaries.
- Use `match` and patterns for structural choice.
- Treat pipelines as ordinary calls in readable value-flow order.
- Treat block calls as ordinary calls with attached caller-side blocks.
- Let the callee own block policy and invoke the caller's block with `yield`.
- Keep symbolic code behind explicit quote/rewrite boundaries.
- Keep effects and capabilities visible when they matter.

## Open Questions

- Exact grammar for grouped constraints in complex parameter, pattern, and block
  binding positions.
- Exact Nomi IR boundary: how long Python AST remains a transitional substrate.
- Whether bare constraint declarations such as `port:int, port > 0` are admitted
  in the first implementation.
- Detailed block scoping rules for new names, rebinding, `return`, `break`,
  `continue`, `global`, and `nonlocal`.
- Whether block bodies use final-expression values everywhere or only in
  selected value-producing positions.
- Exact method/member export syntax for data-local functions.
- Exhaustiveness checking timeline for `match`.
- Exact syntax for future quote/rewrite and scoped notation.
- Whether a future `shape` keyword is valuable enough after explicit decode and
  structural patterns exist.

## Source Material Compressed

This synthesis deduplicates these source clusters:

- Active foundation and spec:
  - `documentation/design_review/README.md`
  - `documentation/design_review/language_foundation.md`
  - `documentation/design_review/language_spec.md`
- Focused feature pillars:
  - `documentation/design_review/binding_constraints_feature.md`
  - `documentation/design_review/block_calls_feature.md`
- Design spine and guardrails:
  - `documentation/design_review/first_principles_programming_model.md`
  - `documentation/design_review/language_coherence_model.md`
  - `documentation/design_review/cognitive_language_vision.md`
  - `documentation/design_review/hierarchical_language_research_plan.md`
  - `documentation/design_review/research_notes_synthesis.md`
  - `documentation/design_review/implementation_todos.md`
- Adjacent notes:
  - `documentation/delta_on_python.md`
  - `documentation/yield_to_block.md`
  - `documentation/positioning_ambition_risk.md`
  - `documentation/Notes/tractable_sophistication.md`
  - `documentation/Notes/category_theory_detour.md`
  - `documentation/DRAFT/type_theory_design_guide.md`
- Archive source material:
  - `documentation/design_review_archive/*.md`

Archived docs mainly contributed historical comparison, syntax experiments,
feature inventories, and risk framing. Their repeated thesis is preserved here:
Nomi should be ambitious, but ambition must pass through a small, inspectable,
diagnostic-friendly core.
