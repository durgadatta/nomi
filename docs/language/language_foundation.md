# Nomi Language Foundation

> Status: canonical design foundation for the next design pass.
>
> This document consolidates the active design-review direction into one
> operational foundation. Older files in this directory remain useful source
> notes, but this file is the decision surface for converging toward concrete
> syntax and implementation.

## Purpose

Nomi should become a general-purpose language for ordinary, medium-level
programming: scripts, CLIs, data cleanup, notebooks, small services, app logic,
configuration, file processing, API boundaries, teaching examples, and
maintainable glue between libraries.

The first target is not systems programming, memory management, advanced
concurrency, type-level proof, macro-heavy metaprogramming, or expert notation.
Those areas can be studied later, but they must not distort the first language
users learn.

The goal of this document is to provide a path from ambition to visible syntax:

```text
principles -> primitives -> surface forms -> reductions -> diagnostics -> tests
```

If an idea cannot move along that path, it remains research material rather
than becoming part of the language.

For the adoption-oriented gap map that sits above individual feature design,
see [Language Direction And Gap Map](language_direction_and_gap_map.md). It
names the documentation and design gaps Nomi must fill if it wants Python-like
everyday usefulness without becoming a syntax collage.

For aspirational examples that keep the design grounded in ordinary work, see
[Target Program Fixtures](target_program_fixtures.md).

## Product Promise

Nomi should let a programmer learn a small set of operations and see them recur
everywhere:

```text
name a value
check what must be true
transform values with functions
group related values
choose by structure
repeat a transformation over collections
attach a block of behavior to a policy
explain what happened
```

The language should be easy to remember after time away. A user should not need
to recall many parallel mini-languages for validation, records, pattern
matching, iteration, callbacks, tests, and diagnostics.

The everyday experience should be:

```text
small script -> clearer script -> reusable functions -> named data -> checked
boundaries -> readable transformations -> explainable failures
```

## Design Thesis

Programming is the act of turning intention into executable structure. A
language should help a person form, inspect, revise, and trust that structure.

Nomi can learn from Python, ML/Haskell, Lisp/Scheme, ALGOL, Ruby, Kotlin, Rust,
Swift, R, APL, SQL, Mathematica, Pydantic, JSON Schema, Racket contracts, and
many other traditions. It should not collect their surface syntax. It should
extract durable operations and translate them into one coherent core.

The rule is:

```text
reference tradition -> extracted need -> Nomi primitive -> user syntax
```

Never:

```text
reference tradition -> copied syntax -> explanation after the fact
```

## Scope For The First Usable Language

The first usable Nomi should be excellent at:

- defining functions and calling libraries;
- binding values with readable constraints;
- declaring simple data values;
- converting messy external inputs into checked internal values;
- matching on variants and structures;
- transforming lists, rows, and mappings;
- writing small policy blocks such as `using`, `retry`, `transaction`, and
  `test`;
- producing helpful diagnostics;
- embedding examples close to the code they explain.

The first usable Nomi should deliberately postpone:

- manual memory management;
- threads, multiprocessing, async scheduling, and distributed execution;
- global macro systems;
- advanced symbolic rewrite;
- dependent types or full proof systems;
- optimizer-oriented syntax;
- implicit effect tracking;
- custom syntax plugins.

Postponed does not mean rejected. It means the everyday language must be solid
before advanced layers are allowed to add pressure.

## Coherence Contract

Every feature must respect these contracts.

### One Binding Story

Names are introduced through binding.

Assignment, function parameters, block parameters, loop variables, pattern
captures, imports, and exception aliases should all be understandable as:

```text
receive a value -> optionally check it -> bind it in a scope
```

Surface examples:

```python
age:int, age >= 0 = raw_age

func signup(age:(int, age >= 13)):
    ...

each(users) -> user:User:
    send(user.email)
```

Implementation reduction:

```text
evaluate value once
create tentative binding
check constraints
commit binding or produce BindingError
```

### One Function And Call Story

Functions transform values. Calls evaluate a callee, map arguments to parameter
bindings, run the body, and produce a result.

Pipelines, collection transforms, and composition must reduce to calls. They
may improve readability, but they must not become separate execution models.

### One Data Story

Program-defined domain values are declared with `data`. A data declaration
creates constructors, fields, equality/display rules, and pattern forms.

Fields reuse binding and constraints. Data does not get a private validation
language.

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

This is the shared basis for resource handling, retries, transactions, tests,
tracing, and other time-shaped policies.

### One Explanation Story

Diagnostics are not later decoration. Each semantic event should be able to
explain itself:

- binding explains failed constraints;
- calls explain argument mapping;
- data construction explains field failures;
- patterns explain why they did or did not match;
- pipelines explain intermediate values;
- blocks explain yield, retry, cleanup, and cancellation;
- examples explain intended behavior.

## Operational Core

The first core is small, but not merely minimal for a machine. It is minimal
for a programmer's memory.

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

These are the concepts users should learn. Implementation internals may be
lower-level, but user-facing features should reduce to this set.

### Source

Source code must carry spans early. Diagnostics, examples, traces, and tooling
depend on source locations.

Implementation requirement:

```text
parse source -> Nomi-owned nodes with spans -> evaluate/lower with spans alive
```

Python AST can remain a bootstrap substrate, but Nomi should not depend on
Python AST as the final semantic vocabulary.

### Value

Values are the things programs distinguish and transform:

```python
42
"Ada"
true
none
[1, 2, 3]
{"name": "Ada"}
```

The first language can reuse Python-compatible literals where they help
adoption. Nomi-specific behavior begins when values are bound, checked,
grouped, matched, or explained.

### Binding

Binding is the act of connecting a value to a name or target.

```python
name = "Ada"
age:int = raw_age
age:int, age >= 13 else "Must be at least 13" = raw_age
```

Constraints belong to the binding in a scope. Rebinding without a new
annotation keeps the existing constraint. Rebinding with a new annotation
replaces the constraint set for that local binding.

### Constraint

A constraint is an executable judgement over a tentative binding.

Initial constraint forms:

```python
age:int = value
age:int, age >= 0 = value
email:str, contains(email, "@") = value
```

Constraint kinds:

- type/class checks;
- predicate checks;
- expression checks evaluated with the tentative name available;
- human messages attached with `else`.

Failure produces a structured `BindingError`, not only a string.

### Function

Named functions use `func`:

```python
func add(x:int, y:int) -> int:
    return x + y
```

Arrow functions are expression-level function values:

```python
double = (x:int) => x * 2
```

Parameters are bindings. Return constraints are judgements on the produced
value.

### Call

A call maps arguments to parameter bindings, checks them, executes the body, and
returns a value.

```python
add(2, 3)
send(email=user.email)
```

Argument mapping should follow Python-compatible expectations where possible:
positional arguments, keyword arguments, defaults, `*args`, and `**kwargs`.
Nomi-specific checks happen after arguments are mapped.

### Data

`data` declares program-owned values.

Product data:

```python
data User(id:UserId, email:Email, plan:Plan)
```

Block form for fields and constraints:

```python
data SignupInput:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"
    plan:Plan = Plan.Free
```

Sum data:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)
```

Reduction:

```text
data declaration -> constructor functions + field bindings + pattern forms
```

Data is for values the program is willing to name as part of its own model. It
is not a raw transport format.

### Rethinking Shape

The previous design notes treated `shape` and `data` as peer declaration forms.
That creates a real risk: users may see two ways to declare fields and wonder
which one is "correct."

The revised decision is:

```text
Do not introduce a separate `shape` keyword in the first everyday layer.
```

Instead, split the underlying needs more cleanly:

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

`decode` is the working spelling for an explicit decoder. The final spelling
may still be refined, but the design commitment is that raw external structure
does not silently become domain data.

or through an explicit pattern:

```python
match request.json:
    case {"email": email:(str, contains(email, "@")), "age": age:(int, age >= 13)}:
        signup_input = SignupInput(email=email, age=age)
```

This keeps the user rule simple:

```text
Use data when you are naming a value your program owns.
Use patterns and constraints when you are recognizing values you received.
Use an explicit decoder when received structure becomes owned data.
```

The word "shape" remains useful as an ordinary design term for structural form.
It should not become a keyword unless experience proves that named structural
contracts without owned values are common enough to deserve syntax.

If a future `shape` keyword is admitted, it must obey this rule:

```text
shape = named structural pattern/constraint, not a second data declaration
```

It must not create constructors, nominal variants, or another field system.

### Pattern And Match

Patterns inspect structure and bind names.

```python
(x:int, y:int) = point
```

```python
match fetch_user(id):
    case Ok(user):
        user.name
    case Err(error):
        explain(error)
```

Mapping patterns let external data be recognized without declaring a second
record-like entity:

```python
match raw:
    case {"email": email:str, "age": age:(int, age >= 13)}:
        SignupInput(email=email, age=age)
```

Reduction:

```text
pattern -> structural test + tentative bindings + constraints
case -> pattern + optional guard + body
```

### Collection

Most everyday programs transform groups of values. Nomi should make this
readable without requiring a separate query language for simple work.

Target style:

```python
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Reduction:

```text
pipeline -> calls in left-to-right order
where/select/map -> repeated calls with element bindings
fold/group -> accumulation over collection values
```

The first implementation can provide library functions before adding every
piece of syntax.

### Block

Blocks express caller-side behavior controlled by a callee.

```python
retry(3, on=NetworkError):
    send(request)
```

```python
using(open(path)) -> file:
    text = file.read()
```

Reduction:

```text
block call -> ordinary call + attached Block value
yield -> invoke attached Block with optional yielded values
block parameter -> binding target checked by the shared binding engine
```

Blocks should serve everyday control policies first: resource handling,
transactions, retries, tracing, fixtures, and local testing.

Advanced concurrency may later use the same foundation, but it should not drive
the first design.

### Example

Examples are executable anchors for behavior.

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

An example should be usable as documentation, a test, and an explanation source.
It is not a proof system in the first language.

### Trace And Diagnostic

The runtime should record enough semantic events to explain failures and
surprising results.

Minimum first diagnostic target:

```text
BindingError: age failed constraint age >= 13
  value: 12
  binding: field age in SignupInput.decode(...)
  note: Must be at least 13
```

Implementation should introduce trace records before the language grows
advanced features. Otherwise explanation becomes a retrofit.

## Concrete Syntax Runway

This section is not a final grammar. It is the syntax direction that future
feature specs and tests should converge toward.

### Milestone 1: Binding, Constraints, Functions

```python
age:int, age >= 13 else "Must be at least 13" = raw_age
email:str, contains(email, "@") = raw_email

func signup(age:(int, age >= 13), email:(str, contains(email, "@"))) -> str:
    return email.lower()

result = signup(age, email)
```

Acceptance criteria:

- assignment constraints work;
- parameter constraints use the same binding engine;
- failed checks produce `BindingError`;
- source spans survive into diagnostics;
- syntax has tests for success and failure.

### Milestone 2: Product Data And Boundary Conversion

```python
data SignupInput:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"

data User(id:UserId, email:Email)

func signup(raw:dict) -> User:
    signup_input = SignupInput.decode(raw)
    return User(id=new_user_id(), email=Email(signup_input.email))
```

Acceptance criteria:

- data constructors route fields through binding constraints;
- field access, equality, and display are defined;
- `decode` conversion is explicit and diagnostic-rich;
- extra and missing external fields have documented policy.

### Milestone 3: Variants And Match

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

Acceptance criteria:

- variants construct values;
- match reuses pattern binding;
- match failure and constraint failure are distinguishable;
- diagnostics can explain why a case did not match.

### Milestone 4: Collections And Pipelines

```python
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Acceptance criteria:

- pipeline lowers to ordinary calls;
- each stage can be traced;
- collection operations bind each element in a normal context;
- library equivalents exist before syntax becomes mandatory.

### Milestone 5: Blocks As Policy

```python
retry(3, on=NetworkError):
    send(request)

using(open(path)) -> file:
    text = file.read()
```

Acceptance criteria:

- block calls are calls with attached blocks;
- `yield` invokes the attached block;
- block parameters use the shared binding engine;
- diagnostics show yield/resume/failure events.

### Milestone 6: Examples And Explanation

```python
func slugify(title:str) -> str:
    examples:
        " Hello World " => "hello-world"
    return title.strip().lower().replace(" ", "-")
```

Acceptance criteria:

- examples attach to functions as structured metadata;
- examples can run as tests;
- failures point to the example and the evaluated call;
- examples do not introduce a separate testing language.

## A Target Everyday Program

This is the kind of program the first language should make clear.

```python
data Config:
    input_path:str
    output_path:str
    min_age:int, min_age >= 0 = 13

data Person:
    name:str
    email:str, contains(email, "@")
    age:int, age >= 0

data SignupReport:
    accepted:list[Person]
    rejected:int

func load_people(path:str) -> list[Person]:
    rows = read_csv(path)
    return rows |> map(Person.decode)

func keep_allowed(people:list[Person], min_age:int) -> list[Person]:
    return people |> where(_.age >= min_age)

func main(raw_config:dict):
    config = Config.decode(raw_config)
    people = load_people(config.input_path)
    accepted = keep_allowed(people, config.min_age)
    report = SignupReport(accepted=accepted, rejected=len(people) - len(accepted))
    write_json(config.output_path, report)
```

This program uses only the everyday core:

- data declarations;
- field constraints;
- explicit external conversion;
- functions;
- pipelines;
- ordinary library calls.

No macros, effect systems, async model, memory model, or advanced type theory is
required for it to be useful.

## Learning From Other Languages

Nomi should learn from many programming efforts, but each lesson must be
translated into the core.

| Tradition | Durable lesson | Nomi translation |
| --- | --- | --- |
| Python | Readable indentation, ordinary calls, practical libraries | Keep the first surface familiar and low-ceremony. |
| ML/Haskell/Elm/F# | Algebraic data and pattern matching | `data`, variants, constructors, and `match`. |
| Kotlin/Swift/Rust | Practical null/result modeling and value declarations | Data values, `Result`, optional conventions, constrained constructors. |
| Lisp/Scheme | Small regular core and code as data | Keep regular reductions; postpone explicit syntax values until later. |
| Ruby/Kotlin | Blocks/trailing lambdas for caller-side behavior | Block calls with explicit `yield`, not implicit receiver magic. |
| SQL/R/APL/dataframes | Whole-data transformation | Collection/table operations that reduce to calls and element bindings. |
| JSON Schema/Pydantic/Clojure spec | External validation and conformance | Explicit decoders plus constraints and structural patterns. |
| Racket contracts/Eiffel | Runtime boundaries with explanations | Binding constraints and structured diagnostics. |
| ALGOL/Pascal | Lexical blocks and clear scope | Indentation and block structure as the visual skeleton. |
| Shell/PowerShell | Pipeline readability | Value pipelines, not text-only streams. |
| Mathematica | Symbolic rewrite and calculational style | Later explicit `quote`/rewrite boundary, never ambient magic. |

This table is not a shopping list. It is an accountability device: every
borrowed idea must name what is kept and what is refused.

## Feature Admission Protocol

Before adding syntax, answer these questions in the feature spec:

1. What everyday programming problem does this make clearer?
2. Which core primitive does it extend?
3. What lower-level reduction teaches the feature?
4. What visible boundary prevents implicit magic?
5. What is the smallest readable example?
6. What diagnostic appears when it fails?
7. Which tests prove the semantics?
8. Which similar spellings were rejected?
9. How will a beginner remember when to use it?

Reject or redesign the feature when:

- it duplicates an existing story;
- it only exists because another language has it;
- it requires global hidden behavior;
- it makes common code look expert-only;
- it cannot be explained by diagnostics;
- it cannot be tested in a small example;
- it introduces a second field, binding, pattern, block, or call system.

## Syntax Style Rules

Prefer:

- indentation for blocks;
- ordinary function calls;
- names over punctuation when the operation is uncommon;
- one good spelling over aliases;
- explicit boundary words for risky power;
- examples before abstract prose;
- syntax that can fit in a small tutorial.

Avoid in the everyday layer:

- heavy symbolic operators;
- multiple equivalent block spellings;
- implicit receivers;
- ambient rewriting;
- hidden conversions from raw external data into domain values;
- advanced type-theory vocabulary in user-facing syntax;
- feature names that sound precise but overlap in practice.

## Implementation Spine

The implementation should proceed in the order that preserves explanation.

```text
Source nodes with spans
  -> Value display and module Context
  -> BindingTarget
  -> Constraint and BindingError
  -> shared assignment/parameter binding
  -> data constructors and field binding
  -> explicit mapping-to-data conversion
  -> pattern binding and match
  -> pipeline lowering to calls
  -> Block representation and yield
  -> examples and trace records
```

Do not implement a later feature by bypassing an earlier layer it should stress.
For example, block parameters must not have a private validation path; they
must use `BindingTarget` and `Constraint`.

## Documentation Spine

This document should be the single design entry point for the next phase.

Supporting docs should become one of three things:

- focused feature specs for accepted syntax;
- archived research notes;
- implementation notes tied to tests.

The active design-review folder should not keep several broad documents that
repeat the same vision in slightly different language. Broad vision belongs
here. Feature-specific detail belongs in focused specs.

Recommended next focused specs:

```text
bindings_constraints_and_diagnostics.md
data_and_boundary_conversion.md
patterns_and_match.md
pipelines_and_collections.md
block_calls.md
examples_and_traces.md
```

Each focused spec should use this shape:

```text
Everyday problem
User syntax
Semantic reduction
Diagnostics
Rejected alternatives
Implementation slice
Tests
Open questions
```

## Consistency Checklist

Use this checklist before accepting a design change:

- Does it reduce to the operational core?
- Does it reuse binding, constraint, call, pattern, data, block, or trace
  machinery instead of inventing a sibling?
- Can a user decide when to use it from one sentence?
- Can a beginner write a useful example before seeing advanced theory?
- Does it avoid overloading one syntax with unrelated meanings?
- Does it avoid creating two ways to declare the same thing?
- Does it produce a diagnostic in the language's own vocabulary?
- Can it be implemented in a focused milestone?
- Does it keep advanced topics from leaking into the everyday language?

## Near-Term Decisions

The next design pass should make these decisions explicit:

1. Keep `func` as the named function declaration unless a better spelling wins
   by the feature-admission protocol.
2. Keep constrained binding as the first semantic pillar.
3. Treat `data` as the first and only field-declaration keyword in the everyday
   layer.
4. Use explicit conversion such as `DataName.decode(raw)` for external data
   boundaries before considering a `shape` keyword.
5. Define data fields as binding declarations.
6. Define function parameters as binding declarations.
7. Define block parameters as binding targets.
8. Define patterns as structural tests plus tentative bindings.
9. Implement diagnostics with source spans before broadening syntax.
10. Move advanced symbolic rewrite, effects, async, memory, and concurrency out
    of the first-language path.

## The Standard Of Success

Nomi succeeds when a user can read a medium-sized program and say:

```text
I know where values enter.
I know what must be true.
I know how data is built.
I know how alternatives are handled.
I know how collections are transformed.
I know what block policy controls this body.
I know why the program failed.
```

That is the foundation from which sophistication can emerge. The language can
grow only when new power preserves that clarity.

The wider adoption test is described in
[Language Direction And Gap Map](language_direction_and_gap_map.md): Nomi
should make ordinary work easier as it becomes more precise, not merely more
theoretically expressive.
