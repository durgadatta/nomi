# Combined Nomi Design Docs

This generated draft consolidates Nomi design documents into one file for review.
Original source paths are preserved before each document. Active design-review material appears first; archived material remains marked as archive/source material.

## Table of Contents

- Active Design Review
  - [documentation/design_review/README.md](#documentation-design-review-readme-md)
  - [documentation/design_review/language_spec.md](#documentation-design-review-language-spec-md)
  - [documentation/design_review/language_foundation.md](#documentation-design-review-language-foundation-md)
  - [documentation/design_review/first_principles_programming_model.md](#documentation-design-review-first-principles-programming-model-md)
  - [documentation/design_review/language_coherence_model.md](#documentation-design-review-language-coherence-model-md)
  - [documentation/design_review/cognitive_language_vision.md](#documentation-design-review-cognitive-language-vision-md)
  - [documentation/design_review/binding_constraints_feature.md](#documentation-design-review-binding-constraints-feature-md)
  - [documentation/design_review/block_calls_feature.md](#documentation-design-review-block-calls-feature-md)
  - [documentation/design_review/implementation_todos.md](#documentation-design-review-implementation-todos-md)
  - [documentation/design_review/research_notes_synthesis.md](#documentation-design-review-research-notes-synthesis-md)
  - [documentation/design_review/hierarchical_language_research_plan.md](#documentation-design-review-hierarchical-language-research-plan-md)
- Design-Adjacent Notes
  - [documentation/delta_on_python.md](#documentation-delta-on-python-md)
  - [documentation/yield_to_block.md](#documentation-yield-to-block-md)
  - [documentation/positioning_ambition_risk.md](#documentation-positioning-ambition-risk-md)
  - [documentation/Notes/tractable_sophistication.md](#documentation-notes-tractable-sophistication-md)
  - [documentation/Notes/category_theory_detour.md](#documentation-notes-category-theory-detour-md)
  - [documentation/Notes/meta.md](#documentation-notes-meta-md)
  - [documentation/DRAFT/type_theory_design_guide.md](#documentation-draft-type-theory-design-guide-md)
- Archived Design Review Source Material
  - [documentation/design_review_archive/README.md](#documentation-design-review-archive-readme-md)
  - [documentation/design_review_archive/ai-codex_project_overview_vision.md](#documentation-design-review-archive-ai-codex-project-overview-vision-md)
  - [documentation/design_review_archive/proposed_language_feature_design_plan.md](#documentation-design-review-archive-proposed-language-feature-design-plan-md)
  - [documentation/design_review_archive/language_syntax_synthesis.md](#documentation-design-review-archive-language-syntax-synthesis-md)
  - [documentation/design_review_archive/proposed_syntax_samples.md](#documentation-design-review-archive-proposed-syntax-samples-md)
  - [documentation/design_review_archive/cross_language_feature_synthesis.md](#documentation-design-review-archive-cross-language-feature-synthesis-md)
  - [documentation/design_review_archive/radical_language_feature_ideas.md](#documentation-design-review-archive-radical-language-feature-ideas-md)
  - [documentation/design_review_archive/everyday_radical_language_ideas.md](#documentation-design-review-archive-everyday-radical-language-ideas-md)
  - [documentation/design_review_archive/streamlined_programmer_experience_design.md](#documentation-design-review-archive-streamlined-programmer-experience-design-md)
  - [documentation/design_review_archive/nomi_language_revision_report.md](#documentation-design-review-archive-nomi-language-revision-report-md)

---

# Active Design Review

---

<a id="documentation-design-review-readme-md"></a>

# Source: `documentation/design_review/README.md`

# Design Review

> Status: active design workspace.

This directory is the active working surface for Nomi language design. The
prototype is a seed and a laboratory; the design target is a usable
general-purpose language for ordinary, medium-level programming that can grow
into deeper sophistication without losing its core.

The current canonical entry point is
[Nomi Language Foundation](language_foundation.md). Start there before reading
or editing the older synthesis documents.

## Current Focus

The active design focus is:

> A friendly everyday language whose sophistication emerges from a small set of
> remembered operations: values, bindings, constraints, functions, calls, data,
> patterns, collections, blocks, examples, traces, and diagnostics.

The next design pass should converge from the foundation document into focused
feature specs and executable syntax examples. Broad vision without operational
syntax is not enough; every accepted idea needs a reduction, diagnostic story,
implementation slice, and tests.

## Design Spine

Nomi should start from first principles: what values are, how names work, how
truth is judged, how transformations compose, how values group, how choices are
made, how repeated transformations stay readable, and how programs explain
themselves. Python, ML/Haskell, Lisp/Scheme, ALGOL, Ruby, Kotlin, Rust, Swift,
R, APL, SQL, Mathematica, Pydantic, JSON Schema, and other efforts are reference
experiments, not syntax inventories.

The current core concepts are:

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

The admission rule for new syntax is:

> Add syntax only when it reduces to a small semantic primitive and makes a
> common programming pattern clearer at the call site, with diagnostics and
> tests that prove the intended semantics.

Advanced symbolic rewrite, effects, capabilities, async, concurrency, memory
models, and custom notation remain research topics until the everyday core is
stable.

## Active Documents

- [Nomi Language Foundation](language_foundation.md): canonical foundation for
  the next phase. It consolidates the broad design direction, rethinks
  `shape`/`data`, defines the operational core, and gives a concrete syntax
  runway.
- [Nomi Language Specification](language_spec.md): draft concrete language spec
  for the intended Nomi language: lexical structure, values, bindings,
  constraints, functions, data, patterns, collections, blocks, modules,
  examples, diagnostics, and conformance.
- [Binding Constraints Feature](binding_constraints_feature.md): syntax,
  semantics, desugaring, examples, diagnostics, and edge cases for constrained
  binding. This should be revised against the foundation before implementation
  expansion.
- [Block Calls As Control Values](block_calls_feature.md): focused study of
  caller-side block syntax, `yield`, policy blocks, tradeoffs, and small-core
  reduction. This remains useful, but advanced concurrency implications are not
  first-path work.
- [Implementation Todos](implementation_todos.md): staged backlog. It should be
  updated after focused specs are rewritten from the foundation.

## Supporting Source Notes

These files are useful background, but they are no longer parallel canonical
visions:

- [Cognitive Language Vision](cognitive_language_vision.md)
- [First-Principles Programming Model](first_principles_programming_model.md)
- [Hierarchical Language Research Plan](hierarchical_language_research_plan.md)
- [Research Notes Synthesis](research_notes_synthesis.md)
- [Language Coherence Model](language_coherence_model.md)

Use them to recover rationale. Use `language_foundation.md` to decide what to
build next.

## Archived Source Notes

The previous design-review files were valuable, but they overlapped heavily:
several restated the same small-core philosophy, syntax catalog, cross-language
synthesis, and radical feature staging. They are preserved under
`../design_review_archive/` as source material, not active specification.

Use the archive to recover design context. Use this directory to decide what to
build next.

---

<a id="documentation-design-review-language-spec-md"></a>

# Source: `documentation/design_review/language_spec.md`

# Nomi Language Specification

> Status: draft language specification.
>
> This document specifies the intended Nomi language, not the current
> implementation. It is concrete enough to guide syntax examples, parser work,
> diagnostics, documentation, and teaching material. When this document
> conflicts with older design notes, this document wins unless the user or a
> later accepted spec explicitly overrides it.

## 1. Design Target

Nomi is a general-purpose language for everyday programs that should remain
clear as they grow:

- scripts and automation;
- command-line tools;
- notebooks and exploratory work;
- data cleanup and transformation;
- API and configuration boundaries;
- small services and application logic;
- teaching examples;
- glue code that should still be readable six months later.

Nomi is not designed first around manual memory, advanced concurrency,
metaprogramming, proof systems, or compiler-oriented cleverness. Those may
become later layers, but the base language must be teachable, memorable, and
useful without them.

The design rule is:

```text
few remembered operations, many composable uses
```

The user should recognize the same ideas everywhere:

```text
value
binding
constraint
function
call
data
pattern
match
collection
block
module
example
diagnostic
```

## 2. Specification Style

This specification uses normative words:

- **must**: required language behavior;
- **must not**: forbidden language behavior;
- **should**: expected behavior with room for later refinement;
- **may**: allowed behavior.

Code examples in this document are Nomi unless marked otherwise.

Grammar snippets are descriptive rather than a complete parser grammar. A later
grammar document may refine details, but it must preserve the semantics here.

## 3. Program Structure

A Nomi program is a sequence of top-level declarations and executable
statements.

```python
import csv

data Person:
    name:str
    email:str, contains(email, "@")

func load(path:str) -> list[Person]:
    rows = csv.read(path)
    return rows |> map(Person.decode)

people = load("people.csv")
print(len(people))
```

A file is a module. Top-level statements execute in module order when the file
is run as a program. Top-level declarations bind names in the module scope.

The module name is derived from its path unless an optional declaration appears
at the top:

```python
module app.signup
```

## 4. Lexical Structure

### 4.1 Source Text

Source files are Unicode text. UTF-8 is the required interchange encoding.

Newlines separate logical lines except inside open parentheses, brackets, or
braces.

### 4.2 Comments

Line comments begin with `#` and continue to the end of the line.

```python
# normalize before validation
email = raw.email.strip().lower()
```

Documentation comments are ordinary comments immediately preceding a
declaration. Tooling may attach them to the following declaration.

```python
# Return a lowercase, trimmed email address.
func normalize_email(email:str) -> str:
    return email.strip().lower()
```

### 4.3 Layout

Indentation is significant. A line ending in `:` begins an indented block.

```python
if age >= 18:
    label = "adult"
else:
    label = "minor"
```

Tabs are not part of the reference style. Conforming tools should reject mixed
tabs and spaces in indentation.

A line may continue after `=`, `return`, `=>`, `|>`, a binary operator, or an
open delimiter. The continued expression must be indented relative to the line
that introduced it.

### 4.4 Identifiers

Identifiers name bindings, functions, modules, data constructors, fields, and
type parameters.

Reference style:

```text
lower_snake_case      value, function, module, field
UpperCamelCase       data type, variant constructor, type parameter
_leading_underscore  private or intentionally local convention
_                   wildcard pattern or placeholder
```

The style is not merely aesthetic. In patterns, bare lowercase identifiers bind
new names, while uppercase identifiers are resolved as constructors or named
constants.

### 4.5 Keywords

Reserved keywords:

```text
and as break case const continue data elif else examples except false finally
for from func if import in is match module none not or raise return true try
while yield export
```

Future-reserved keywords:

```text
effect extend impl interface protocol quote shape trait use world
```

Future-reserved words are not active syntax in the everyday language.

## 5. Values

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

### 5.1 Literals

```python
42
3.14
true
false
none
"hello"
'hello'
[1, 2, 3]
(1, 2)
{"name": "Ada", "age": 36}
```

`true`, `false`, and `none` are the canonical literals. Compatibility layers
may accept `True`, `False`, and `None`, but this specification uses lowercase.

### 5.2 Equality And Identity

`==` compares values for semantic equality.

`is` compares identity. It should be used only when identity matters.

Data values compare by constructor and field values unless a later spec
declares a different equality policy.

### 5.3 Truth

Conditions require a boolean value.

Nomi must not use Python-style broad truthiness for ordinary conditions in the
core language. If a program wants to test emptiness, it should say so:

```python
if len(items) > 0:
    ...
```

This avoids accidental branching on numbers, strings, lists, or `none`.

## 6. Bindings And Scope

A binding connects a value to a name or pattern target in a scope.

```python
name = "Ada"
age:int = raw_age
email:str, contains(email, "@") = raw_email
```

Scopes:

- module scope;
- function scope;
- block scope;
- match-case scope;
- comprehension or collection-transform scope.

Names are resolved lexically. Inner scopes may shadow outer bindings.

### 6.1 Rebinding

Bindings may be rebound in the same mutable local scope:

```python
count:int, count >= 0 = 0
count = count + 1
```

Rebinding without a new annotation keeps the active constraints for that
binding. Rebinding with a new annotation replaces that binding's constraint set
in the current scope.

```python
value:int = 1
value = 2       # checked as int
value:str = "2" # new local constraint set
```

### 6.2 Constants

`const` introduces a binding that may not be rebound in the same scope.

```python
const pi:float = 3.14159
```

Attempting to rebind a constant raises `BindingError`.

### 6.3 Assignment Targets

Assignment targets may be:

- a name;
- a tuple or list pattern;
- a data pattern;
- a mapping pattern;
- a field target when the receiver is explicitly mutable.

The everyday language does not include mutable data fields. Field assignment is
reserved for explicit mutable library types and must not be confused with
ordinary data values.

## 7. Constraints

A constraint is an executable judgement over a tentative binding.

```python
age:int, age >= 13 else "Must be at least 13" = raw_age
```

Binding proceeds as:

```text
evaluate right side once
tentatively bind target names
check constraints in the tentative environment
commit bindings if all checks pass
raise BindingError if any check fails
```

### 7.1 Constraint Forms

Type or class constraint:

```python
age:int = value
```

Predicate constraint:

```python
email:str, contains(email, "@") = value
```

Expression constraint:

```python
amount:int, amount > 0 = value
```

Message constraint:

```python
age:int, age >= 13 else "Must be at least 13" = value
```

Multiple constraints are evaluated from left to right.

### 7.2 Constraint Names

Built-in constraint names:

```text
Any bool int float str list dict tuple function data module error
```

Parameterized constraints:

```python
list[int]
dict[str, int]
Result[User, SignupError]
```

The language treats type annotations as constraints first. Static tooling may
use them for analysis, but runtime semantics must not depend on a full static
type checker.

### 7.3 Constraint Failure

Constraint failure raises `BindingError`.

Minimum diagnostic fields:

```text
name
value
constraint
message
source_span
binding_kind
```

Example:

```text
BindingError: age failed constraint age >= 13
  value: 12
  binding: parameter age in signup(...)
  note: Must be at least 13
```

## 8. Expressions

Expressions produce values.

Expression categories:

- literals;
- names;
- calls;
- field access;
- indexing;
- operators;
- `if` expressions;
- `match` expressions;
- collection literals;
- arrow functions;
- parenthesized expressions;
- pipelines.

### 8.1 Operators

Core operators:

```text
or
and
not
== != < <= > >=
is
in
|>
+ -
* / // %
**
.
[]
()
```

`and` and `or` short-circuit and require boolean operands.

The pipeline operator `|>` passes the value on its left into the call or
function expression on its right:

```python
clean =
    raw
    |> strip
    |> lower
    |> normalize_space
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

### 8.2 Field Access And Indexing

```python
user.email
items[0]
mapping["key"]
```

Field access on data values reads a declared field. Missing fields raise
`FieldError`.

Indexing behavior is defined by the receiver's type.

### 8.3 Conditional Expressions

`if` may be used as a statement or as a value-producing expression.

```python
label =
    if age >= 18:
        "adult"
    else:
        "minor"
```

All branches of a value-producing `if` must produce a value. Conditions must be
boolean.

### 8.4 Block Values

Some blocks are value-producing: `if` expressions, `match` expressions, and
caller-side blocks invoked by `yield`.

The value of a value-producing block is the value of its last expression.
Assignments, declarations, and loop statements produce `none`. A block used in
a value position must end with an expression or an explicit `return` from the
enclosing function.

## 9. Functions And Calls

### 9.1 Function Declarations

```python
func name(parameter_list) -> return_constraint:
    body
```

Example:

```python
func add(x:int, y:int) -> int:
    return x + y
```

`return` exits the current function. A function with no explicit return returns
`none`.

### 9.2 Parameters

Parameters are bindings.

```python
func signup(
    email:(str, contains(email, "@")),
    age:(int, age >= 13),
    plan:Plan = Plan.Free,
) -> SignupInput:
    return SignupInput(email=email, age=age, plan=plan)
```

Parameter kinds:

- positional or keyword;
- keyword-only after `*`;
- variadic positional `*items`;
- variadic keyword `**options`;
- defaulted parameters.

After arguments are mapped to parameters, each parameter binding is validated.

### 9.3 Arrow Functions

Arrow functions are expression-level function values.

```python
double = (x:int) => x * 2
is_adult = (age:(int, age >= 18)) => true
```

Arrow functions contain one expression. Use `func` for named or block-bodied
functions.

### 9.4 Calls

```python
add(1, 2)
send(email=user.email)
```

Calls evaluate the callee, evaluate arguments left to right, map arguments to
parameters, validate parameter constraints, execute the body, and return the
result.

Unknown arguments, duplicate arguments, missing required arguments, and wrong
arity raise `CallError`.

## 10. Data Declarations

`data` defines program-owned values.

### 10.1 Product Data

Single-line form:

```python
data User(id:UserId, email:Email, plan:Plan)
```

Block form:

```python
data User:
    id:UserId
    email:Email
    plan:Plan = Plan.Free
```

Constructor:

```python
user = User(id=id, email=email)
```

Data fields are read-only in the everyday language.

### 10.2 Field Constraints

Fields are bindings checked by the constructor.

```python
data Person:
    name:str
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 0
```

Construction fails with `BindingError` or `ConstructionError` containing the
field path.

### 10.3 Sum Data

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)
```

`Ok` and `Err` are constructors and patterns.

```python
result = Ok(user)

match result:
    case Ok(user):
        user.name
    case Err(error):
        explain(error)
```

### 10.4 Data Conversion From External Values

Raw external structure does not silently become domain data.

`DataName.decode(value)` is the standard explicit decoder for data declarations.

```python
signup_input = SignupInput.decode(raw)
```

Default decoder policy:

- mapping keys correspond to field names;
- missing required fields fail;
- unknown fields fail;
- defaults are applied after required fields are checked;
- field constraints are checked exactly as constructor constraints;
- errors include the field path.

Lenient decoding is a library concern and must be explicit.

### 10.5 Display

Data values display as constructor calls:

```text
User(id=42, email="a@b.com", plan=Free)
```

Display should be stable enough for diagnostics and examples, but it is not a
serialization format.

## 11. Patterns And Match

Patterns test structure and bind names.

### 11.1 Pattern Forms

Wildcard:

```python
_
```

Literal:

```python
42
"ok"
true
none
```

Capture:

```python
name
name:int
name:(int, name >= 0)
```

Tuple or list:

```python
(x, y)
[first, *rest]
```

Mapping:

```python
{"email": email:str, "age": age:(int, age >= 13)}
```

Data constructor:

```python
User(id=id, email=email)
Ok(value)
Err(error)
```

Alternative:

```python
Ok(value) | Err(value)
```

All alternatives in one alternative pattern must bind the same names with
compatible constraints.

Guard:

```python
case User(age=age) if age >= 18:
    ...
```

### 11.2 Match

```python
match value:
    case pattern:
        body
    case pattern if guard:
        body
    else:
        body
```

Cases are tried in order. The first case whose pattern and guard succeed is
selected.

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

All selected value-producing case bodies must produce a value.

### 11.3 Pattern Failure Versus Constraint Failure

In `match`, pattern failure means the case is skipped.

Constraint failure during tentative case binding also skips the case before the
body starts.

In direct destructuring assignment, failure raises `PatternError` or
`BindingError`.

## 12. Collections And Repetition

### 12.1 Loops

```python
for item in items:
    print(item)
```

```python
while remaining > 0:
    remaining = remaining - 1
```

`break` exits the nearest loop. `continue` begins the next iteration.

Loop variables are bindings in the loop body scope.

### 12.2 Collection Transforms

The standard transform vocabulary:

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

Examples:

```python
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

```python
total =
    orders
    |> select(_.amount)
    |> fold(0, (sum, amount) => sum + amount)
```

Collection operations are library functions with ordinary call semantics. The
pipeline is syntax for readable value flow, not a separate query language.

### 12.3 Comprehensions

List comprehensions are permitted as sugar over transforms:

```python
names = [user.name for user in users if user.active]
```

They reduce to `where` plus `select`.

## 13. Blocks And Yield

A block is caller-side code attached to a call.

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

### 13.1 Callee Semantics

A function invokes its attached block with `yield`.

```python
func each(items):
    for item in items:
        yield item
```

`yield value` invokes the attached block, binds yielded values to the block
parameter target, executes the block body in the caller lexical environment,
and returns the block result to the callee.

Calling `yield` when no block is attached raises `BlockError`.

### 13.2 Block Result

The value of a block body is the value of its last expression, or `none` if it
does not produce a value.

```python
func twice():
    a = yield
    b = yield
    return [a, b]

values = twice():
    now()
```

### 13.3 Control Boundaries

`return` inside a block returns from the nearest lexically enclosing `func`, not
from the callee that yielded to the block.

Nonlocal block returns may be restricted by a later spec if they make
diagnostics unclear. Implementations must report them explicitly if supported.

## 14. Errors

Expected alternatives should usually be modeled with data:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)
```

Unexpected or exceptional failures use errors.

### 14.1 Raising

```python
raise Error("missing file")
```

### 14.2 Handling

```python
try:
    user = load_user(id)
except NotFound as error:
    return Err(error)
finally:
    cleanup()
```

`except` clauses are tried in order. The exception alias is a binding.

### 14.3 Standard Error Categories

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

All errors should carry message, source span when available, and structured
context.

## 15. Examples

`examples:` attaches executable examples to a declaration.

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

An example has input expression on the left and expected output expression on
the right.

For multi-argument functions:

```python
func add(x:int, y:int) -> int:
    examples:
        (2, 3) => 5
    return x + y
```

Examples are:

- documentation;
- runnable tests;
- diagnostic anchors;
- optional runtime metadata.

Example failure must report the example span, evaluated input, expected output,
and actual output.

## 16. Modules And Imports

### 16.1 Module Declarations

```python
module app.signup
```

The declaration, if present, must be first except for comments.

### 16.2 Imports

```python
import csv
import app.users as users
from app.email import normalize_email, Email
```

Imports bind module values or exported names in the current module scope.

### 16.3 Exports

Top-level names are exported unless they begin with `_`.

Explicit export lists may restrict exports:

```python
export User, signup
```

If an `export` declaration appears, only listed names are exported.

## 17. Methods And Member Calls

The everyday core does not include classes or inheritance.

Data plus functions is the primary modeling style:

```python
data User:
    name:str
    email:Email

func display_name(user:User) -> str:
    return user.name
```

Member calls are permitted only when a function is explicitly exported as a
member by the data declaration or standard library.

```python
data User:
    name:str
    email:Email

    func display_name(self) -> str:
        return self.name

user.display_name()
```

This is sugar for a function whose first parameter is `self`. There is no
implicit inheritance, monkey patching, hidden receiver scope, or global method
mutation in the core language.

## 18. Standard Prelude

The standard prelude is automatically available.

Required names:

```text
true false none
Any bool int float str list dict tuple function
print len range
contains
map where select fold group sort take drop count any all
using retry transaction test trace
Result Ok Err Option Some NoneValue
Error BindingError CallError ConstructionError DecodeError FieldError
IndexError MatchError ModuleError PatternError
```

`none` is the absence value. `NoneValue` is the optional-data variant used when
the program wants absence as explicit data rather than an ambient value.

```python
data Option[T]:
    Some(value:T)
    NoneValue()
```

## 19. Grammar Summary

This grammar is a guide for the concrete surface.

```text
program       ::= module_decl? statement*
module_decl   ::= "module" module_name newline

statement     ::= declaration
                | assignment
                | const_decl
                | if_stmt
                | match_stmt
                | for_stmt
                | while_stmt
                | try_stmt
                | return_stmt
                | raise_stmt
                | break_stmt
                | continue_stmt
                | expr_stmt

declaration   ::= import_decl | export_decl | data_decl | func_decl

assignment    ::= target constraint_list? "=" expression
const_decl    ::= "const" identifier constraint_list? "=" expression
target        ::= identifier | pattern

constraint_list ::= ":" constraint ("," constraint)*
constraint    ::= type_expr | expression ("else" string)?

func_decl     ::= "func" identifier "(" params? ")" return_decl? ":" block
return_decl   ::= "->" constraint
params        ::= param ("," param)* ","?
param         ::= identifier constraint_list? default?
default       ::= "=" expression

data_decl     ::= "data" identifier type_params? data_body
data_body     ::= "(" fields? ")" | ":" indented_data_members
data_member   ::= field | variant | func_decl
field         ::= identifier constraint_list? default?
variant       ::= identifier "(" fields? ")"

expression    ::= literal
                | identifier
                | call
                | field_access
                | index
                | operator_expr
                | if_expr
                | match_expr
                | arrow_func
                | collection_literal
                | pipeline_expr

pattern       ::= "_"
                | literal
                | capture_pattern
                | tuple_pattern
                | list_pattern
                | mapping_pattern
                | constructor_pattern
                | pattern "|" pattern

block_call    ::= call block_params? ":" block
block_params  ::= "->" target
```

## 20. Out Of Scope For The Core Spec

The following are intentionally excluded from the first core:

- class inheritance;
- mutable data fields by default;
- implicit conversions;
- global monkey patching;
- operator overloading by user code;
- macro systems;
- custom syntax extensions;
- symbolic quotation and rewrite;
- async/await;
- threads and multiprocessing;
- manual memory management;
- capability/effect typing;
- dependent types;
- full type inference requirements.

Later specs may add some of these as layers. They must not change the meaning
of existing core programs.

## 21. Design Reference Documents

This spec learned document shape and design pressure from these references. The
references are not Nomi's authority; they are comparison points.

- Scheme R7RS: https://r7rs.org/
- Haskell 2010 Language Report: https://www.haskell.org/onlinereport/haskell2010/
- ALGOL 60 Revised Report: https://archive.computerhistory.org/resources/text/algol/algol_bulletin/EX/RR60/INDEX.HTM
- Python Language Reference: https://docs.python.org/3/reference/
- Kotlin Language Specification: https://kotlinlang.org/spec/kotlin-spec.html
- Ruby Syntax Reference: https://docs.ruby-lang.org/en/master/syntax_rdoc.html
- Scala 3 Reference: https://docs.scala-lang.org/scala3/reference/

## 22. Conformance

A conforming Nomi implementation must:

- parse the lexical structure and block layout described here;
- implement the core values and literals;
- implement lexical binding and scope;
- validate constraints at binding boundaries;
- implement functions, calls, and arrow functions;
- implement product and sum `data`;
- implement explicit data decoding through `DataName.decode`;
- implement patterns and `match`;
- implement loops and collection transform calls;
- implement block calls and `yield`;
- implement structured errors;
- attach examples to declarations and provide a way to run them;
- provide the standard prelude;
- produce diagnostics with source spans where source is available.

An implementation may omit future-reserved features. It must not accept syntax
whose meaning conflicts with this specification.

---

<a id="documentation-design-review-language-foundation-md"></a>

# Source: `documentation/design_review/language_foundation.md`

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

---

<a id="documentation-design-review-first-principles-programming-model-md"></a>

# Source: `documentation/design_review/first_principles_programming_model.md`

# First-Principles Programming Model

> Status: active foundation.
>
> This is the main spine for Nomi language design. Other languages are useful
> references, but the language should be built upward from the nature of
> programming itself: how a mind turns intention into executable structure.

## Starting Point

Programming is not primarily the act of writing instructions for a machine.

Programming is the act of externalizing thought into an executable model:

```text
intention
  -> distinction
  -> representation
  -> transformation
  -> consequence
  -> explanation
```

A program lets a person say:

- what kinds of things exist,
- what names matter,
- what must be true,
- how values change or produce other values,
- what alternatives are possible,
- what happens over time,
- what parts of the outside world are touched,
- why a result, failure, or action occurred.

The machine executes the program. The language should serve the mind that has
to form, inspect, revise, and trust it.

## The First Question

The first design question is not:

> What syntax should Nomi borrow?

The first design question is:

> What are the primitive cognitive acts of programming?

Only after answering that should Nomi ask which existing languages have useful
precedents.

## Primitive Cognitive Acts

### 1. Distinguish

Before computation, there is distinction: this value rather than that value,
this case rather than that case, this concept rather than noise.

Language role:

```text
value
literal
identity
equality
variant
```

Examples:

```python
42
"Ada"
True
Plan.Free
```

Design consequence:

Nomi needs clear values before it needs clever syntax. Every advanced feature
must eventually say what values it introduces or transforms.

### 2. Name

The mind cannot work with everything at once. It names.

Language role:

```text
binding
scope
context
```

Example:

```python
email = payload.email
```

Design consequence:

Binding is foundational because it connects a value to a concept inside a
scope. Assignment, parameters, imports, pattern captures, block parameters, and
shape fields should all be understood as naming acts.

### 3. Judge

Programs need boundaries where values are accepted, rejected, refined, or
explained.

Language role:

```text
constraint
predicate
type
shape
invariant
diagnostic
```

Example:

```python
age:int, age >= 13 else "Must be at least 13" = payload.age
```

Design consequence:

Types, predicates, validation, contracts, examples, and tests are all forms of
judgement. They should not become unrelated subsystems.

### 4. Transform

A program relates values to values.

Language role:

```text
function
call
expression
rule
pipeline
composition
```

Examples:

```python
normalize(email)

clean =
    raw
    |> strip
    |> lower
```

Design consequence:

Functions, pipelines, symbolic rules, queries, and array transforms are all
forms of transformation. Their surface forms may differ, but their reduction
should be compatible.

### 5. Choose

Programs branch because values have structure and situations differ.

Language role:

```text
condition
pattern
match
guard
variant
```

Example:

```python
match result:
    case Ok(value):
        value
    case Err(error):
        explain(error)
```

Design consequence:

Conditionals, pattern matching, exception handling, result handling, and shape
matching are forms of choosing. Nomi should prefer structural choice over
stringly or ad hoc branching.

### 6. Group

Thought groups things into records, variants, lists, tables, modules, and
domains.

Language role:

```text
data
shape
collection
table
module
namespace
```

Example:

```python
data User(id:UserId, email:str, plan:Plan)
```

Design consequence:

Data structures are not storage details first. They are conceptual groupings.
The language should make owned data, external shape, collection, and table
structure feel related.

### 7. Repeat And Accumulate

Many programs apply a thought across many values and collect the consequences.

Language role:

```text
iteration
map
filter
fold
rank
query
stream
```

Example:

```python
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Design consequence:

Loops, comprehensions, pipelines, APL-style array thinking, table queries, and
streams should be views of repeated transformation, not separate worlds.

### 8. Sequence In Time

Some computations are timeless transformations. Others happen in time: acquire,
try, wait, retry, cancel, clean up.

Language role:

```text
block
yield
policy
transaction
resource
concurrency
```

Example:

```python
retry(3):
    send(request)
```

Design consequence:

Control constructs should be understood as policies over time. Block calls are
Nomi's candidate primitive for caller-side control.

### 9. Touch The World

Programs read files, talk to networks, use clocks, generate randomness, launch
processes, mutate databases, and affect people.

Language role:

```text
effect
world
capability
permission
boundary
```

Example:

```python
with world(fs, network) as w:
    page = w.network.get(url)
```

Design consequence:

Effects should not disappear into ambient global power. The language should
make contact with the world visible enough to reason about, test, replay, and
explain.

### 10. Explain

A program that cannot explain itself is cognitively incomplete.

Language role:

```text
example
trace
diagnostic
proof
counterexample
history
```

Example:

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

Design consequence:

Examples, tests, traces, proofs, and diagnostics are not external accessories.
They are part of making programs thinkable.

### 11. Reflect And Rewrite

Sometimes the program must talk about program-shaped structure.

Language role:

```text
quote
syntax value
rewrite
macro
notation
expansion
```

Example:

```python
expr = quote:
    x + 0

simple = expr /. a + 0 -> a
```

Design consequence:

Reflection is powerful only when bounded. Ordinary code should run normally.
Code becomes data through explicit quotation or scoped notation.

## The Build-Up Ladder

Nomi should be designed upward in this order:

```text
1. values: what can be distinguished
2. bindings: how values become named concepts
3. constraints: how concepts are judged and refined
4. functions/calls: how values transform
5. data/shapes: how values group into structure
6. patterns/match: how structure is inspected
7. collections/tables: how transformation scales across many values
8. blocks/yield: how time-shaped control is abstracted
9. effects/worlds/capabilities: how programs touch reality
10. examples/traces/diagnostics: how behavior explains itself
11. quote/rewrite/notation: how programs transform program-shaped ideas
```

This is not an implementation order. It is a conceptual dependency order. A
later feature may be prototyped early, but its design should reduce back down
this ladder.

## Small Core Candidate

The first-principles ladder suggests a small semantic core:

```text
Value
Context
Binding
Constraint
Function
Call
Data
Pattern
Block
Yield
Effect
Quote
Rewrite
Trace
```

Surface syntax should reduce into this core.

Examples:

```text
parameter       -> binding in function-call context
shape field     -> binding plus constraint over external structure
pipeline        -> ordered calls over a flowing value
block call      -> call plus attached block value
match case      -> pattern plus conditional binding
transaction     -> block policy plus effect boundary
rewrite rule    -> pattern transform over quoted values
example         -> executable judgement plus trace expectation
```

The core may change, but changes should be justified from first principles, not
because another language has a feature.

## Role Of Other Languages

Other languages are reference experiments. They show possible answers to
first-principles questions:

| First-principles need | Useful references |
| --- | --- |
| Local readability and ordinary work | Python |
| Algebraic structure and pure transformation | Haskell, ML, Scala |
| Symbolic representation and rewrite | Mathematica, Lisp, Scheme |
| Caller-side control | Ruby, Kotlin, Python generators/context managers |
| Whole-data transformation | APL, KDB/q, SQL, dataframe systems |
| Blocks and lexical structure | ALGOL, Python, Scheme |
| Absence and practical data modeling | Kotlin, Swift, Rust |
| Effects and authority | Haskell, Rust, capability systems |

The design process is:

```text
first-principles need
  -> study existing language answers
  -> extract the durable idea
  -> translate into Nomi's core
  -> choose syntax that makes the idea locally readable
```

The process is not:

```text
admired syntax
  -> copy into Nomi
```

## Design Review Questions

Every feature proposal should answer:

1. Which primitive cognitive act does this support?
2. Which rung of the build-up ladder does it depend on?
3. What new value, binding, transformation, choice, effect, or explanation does
   it introduce?
4. How does it reduce to the small core candidate?
5. Which existing languages illuminate the problem?
6. What does Nomi deliberately refuse to copy from them?
7. How will the feature help a programmer think more clearly?

If those answers are weak, the feature is premature.

---

<a id="documentation-design-review-language-coherence-model-md"></a>

# Source: `documentation/design_review/language_coherence_model.md`

# Language Coherence Model

> Status: active design constraint.
>
> Nomi must not become a collection of admired syntax from other languages.
> Every feature must first be justified from the
> [First-Principles Programming Model](first_principles_programming_model.md),
> then translated into one coherent language model before it is allowed to
> become Nomi syntax.

## Central Claim

Nomi is not Python plus Haskell plus Mathematica plus Kotlin plus Ruby plus
Scheme plus APL plus ALGOL.

Nomi is one language whose surface should feel Python-readable, whose semantics
should be regular like Scheme and ALGOL, whose modeling should learn from
Haskell and Kotlin, whose symbolic layer should learn from Mathematica, whose
control abstraction should learn from Ruby, and whose data transformation style
should learn from APL.

The source languages are teachers, not ingredients. First principles are the
spine.

## The Whole-Language Shape

The unifying picture is:

```text
program
  = scoped declarations
  + expressions that produce values
  + bindings that name and constrain values
  + blocks that pass control-shaped code to calls
  + patterns that inspect and bind structure
  + explicit quoted forms that treat code as data
  + effects/capabilities that bound contact with the outside world
  + examples/traces/diagnostics that explain behavior
```

This is the conceptual grammar. Every feature should occupy one of these roles
or explain why the core needs a new role.

## Translation, Not Collection

Borrowed features must be translated into Nomi's semantic vocabulary. The order
is always:

```text
primitive programming need
  -> existing language references
  -> extracted idea
  -> Nomi semantic role
  -> Nomi syntax
```

| Source idea | Do not copy | Nomi translation |
| --- | --- | --- |
| Python decorators/context managers | More special-purpose function wrapping and resource protocols | Block policies and function policies with explicit desugaring. |
| Haskell monads/effects | Abstract ceremony as the daily style | Scoped effects, result values, and capability boundaries that explain what code can touch. |
| Mathematica rewrite rules | Global magical rewriting | Explicit quoted expressions and scoped rewrite application. |
| Kotlin null-safety | A separate null mini-language | Absence as constrained binding, optional shape fields, safe access, and result/option data. |
| Ruby blocks | Implicit receiver-heavy DSLs | Caller-side blocks with visible block parameters and explicit `yield`. |
| Scheme macros | Unbounded compile-time language mutation | Scoped code-as-data transforms with inspectable expanded forms. |
| APL array density | Glyph-heavy tacit code as default | Whole-collection operations with readable rank/shape concepts and traceable stages. |
| ALGOL blocks | Old procedural ceremony | Lexical block structure as the visual skeleton for scope, control, and policy. |

An idea enters Nomi only after this translation. If it cannot be translated, it
remains background inspiration.

## Coherence Invariants

These invariants protect the language from becoming a feature pile.

### One Binding Story

Names are introduced by binding. Assignment, parameters, block parameters, loop
variables, destructuring, match captures, shape fields, imports, and exception
aliases should share the same conceptual operation.

```python
age:int, age >= 0 = payload.age

func signup(age:(int, age >= 13)):
    ...

each(users) -> user:User:
    ...

match payload:
    case {"age": age:(int, age >= 13)}:
        ...
```

If these need four validation systems, the language is incoherent.

### One Block Story

A block is caller-side code attached to a call. The callee can invoke it with
`yield`, possibly with values.

```python
retry(3):
    send(request)

transaction(db) -> tx:
    tx.insert(user)
```

Context managers, retries, tests, cleanup, tracing, and structured concurrency
should be library-visible uses of the same block idea, not separate control
languages.

### One Pattern Story

Patterns test structure and bind names. Pattern binding, match cases,
destructuring assignment, algebraic data variants, and shape matching should
reuse one pattern model.

```python
(x, y) = point

match result:
    case Ok(value):
        value
    case Err(error):
        explain(error)
```

### One Expression Flow Story

Nested calls, pipelines, composition, collection transforms, table queries, and
calculational blocks should be different views of value flow.

```python
clean = strip >> lower >> normalize_space

name =
    raw
    |> strip
    |> lower
    |> normalize_space
```

Pipeline applies a value now. Composition builds a function for later. Query and
array operations are structured transformations in the same family.

### One Symbolic Boundary

Ordinary code runs. Quoted code is data.

```python
expr = quote:
    x + 0

simple = expr /. a + 0 -> a
```

Symbolic rules, macros, code transformations, and notation definitions must
cross an explicit boundary. This lets Nomi learn from Mathematica and Scheme
without making ordinary code unpredictable.

### One Effect Boundary

Effects are not shameful, but they should be cognitively visible when they
matter.

```python
with world(fs, network) as w:
    page = w.network.get(url)
    w.fs.write(path, page)
```

This can start as runtime convention and become stronger over time. The
coherence requirement is that IO, time, randomness, subprocesses, database
transactions, and simulation eventually speak in compatible terms of worlds,
capabilities, and block policies.

### One Explanation Story

Every major feature should produce explanations in its own semantic vocabulary:

- binding explains failed constraints,
- block control explains yield/resume/retry/cancel,
- pattern matching explains why a case matched or failed,
- pipelines explain intermediate values,
- symbolic rewrite explains which rule fired,
- effects explain what authority was used,
- examples explain intended behavior.

Diagnostics are not afterthoughts. They are part of the language's cognitive
contract.

## Surface Design Rules

### Prefer A Shared Shape Over A Famous Spelling

If a borrowed spelling does not fit Nomi's shared grammar, use a different
spelling.

For example, Haskell's `>>=` is powerful, but Nomi should not import it merely
because it is canonical. The Nomi question is: does this become a block policy,
a pipeline stage, a result combinator, or a capability boundary?

### Prefer Visible Boundaries

Advanced power is welcome when its boundary is visible:

- `quote:` for symbolic/code-as-data,
- `use name:` for scoped notation,
- `world(...)` for capability scopes,
- `shape` for external data boundaries,
- block calls for control policies.

Invisible ambient behavior should be treated as design debt.

### Prefer One Good Spelling

When two syntax forms express the same cognitive operation, one should usually
win. Aliases are expensive because they split the programmer's mental model.

### Prefer Desugaring That Teaches

A desugaring is not only an implementation trick. It is a way to teach the
feature.

Good desugaring says:

```text
this feature is really binding plus constraints
this feature is really a call plus a block
this feature is really a quoted expression plus a rewrite rule
```

Bad desugaring says:

```text
the compiler has a secret special case here
```

## A Coherent Target Example

This example intentionally combines ideas from several traditions while making
them pass through one Nomi shape.

```python
shape SignupPayload:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"
    plan:Plan = Plan.Free

data SignupResult:
    Created(user:User)
    Rejected(reason:SignupError)

func signup(raw:dict, services:SignupServices) -> SignupResult:
    examples:
        {"email": "a@b.com", "age": 18} => Created(...)

    payload:SignupPayload = raw

    user =
        payload
        |> normalize_signup
        |> build_user

    transaction(services.db):
        services.db.users.insert(user)
        audit("signup", user.id)

    return Created(user)
```

This is not syntax collage:

- `shape` uses binding and constraints.
- `data` creates pattern-matchable variants.
- `examples` attach behavior to a function.
- `|>` expresses value flow.
- `transaction` is a block policy.
- diagnostics can explain each boundary.

The language feels larger than Python, but the mental model is smaller than a
bag of unrelated features.

## Rejection Tests

Reject or redesign a feature when:

- it only exists because another language has it,
- it introduces a second meaning for binding, blocks, patterns, effects, or
  symbolic code,
- it requires global magic to be useful,
- it cannot produce a meaningful explanation when it fails,
- it makes common code read like expert-only notation,
- it cannot be scoped, desugared, or inspected,
- it competes with an existing Nomi spelling for the same operation.

## Design Review Questions

Every feature proposal should answer:

1. Which Nomi primitive does this extend?
2. Which cognitive operation does it improve?
3. Which borrowed tradition inspired it?
4. What did we deliberately not copy from that tradition?
5. How does it compose with binding, blocks, patterns, expression flow, symbolic
   boundaries, and diagnostics?
6. What is the smallest example where it makes the whole language feel more
   coherent?

If these answers are weak, the feature is not ready.

---

<a id="documentation-design-review-cognitive-language-vision-md"></a>

# Source: `documentation/design_review/cognitive_language_vision.md`

# Cognitive Language Vision

> Status: active long-horizon design.
>
> This document defines the forward-looking language target. It is not bounded
> by the current Python-hosted prototype. Implementation exists to test and
> refine the design, not to decide the ambition.

## Thesis

Nomi is a general-purpose programming language optimized for cognition.

The scarce resource is not CPU cycles, memory, or parser convenience. The scarce
resource is the programmer's ability to hold a program in mind, reshape it,
trust it, explain it, and compose it with other ideas.

Nomi should feel locally readable like Python, but it should not be "Python plus
features." More importantly, it should not begin by collecting features from
other languages. The main design spine is the
[First-Principles Programming Model](first_principles_programming_model.md):
build upward from primitive cognitive acts, then use existing languages as
reference experiments.

Several language families illuminate the design:

- Python's indentation, names, calls, libraries, and everyday readability,
- Haskell's algebraic modeling, purity boundaries, compositional functions, and
  type-shaped thinking,
- Mathematica's symbolic expressions, rules, rewrite systems, and calculational
  style,
- Kotlin's null-safety, data modeling, extension-oriented ergonomics, and
  pragmatic defaults,
- Ruby's caller-side blocks and humane internal DSLs,
- Scheme's small core, lexical clarity, code-as-data, and scoped abstraction,
- APL's whole-collection thinking, rank awareness, and transformation density,
- ALGOL's block structure, lexical scope, and procedural clarity.

The goal is not eclectic syntax. The goal is a language where references from
other languages are translated into one first-principles semantic grammar. The
active coherence rules are defined in
[Language Coherence Model](language_coherence_model.md).

## Not A Syntax Collage

Nomi should not collect language features because they are famous, elegant, or
historically important. A feature belongs only when it becomes part of the same
whole.

That means:

- Haskell contributes algebraic modeling and effect thinking, not necessarily
  Haskell's visual style.
- Mathematica contributes explicit symbolic transformation, not ambient magical
  rewriting of ordinary code.
- Ruby contributes caller-side blocks, not uncontrolled implicit receivers.
- Scheme contributes regularity and code-as-data boundaries, not a separate
  parenthesized sublanguage.
- APL contributes whole-data thinking, not default glyph density.

The source languages are teachers. Nomi must still have one grammar of thought.

## Cognitive Priorities

Nomi should optimize for these human operations:

- reading a small fragment without global context,
- naming a concept exactly once and reusing it everywhere,
- turning informal invariants into executable constraints,
- moving between concrete examples and general rules,
- transforming data left-to-right without nesting noise,
- representing structure without ceremony,
- making hidden control explicit enough to inspect,
- treating code-shaped ideas as values when explicitly requested,
- asking the runtime why a value, branch, or result happened,
- letting advanced notation exist inside a controlled scope.

Performance matters eventually, but it is not the design north star. A slower
language that helps the programmer think better can later be optimized. A
confusing language made fast has already lost the central battle.

## The Semantic Spine

The language should reduce many surface features to a small set of ideas:

```text
value
binding
constraint
function
call
block
yield
pattern
data
shape
collection
table
quote
rewrite
effect
world
capability
example
trace
diagnostic
module
use
```

This is not a minimal machine core. It is a cognitive core: the concepts a
programmer should be able to learn once and recognize everywhere.

## Source-Language Synthesis

| Source | Durable idea | Nomi direction |
| --- | --- | --- |
| Python | Local readability, ordinary calls, indentation, practical libraries | Keep as surface baseline and migration bridge. |
| Haskell | Types as structure, pure functions, algebraic data, pattern matching | Use algebraic modeling and effect boundaries without making daily code feel scholastic. |
| Mathematica | Expressions as data, symbolic rules, rewrite-driven thinking | Add explicit quoted expressions and scoped rewrite systems. |
| Kotlin | Nullable values, data classes, extension functions, ergonomic defaults | Make absence, data, and local extension predictable and lightweight. |
| Ruby | Blocks as caller-side behavior, expressive internal DSLs | Generalize block calls with inspectable `yield` semantics. |
| Scheme | Small regular core, lexical scope, macros as transformation | Keep regularity and explicit code-as-data boundaries. |
| APL | Whole-array operations, rank, shape, tacit composition | Make collection and table transformations dense but still readable. |
| ALGOL | Blocks, scope, structured control | Preserve block clarity as the visual and semantic skeleton. |

Borrowing should happen at the idea level. If a feature imports visual clutter,
implicit magic, or several equivalent spellings, it has probably imported the
wrong layer.

## Feature Pillars

### 1. Binding, Constraints, And Shape

Binding is the act of receiving a value into a name or structure. Constraints
turn that act into a semantic boundary.

```python
payload:SignupPayload = request.json
user = User(id=new_id(), email=payload.email)
```

This pillar covers assignment, parameters, destructuring, pattern captures,
external data, forms, CLI arguments, config, and diagnostics.

### 2. Blocks As Control Values

Caller-side blocks let libraries define control forms without adding a keyword
for every policy.

```python
retry(3, on=NetworkError):
    send(request)

transaction(db) -> tx:
    tx.insert(user)
```

This pillar covers resource scopes, retry, timeout, transactions, tests,
cleanup, logging, tracing, permissions, structured concurrency, and local
policies.

### 3. Expression Orientation And Transformation Flow

Programs should support direct expression of value flow without turning simple
steps into nested calls.

```python
summary =
    text
    |> parse
    |> normalize
    |> summarize
```

This pillar covers pipelines, function composition, final-expression return,
`match` expressions, scoped intermediate bindings, and calculation blocks.

### 4. Algebraic Data And Pattern Thinking

Programs should model alternatives directly.

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)

match response:
    case Ok(user):
        render(user)
    case Err(error):
        explain(error)
```

This pillar brings Haskell/ML-style modeling into a Python-readable surface.

### 5. Collections, Arrays, Tables, And Queries

Nomi should make whole-data transformations first-class without forcing a
separate string language.

```python
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Future array and table work should learn from APL, SQL, KDB/q, dataframes, and
Mathematica while preserving inspectable desugaring.

### 6. Symbolic Expressions And Rewrite Rules

Code-shaped syntax should become data only at explicit boundaries.

```python
expr = quote:
    x + 0

simplified = expr /. a + 0 -> a
```

This pillar enables algebra, program transformation, macros, optimizer passes,
teaching tools, and AI-assisted refactoring without making ordinary runtime code
magically symbolic.

### 7. Effects, Worlds, And Capabilities

Side effects should be understandable as scoped capabilities rather than ambient
global permission.

```python
with world(fs, network) as w:
    page = w.network.get(url)
    w.fs.write(path, page)
```

This does not need to become Haskell's IO model. The point is cognitive
explicitness: what can this code touch, and under which policy?

### 8. Examples, Tests, Proofs, And Explanation

The language should let examples become executable semantic anchors.

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

The runtime should eventually answer questions such as:

- why did this constraint fail?
- why did this match case win?
- which values flowed through this pipeline?
- which examples define the intended behavior?

### 9. Scoped Notation And Local Language Growth

Nomi should permit domain notation only inside explicit scopes.

```python
use units:
    speed = 30 km / hour
```

This is a dangerous feature unless scoped, inspectable, and desugarable. Used
carefully, it lets the language grow toward the user's problem rather than
forcing every problem into generic syntax.

## Target Daily Example

```python
shape SignupPayload:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"
    plan:Plan = Plan.Free

data User(id:UserId, email:str, plan:Plan)

func signup(payload:SignupPayload) -> Result[User, SignupError]:
    examples:
        {"email": "a@b.com", "age": 18} => Ok(User(...))

    user =
        payload
        |> validate
        |> build_user

    transaction(db):
        db.users.insert(user)
        audit("signup", user.id)

    return Ok(user)
```

This example combines shape binding, data modeling, result values, examples,
pipelines, transactions, and audit policy. The ambition is not to implement all
of this immediately. The ambition is to keep every implemented feature pointed
toward code like this.

## Design Discipline

New features should pass these questions:

1. What cognitive operation does this make easier?
2. What source-language idea is being borrowed, and at what abstraction level?
3. What primitive does it reduce to?
4. What boundary keeps it from becoming implicit magic?
5. How will diagnostics explain it when it fails?
6. Can this feature compose with binding, blocks, patterns, and examples?

If a feature is powerful but not explainable, it stays in the archive. If it is
explainable and cognitively useful, implementation difficulty is not a reason to
drop it.

---

<a id="documentation-design-review-binding-constraints-feature-md"></a>

# Source: `documentation/design_review/binding_constraints_feature.md`

# Binding Constraints Feature

> Status: active feature design.
>
> Goal: make constrained binding one detailed pillar of the broader
> cognition-first language vision. The current prototype is relevant evidence,
> not a boundary on the design.

First-principles position:

```text
Name -> Judge -> Explain
```

Binding constraints exist because a program must name values, judge whether
they satisfy a concept, and explain failures at the boundary where values enter
meaningful use.

## One Sentence

A Nomi binding may carry constraints; the value is tentatively bound, checked in
the binding context, and committed only if every constraint succeeds.

```python
age:int, age >= 0 = payload.age
email:str, contains(email, "@") = payload.email
```

## Why This Feature

Binding appears everywhere:

- assignment,
- annotated assignment,
- function parameters,
- default arguments,
- block parameters,
- loop variables,
- `except ... as ...`,
- `with ... as ...`,
- imports,
- destructuring,
- pattern matching,
- future shape binding for JSON, forms, config, and CLI values.

Python already has pieces of this idea, but they are split across type hints,
dataclasses, `pydantic`, `argparse`, pattern matching, manual validation, and
custom exceptions. Nomi can make the recurring operation explicit:

> receiving a value into a name is a boundary where shape and meaning can be
> checked.

## Prototype Seed

The current prototype already supports part of this design:

```python
is_positive = (x) => x > 0
score:int, is_positive = 72
```

Relevant implementation points:

- `prototype/grammar/layers/bindings.lark` handles annotated assignment with constraint lists in the `annassign` rule.
  list.
- `prototype/parser/python/binding.py` lowers annotated assignment to
  `ast.AnnAssign`.
- `prototype/interpreter/nomi/binding.py` turns annotations into predicates.
- `prototype/interpreter/nomi/env.py` stores and checks constraints on
  assignment.
- `prototype/tests/e2e/test_nomi_scenarios.py` has an end-to-end constrained
  binding scenario.

This spec extends that seed into a coherent feature. It should be read forward:
the desired semantics are allowed to exceed what the current interpreter can do.

## Surface Syntax

### Assignment Binding

```python
name = value
name:Type = value
name:Type, predicate = value
name:Type, expression_using_name = value
```

Examples:

```python
count:int = raw_count
count:int, count >= 0 = raw_count
email:str, contains(email, "@") = raw_email
```

The comma after `:` separates constraints on one binding, not multiple
assignment targets.

### Bare Constraint Declaration

A binding may declare constraints before the value is assigned:

```python
port:int, port > 0, port < 65536
port = config.port
```

This keeps useful Python-like annotation shape while changing the runtime
meaning: the constraint affects later assignment in the same binding scope.

### Rebinding

Rebinding without a new annotation keeps the current constraint:

```python
age:int, age >= 0 = 34
age = 35        # checked
age = -1        # BindingError
```

Rebinding with a new annotation replaces the previous constraint set in that
scope:

```python
value:int = 1
value:str = "one"
```

This matches the current prototype direction and avoids invisible accumulation.

### Parameter Binding

Function parameters are bindings:

```python
func withdraw(account:Account, amount:(Money, amount > 0)):
    account.debit(amount)
```

Parentheses group multiple constraints for one parameter so the comma does not
look like another parameter:

```python
func f(a:int, b:(int, b > 20)):
    ...
```

Parameter constraints are checked after Python-compatible argument mapping:
positional arguments, keyword arguments, defaults, `*args`, and `**kwargs` are
resolved first; then each resulting parameter binding is validated.

### Block Parameter Binding

Caller-side blocks use the same binding rules:

```python
each(users) -> user:User:
    send(user.email)

pairs(headers) -> key:str, value:str:
    print(key, value)
```

The callee controls when values are yielded; the caller controls how yielded
values are bound.

The current implementation does a simpler one-to-one mapping for yielded block
values. The target design should reuse the same binding engine used by function
parameters.

### Pattern Binding

Destructuring and match cases should validate names at the same boundary:

```python
(x:int, y:int) = point
{"age": age:(int, age >= 0), "email": email:str} = payload
```

Match cases:

```python
match payload:
    case {"age": age:(int, age >= 13), "email": email:str}:
        signup(age, email)
```

Pattern failure and constraint failure are different:

- pattern failure means this shape did not match,
- constraint failure means this shape matched but the value was invalid.

For `match`, constraint failure should make the case fail unless the case body
has already started. For direct assignment, constraint failure raises.

### Shape Binding

`shape` is a future declaration form for external structural data:

```python
shape SignupPayload:
    email:str, contains(email, "@")
    age:int, age >= 13 else "Must be at least 13"
    name:str?
```

Usage:

```python
payload:SignupPayload = request.json
```

`shape` is one of the most important downstream use cases for the feature. It
turns request/config/form/CLI validation into ordinary binding and should shape
the design even before it is implemented.

## Constraint Kinds

### Type Constraint

```python
age:int = value
```

Meaning:

```python
isinstance(value, int)
```

Open question: exact handling of generics such as `list[int]` depends on the
eventual type/value representation. The design target should still include
parameterized constraints, algebraic data, and shape declarations.

### Predicate Constraint

```python
is_positive = (x) => x > 0
amount:int, is_positive = value
```

Meaning:

```python
is_positive(value)
```

The predicate should return truthy or raise a useful error.

### Expression Constraint

```python
amount:int, amount > 0 = value
```

The expression is evaluated with the binding name available as the tentative
value.

Conceptual lowering:

```python
tmp = value
if not isinstance(tmp, int):
    raise BindingError(...)
if not (tmp > 0):
    raise BindingError(...)
amount = tmp
```

The actual runtime may compile the expression into a predicate, as the current
prototype does, but the programmer-facing semantics are tentative binding plus
validation.

### Message Constraint

Human-facing failure messages are attached to individual constraints:

```python
age:int, age >= 13 else "Must be at least 13" = payload.age
```

This should lower to structured diagnostic metadata, not merely string
concatenation.

## Failure Model

Introduce a Nomi-level `BindingError`.

Minimum fields:

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

The exact exception class can initially subclass `TypeError` for compatibility,
but tests should assert the Nomi-level behavior and metadata once available.

## Scope Semantics

Constraints belong to a binding in a scope.

Rules:

- a local annotation sets the local constraint set,
- plain assignment to an existing local constrained binding is checked,
- `global` assignment checks the global binding's constraints,
- `nonlocal` assignment checks the nearest enclosing binding's constraints,
- shadowing creates an independent binding with independent constraints,
- deleting a binding should remove its local constraints unless a future design
  introduces explicit persistent declarations.

This matches the current environment tests and gives implementation a clear
target.

## Desugaring

Every constrained binding follows the same sequence:

```text
1. Evaluate the right-hand side once.
2. Tentatively bind the value against the target name or pattern.
3. Evaluate constraints in the tentative binding context.
4. If any constraint fails, raise or report a structured BindingError.
5. If all constraints pass, commit the binding to the target scope.
```

For parameters:

```text
1. Resolve call arguments to parameters.
2. Apply defaults, varargs, and keyword rules.
3. Validate each parameter binding.
4. Enter the function body with committed bindings.
```

For block parameters:

```text
1. The callee yields zero or more values.
2. The caller's block parameter target binds those values.
3. Constraints are checked.
4. The block runs only after successful binding.
```

For pattern matching:

```text
1. Test structural pattern shape.
2. Tentatively bind captured names.
3. Check captured-name constraints.
4. If shape or constraints fail, try the next case.
5. If they pass, run the case body.
```

## Interaction With Other Features

### `func` And Arrow Functions

`func` definitions and arrow functions share parameter binding semantics.

```python
is_adult = (age:(int, age >= 18)) => True
```

If arrow parameters cannot support this immediately, the parser should reject
the syntax intentionally rather than silently accepting weaker semantics.

### Pattern Matching

Constrained captures should reuse the same `BindingTarget` model as assignment.
The grammar should avoid one-off pattern-only validation rules.

### Yield-To-Block

Block parameters should become a direct client of the constrained binding
engine. This is the cleanest way to close the current gap between function
argument mapping and yielded-value mapping.

### Future `data`

`data User(id:int, email:str)` creates an owned value type. The field
constraints are binding constraints on constructor arguments.

### Future `shape`

`shape SignupPayload` creates a structural binding constraint over external
data. A shape is not an owned runtime class by default; it is a validation and
projection boundary.

## Non-Goals For The First Detailed Pass

- static type inference,
- full generic runtime type checking,
- dependent types,
- custom user-defined parser syntax,
- implicit coercion,
- accumulation of old constraints across re-annotation,
- global validation hooks that fire outside binding.

## Design Tests

A proposed implementation is coherent only if all of these examples have one
semantic story:

```python
age:int, age >= 0 = value
```

```python
func signup(age:(int, age >= 13)):
    ...
```

```python
each(users) -> user:User:
    ...
```

```python
{"age": age:(int, age >= 13)} = payload
```

```python
match payload:
    case {"age": age:(int, age >= 13)}:
        ...
```

If any of these needs a separate validation mechanism, the implementation is
drifting away from the feature.

---

<a id="documentation-design-review-block-calls-feature-md"></a>

# Source: `documentation/design_review/block_calls_feature.md`

# Block Calls As Control Values

> Status: focused feature design.
>
> This is the first focused follow-up to the cognition-first language direction.
> It studies one syntax/idea deeply: caller-side blocks attached to calls, and
> how they reduce to a small core without becoming a pile of copied Ruby,
> Python, Kotlin, or Scheme syntax.

First-principles position:

```text
Transform -> Sequence In Time -> Touch The World -> Explain
```

Block calls exist because some transformations are time-shaped policies:
acquire, yield, retry, cancel, clean up, authorize, and explain.

## One Sentence

A Nomi block call is an ordinary call with caller-side code attached; the callee
may invoke that code explicitly with `yield`.

```python
retry(3, on=NetworkError):
    send(request)

transaction(db) -> tx:
    tx.insert(user)
```

## Why This Idea Belongs

Many everyday programming patterns are control policies:

- acquire and release a resource,
- retry an operation,
- add a timeout,
- run a transaction,
- collect logs and traces,
- run a test with fixtures,
- schedule parallel work,
- temporarily grant a capability,
- validate setup before a body runs,
- clean up after success, failure, or cancellation.

Python has several partial answers: `with`, decorators, callbacks, generators,
context managers, `async with`, fixtures, and higher-order functions. Ruby has a
clearer general idea: a method can receive a caller-side block and `yield` to
it. Kotlin has trailing lambdas. Scheme has functions and continuations. ALGOL
has block structure.

Nomi should translate those ideas into one coherent construct:

> A block is control-shaped code supplied by the caller to a callee-owned policy.

## Core Form

Zero-yield-value block:

```python
retry(3):
    send_request()
```

Yielded-value block:

```python
using(open(path)) -> file:
    data = file.read()
```

Multiple yielded values:

```python
pairs(headers) -> key, value:
    print(key, value)
```

Constrained block parameter:

```python
each(users) -> user:User:
    send(user.email)
```

Pattern block parameter:

```python
events(stream) -> {"type": "click", "target": target}:
    record_click(target)
```

The block parameter syntax after `->` is a binding target. That is the key
coherence decision: block parameters should not invent a new parameter system.
They reuse the binding/pattern/constraint story.

## Callee Form

The callee uses `yield` to invoke the attached block:

```python
func retry(times, on=Exception):
    for attempt in range(times):
        try:
            yield
            return
        except on:
            if attempt == times - 1:
                raise
```

Yielding values:

```python
func each(items):
    for item in items:
        yield item
```

Bidirectional yield is allowed as the coroutine layer matures:

```python
func ask(prompt):
    answer = yield prompt
    return normalize(answer)
```

The first operational subset may support only simple `yield` and `yield value`,
but the design target is a resumable call point where the block can return a
value to the callee.

## Reduction To Small Core

Surface:

```python
transaction(db) -> tx:
    tx.insert(user)
```

Conceptual reduction:

```text
block_value =
    Block(
        caller_env=current lexical environment,
        binding_target=tx,
        body=[tx.insert(user)],
    )

transaction(db, __block__=block_value)
```

Inside the callee:

```python
yield value
```

reduces to:

```text
invoke __block__ with yielded value
bind yielded value to the block binding target
execute block body in caller lexical environment
return block result to the callee
```

This keeps the small core:

```text
value
binding
function
call
block
yield
pattern
constraint
effect
diagnostic
```

No new control keyword is needed for `retry`, `transaction`, `using`, `timeout`,
or `trace`. They are functions that own policy and invoke a caller-supplied
block.

## Variations Considered

### Variation 1: Python `with` Only

```python
with transaction(db) as tx:
    tx.insert(user)
```

Strengths:

- familiar to Python programmers,
- clear resource acquisition/release shape,
- easy to explain for simple setup/cleanup.

Weaknesses:

- specialized around enter/exit,
- awkward for retry because the body must run multiple times,
- awkward for yielded streams of values,
- separate from decorators, fixtures, and higher-order control,
- does not naturally generalize to bidirectional coroutine communication.

Nomi decision:

`with` can remain as a compatibility or library surface, but it should reduce to
block calls or block policies. It should not be the only control abstraction.

### Variation 2: Higher-Order Functions With Arrow Lambdas

```python
retry(3, () => send_request())

using(open(path), (file) =>:
    data = file.read()
)
```

Strengths:

- small theoretical core,
- familiar in functional languages,
- easy to pass around as values.

Weaknesses:

- visually noisy for multiline control,
- creates a function scope when the programmer often wants caller-local code,
- makes policy look like data plumbing instead of control structure,
- poor fit with Python-like indentation.

Nomi decision:

Function values remain important, but block calls should exist for
control-shaped code. A block is not merely a prettier lambda; it has caller-side
execution and control-flow semantics.

### Variation 3: Ruby `do ... end`

```ruby
retry(3) do
  send_request()
end
```

Strengths:

- proven ergonomic model,
- method-owned control is natural,
- block parameters are clear in Ruby.

Weaknesses:

- `do/end` conflicts with Nomi's Python-readable indentation direction,
- Ruby's implicit receiver conventions are too magical for Nomi,
- Ruby has several block spellings and subtle precedence issues.

Nomi decision:

Borrow the semantic idea, not the surface. Nomi uses indentation:

```python
retry(3):
    send_request()
```

### Variation 4: Kotlin Trailing Lambda

```kotlin
retry(3) {
    sendRequest()
}
```

Strengths:

- clean for single trailing blocks,
- strong fit with builder APIs and scoped receivers.

Weaknesses:

- braces are less consistent with Nomi's Python-like block structure,
- implicit receivers can obscure which object owns a name,
- multiple lambdas and receiver lambdas add mental overhead.

Nomi decision:

Borrow trailing behavior, reject brace syntax and implicit receiver defaults.
If receiver-like scopes are added later, they must be explicit and inspectable.

### Variation 5: Full Continuations

Scheme-style continuations could express almost every control pattern.

Strengths:

- extremely general,
- theoretically elegant,
- captures nonlocal control and advanced flow.

Weaknesses:

- too hard for ordinary local reasoning,
- diagnostics become difficult,
- too powerful as the default explanation for everyday control.

Nomi decision:

Keep resumable `yield` as the practical control primitive. Full continuation
power may exist internally or in advanced scoped features, but it should not be
the ordinary user-facing model.

### Variation 6: Dedicated Keywords For Each Policy

```python
retry 3:
    ...

timeout 5s:
    ...

transaction db:
    ...
```

Strengths:

- highly readable for a few built-in policies,
- easy to optimize or special-case.

Weaknesses:

- grows the language by keyword accumulation,
- makes libraries second-class,
- violates the goal of reducing many patterns to a small core.

Nomi decision:

Policy names should usually be functions. Syntax should make the block
attachment smooth, not create a keyword for each policy.

## Chosen Direction

Use this syntax:

```python
call(args):
    block_body

call(args) -> binding_target:
    block_body
```

with this meaning:

- `call(args)` is evaluated as an ordinary call,
- the indented body is packaged as a caller-side block,
- the optional `-> binding_target` describes how yielded values bind into the
  block body,
- `yield` inside the callee invokes the block,
- block invocation uses the same binding, pattern, and constraint rules as the
  rest of the language,
- the block executes in the caller's lexical context, under well-defined
  rebinding rules.

## Scope And Binding

The hardest design choice is whether the block runs in a new function-like
scope or in the caller's scope.

Chosen direction:

> A block executes in the caller's lexical environment, but yielded values are
> introduced through an explicit binding target.

Example:

```python
total = 0

each(items) -> item:int:
    total += item
```

`total` is the caller's binding. `item` is the block parameter binding for each
yield.

Open design details:

- Does assigning a new name inside a block create a binding visible after the
  block?
- Should there be a `scope:` or `let:` wrapper for block-local names?
- How do `global` and `nonlocal` interact with block execution?
- Can a block return early from the enclosing function, or only from the block?

Default position:

- existing caller bindings may be read and rebound,
- yielded parameters are scoped to the block invocation,
- new names should be local to the block unless explicitly exported,
- nonlocal control such as `return`, `break`, and `continue` needs a separate
  rule per enclosing construct.

This should be specified carefully before blocks become too powerful.

## Result Semantics

There are three possible meanings for a block call's result.

Option A: result is always the callee return value.

```python
result = retry(3):
    send()
```

Option B: result is the last block expression.

```python
value = using(resource) -> r:
    r.read()
```

Option C: result is whatever the callee returns, and the callee may choose to
use the block result.

```python
func using(resource):
    acquired = acquire(resource)
    try:
        return yield acquired
    finally:
        release(acquired)
```

Chosen direction:

Option C. The block call expression returns the callee's return value. If the
callee wants the block's value, it receives it as the result of `yield` and can
return it.

This keeps control ownership with the callee and makes `yield` the explicit
boundary.

## Error And Cancellation Semantics

Block calls must define failure clearly:

- if the block body raises, the exception resumes at the callee's `yield`,
- the callee may catch, retry, translate, or re-raise it,
- `finally` in the callee must run when the block exits by success, failure, or
  cancellation,
- diagnostics should show both the callee policy frame and caller block frame.

Example:

```python
func retry(times, on=Exception):
    for attempt in range(times):
        try:
            return yield
        except on as error:
            if attempt == times - 1:
                raise
```

The exception belongs to the block body, but policy belongs to `retry`.

## Coherence With Other Features

### Binding And Constraints

Block parameters are binding targets:

```python
each(users) -> user:(User, user.active):
    send(user.email)
```

The yielded value is tentatively bound, constraints are checked, and the block
body runs only after successful binding.

### Patterns And Data

Blocks can receive structured values:

```python
events(stream) -> Click(target):
    record(target)
```

This should reuse match/destructuring patterns.

### Pipelines

Block policies can appear inside expression flow when the return value is clear:

```python
result =
    fetch(url)
    |> retrying(3, _)
    |> parse_json
```

But normal block calls are better for control policies with multi-line bodies.

### Effects And Capabilities

Capabilities are naturally scoped by block calls:

```python
with world(fs, network) -> w:
    data = w.network.get(url)
    w.fs.write(path, data)
```

Whether the spelling is `with world(...)` or `world(...):`, the semantic model
should be a block policy that grants capabilities for the body.

### Examples And Tests

Tests and examples are block policies:

```python
test "signup rejects young user":
    expect(signup({"age": 12})).is Err
```

This may later be syntax sugar for a block call:

```python
test("signup rejects young user"):
    expect(signup({"age": 12})).is Err
```

### Symbolic Code

Blocks are runtime control, not symbolic transformation. Symbolic blocks need an
explicit boundary:

```python
rule = quote:
    x + 0 -> x
```

This prevents block syntax from becoming a hidden macro system.

## Diagnostics

A block-aware diagnostic should answer:

- which call owned the control policy?
- where did the callee yield?
- what values were yielded?
- how were yielded values bound?
- did a block parameter constraint fail?
- did the block raise?
- did the callee retry, suppress, translate, or re-raise?

Example diagnostic shape:

```text
BlockError: yielded value failed block parameter constraint
  policy: each(users)
  yield: item at each.nomi:3
  block parameter: user:User
  value: {"name": "Ada"}
  note: expected User
```

This is part of the feature, not optional tooling.

## Syntax Admission Rule

The block-call syntax is admitted because it:

- reduces many control policies to call plus block plus yield,
- preserves Python-readable indentation,
- borrows Ruby's best control abstraction without copying Ruby's receiver magic,
- generalizes Python `with` without being limited to enter/exit,
- composes with constrained binding and patterns,
- creates a natural home for effects, tests, transactions, tracing, and cleanup,
- has an inspectable desugaring.

## Implementation Todo Slice

- Parse `call(args): suite` as a block call.
- Parse `call(args) -> binding_target: suite`.
- Represent attached blocks explicitly rather than as an ad hoc keyword long
  term.
- Route yielded values through the shared binding engine.
- Define block lexical scope and rebinding rules.
- Support `yield` returning the block body's result.
- Propagate block exceptions back through the yielding callee.
- Add diagnostics for yield location, block binding, and policy frames.
- Add examples for `retry`, `using`, `transaction`, `each`, `test`, and
  `world`.

## Open Questions

- Should `with resource -> r:` be canonical syntax, or should all policy blocks
  use ordinary call form?
- Should block bodies have final-expression return by default?
- Should new names inside a block escape to the surrounding scope?
- Should `return` inside a block return from the block, the callee, or the
  enclosing caller function?
- How should async block policies compose with normal block policies?
- Can block values be named and passed explicitly, or should that be a separate
  later feature?

These questions should be answered by preserving one block story, not by adding
special cases for each policy.

---

<a id="documentation-design-review-implementation-todos-md"></a>

# Source: `documentation/design_review/implementation_todos.md`

# Language Feature Todos

> Status: staged backlog for the forward-looking language design.

This backlog turns
[First-Principles Programming Model](first_principles_programming_model.md),
[Hierarchical Language Research Plan](hierarchical_language_research_plan.md),
[Cognitive Language Vision](cognitive_language_vision.md), and
[Binding Constraints Feature](binding_constraints_feature.md) into
implementation-sized work. The current prototype is a bootstrap path, not a
limit on what should be designed.

## Track 0: First Principles, Vision, And Design Fixtures

- [ ] Maintain the first-principles programming model as the main spine of the
  language design.
- [ ] Use the hierarchical language research plan to order focused design
  commits from primitive layers upward.
- [ ] For each feature, identify the primitive cognitive act it supports before
  comparing language precedents.
- [ ] Maintain one canonical cognitive-language vision document and keep it
  ahead of the implementation.
- [ ] Maintain the language coherence model as a blocking design review for new
  features.
- [ ] Extract promising ideas from `documentation/design_review_archive/` into
  active feature specs only when they can share the same semantic spine.
- [ ] For each promoted idea, document what Nomi keeps from the source language
  and what it deliberately refuses to copy.
- [ ] Add target Nomi programs that intentionally use not-yet-implemented
  features: shape binding, algebraic data, pipelines, block policies, symbolic
  rewrite, table queries, and examples.
- [ ] Add executable examples for the accepted surface forms under
  `prototype/tests/data/sample_sources/interpreter/`.
- [ ] Add a small design-fixture file that contains desired future syntax even
  before all examples parse.
- [ ] Add a test matrix that distinguishes currently supported, planned, and
  intentionally rejected syntax.

## Track 1: Binding, Constraints, And Shape

- [ ] Introduce a runtime `BindingError` type with fields for name, value,
  failed constraint, source span when available, binding kind, and optional
  human message.
- [ ] Replace plain `TypeError` constraint failures with `BindingError`, while
  keeping compatibility where existing tests expect `TypeError`.
- [ ] Add a `Constraint` representation instead of storing bare predicate
  callables only. It should preserve the original expression/name and support
  diagnostics.
- [ ] Add a `BindingTarget` abstraction for name binding, tuple/list
  destructuring, mapping destructuring, and later pattern captures.
- [ ] Implement tentative binding and commit/rollback so failed constraints do
  not leak partially bound names.

### Parser And AST Shape

- [ ] Keep current assignment syntax working:
  `x:int, x > 0 = value`.
- [ ] Decide whether bare declaration syntax is accepted now:
  `x:int, x > 0`.
- [ ] Parse grouped parameter constraints:
  `func f(x:(int, x > 0)): ...`.
- [ ] Parse constrained block parameters:
  `each(xs) -> x:int: ...` and `pairs(xs) -> k:str, v:int: ...`.
- [ ] Parse constrained destructuring targets:
  `(x:int, y:int) = point`.
- [ ] Parse constrained match captures:
  `case {"age": age:(int, age >= 13)}:`.
- [ ] Preserve enough source location data for useful diagnostics.

### Parameter Binding

- [ ] Route function call argument mapping through the same binding-validation
  path used by assignment.
- [ ] Validate defaulted parameters after defaults are applied.
- [ ] Define how constraints apply to `*args` and `**kwargs`.
- [ ] Add tests for positional-only, keyword-only, defaults, varargs, and
  keyword arguments.
- [ ] Ensure arrow functions either support constrained parameters or reject
  them with a clear parse/runtime error.

### Block Parameter Binding

- [ ] Replace one-to-one yielded-value mapping with the shared binding engine.
- [ ] Support constrained single block parameters:
  `each(xs) -> item:int: ...`.
- [ ] Support constrained multi-value block parameters:
  `pairs(xs) -> key:str, value:int: ...`.
- [ ] Define behavior when the callee yields the wrong number of values.
- [ ] Add tests that failed block-parameter constraints prevent block body
  execution.

### Pattern And Destructuring Binding

- [ ] Reuse `BindingTarget` for tuple/list destructuring assignment.
- [ ] Reuse `BindingTarget` for mapping destructuring assignment.
- [ ] Add constrained pattern captures in `match`.
- [ ] Define direct assignment failure as `BindingError`.
- [ ] Define match-case constraint failure as case non-match before body entry.
- [ ] Add tests that partial pattern bindings do not leak on failure.

### Human Diagnostics

- [ ] Add `else "message"` syntax for individual constraints.
- [ ] Carry messages through `Constraint`.
- [ ] Produce diagnostics that name the binding kind: assignment, parameter,
  block parameter, destructuring target, or match capture.
- [ ] Include the failing source expression when available.
- [ ] Add regression tests for multi-constraint failures.

### Shape Binding

- [ ] Add a minimal `shape` declaration grammar.
- [ ] Implement shape validation over mappings first.
- [ ] Support optional fields with `?`.
- [ ] Support defaulted fields.
- [ ] Reuse binding constraints for each field.
- [ ] Add examples for request JSON, config, form data, and CLI args.

## Track 2: Blocks As Control Values

- [ ] Use `block_calls_feature.md` as the canonical focused feature spec.
- [ ] Specify block calls as calls with attached caller-side code and explicit
  `yield` points.
- [ ] Define block scoping: which names are read, rebound, shadowed, and
  captured.
- [ ] Implement block parameters through the shared binding engine.
- [ ] Add standard block policies: `using`, `retry`, `timeout`, `transaction`,
  `trace`, and `test`.
- [ ] Add diagnostics that show when and why a block was entered, yielded,
  resumed, retried, or cancelled.

## Track 3: Expression Flow, Pipelines, And Composition

- [ ] Specify `|>` pipeline semantics, including placeholder `_` and simple
  single-argument shorthand.
- [ ] Specify `>>` function composition separately from pipeline application.
- [ ] Add final-expression return for selected expression-oriented blocks.
- [ ] Add scoped intermediate bindings for calculational expressions.
- [ ] Add trace output for pipeline stages so the programmer can inspect value
  flow.

## Track 4: Algebraic Data, Results, And Pattern Matching

- [ ] Specify `data` declarations for product and sum types.
- [ ] Define constructor, field access, equality, display, and destructuring
  behavior.
- [ ] Add `Result[T, E]` and optional-value conventions.
- [ ] Extend `match` to cover algebraic variants, guards, constraints, and
  expression results.
- [ ] Add exhaustiveness diagnostics as an eventual goal, even if runtime-only
  checking comes first.

## Track 5: Collections, Arrays, Tables, And Queries

- [ ] Specify a collection transform vocabulary: `map`, `where`, `select`,
  `group`, `join`, `sort`, `fold`, and `window`.
- [ ] Decide which operations are syntax and which remain library-led block
  calls.
- [ ] Add table/row/column shape concepts that reuse binding and constraints.
- [ ] Explore APL-style rank and whole-array operations with readable spelling.
- [ ] Add examples for ordinary lists, records, dataframes, and time-indexed
  data.

## Track 6: Symbolic Expressions And Rewrite Rules

- [ ] Specify `quote:` as the explicit boundary where code-shaped syntax becomes
  data.
- [ ] Specify rewrite rules such as `expr /. pattern -> replacement`.
- [ ] Define evaluation boundaries so ordinary runtime code is not implicitly
  symbolic.
- [ ] Add a small expression AST model independent of Python's AST where needed.
- [ ] Add examples for algebra simplification, code transformation, and
  teaching/debugging tools.

## Track 7: Effects, Worlds, Capabilities, And Policies

- [ ] Specify capability scopes for filesystem, network, time, randomness,
  subprocesses, and environment access.
- [ ] Explore `world` values for simulation, test isolation, and replay.
- [ ] Define how block policies interact with capabilities.
- [ ] Add effect-aware diagnostics: what did this code touch, and under what
  authority?
- [ ] Keep this cognitive and inspectable rather than making it a resource
  optimization project.

## Track 8: Examples, Tests, Explanation, And Trace

- [ ] Specify `examples:` blocks inside functions and data/shape declarations.
- [ ] Let examples serve as tests, documentation, and behavioral anchors.
- [ ] Add `explain(expr)` or equivalent runtime explanation hooks.
- [ ] Add trace objects for constraints, matches, pipelines, block control, and
  rewrites.
- [ ] Make diagnostics speak in feature terms, not interpreter internals.

## Track 9: Scoped Notation And Language Growth

- [ ] Specify `use` scopes for enabling extension syntax or domain notation.
- [ ] Require every notation extension to provide a desugaring.
- [ ] Add guardrails against global syntax mutation.
- [ ] Prototype one small notation domain, such as units or symbolic algebra.
- [ ] Ensure tooling can show the expanded form on demand.

## Track 10: Cleanups And Coherence Checks

- [ ] Before implementing a feature, answer the coherence questions from
  `language_coherence_model.md`.
- [ ] Reject or redesign any feature that adds a second unrelated story for
  binding, blocks, patterns, expression flow, symbolic code, effects, or
  diagnostics.
- [ ] Remove duplicate ad hoc validation paths after the shared binding engine
  covers assignment, parameters, blocks, and patterns.
- [ ] Update `documentation/delta_on_python.md` to point to the canonical
  constrained-binding spec.
- [ ] Update `documentation/yield_to_block.md` with the block-parameter binding
  decision once implemented.
- [ ] Add a conformance-style test file containing the design tests from the
  feature spec.
- [ ] Mark archived design-review docs as background source material only.

## Milestone Sequence

The first milestone should still be coherent, but it should point beyond the
current prototype:

```python
func signup(age:(int, age >= 13), email:(str, contains(email, "@"))):
    return email

payload_age:int, payload_age >= 13 = 18
payload_email:str, contains(payload_email, "@") = "a@b.com"
result = signup(payload_age, payload_email)
```

Milestone 1 means:

- assignment constraints still work,
- parameter constraints work through real argument mapping,
- failures produce `BindingError`,
- tests cover success and failure,
- docs and implementation use the same vocabulary.

Milestone 2 should make blocks and shape binding real:

```python
shape SignupPayload:
    email:str, contains(email, "@")
    age:int, age >= 13

payload:SignupPayload = request.json

transaction(db):
    db.users.insert(payload.email)
```

Milestone 3 should make data flow readable:

```python
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Milestone 4 should make algebraic data and match central:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)

match fetch_user(id):
    case Ok(user):
        user.name
    case Err(error):
        explain(error)
```

Milestone 5 should open explicit symbolic power:

```python
expr = quote:
    x + 0

simple = expr /. a + 0 -> a
```

---

<a id="documentation-design-review-research-notes-synthesis-md"></a>

# Source: `documentation/design_review/research_notes_synthesis.md`

# Research Notes Synthesis

> Status: active synthesis note.
>
> This document distills a large, informal collection of research notes into
> coherent design pressure for Nomi. It is not a literature review. It is a map
> from scattered anchors to language-design work that can be implemented
> hierarchically.
>
> The links and book/article names in the raw notes are treated as research
> leads. They are not all validated here. The synthesis below is based on the
> themes and observations in the notes.

## Central Synthesis

The notes repeatedly circle one idea:

> Programming is the controlled growth of sophistication from simple elements,
> where every layer should remain peelable, inspectable, and reducible to a
> smaller core.

This is stronger than "take good ideas from languages." It says the language
must support a discipline of construction:

```text
primitive values
  -> names and contexts
  -> judgement and constraints
  -> transformations
  -> structured data
  -> patterns and decomposition
  -> repeated/array/table transformations
  -> time-shaped control
  -> effects and worlds
  -> examples, traces, explanations
  -> symbolic reflection and rewrite
```

The raw notes contain many references, but the useful organizing principle is
not historical chronology or language family. It is the progressive reification
of thought into executable structure.

## Major Research Pressures

### 1. Rewriting, Unification, And Symbolic Reduction

Raw anchors:

- term rewriting,
- substitutions and unification,
- equational unification modulo a theory,
- e-graphs and equality saturation,
- anti-unification,
- resolution theorem proving,
- description logic,
- Mathematica rewrite rules,
- Lisp symbolic expressions,
- logic variables.

Design pressure:

Nomi needs an explicit symbolic layer where program-shaped values can be
matched, transformed, normalized, generalized, and explained.

Important distinctions:

- pattern matching is one-way shape recognition,
- unification solves for substitutions that make shapes agree,
- equational unification adds background equations,
- rewriting transforms a matched term,
- strategies control which rewrite applies,
- normal forms are values that cannot reduce further under a chosen system.

Nomi implication:

Do not make ordinary code implicitly symbolic. Add an explicit `quote` boundary
and later add rewrite/unification tools over quoted syntax values.

Layer placement:

```text
L6 patterns and choice
L10 traces and explanation
L11 quote, rewrite, notation
```

Concrete future specs:

```text
quote_and_syntax_values_feature.md
rewrite_rules_feature.md
unification_and_patterns_feature.md
normal_forms_and_rewrite_strategies_feature.md
```

Small-core reduction:

```text
quoted syntax -> SyntaxValue
pattern -> Pattern over SyntaxValue or Value
unification -> substitutions over Pattern variables
rewrite -> Pattern + replacement + strategy
normalization -> repeated rewrite with trace
```

### 2. Binding, Environment, Store, And Scope

Raw anchors:

- R. D. Tennent on binding versus updating, environment versus store, scope
  versus lifetime,
- Tennent's correspondence principle,
- ALGOL block structure,
- Dijkstra and Landin on parameterless procedures and language semantics,
- Python global/nonlocal/env implementation friction,
- R first-class environments and data masks,
- Scala `val`/`var`,
- Pascal `with`,
- Ruby block parameter passing closer to assignment.

Design pressure:

Nomi's binding story must be made precise before higher features pile up.
Several raw implementation issues are symptoms of the same missing model:

- constraints and global/nonlocal assignment can drift apart,
- function arguments and assignment are not yet one operation,
- block parameters are not yet normal bindings,
- module environments are not yet cleanly separated,
- context manager/yield control stretches the environment model.

Nomi implication:

Binding is not just assignment syntax. It is the act of introducing a name into
a context. Updating storage is separate. This should become an explicit model.

Layer placement:

```text
L0 source, context, spans
L2 bindings and scope
L3 constraints and diagnostics
L8 blocks and yield
```

Concrete future specs:

```text
source_context_spans_feature.md
bindings_and_scope_feature.md
environment_store_lifetime_feature.md
module_context_feature.md
```

Small-core reduction:

```text
definition -> Context extension
assignment -> Binding or Store update, depending on target
parameter -> Binding in call context
block parameter -> Binding in block invocation context
import -> Binding of module/member value
```

### 3. Functions, Composition, And Function Algebra

Raw anchors:

- Landin, Strachey, McCarthy, Backus, Lisp `apply`,
- combinatory logic,
- function-level programming,
- Haskell composition, Kleisli composition, monads, applicatives, functors,
- pipelines in R, Julia, Rust-like `|>`,
- Mathematica `Apply`, `Map`, `Thread`, `Through`,
- R's "everything that happens is a function call",
- Python friction around lambda, decorators, methods, and pipeline style.

Design pressure:

Nomi needs a strong account of transformation before it adds richer surface
features. Function, call, pipeline, map, thread, method call, operator, and
composition should be related, not isolated.

Important distinctions:

- ordinary composition: `A -> B -> C`,
- Kleisli/effectful composition: `A -> M[B] -> M[C]`,
- applicative combination: combine independent contextual values,
- map/lift: transform inside a context,
- flatMap/bind: transform and flatten context,
- pipeline: value-first spelling of call sequence,
- method call: receiver-first spelling of call.

Nomi implication:

Do not import monad syntax. Understand the need: sequencing transformations
that carry context, failure, nondeterminism, logging, IO, or other effects.
Expose a readable direct style first; let deeper algebra guide reduction and
diagnostics.

Layer placement:

```text
L4 functions, calls, transformation
L7 collections, tables, repetition
L8 blocks, yield, time-shaped control
L9 effects, worlds, capabilities
```

Concrete future specs:

```text
functions_and_calls_feature.md
pipelines_and_composition_feature.md
function_lifting_and_contexts_feature.md
operator_and_infix_naming_feature.md
```

Small-core reduction:

```text
function definition -> Binding of Function value
call -> argument binding + body evaluation
pipeline -> ordered calls
method call -> call with receiver binding
lift/map -> call under a context policy
flatMap/bind -> call + context flattening rule
```

### 4. Blocks, Coroutines, Resumable Control, And Effects

Raw anchors:

- Ruby blocks, procs, lambdas, fibers,
- Python generators, `yield from`, context managers, `throw`, `close`,
- PEP 340/343 and retry-context-manager friction,
- delimited continuations,
- algebraic effects and handlers,
- resumable exceptions,
- R conditions, signals, restarts, `on.exit`,
- direct-style effects,
- Koka, Eff, OCaml effects,
- function color and async.

Design pressure:

There is a recurring need to abstract time-shaped behavior without collapsing
everything into callbacks, decorators, context managers, or monads.

The core issue is inversion of control:

- a function call is caller-controlled,
- a coroutine or block policy can return control multiple times,
- a handler can resume at the point of a signal,
- a context policy can wrap, retry, suppress, or translate failure.

Nomi implication:

Block calls and `yield` are a first candidate for user-facing control policy.
Algebraic effects and resumable exceptions should be studied as deeper models,
but the daily surface should stay direct and inspectable.

Layer placement:

```text
L8 blocks, yield, time-shaped control
L9 effects, worlds, capabilities
L10 traces and explanation
```

Concrete future specs:

```text
block_calls_feature.md
block_scope_and_control_flow_feature.md
signals_conditions_restarts_feature.md
effects_worlds_capabilities_feature.md
structured_concurrency_feature.md
```

Small-core reduction:

```text
block call -> Call + attached Block value
yield -> invoke attached Block at continuation point
signal/effect -> suspend with request value
handler -> policy that supplies response or resumes/aborts
context manager -> block policy with acquire/release protocol
```

### 5. Data Construction, Deconstruction, And Algebraic Modeling

Raw anchors:

- ADTs, product and sum types,
- GADTs,
- Scala case classes, companion objects, `apply`/`unapply`,
- Kotlin data classes and receiver functions,
- Pascal records, enumerations, subranges, sets,
- F-algebras, catamorphisms, anamorphisms,
- inductive and coinductive types,
- lenses as decomposition/recomposition.

Design pressure:

Programs need a unified account of construction and deconstruction.

The notes repeatedly point to a duality:

- construct data from parts,
- observe/deconstruct data into parts,
- match shapes,
- transform recursively,
- preserve invariants.

Nomi implication:

`data`, `shape`, constructor calls, pattern matching, and deconstruction should
be designed together. Scala's `apply/unapply` is useful evidence, but Nomi
should choose names and syntax that reveal construction/deconstruction directly
instead of relying on convention.

Layer placement:

```text
L5 data and shape
L6 patterns and choice
L10 examples and explanation
```

Concrete future specs:

```text
data_declarations_feature.md
shape_binding_feature.md
constructors_and_deconstructors_feature.md
patterns_and_match_feature.md
recursive_data_and_folds_feature.md
```

Small-core reduction:

```text
data declaration -> constructors + fields + pattern shape
shape declaration -> structural constraint + projection
deconstructor -> Pattern producer
fold/catamorphism -> structured recursion over data
lens -> focus + residue + reconstruction rule
```

### 6. Array, Table, Vector, And Listable Thinking

Raw anchors:

- APL, J, K, Q, Shakti,
- Backus function-level programming,
- Mathematica `Listable`, `Thread`, `MapThread`, `Apply`, `Through`,
- R vectors, recycling, attributes, data frames, tibbles, data masks,
- Python PEP 225 and element-wise operators,
- Pandas pipe/query friction,
- collection transforms and selectors.

Design pressure:

Scalar-first languages make whole-data programming feel bolted on. Array-first
languages are powerful but can become visually dense. Nomi should support
whole-collection thought without making glyph-density the default style.

Important distinctions:

- map one function over one collection,
- thread a function over several aligned collections,
- lift scalar operations over context,
- select/project by name or position,
- preserve shape/rank metadata,
- reduce/fold/accumulate,
- query table-shaped data.

Nomi implication:

Collection behavior should be designed as a layer over functions, calls,
binding, and shape. Do not add ad hoc list magic one operation at a time.

Layer placement:

```text
L4 functions and calls
L5 data and shape
L7 collections, tables, repetition
```

Concrete future specs:

```text
collection_transforms_feature.md
listable_and_threaded_calls_feature.md
tables_and_queries_feature.md
rank_and_shape_feature.md
selectors_and_slicing_feature.md
```

Small-core reduction:

```text
listable call -> lift scalar Function over Collection context
threaded call -> aligned element bindings + repeated Call
table query -> shape-bound row bindings + collection transform
selector -> pattern/projection over structured Value
```

### 7. Quotation, Non-Standard Evaluation, And Contextual Names

Raw anchors:

- Lisp S-expressions and M-expressions,
- Lisp `quote`, `eval`, `apply`,
- Mathematica expression heads and parts,
- R `quote`, `substitute`, quosures, data masks, tidy evaluation,
- Julia macros, quote/unquote/splice,
- Python string-based query workarounds,
- symbolic names for plotting, formulas, and data analysis.

Design pressure:

Users often need to refer to code, names, columns, formulas, or expressions as
values. Existing languages either make this too magical or too stringly.

Nomi implication:

Quotation needs a first-class, explicit model:

- syntax values know source spans,
- quoted expressions can carry environment when needed,
- unquote/splice should be explicit,
- data masks or contextual name resolution must be scoped,
- expansion must be inspectable.

Layer placement:

```text
L0 source and spans
L2 bindings and contexts
L10 traces and explanation
L11 quote, rewrite, notation
```

Concrete future specs:

```text
quote_and_syntax_values_feature.md
quasiquote_unquote_feature.md
contextual_name_resolution_feature.md
data_masks_and_formulas_feature.md
scoped_notation_feature.md
```

Small-core reduction:

```text
quote -> SyntaxValue + Span
quosure -> SyntaxValue + Context
unquote -> explicit evaluation inside quoted syntax
data mask -> scoped Context layered before lexical Context
macro/notation -> SyntaxValue -> SyntaxValue transform with expansion trace
```

### 8. Logic, Modal Reasoning, And Program Judgement

Raw anchors:

- Boole's laws of thought,
- Tarski object/meta-language,
- modal logic and Kripke semantics,
- dynamic logic,
- Hoare triples and Dijkstra weakest preconditions,
- resolution theorem proving,
- description logic,
- bounded rationality and formalism as occasional validation.

Design pressure:

Nomi should not force users to program in formal logic. But the language should
be designed so that formal reasoning can attach where it helps.

Useful first-principles distinction:

- propositional truth: isolated truth at a point,
- modal truth: truth across reachable states/worlds,
- dynamic logic: truth after program execution,
- Hoare logic: pre/post judgement around commands,
- constraints: local judgement at a binding boundary.

Nomi implication:

Start with executable constraints, examples, and traces. Later, allow stronger
reasoning over worlds, effects, and state transitions. Formalism is a tool for
resolving deep ambiguity, not a burden on daily use.

Layer placement:

```text
L3 constraints and judgement
L9 effects/worlds/capabilities
L10 examples/traces/explanation
L11 symbolic reasoning
```

Concrete future specs:

```text
examples_traces_explanation_feature.md
state_transition_judgement_feature.md
modal_worlds_and_reachability_feature.md
```

Small-core reduction:

```text
constraint -> local judgement
example -> executable judgement over call/result
trace -> observed transition sequence
world -> point of evaluation plus reachable alternatives
proof/check -> optional judgement over traces or symbolic forms
```

### 9. Historical And Human-Centered Language Design

Raw anchors:

- Boole, Leibniz, Turing, Church, Godel, Shannon,
- Babbage and Ada,
- Dijkstra, Naur, Landin, Strachey, McCarthy,
- ALGOL 60/68, Pascal, Modula, Oberon,
- Tennent, Reynolds, Hoare, Scott, Plotkin,
- Gabriel, Tomas Petricek, Jonathan Edwards, Subtext,
- Python, Ruby, R, Scala, Kotlin, Mathematica.

Design pressure:

Language design is a human activity. Formal systems matter, but natural
language, documentation, notation, examples, and the programmer's memory matter
too.

The notes point to a productive tension:

- ALGOL-like discipline and reports,
- Lisp-like minimalism and symbolic power,
- Python/Ruby/R pragmatism,
- Mathematica's expression uniformity,
- Haskell/ML's algebraic clarity,
- Dijkstra/Tennent-style semantic principles,
- AI-assisted exploration and critique.

Nomi implication:

Use formal tools when they clarify. Avoid making users carry formal machinery
for routine programming. Preserve the ability to explain every layer in natural
language.

Layer placement:

```text
all layers, especially documentation and diagnostics
```

Concrete future specs:

```text
language_report_style_guide.md
design_review_process.md
diagnostic_language_guidelines.md
```

## Cross-Cutting Theses To Carry Forward

### Thesis 1: Hierarchy Is The Main Tool Against Complexity

Strachey-style hierarchical construction and the first-principles ladder point
in the same direction. Nomi should let programmers build bigger concepts from
smaller ones, then peel the layers back when something fails.

Design consequence:

Every feature spec should include a reduction story.

### Thesis 2: Binding And Context Are More Fundamental Than Syntax

Many scattered notes about parameters, assignment, environments, modules,
R data masks, Scala implicits, `with`, and non-standard evaluation are really
about one thing:

> In which context is this name resolved, and what does binding it mean?

Design consequence:

Bindings, scope, context stacks, and source spans should be implemented before
fancier syntax spreads.

### Thesis 3: Rewriting Is Powerful Only Behind Explicit Boundaries

Term rewriting, Mathematica, Lisp, R quasiquotation, Julia macros, and
e-graphs all point to symbolic transformation. They also warn against hidden
magic.

Design consequence:

`quote`, `rewrite`, `use`, and expansion trace are required boundaries.

### Thesis 4: Effects Need Direct Style And Explanation

Monads, applicatives, algebraic effects, continuations, exceptions, context
managers, and R conditions are different answers to sequencing contextual
computation.

Design consequence:

Nomi should first offer readable direct-style block/effect constructs, while
keeping a deeper algebraic interpretation available for design and diagnostics.

### Thesis 5: Whole-Data Thinking Must Be Designed, Not Patched On

APL/J/K/Q, R, Mathematica, Pandas, and Python's rejected element-wise operator
ideas show that scalar-first design creates friction.

Design consequence:

Listable/threaded calls, collection transforms, rank/shape, and table queries
should be one layer over functions and binding.

### Thesis 6: Explanation Is A Language Feature

The notes repeatedly return to trace, diagnostics, examples, proof, and the
difficulty of reasoning about control flow. Explanation cannot wait until
tooling.

Design consequence:

Every semantic event should eventually be traceable:

```text
bind
judge
call
match
yield
effect
rewrite
example-check
```

## Mapping Notes To The Hierarchical Plan

| Layer | Raw-note themes to digest | Next design artifact |
| --- | --- | --- |
| L0 source/context/spans | Tarski object/meta-language, R srcref, source refs, diagnostics, module/env friction | `source_context_spans_feature.md` |
| L1 values | Boole things/propositions, Lisp atoms/pairs, Mathematica atoms/heads, R vectors/scalars | `values_and_literals_feature.md` |
| L2 binding/scope | Tennent binding/store, ALGOL blocks, R env/data masks, Scala val/var, Pascal with | `bindings_and_scope_feature.md` |
| L3 constraints/judgement | refinement types, description logic, modal truth, BindingError, examples/tests | `constraints_and_diagnostics_feature.md` |
| L4 functions/calls | Landin/Strachey, Lisp apply, Backus, pipelines, Kleisli, function algebra | `functions_and_calls_feature.md` |
| L5 data/shape | ADTs, GADTs, Scala apply/unapply, Pascal records/subranges, shape validation | `data_declarations_feature.md` |
| L6 patterns/choice | unapply, pattern matching, unification, conditionals, dynamic logic | `patterns_and_match_feature.md` |
| L7 collections/tables | APL/J/K/Q, R vectors/dataframes, Mathematica Listable/Thread, Pandas pipe/query | `collection_transforms_feature.md` |
| L8 blocks/yield | Ruby blocks, Python generators/context managers, coroutines, delimited continuations | `block_scope_and_control_flow_feature.md` |
| L9 effects/worlds | algebraic effects, monads, R conditions/restarts, capabilities, modal worlds | `effects_worlds_capabilities_feature.md` |
| L10 examples/traces | Boole judgement, examples as semantics, tracing, diagnostics, Hoare/Dijkstra | `examples_traces_explanation_feature.md` |
| L11 quote/rewrite | term rewriting, Lisp/R/Julia/Mathematica quotation, e-graphs, macros | `quote_and_syntax_values_feature.md` |

## Candidate Near-Term Commit Series

The raw notes suggest this bottom-up sequence:

1. Source/context/spans: establish inspectable artifacts.
2. Values/literals: clarify atoms, collections, absence, identity, display.
3. Binding/environment/store: separate naming from mutation.
4. Constraints/diagnostics: unify type, predicate, and message judgement.
5. Functions/calls: make call semantics and argument binding central.
6. Data/shape: owned data versus external structure.
7. Patterns/match/unification boundary: choice and deconstruction.
8. Pipelines/function algebra: composition, lifting, threading.
9. Collections/tables/rank: whole-data transformation.
10. Blocks/control/effects: refine block calls, then conditions/effects.
11. Examples/traces/explanation: make behavior inspectable.
12. Quote/rewrite/notation: symbolic power after lower layers are stable.

This sequence differs slightly from the previous roadmap by splitting
function algebra and collection/rank work more explicitly.

## Immediate Implementation Implications

The notes point to several implementation tasks that should support the design
without overfitting to current syntax:

- introduce Nomi-owned IR nodes with source spans,
- separate `Context`, `Binding`, and future `Store` concepts,
- make assignment, parameters, imports, block parameters, and pattern captures
  use one binding path,
- replace bare constraint predicates with structured `Constraint` values,
- introduce trace records for semantic events before building advanced
  explanations,
- lower surface forms into a smaller evaluator core,
- treat Python AST as a bootstrap tool, not the long-term semantic model,
- document every semantic feature with reduction to the first-principles core.

## Research Notes That Need Focused Follow-Up

These raw clusters are rich enough to deserve dedicated notes later:

- R evaluation model: promises, quosures, data masks, replacement forms,
  vector semantics, conditions/restarts.
- Mathematica expression model: heads, parts, attributes, Listable, Thread,
  Apply, rewrite rules.
- Scala/Kotlin object/context model: `apply`, `unapply`, extension methods,
  givens/usings, receiver functions.
- ALGOL/Pascal/Tennent/Landin line: binding, correspondence, block structure,
  semantic principles.
- Category-theory line: functors, monads, adjunctions, F-algebras, lenses,
  Lawvere theories, but only where they clarify concrete language design.
- Logic/reasoning line: modal logic, dynamic logic, Hoare triples,
  description logic, resolution, unification.
- Array-language line: APL/J/K/Q/Shakti, rank, shape, function-level style.

## Guardrail Against Rabbit Holes

The notes contain many deep trails. A trail becomes useful for Nomi only when it
can answer this:

```text
What primitive programming act does this clarify,
what layer does it belong to,
and what implementable feature does it suggest?
```

If the answer is unclear, keep it as background inspiration. Do not promote it
to active design yet.

---

<a id="documentation-design-review-hierarchical-language-research-plan-md"></a>

# Source: `documentation/design_review/hierarchical_language_research_plan.md`

# Hierarchical Language Research Plan

> Status: active research and implementation roadmap.
>
> This document turns the first-principles model into a concrete design and
> implementation ladder. The rule is: primitive ideas first, progressively more
> sophisticated features later, and every higher layer must reduce back down to
> the smaller core beneath it.

## Purpose

Nomi should be researched and implemented as a hierarchy, not as a flat feature
wishlist.

Each layer should answer:

- what primitive cognitive act it supports,
- what semantic core it adds,
- which lower layers it depends on,
- which concrete syntax ideas are worth exploring,
- what variations and tradeoffs need study,
- what small prototype would prove the idea,
- how the layer reduces back to the core.

The shape is:

```text
L0  source, context, spans
L1  values
L2  bindings and scope
L3  constraints, judgement, diagnostics
L4  functions, calls, transformation
L5  data and shape
L6  patterns and choice
L7  collections, tables, repetition
L8  blocks, yield, time-shaped control
L9  effects, worlds, capabilities
L10 examples, traces, explanation
L11 quote, rewrite, notation
```

This is both a research ladder and an implementation ladder. A later feature
may be prototyped early, but its design is not complete until it reduces to the
layers below it.

## Research Method

The companion [Research Notes Synthesis](research_notes_synthesis.md) maps the
raw research anchors into this hierarchy. Use it as the intake layer before
promoting scattered notes into focused feature specs.

For each layer:

1. Start from the first-principles need.
2. Define the semantic role in Nomi's small core.
3. Study references from other languages only as possible answers.
4. Compare syntax variations.
5. Choose one preferred direction and name rejected alternatives.
6. Write a focused feature spec.
7. Add target examples, including not-yet-implemented syntax when useful.
8. Implement the smallest useful operational slice.
9. Add diagnostics and explanation hooks early.
10. Revisit the layer once higher layers stress it.

Every focused feature spec should include this header:

```text
First-principles act:
Core primitives:
Depends on:
Enables:
Reduction:
Open tradeoffs:
```

## L0: Source, Context, And Spans

First-principles act:

```text
make thought inspectable
```

Core primitives:

```text
Source
Span
Context
Module
Diagnostic
```

Why it comes first:

Before values or syntax become meaningful, the language needs a durable notion
of source location, lexical context, module boundary, and diagnostic attachment.
Without this, later explanation features become retrofits.

Concrete ideas:

- source spans attached to every parsed node,
- a module object as an executable namespace,
- a context stack for lexical scopes and dynamic policy scopes,
- comments and doc blocks that can attach to declarations,
- stable internal representation independent of Python AST where needed.

Variations to research:

- lower directly to Python AST versus introduce a Nomi IR first,
- keep indentation exactly Python-like versus define Nomi-specific layout rules,
- make comments inert text versus attach doc/comment values to syntax nodes,
- file-as-module versus explicit `module name:` declaration.

Reduction:

```text
source text -> parsed forms with spans -> Nomi IR -> evaluation in Context
```

Small prototype:

- parse a file into Nomi-owned nodes with spans,
- report a diagnostic with exact source location,
- preserve module-level bindings in a `Context`.

Focused spec to write:

```text
source_context_spans_feature.md
```

## L1: Values

First-principles act:

```text
Distinguish
```

Core primitives:

```text
Value
Identity
Equality
Display
```

Concrete ideas:

- literals: number, string, bool, none/absence,
- structured literal values: list, tuple, dict, set,
- value identity versus equality,
- display/repr rules for diagnostics,
- eventual exact numeric tower: int, float, decimal, rational, complex,
- symbolic values only behind explicit `quote`.

Variations to research:

- Python-compatible literals versus cleaned-up Nomi literal grammar,
- one absence value (`None`) versus option-style `Some/None`,
- decimal/rational exactness as syntax versus library values,
- mutable collections by default versus persistent values for selected data.

Reduction:

```text
literal syntax -> Value
collection literal -> Value containing Values
display -> Value rendered with context
```

Small prototype:

- define a Nomi `Value` protocol or IR-level value representation,
- keep Python-hosted values where useful but wrap diagnostics around them,
- add value display tests independent of Python's default `repr` where needed.

Focused spec to write:

```text
values_and_literals_feature.md
```

## L2: Bindings And Scope

First-principles act:

```text
Name
```

Core primitives:

```text
Binding
Context
Scope
Name
```

Concrete ideas:

- simple binding: `name = value`,
- lexical scope and shadowing,
- module scope,
- block-local names versus caller-visible names,
- destructuring as binding to a shape,
- imports as bindings,
- explicit constant/non-rebindable bindings,
- possible `let` or `scope` form for local contexts.

Variations to research:

- Python assignment semantics versus more explicit rebinding rules,
- block-created names escape versus stay local,
- `const name = value` versus `name const = value` versus binding policy,
- imports as ordinary bindings versus special module operation,
- dynamic binding as an advanced explicit feature.

Reduction:

```text
name = value -> bind name to Value in Context
parameter -> bind argument Value in call Context
import -> bind module/member Value in Context
destructuring -> pattern-shaped binding
```

Small prototype:

- write an explicit `BindingTarget` model for names and destructuring,
- make assignment and function parameters use the same binding path,
- add tests for shadowing, deletion, globals, nonlocals, and block scope.

Focused spec to write:

```text
bindings_and_scope_feature.md
```

## L3: Constraints, Judgement, And Diagnostics

First-principles act:

```text
Judge
Explain
```

Core primitives:

```text
Constraint
Judgement
Diagnostic
Trace
```

Concrete ideas:

- type/class constraints,
- predicate constraints,
- expression constraints in tentative binding context,
- human messages with `else`,
- structured `BindingError`,
- constraints on assignment, parameters, block parameters, patterns, and shape
  fields,
- examples/tests as later judgement forms.

Variations to research:

- constraints as runtime checks versus optional static analysis,
- accumulating constraints versus re-annotation replaces constraints,
- `x:int, x > 0` versus `x: int where x > 0`,
- failure raises immediately versus returns structured `Result`,
- message syntax: `else "..."` versus `because "..."`.

Reduction:

```text
constraint syntax -> Constraint value
constrained binding -> tentative Binding + Constraint checks + Diagnostic
```

Small prototype:

- replace bare predicates with `Constraint` objects,
- add `BindingError` with source span and failed constraint,
- route assignment and parameters through the same judgement path.

Focused spec already started:

```text
binding_constraints_feature.md
```

Next focused spec:

```text
constraints_and_diagnostics_feature.md
```

## L4: Functions, Calls, And Transformation

First-principles act:

```text
Transform
```

Core primitives:

```text
Function
Call
ArgumentMap
Return
```

Concrete ideas:

- named functions with `func`,
- arrow functions,
- expression-bodied and block-bodied functions,
- parameter binding through the shared binding engine,
- return constraints,
- final-expression return for expression-oriented blocks,
- pipelines and composition as call structure,
- partial application and placeholder `_` as later features.

Variations to research:

- `func f(...):` versus `f = func(...):`,
- arrow syntax `(x) => expr` versus `fn(x) -> expr`,
- final expression return everywhere versus only in selected forms,
- pipeline placeholder `_` required versus optional single-argument shorthand,
- composition operator `>>` versus named `compose`.

Reduction:

```text
func definition -> bind name to Function
arrow expression -> Function value
call -> evaluate callee + map arguments to parameter bindings + execute body
pipeline -> nested or sequenced calls
composition -> Function value that performs calls in order
```

Small prototype:

- make argument mapping produce binding operations,
- add a focused pipeline parser experiment,
- trace call and return values for diagnostics.

Focused specs to write:

```text
functions_and_calls_feature.md
pipelines_and_composition_feature.md
```

## L5: Data And Shape

First-principles act:

```text
Group
Judge
```

Core primitives:

```text
Data
Shape
Field
Constructor
```

Concrete ideas:

- `data` for owned program values,
- product data: `data User(id:UserId, email:str)`,
- sum data: variants such as `Ok(value)` and `Err(error)`,
- `shape` for external structural data,
- optional fields and defaulted fields,
- constructor constraints,
- shape-to-data transformation.

Variations to research:

- `data User(...)` single-line form versus block form,
- product-only first versus sum types from the beginning,
- structural shape versus nominal shape,
- optional marker `?` versus `Option[T]`,
- default values in shape declarations versus separate normalization step.

Reduction:

```text
data declaration -> constructors + field bindings + pattern shape
shape declaration -> named Constraint over external structure
field -> binding plus optional constraint/default
```

Small prototype:

- implement a minimal `data` declaration as constructor plus fields,
- implement `shape` over dictionaries,
- allow shape binding with structured diagnostics.

Focused specs to write:

```text
data_declarations_feature.md
shape_binding_feature.md
```

## L6: Patterns And Choice

First-principles act:

```text
Choose
Name
```

Core primitives:

```text
Pattern
Match
Guard
BindingTarget
```

Concrete ideas:

- destructuring assignment,
- `match` statements and expressions,
- pattern guards,
- constraint patterns,
- data variant patterns,
- shape patterns,
- or-patterns and wildcard patterns,
- exhaustiveness diagnostics later.

Variations to research:

- Python-like `match/case` versus expression-first `match value: ...`,
- constraint in pattern `age:(int, age >= 13)` versus guard `if age >= 13`,
- match failure as error versus non-match depending on context,
- structural matching before nominal matching versus nominal-first.

Reduction:

```text
pattern -> structural test + tentative bindings
case -> pattern + optional guard + body
destructuring assignment -> pattern binding that raises on failure
match expression -> ordered cases that produce a value
```

Small prototype:

- reuse `BindingTarget` for destructuring and match captures,
- define direct pattern-binding failure,
- add trace explaining why cases failed.

Focused spec to write:

```text
patterns_and_match_feature.md
```

## L7: Collections, Tables, And Repetition

First-principles act:

```text
Repeat And Accumulate
Transform
```

Core primitives:

```text
Collection
Iterator
Transform
Fold
Table
```

Concrete ideas:

- readable whole-collection transforms,
- `map`, `where`, `select`, `group`, `join`, `sort`, `fold`,
- comprehensions as syntax over transforms,
- table rows as shape-bound records,
- array rank and shape concepts inspired by APL,
- streaming transforms and lazy collections.

Variations to research:

- method style `users.where(...)` versus pipeline `users |> where(...)`,
- block transforms `where(users) -> user: ...` versus arrow predicates,
- SQL-like query block versus function pipeline,
- APL-like rank operators versus named rank-aware functions,
- eager versus lazy default.

Reduction:

```text
map/filter/query -> repeated calls with binding of each element
table row -> shape-bound value
group/fold -> accumulation over collection values
rank operation -> transform parameterized by shape metadata
```

Small prototype:

- implement a tiny transform library using existing functions,
- add pipeline syntax only after call semantics are stable,
- add trace of collection stages.

Focused specs to write:

```text
collection_transforms_feature.md
tables_and_queries_feature.md
rank_and_shape_feature.md
```

## L8: Blocks, Yield, And Time-Shaped Control

First-principles act:

```text
Sequence In Time
Touch The World
Explain
```

Core primitives:

```text
Block
Yield
Policy
ContinuationPoint
```

Concrete ideas:

- block calls,
- yielded block parameters,
- retry, timeout, using, transaction, trace, test,
- block result semantics,
- exception propagation through yield,
- block-local versus caller-visible scope,
- structured concurrency later.

Variations to research:

- block call syntax `call(args):` versus `with call(args):`,
- yielded parameter arrow `-> x` versus block parameter inside body,
- block result owned by callee versus last expression of block,
- full continuations versus practical resumable yield,
- async blocks integrated now versus later.

Reduction:

```text
block call -> call + attached Block value
yield -> invoke attached Block at continuation point
policy -> function that controls when/how block is invoked
```

Small prototype:

- use `block_calls_feature.md`,
- replace ad hoc block keyword with explicit block representation,
- route block parameters through binding engine,
- add yield diagnostics.

Focused spec already started:

```text
block_calls_feature.md
```

Next focused specs:

```text
block_scope_and_control_flow_feature.md
structured_concurrency_feature.md
```

## L9: Effects, Worlds, And Capabilities

First-principles act:

```text
Touch The World
Judge
Explain
```

Core primitives:

```text
Effect
World
Capability
Policy
Audit
```

Concrete ideas:

- capability values for filesystem, network, time, randomness, subprocess,
  environment, database,
- `world(...)` scopes,
- transactions as effect policies,
- simulation and replay worlds,
- effect traces,
- explicit permission boundaries.

Variations to research:

- Haskell-like effect types versus runtime capability scopes,
- ambient standard library access versus explicit imported capabilities,
- `with world(...) as w:` versus `world(...) -> w:`,
- effect tracking as diagnostics only versus enforced restrictions,
- single world object versus separate capability objects.

Reduction:

```text
capability -> Value granting operations
world scope -> block policy that binds capabilities
effectful operation -> call through capability value + trace event
transaction -> block policy over effect log/commit/rollback
```

Small prototype:

- introduce a simple `World` object for file/time/network stubs,
- run examples against fake worlds,
- record effect trace events.

Focused spec to write:

```text
effects_worlds_capabilities_feature.md
```

## L10: Examples, Traces, And Explanation

First-principles act:

```text
Explain
Judge
```

Core primitives:

```text
Example
Trace
Diagnostic
Expectation
```

Concrete ideas:

- `examples:` blocks inside functions and declarations,
- examples as tests and documentation,
- `explain(value_or_expr)`,
- trace for binding, calls, patterns, blocks, effects, pipelines, rewrites,
- counterexamples from failed constraints or properties,
- diagnostics written in feature vocabulary.

Variations to research:

- examples embedded in functions versus separate declarations,
- examples as compile-time tests versus runtime metadata,
- trace always available versus opt-in tracing,
- proof/property syntax now versus examples first,
- human messages attached to constraints versus generated explanation.

Reduction:

```text
example -> executable judgement over calls/values
trace -> structured record of core semantic events
diagnostic -> rendered explanation from trace + span + judgement
```

Small prototype:

- add trace records for binding constraint failures,
- add examples as ordinary test data attached to a function object,
- render one high-quality diagnostic.

Focused spec to write:

```text
examples_traces_explanation_feature.md
```

## L11: Quote, Rewrite, And Notation

First-principles act:

```text
Reflect And Rewrite
Transform
```

Core primitives:

```text
Quote
SyntaxValue
RewriteRule
Expansion
UseScope
```

Concrete ideas:

- `quote:` block for code-shaped values,
- rewrite rules over quoted expressions,
- explicit evaluation boundary,
- scoped macros or transforms,
- `use` scopes for domain notation,
- inspectable expansion.

Variations to research:

- `quote:` blocks versus prefix quote syntax,
- Mathematica-like `/.` versus named `rewrite(expr, rule)`,
- rewrite rules as values versus declaration forms,
- macros as compile-time functions versus runtime syntax transforms,
- notation definitions allowed globally versus only inside `use` scopes.

Reduction:

```text
quote -> SyntaxValue
rewrite rule -> Pattern over SyntaxValue + replacement SyntaxValue
macro/notation -> scoped rewrite over syntax before evaluation
expansion -> traceable transformation from syntax to lower syntax
```

Small prototype:

- define a tiny Nomi expression AST,
- quote a subset of expressions into syntax values,
- apply one rewrite rule with trace output.

Focused specs to write:

```text
quote_and_syntax_values_feature.md
rewrite_rules_feature.md
scoped_notation_feature.md
```


## First Implementation Spine

The first operational implementation path should be:

```text
Nomi IR with spans
  -> Value and Context model
  -> BindingTarget and lexical scope
  -> Constraint and BindingError
  -> Function call argument binding
  -> Data/Shape declarations
  -> Pattern binding and match
  -> Pipeline lowering to calls
  -> Explicit Block representation and yield
  -> Trace records and diagnostics
```

This path deliberately postpones advanced symbolic rewrite and capabilities
until the lower semantic events are traceable.

## Research Guardrails

- Do not add syntax before naming the primitive cognitive act.
- Do not add a feature that bypasses the lower layers it should reduce to.
- Do not copy a language's surface spelling until the semantic role is clear.
- Do not treat diagnostics as a later UI concern.
- Do not let current implementation convenience decide the long-term model.
- Do not flatten the roadmap into independent features; preserve dependency.

---

# Design-Adjacent Notes

---

<a id="documentation-delta-on-python-md"></a>

# Source: `documentation/delta_on_python.md`

# Function

## Defining a Function

Function **definition** and **application** are the most fundamental constructs of the language — most other features can be expressed in terms of these, either directly or conceptually.

In Python, there are two primary ways to define functions: using `def` and `lambda`.

### Renaming `def` to `func`

In Nomi, `def` has been renamed to **`func`** for greater semantic clarity.  
The word “define” (`def`) is too generic — it could mean defining **any** value (an integer, a class, etc.).  
While Python treats functions as *first-class values* (they can be passed around and returned), their definition syntax is syntactically coupled with a binding statement.

Thus, `func` is a more explicit and focused keyword for defining functions as values.

However, the **binding statement** and **block structure** of function definition are retained.  
In other words, no separate form like `my_func = func(...)` is introduced for named function declarations.  
The intention is to preserve Python’s familiar **declarative style**, while giving it clearer semantics through `func`.

For the most common use cases where functions are treated as *values* — especially for concise, inline, or higher-order uses — Nomi introduces a simplified **arrow-based function literal syntax** (described below).  
This serves the role of Python’s `lambda`, but with fewer arbitrary restrictions and clearer alignment with function theory.

Another key reason to retain the `func` block structure is to **respect the existing decorator model**.  
Decorators in Python operate at the level of *function definitions* rather than assignments.  
Splitting them into `name = func(...)` would complicate decorator semantics and break the familiar annotation flow:

```python
@decorator
func greet(name):
    print("Hello", name)
```

Therefore, Nomi enforces the *block-style* structure for nontrivial functions — those that require decorators, annotations, or multiple statements — while providing the arrow syntax for simple, expression-oriented functions.

### Rethinking `lambda`

The word *lambda* originates from **lambda calculus**, where Alonzo Church and Haskell Curry made foundational contributions.  
In that formalism, *all* functions are “lambdas” — that is, function values of type `λ`. In the same way that `3` is an `int`, every function is a `λ`.  

However, in Python, the name `lambda` has gradually acquired a narrower, informal association with “anonymous functions,” which is a misleading simplification of its theoretical roots.

That said, there are concrete syntactic and semantic differences between Python’s `def` and `lambda` beyond naming and anonymity.

### Differences in Python

* **Lambda:**
  * Parameters **cannot** be enclosed in parentheses.
  * Because of the above, **type hints** are not allowed (since `:` is already used for expression delimiting).
  * It can contain **only a single expression**, and **no explicit `return`** statement.
  * **Tuples** must be explicitly wrapped due to the “single expression” restriction.
    * For example, `return x, y` must be written as `=> (x, y)`, not `=> x, y` (the latter would evaluate `x` and then `y` separately).

Many of these restrictions stem from Python’s early **L1(1)** grammar (Left-to-right, leftmost derivation parsing with one-token lookahead).  
Python has since moved to **PEG parsing** (Parsing Expression Grammar), which removes many of those historical constraints.  
Guido van Rossum has written about this evolution [on Medium](https://medium.com/@gvanrossum_83706/peg-parsers-7ed72462f97c).

### Nomi’s Approach

In Nomi, the gap between named and literal functions is **further minimized**.  
Only the last two divergences (explicit `return` and multiple expressions) remain for simplicity and readability.

Nomi introduces a concise **arrow syntax** for function literals:

```python
(x, y) => x + y
(x:int) => x^2      # with type annotation
() => print("no-arg function")
(x, y) => (x^2, y^2)
```


# Binding

> Current design note: the active, implementation-oriented version of this idea
> now lives in
> [Binding Constraints Feature](design_review/binding_constraints_feature.md).

Binding is a fundamental concept as well. This is deeply connected to functions - function call is literally the evaluation of the function body with the arguments bound to the parameter on top of existing binding at the time of function definition (lexical closure -only this supported here for now) or the execution time (dynamic closure). It occurs in many contexts, most visibly in **assignment**, but also in:

* Function call arguments-to-parameter mapping  
* Iteration variables in `for` loops  
* `as` constructs in context managers (`with cm as var`)  
* Exception handling (`except Exception as e`)  
* Pattern matching  
* Packing/unpacking  
* Imports

Python currently supports **type annotations (hints)**, but they are **not enforced** by the interpreter. Some libraries, such as `dataclass` or `pydantic`, rely on them for runtime validation. *(Note: `pydantic` behavior may break under the changes proposed here.)*

---

## Binding Validation in Nomi

Nomi supports **enforced binding validation**. Each variable can optionally be annotated with:

* **Type/Class** (e.g., `int`)  
* **Predicate function** (e.g., `is_positive`)  
* **Expression** that can be interpreted as a predicate in the context of the variable (e.g., `a: a > 20 = 22`)

If any annotation fails its check, a **`TypeError`** is raised.

```python
is_pos = (a) => a > 0
a = 1
a:int = 1
a:int, is_positive, a > 20 = 19  # raises TypeError

b: b>20
b = 19 # fails

b:int = 10 # any new constraints the entire constraints
```

Note: When a variable is rebound with new annotations, **all previous annotations are reset**.

---

## Argument-to-Parameter Mapping

The same binding validation extends to **function calls**.  

To distinguish between multiple parameters and multiple constraints on a single parameter, **constraints must be wrapped in parentheses**:

```python
func f(a:int, b:(int, b > 20)):
    pass

f(x, y)  # Enforces corresponding constraints on each parameter
```

**Important notes:**

* Argument-to-parameter mapping is similar to multiple assignment (`a, b = x, y`) but not identical.  
  * Example: `x = 1, 2` is valid assignment, but for `func f(x)`, `f(1, 2)` is invalid.  
* Python’s rules for argument mapping (positional/keyword, defaults, varargs) carry over.  
* **Constraints are enforced after arguments are mapped to parameters**.

## TODO
* support other constraints such as `const`
  * `a:int, const = 4 `
* add the ability to make the function parameter bind dynamically when selectively request
  * something like -  `f(a:int,b:(int, dynamic), c, ...)`


There are other semantic aspect relevant to parameters but not in bare assignment such as pos-only, keyword-only, mandatory or optional etc; currently Python support them with special marker such as "/" or "*". Additional we may also have lexical(default) or dynamic etc. 


> Note: The harmonization between `def`/`lambda` discussed earlier could also apply here in between assignment and arg-param mapping, but this is more subtle and requires further exploration.


# Coroutine Blocks and Unified Control

Coroutines represent a powerful and deeply studied generalization of control flow — the ability to **pause and resume execution** at arbitrary points, rather than always running a function from start to finish.  
Python’s **generators** (`yield`) are one practical specialization of this idea, trading full generality for usability and clarity.

The exploration of **yield-to-block** structures aims to extend this idea beyond iteration — toward a unified, composable foundation for **control constructs**, including retries, context management, and structured concurrency.  
This bridges the gap between **statements and expressions**, **functions and blocks**, and even between **decorators and context managers**.

A concise illustration of how such a construct might work:

```python
func retry(max_times, exc=None):
    if exc is None:
        exc = Exception

    for i in range(max_times):
        try:
            yield  # Execute the block here
            print(f'successful after {i+1} attempts')
            return
        except exc as e:
            print(f'failed: attempt={i+1}, error: {e}')

    print(f'All {max_times} attempts failed!')


retry(3):
    1 / 0
```

Here, the block following retry(3): is implicitly passed to the function and executed at the yield point — allowing the retry logic to surround it seamlessly.
Such a mechanism generalizes Python’s existing context manager model while remaining minimal and explicit.
> *This concept builds on coroutine fundamentals and extends them toward systematic language design.*  
> *See the section on [Ruby-like Blocks](yield_to_block.md) for the historical background and rationale.*  
> *As discussed there, the above construct cannot be implemented naturally in current Python — as noted in this [Stack Overflow question](https://stackoverflow.com/questions/16919570/encapsulating-retries-into-with-block) — a limitation that appears to be intentional by design.*

Blocks can take parameters as well:
```python
func each(items):
    for item in items:
        yield item

# blocks that receives parameters
each([1,2,3]) -> item: # later with class handling, this would typically be [1,2,4].each() -> item: ...
    print(f'each {item}')
```

---

<a id="documentation-yield-to-block-md"></a>

# Source: `documentation/yield_to_block.md`

# Ruby-like Blocks in Python: Historical Context and Design Rationale

> Current design note: block parameters should eventually reuse the same binding
> engine as assignment and function parameters. See
> [Binding Constraints Feature](design_review/binding_constraints_feature.md).
> The broader forward-looking block design is
> [Block Calls As Control Values](design_review/block_calls_feature.md).

The idea of generalizing Python’s context managers to support **Ruby-style implicit block yielding** has appeared repeatedly throughout Python’s design history. These constructs offer elegant generalization and can subsume many specialized control-flow patterns. However, the Python community has traditionally been cautious: such features risk obscuring intent when used in place of explicit **control-flow constructs like loops or exception handlers**.

 > block will be almost like an anonymous function that is passed to generator (to be executed at the yield point) with a notable difference: this block is executed within's the caller environment, not a new function environment.
## Limitations of Current Context Managers

As noted in this [Stack Overflow discussion](https://stackoverflow.com/questions/16919570/encapsulating-retries-into-with-block), patterns such as a `retry` context manager are difficult to express naturally in Python. This difficulty is not accidental—it reflects a deliberate design philosophy that prioritizes **explicit control flow** over implicit abstractions.

The standard library’s [`contextlib`](https://docs.python.org/3/library/contextlib.html) provides narrowly scoped tools to handle specific cases. This indicates a conscious decision: **complex control constructs should evolve through libraries, not the language core**.

## Historical Proposals and Their Outcomes

**Accepted Proposal**
- [PEP 343 – The “with” Statement](https://peps.python.org/pep-0343/): Introduced the modern context manager protocol.

**Rejected or Subsumed Proposals**
- [PEP 310 – Reliable Acquisition/Release Pairs](https://peps.python.org/pep-0310/)
- [PEP 340 – Anonymous Block Statements](https://peps.python.org/pep-0340/)

**Contemporary Discussions and Unresolved Challenges**  
The desire for block scoping hasn't disappeared. A recent [discussion](https://discuss.python.org/t/simplistic-block-scope-a-syntactic-sugar/82952/7) on the Python Discourse forum from 2024 focuses around a "simplistic block scope" as syntactic sugar.  
These proposals explored more general block semantics but were ultimately narrowed in scope to favor explicit, predictable behavior.

---

## Rationale for Revisiting Generalized Blocks

Despite past reservations, this exploration proceeds for several strategic reasons.

### 1. Systematic Design

The language aspires to an **expression-oriented model** that blurs, where appropriate, the line between statements and expressions.  
Where these must coexist, integration should be **natural, minimal, and composable**.

By doing so, we can gradually evolve constructs that **bridge the gap between decorators and context managers**—and more broadly, between **function invocation and block execution**—to achieve a unified control abstraction framework.

Coroutines are deep and powerful constructs with a long history of research.  
The *yield-to-block* mechanism, or Python’s generator model, represents a **specialized trade-off**—favoring practical usability over full generality.  
A highly recommended starting point for understanding coroutine design philosophy is [Simon Tatham’s write-up](https://www.chiark.greenend.org.uk/~sgtatham/quasiblog/coroutines-philosophy/).

The primary motivation for proceeding with a *yield-to-block* structure, despite known reservations in the Python community (many of which are well-founded), is to **lay the groundwork for a more general coroutine infrastructure**—from which more powerful and elegant control constructs could eventually emerge.

At the very least, a coroutine introduces a new primitive:  
the ability to **pause execution at any point and resume later**—a fundamental shift from the traditional stateless “start-to-finish” function model.  
This concept also forms a **bridge between statements and expressions**, opening paths to new compositional abstractions.

Coroutines have already proven useful as the foundation for **lazy iterators**, **context managers** (e.g., `contextlib.contextmanager`), and **test frameworks** like `pytest`.  
Much remains to be explored in how such mechanisms can unify control-flow design more systematically.

### 2. Minimalist Primitives

Functions inherently encapsulate **execution blocks**, **parameterization**, and **scoping**.  
By introducing intermediate abstractions that capture only some of these features, we can:

- Avoid unnecessary function definitions used solely to localize scope or control nesting  
- Reduce boilerplate from defining and immediately invoking small helper functions  
- Preserve a small, orthogonal set of core primitives with broad compositional power

### 3. Composition Over Restriction

Generalized block-yielding constructs promote **composition over specialization**.  
Rather than introducing bespoke syntax for every control-flow need, they provide flexible primitives that can be composed into richer abstractions when necessary.

---

This implementation is exploratory.  
The goal is to test whether the **expressiveness–explicitness balance** can be improved without compromising clarity—acknowledging that future refinement may still be required.


## Current Limitations

* Full expression level yield is not currently supported. For instance, `v=(yield 2) + (yield 3)` does not work - this will not generate [1,2]. This is due to the usage of ast-walking with adhoc pause-resume interpreter. This technical limitation well be eventually be overcome so that yield can occur anywhere in the expression; review the [python doc](https://docs.python.org/3/reference/expressions.html#yieldexpr) carefully. This may require significant re-write of interpreter to by either fully continuation-passing-style or a fully linearized interpreter, i.e. a bytecode interpreter like the CPython's VM.
    * Towards supporting expression-level yield at any place, specific form of `lhs = yield x` is now supported. This enables most of the general functionalities of bi-directional co-routine communication (though the complex expression has to be manually reduced into this form)
    * similar approach will be taken to make function-call resumable
    * later, all expressions will be reduced to call

* General parameter/arguments mapping as in function is not how block receive the yielded values (now 1:1 mapping is done with almost like parallel assignment,  without support for default values, constraints etc.). While we may still keep some restriction like in Python's def vs lambda (can't take type annotation), the gap will be minimized.


* In Python, `finally` in `try` is triggered when the generator is garbage-collected as well. Nomi's evolution has not yet reached that fine level of scrutiny; this will be addressed when low-level meta-implementation details are considered.
    * As reference on this [SO question](https://stackoverflow.com/questions/56062909/try-finally-in-python-3-generator), due to the above, we get different behavior on using `next(gen())` vs `x=gen(); next(x)` in this block.

        ```python
        def gen():
            try:
                while True:
                    yield 1
            finally:
                print("stop")

        next(gen()) # prints stop; GC happens immediately after the call
        # vs x = gen(); next(g) # prints stop after the last stmt (after GC)
        print("after generator") # to easily see the GC point
        ```

---

<a id="documentation-positioning-ambition-risk-md"></a>

# Source: `documentation/positioning_ambition_risk.md`

# Positioning within Ambition and Risk

*This document situates Nomi as a historically grounded, philosophically motivated, and technically risky experiment. It neither retreats into apology nor advances a utopian narrative. Programming languages—rare among human artifacts—do not merely expand what we can compute; they reshape how we think about computation itself.*

---

## Deep Lineage — From Universal Symbolism to Computation

The ambition behind Nomi predates machines.

In the 17th century, **Gottfried Wilhelm Leibniz** envisioned a *characteristica universalis*: a universal symbolic language capable of expressing all reasoning, paired with a *calculus ratiocinator*: a mechanical method for resolving disputes by calculation rather than rhetoric. This was a civilizational wager—an attempt to relocate truth from authority to symbol.

After more than a century, **George Boole** abstracted logic algebraically, laying the foundation for symbolic manipulation that underpins computation today.

The 20th century clarified both the power and limits of formal reasoning. **Gödel (1931)** proved that expressive formal systems contain true but unprovable statements. **Church (1936)** defined computation via lambda calculus, while **Turing (1936)** formalized it mechanically via machines, states, and tape. These results show that vast regions of reasoning are symbolically tractable yet inherently incomplete.

Every programming language since is, implicitly or explicitly, an answer to Leibniz’s unfinished question:  
*what symbols should executable thought be written in, once its limits are known?*

---

## Programming Languages as Intellectual Instruments

Some figures shaped the very notion of a programming language:

- **John McCarthy (LISP)**: symbolic computation, recursion, homoiconicity, macros, and meta-circular evaluation.  
- **Edsger W. Dijkstra**: programming as a discipline of thought; tools shape cognition.  
- **Alan J. Perlis**: “a language is valuable only if it changes how one thinks about programming.”  
- **Milner, Wadler, Peyton Jones (ML/Haskell)**: type inference, parametric polymorphism, algebraic data types, effect systems.  
- **Gosling (Java), van Rossum (Python), Eich (JavaScript)**: languages encode social, pedagogical, and institutional structures.

Nomi consciously positions itself within this intellectual lineage.

---

## Language Evolution, Constraints, and Failure

Semantic elegance alone does not ensure survival. Systems like **ALGOL 68**, **PL/I**, and **Lisp Machines** achieved formal rigor yet faltered due to tooling, pedagogy, or platform economics. Intellectual contributions often outlive their host ecosystems.

Adoption depends on **structural forces**: education, corporate standards, platform lock-in, vendor ecosystems, and network effects. Java, Python, and JavaScript succeeded structurally, not merely semantically. Once a language captures a bottleneck, incidental design choices harden into enduring constraints.

Languages balance a persistent tension: **higher abstraction increases expressive power but reduces local transparency**. ML/Haskell encode complexity in type structure; Python shifts it to runtime dynamism with readable syntax. Nomi designs explicitly around this tension.

**Failed platforms often propagate ideas**:

- ALGOL → block structure, lexical scoping, formal specification  
- LISP → macros, symbolic computation, meta-circular evaluation  
- ML/Haskell → type inference, algebraic data types  
- Smalltalk → late binding, message-passing, image-based IDEs  

Modern languages now mediate **human–machine–AI interaction**: LLM-assisted synthesis, symbolic solvers, autonomous refactoring, and model–program collaboration. Language increasingly acts as a **protocol between cognitive agents**, a frontier that Nomi is explicitly designed to engage.

From these histories, several operational constraints emerge:

- Tooling predicts adoption more than semantic coherence.  
- Pedagogy compounds faster than theoretical elegance.  
- Interoperability outlives purity.  
- Documentation forms part of the semantic substrate.  
- Institutional trust outweighs sophistication.

**Systemic failure is expected**; conceptual propagation is the critical metric. Even partial adoption can influence future designs and propagate enduring ideas.

---

## Rhetoric vs. Implementation, and Synthesis

I am aware of the wide gulf between rhetorical ambition and ad-hoc implementation. Python is the conceptual baseline, but nearly everything beyond its AST interface has been built from scratch: Lark for parsing, a custom evaluator, and a brittle-but-tested resumable control layer. Python’s own `ast.parse` and `exec` are used only for bootstrap testing and incremental change.

The path forward combines historical and modern mechanisms:

* An informal design specification akin to the ALGOL 60 Report.  
* Structured change proposals similar to Python PEPs.  
* Formal reasoning applied sparingly to resolve critical issues, not to preemptively formalize the entire system.

This process synthesizes lessons from historical languages, connecting them to the aspirations of Leibniz, Boole, and modern programming evolution.

---

## Working Posture and Long-Term Motivation
Judging programming languages is exceptionally difficult and long-term. Debate is polarized—academic vs. industrial, purist vs. pragmatist, theory vs. practice. Yet nearly every corner of this landscape contributes lasting value. What appears as lack of rigor may reflect adaptation to constraints.

Progress emerges from perseverance, independent judgment, continuous feedback, and first-principle reasoning. I do not aim to produce world-changing theorems; my grounding is **practical experience** across startups, industry, and academia, combined with hands-on engagement. Curiosity and historical perspective pull toward deeper formal questions without losing concreteness.

Nomi is a living synthesis of:

* The systematic ambition of the ALGOL tradition  
* The hacker elasticity of Lisp  
* The pragmatic humility of Python  
* A long trail of personal mistakes and recoveries  

I am a pragmatist with a formalist conscience and industry scars.

Some inconsistencies are features, not bugs: tolerance for iterative refinement learned from real-world production systems. Many brilliant minds recoil from such messiness and go build cleaner systems elsewhere; both temperaments are necessary.

Most language projects fail. That reality grants permission, not despair. If Nomi leaves behind only a few ideas, tools, or contributors, it will have participated in the same quiet transmission mechanism that carried ALGOL’s scoping, Lisp’s macros, and ML’s type inference into the modern world.

Either way, this is work I can carry for life—refining it continuously, whenever a new historical thread, test case, or insight appears. Rebellion tempered by humility, or humility tempered by audacity.

---

<a id="documentation-notes-tractable-sophistication-md"></a>

# Source: `documentation/Notes/tractable_sophistication.md`

# Design Note: On Building and Understanding Sophistication

Programming is distinguished by its ability to construct highly sophisticated artifacts from seemingly simple elements. This capacity is not unique to programming; nature provides an existence proof in biological evolution, where a small set of mechanical processes—variation and selection—give rise to extraordinary complexity. The lesson here is not to imitate evolution literally, but to recognize that **simple generative rules can support rich, layered structure**.

What evolution lacks, however, is speed and introspection. It operates over immense time scales and offers little leverage for understanding or deliberately reshaping its outcomes. Programming can be seen as an attempt to preserve generativity while drastically compressing time and restoring agency. We seek systems that grow in capability, yet remain *understandable, adaptable, and trustworthy*.

This leads to a central design question:

> How can sophistication emerge without sacrificing intelligibility?

The answer cannot be minimalism alone, nor unchecked expressiveness. What is required is a language whose abstractions grow in layers—each enabling construction, while remaining open to inspection and revision.

---

## Languages as Structure, Not Artifacts

Following Peter Landin, we view a language not as a single fixed artifact but as a member of a **family of languages**. Each member is determined by:

* a set of *problem- or domain-oriented primitives*, and
* a general *compositional framework* that governs how those primitives combine.

The framework is stable; the primitives vary. Expressiveness emerges from their interaction rather than from an ever-expanding set of special cases. This perspective aligns with established ideas in language design—from calculi parameterized by constants, to embedded and domain-specific languages built atop a shared core.

To remain general, this design deliberately avoids committing to specific primitives. Instead, it assumes only that some domain supplies **values**.

---

## Values and Hierarchical Composition

Values form the first axis of construction. They are self-contained, composable, and amenable to equational reasoning. From values we obtain expressions; from expressions, functions. Functions may depend on other functions, yielding **hierarchy**.

Hierarchy is not a stylistic choice. It is the only known organizing principle that allows finite human agents to work with arbitrarily complex systems. Without hierarchy, complexity does not merely become inconvenient—it becomes intractable. Every successful large system, whether biological, social, or computational, relies on layered structure to localize reasoning and enable controlled growth.

Once higher-order functions are admitted, abstraction scales naturally. Functional programming demonstrates that such a system is *theoretically sufficient*: control flow, iteration, and even state can be expressed in terms of value transformation. This reducibility is important, as it provides a firm semantic foundation and connects directly to established formalisms such as the lambda calculus.

However, reducibility does not imply adequacy for human construction. Just as all control flow can be expressed using `goto`, yet structured loops and branches remain indispensable, we should expect—and explicitly allow—**structured abstractions** that encode recurring hierarchical patterns directly.

Accordingly, functional programming is treated here as a foundation rather than a ceiling: a semantic baseline that supports, but does not preclude, richer surface structure.

---

## Structured Values and Collections

Beyond individual values, programs require **structured values**: collections, aggregates, and groupings with internal organization. These are not merely containers. They introduce concepts such as ordering, multiplicity, naming, and invariants—each of which constrains composition and carries meaning.

This view aligns with ideas found across programming languages, from algebraic data types and records to relational models and constrained collections. Treating collections as values with internal laws strengthens reasoning, improves safety, and preserves clarity as systems scale.

---

## The Limits of Definition

There is, however, a boundary to value-oriented thinking. Some phenomena are easier to *perform* than to define. They unfold in time, depend on context, and matter primarily because of their effects on what follows.

Values answer the question *“what is this?”*
Programming also concerns *“what happens?”*

At this boundary, a purely definitional model becomes strained, even if it remains semantically expressive.

---

## Actions and Temporal Composition

To address this, the language introduces **actions**—processes that unfold over time and manifest as effects. Actions are not primarily characterized by the values they produce, but by how they influence subsequent behavior and observation.

Actions compose along dimensions that differ from value composition:

* sequence,
* conditional execution,
* parallel or concurrent execution,
* repetition and iteration,
* nesting into blocks.

Blocks play for actions a role analogous to functions for values, but the symmetry is intentionally imperfect. A function abstracts over inputs to produce a value; a block organizes activity over time. This distinction mirrors long-standing separations in programming language theory between expressions and statements, and is preserved rather than erased.

---

## Two Intertwined Domains

The language is organized around two complementary compositional domains:

* **Values**: timeless, referential, structured for definition and reasoning.
* **Actions**: temporal, effectful, structured for behavior and interaction.

Neither domain is reducible to the other at the level of human understanding, even if one may be reduced to the other for semantic analysis. The design goal is to make their boundary explicit, to control how they interact, and to prevent accidental complexity from leaking across it.

This position aligns with existing practice—seen in the distinction between expressions and statements, pure and impure code, declarative and imperative styles—while seeking a more principled and inspectable integration.

---

## Guiding Principle

Every abstraction admitted into the language must justify itself along three dimensions:

1. **Construction**: What simpler constructs is it built from?
2. **Pattern**: What recurring structure or practice does it capture?
3. **Reversibility**: Can it be peeled away without loss of conceptual footing?

Sophistication is welcome; opacity is not.

The aim of this language is not to eliminate complexity, but to **make complexity grow in a controlled, layered, and reversible way**—fast enough to be useful, structured enough to be understood, and deep without losing the ability to see the bottom.

---

<a id="documentation-notes-category-theory-detour-md"></a>

# Source: `documentation/Notes/category_theory_detour.md`

## A brief detour: category theory

It has been about a month since the last visible update. The short explanation is straightforward: I returned to category theory after many years and ended up spending far longer there than expected.

This text is not a tutorial, nor a declaration of direction. It is a *linking note*: an attempt to explain why this detour belongs alongside the rest of the project, and why the time spent here felt like alignment rather than delay.

### Lineage, not novelty

My understanding of programming languages has always been shaped by a particular lineage: ALGOL 60, Dijkstra, Hoare, structured programming, and the influence of relational and predicate calculus.

That tradition treats programming as a discipline of reasoning. The emphasis is on structure, invariants, and clarity—not on accumulating techniques or tools. Category theory enters here not as a fashionable import, but as a continuation of the same impulse: to improve the language we use to talk about computation.

### What category theory actually changed

Category theory emerged in the 1940s (Eilenberg–Mac Lane) with a quiet shift in emphasis. Instead of organizing mathematics around elements and constructions, it organized it around relationships and composition.

Its long-term contribution was not primarily new results, but unification. Ideas that appeared different on the surface were shown to share the same shape. Once named, those shapes could be reused.

This mirrors the role logic played in programming. Logic did not merely add proofs; it gave programmers working vocabulary: predicate, variable, scope, binding, substitution, evaluation order, type, judgment. Those terms did not stay theoretical—they became practical tools for writing, discussing, and reasoning about programs.

Category theory offers vocabulary at a different level, but with a similar effect: object, morphism, composition, product, coproduct, universal property, adjunction. These words point to patterns programmers already encounter, but often only handle implicitly.

### From abstraction to practice

Seen from the ground, category theory is not about importing exotic mathematics into a language. It is about making familiar ideas precise enough to rely on.

* **Composition** captures the common intuition behind function chaining, pipelines, middleware stacks, dataflow graphs, and build systems—and insists that this glue behave predictably.
* **Products and coproducts** give a clear account of tuples versus sum types, records versus variants, and the symmetry between “and” and “or”.
* **Universal properties** provide a way to define interfaces by the problem they solve uniquely, rather than by enumerating methods and corner cases.
* **Functors** clarify what it means to transform data while preserving structure—something programmers do constantly when mapping over collections, streams, futures, or syntax trees.
* **Equational reasoning** formalizes the expectation that refactoring should preserve meaning, and that equivalent constructions should be interchangeable.

None of this requires categorical syntax to appear in the language. What it requires is design discipline: small cores, lawful composition, and abstractions that behave uniformly rather than surprisingly.

### On restraint and distillation

It is easy to impose category theory—just as it is easy to impose any powerful mathematical idea—superficially. One can graft terminology and abstractions onto a system and claim rigor without gaining clarity.

The harder task is distillation: absorbing the ideas deeply enough that they vanish into a clean, minimal interface.

This problem is familiar in systems work. Large organizations routinely accumulate layers of SaaS products, cloud services, and frameworks, exposing their combined complexity to users. The harder achievement is to absorb that complexity and present a coherent surface, as platforms like Athena or Aladdin attempt to do.

Category theory presents the same challenge. Its value lies not in visible machinery, but in the constraints it imposes on design—on what must exist, what can be derived, and what should be excluded.

### On the pause

Returning to this material has been slow and often disorienting. Intuitions fail; progress is uneven. But the clarity gained here feels qualitatively different from ad hoc progress.

The expectation is that this grounding will make it easier to project rough ideas into cleaner structures, interpolate between partial designs, and extrapolate without losing coherence.

The recent silence, then, has not been inactivity but consolidation. This detour is less a diversion than a reinforcement of foundations, very much in the spirit of the traditions that motivated this project in the first place.


# Temporary Conclusion on the Category Theory Detour

I have now spent hundreds of hours exploring category theory in the context of thinking about Nomi. Over this period, I have learned a substantial amount of terminology and become familiar with many central concepts — adjunctions, limits and colimits, functors, natural transformations, universal properties, and the categorical view of logic. My coverage has expanded significantly. I now recognize recurring structural patterns across different areas, and the internal consistency of my understanding has improved. Ideas that once felt opaque now feel interconnected; I can often see why definitions are shaped the way they are, even if I cannot yet fully command them.

At the same time, much of this knowledge remains partially digested. Some of it is still half-formed: I know the vocabulary, I can trace the formal shapes, but I do not yet grasp the ideas with enough depth and precision to responsibly embed them into the core design of Nomi. I cannot extract from category theory a foundation that feels both technically solid and conceptually earned.

Throughout this detour, I have learned from a range of voices — the structural clarity of Eugenia Cheng, the logical discipline of Peter Smith, the programmer’s perspective of Bartosz Milewski, the applied and conceptual framing of David Spivak, the type-theoretic and foundational insights of Robert Harper and the logical depth of Robert Goldblatt, along with the expository precision of Tom Leinster, the structural and conceptual sensibility of Harold Simmons, and the computational and philosophical bridges built by Noson Yanofsky. Each contributed a different lens, and together they expanded my conceptual landscape.

I remain vaguely but strongly convinced that category theory — particularly in its deep entanglement with logic — can help streamline and clarify many of the foundational ideas behind Nomi. It feels like the right altitude of abstraction. But at this stage, my understanding is not yet mature enough to integrate it in a principled way.

So this path pauses here.

I expect to return to it later, likely with sharper questions and more concrete pressures emerging from the language design itself. For now, category theory remains a background structure: suggestive, powerful, and unfinished in my hands.

This is not an ending, only a suspension.

---

<a id="documentation-notes-meta-md"></a>

# Source: `documentation/Notes/meta.md`

This folder contains exploratory and reflective notes that live upstream of the current design.

They are not specifications, and they are not yet part of the language proper. Instead, they record ideas, vocabularies, and lines of reasoning that are still being absorbed, stress-tested, and clarified.

The separation is intentional. Keeping this material visible without embedding it prematurely helps avoid freezing half-formed intuitions into design decisions. Some notes here may eventually condense into concrete mechanisms; others may disappear entirely once their purpose is served.

Think of these as working notes in the literal sense: a place to reason in public, to sharpen intuition, and to distill external ideas before allowing them to shape the language.

Integration, if it happens, will happen later—when the concepts can be expressed without unnecessary machinery and justified by the design as a coherent whole.

---

<a id="documentation-draft-type-theory-design-guide-md"></a>

# Source: `documentation/DRAFT/type_theory_design_guide.md`

# From ADTs to Dependent Types

## Construction, Elimination, and Pattern Matching

This document is a **stand-alone conceptual note** on how sophisticated programming abstractions arise from a small set of core ideas. It connects algebraic data types, pattern matching, indexed types, guarded sums, and dependent types under a single lens: **construction and elimination**.

The goal is not formal completeness, but *conceptual continuity*: each abstraction layer should feel like a necessary refinement of the previous one, not a leap of faith.

---

## Guiding Principle

> **Types describe what must be provided. Values are witnesses that the description is satisfied.**

Everything below follows from this.

---

## Two Fundamental Notions

### Construction (Introduction)

**Construction** means:

> *Provide enough information (witness + payload) to satisfy a type.*

Examples:

* Pair `(a, b)` witnesses `A × B`
* `Left a` witnesses `A ∨ B`
* `Cons x xs` witnesses `Vec A (n+1)`

A constructor does not merely build data — it *asserts a fact*.

---

### Elimination (Use)

**Elimination** means:

> *Given a witness, extract or refine information guaranteed by the type.*

Examples:

* Using `(a,b)` to obtain `a` and `b`
* Case analysis on `Either`
* Pattern matching on vectors to learn their length

> **Pattern matching is the concrete syntax of elimination.**

To *use* a value is to eliminate its type.

---

## Curry–Howard in One Sentence

| Logic       | Programming  |
| ----------- | ------------ |
| Proposition | Type         |
| Proof       | Value        |
| Implication | Function     |
| Disjunction | Sum type     |
| Conjunction | Product type |

> **A proof is a value; to use a proof is to eliminate its type.**

---

## Ordinary Algebraic Data Types (ADTs)

### Products (AND)

```haskell
(a, b) :: (A, B)
```

* Construction: provide both `a` and `b`
* Elimination: pattern match `(a,b)`

Logical meaning: `A ∧ B`.

---

### Sums (OR)

```haskell
data Either A B = Left A | Right B
```

* Construction: choose a constructor + payload
* Elimination: handle **both cases**

Logical rule:

> **To use `A ∨ B`, you must handle both `A` and `B`.**

This is not a convention; it is the elimination rule for disjunction.

---

## Pattern Matching Is Not Syntax Sugar

Pattern matching:

* Reveals **which constructor was used**
* Refines what you can assume in each branch
* Implements logical **case analysis**

```haskell
f :: Either A B -> C
f (Left a)  = c_from_a a
f (Right b) = c_from_b b
```

Logical form:

```
(A → C) ∧ (B → C)
------------------
      A ∨ B → C
```

Pattern matching is *how proofs are used*.

---

## Indices: Making the Tag Explicit

### Indexed View of `Either`

Conceptually:

```
Either A B ≅ Σ b : Bool. Payload(b)
```

Where:

* `true  → Payload = A`
* `false → Payload = B`

Here:

* The **index** (`Bool`) is primary
* The constructor is a *witness that the index is satisfied*

Tags were indices all along.

---

## Indexed Types

### Example: Vectors

```idris
data Vec A : Nat -> Type where
  Nil  : Vec A 0
  Cons : A -> Vec A n -> Vec A (n+1)
```

* The index (`Nat`) restricts which constructors are possible
* Pattern matching refines the index

```idris
head : Vec A (S n) -> A
head (Cons x xs) = x
```

Impossible cases are **unrepresentable**: no value can be constructed whose type would require handling them.

---

## Guarded Sums

A **guarded sum** is an indexed sum where:

> The payload exists *only if* a predicate or index allows it.

---

### Degenerate Guard: `Either`

* Index = `Bool`
* Guard is trivial
* Constructor acts as a tag

This is the simplest guarded sum.

---

### Non-trivial Guard

```
Σ n : Nat. (n > 0) × Vec A n
```

* Payload exists only when the predicate holds
* Construction requires a proof
* Elimination refines the predicate

The guard is *semantic*, not merely structural.

---

## Dependent Pairs (Σ-types)

```
Σ x : A. P(x)
```

* Construction: `(x, proof_of_P(x))`
* Elimination: pattern match `(x,p)`

This generalizes:

* Records
* Guarded sums
* Existential types

---

## Dependent Functions (Π-types)

```
Π x : A. B(x)
```

* Generalizes functions `A -> B`
* Output type depends on input value

Logical meaning:

> For every `x`, if `x : A`, then `B(x)` holds.

Function application is **implication elimination**.

---

## Refinement Types

```
{x : Int | x > 0}
```

* Implicit Σ-type
* Proof is erased
* Same logical meaning as dependent pair

Refinement types trade explicitness for convenience.

---

## Pattern Matching as the Core Mechanism

Pattern matching:

* Eliminates values
* Refines indices
* Reveals witnesses
* Enforces guards

> **All explicit use of proofs in programming reduces to elimination, most commonly realized as pattern matching.**

---

## Conceptual Hierarchy

```
Ordinary ADTs
  ↓ (add indices)
Indexed Types / GADTs
  ↓ (add predicates)
Guarded Sums
  ↓ (generalize)
Σ-types (dependent pairs)
  ↓
Π-types (dependent functions)
```

Every step preserves the same ideas:

* Construction = provide witness + payload
* Elimination = refine using the witness

---

## Manifesto: Sophistication Without Obscurity

* Abstractions must grow by **refinement**, not replacement
* Every feature must admit clear construction and elimination rules
* Tags should become indices when they start carrying meaning
* Guards should be enforced by types, not conventions
* Pattern matching should be the primary eliminator

> **Sophistication is disciplined reuse under constraint.**

Dependent types are not a new idea — they are what remains when nothing unnecessary is left implicit.

---

## Bridging to Concrete Syntax

A language design guided by these ideas would:

* Treat constructors as *witness builders*, not just data creators
* Make indices explicit where they matter, implicit where they do not
* Use pattern matching as the *only* eliminator for structured data
* Allow gradual migration:

  * ADTs → GADTs → guarded sums → dependent pairs

### Example Design Moves

* Replace ad-hoc boolean flags with indexed constructors
* Replace partial functions with guarded input types
* Prefer elimination-by-pattern over runtime checks

The aim is not maximal expressiveness, but **semantic alignment**: the structure of programs should mirror the structure of their reasoning.

---

## Closing Perspective

> Sophistication is not the accumulation of features, but the disciplined reuse of a small number of ideas under increasing constraint.

Construction, elimination, and pattern matching are those ideas.

---

# Archived Design Review Source Material

---

<a id="documentation-design-review-archive-readme-md"></a>

# Source: `documentation/design_review_archive/README.md`

# Design Review Archive

> Status: archived source material.

These files were moved out of `documentation/design_review/` because they
overlap heavily. They remain useful as background: cross-language comparison,
syntax sketches, radical feature ideas, and broad programmer-experience notes.

The active design workspace is now `documentation/design_review/`.

Current active focus:

- `../design_review/first_principles_programming_model.md`
- `../design_review/hierarchical_language_research_plan.md`
- `../design_review/research_notes_synthesis.md`
- `../design_review/cognitive_language_vision.md`
- `../design_review/language_coherence_model.md`
- `../design_review/binding_constraints_feature.md`
- `../design_review/implementation_todos.md`

When reviving an idea from this archive, promote only the smallest useful piece
into an active feature spec with syntax, semantics, desugaring, diagnostics, and
implementation tasks.

---

<a id="documentation-design-review-archive-ai-codex-project-overview-vision-md"></a>

# Source: `documentation/design_review_archive/ai-codex_project_overview_vision.md`

# Nomi Project Overview and Vision

> Disclaimer: This document was generated by OpenAI Codex based on the existing Nomi README, documentation notes, and repository structure as of the time it was created. It should be treated as an AI-assisted summary, not as a canonical language specification.

## Purpose

Nomi is an experimental programming language built around a small, coherent core: variables, functions, binding, and application. Its central goal is to make programming more systematic and human-readable without losing the ability to scale toward serious software construction.

The project treats Python as both a semantic baseline and a practical bootstrap environment. Nomi starts from familiar Python concepts, then refines them into a more expression-oriented and compositional model.

## Core Ambition

Nomi aims to reduce conceptual fragmentation in programming. Modern development spans frontend, backend, data, AI, systems, deployment, testing, and configuration, each with its own tools and mental models. Nomi's long-term ambition is to provide a smaller set of primitives that can grow across domains without forcing constant paradigm switching.

The design is guided by several principles:

- Keep the core language small and orthogonal.
- Prefer composition over special-case machinery.
- Preserve readability and local reasoning.
- Let sophisticated abstractions grow from simpler ones.
- Keep abstractions reversible: they should be explainable in terms of lower-level constructs.
- Use formal ideas where they clarify the design, but avoid over-formalization that hurts usability.

Performance is not the first priority. The current priority is semantic clarity, expressive power, and a language model that remains understandable as it grows.

## Key Components

### Surface Language

Nomi currently explores a Python-like surface syntax with targeted changes:

- `func` replaces `def` to make function definition explicit.
- Arrow functions provide concise expression-level function literals.
- Bindings can carry enforced type and predicate constraints.
- Generator-style control is generalized through yield-to-block constructs.

These changes are not intended as cosmetic syntax tweaks. They are experiments in making functions, binding, validation, and control flow more uniform.

### Parser

The parser lives under `prototype/parser/` and uses Lark grammar definitions from `prototype/grammar/`. The parser lowers Nomi syntax into Python AST structures, giving the project a concrete intermediate representation while preserving a path toward future independence.

There are separate parser layers for Python-compatible syntax and Nomi-specific syntax. This makes it possible to compare Nomi's behavior against Python while introducing semantic changes incrementally.

### Interpreter

The interpreter lives under `prototype/interpreter/`. It is a layered runtime that evaluates Python AST-like structures directly rather than delegating normal execution to Python's `exec`.

Important interpreter areas include:

- Environment and binding models.
- Function definition, closure handling, and argument binding.
- Control flow evaluation.
- Exception handling.
- Generator and coroutine state.
- Nomi-specific constraint enforcement and block behavior.

Python remains the host language, but the interpreter is intentionally custom. This keeps the design inspectable and prepares the project for a possible future VM, bytecode interpreter, or standalone runtime.

### Constraint System

Nomi treats binding as a core operation. Assignment, function parameters, loop variables, pattern-like binding, and related constructs are all viewed as places where names become associated with values.

The constraint system builds on that idea. Bindings may carry:

- Type constraints, such as `int`.
- Predicate constraints, such as `is_positive`.
- Expression-level constraints, such as `a > 20`.

When a value is bound, the relevant constraints are checked and a `TypeError` is raised if validation fails. This moves type-like validation from optional documentation into runtime language behavior.

### Yield-to-Block Control

Nomi explores generalized block control through a yield-to-block model. A function can yield to a block supplied by the caller, allowing patterns such as retry logic, scoped execution, context-like behavior, and block iteration to be expressed through a common mechanism.

This is one of the most ambitious and delicate parts of the prototype. It attempts to bridge:

- Functions and blocks.
- Statements and expressions.
- Decorators and context managers.
- Generators and more general coroutines.

The current implementation works for tested cases but remains an active design and implementation risk.

### Tests and Examples

The test suite lives under `prototype/tests/` and covers parser behavior, interpreter behavior, regression samples, and unit-level environment behavior. Example programs live under `prototype/tests/data/sample_sources/` and `scripts/`.

Tests are essential to the current development style because Nomi is evolving by semantic substitution: Python-compatible behavior is preserved where desired, while Nomi-specific behavior is introduced deliberately and checked against examples.

## Intellectual Lineage

Nomi is informed by a long programming language tradition:

- Lambda calculus and functional programming for compositional foundations.
- ALGOL and Landin-style language families for structured language design.
- Lisp for symbolic flexibility and meta-level thinking.
- Python for readability, approachability, and pragmatic iteration.
- ML, Haskell, Scala, Rust, and Julia for modern lessons in type systems, abstraction, and systems design.

The project is also shaped by the broader history of symbolic reasoning, from Leibniz and Boole through Church, Turing, and later programming language research.

## AI Complementarity

Nomi is not an AI system, but it is being designed in an AI-saturated software world. AI expands the search space: it can propose, synthesize, compare, and critique. A programming language does the opposite kind of work: it compresses intent into durable, inspectable, executable structure.

Nomi's role is therefore complementary to AI. It aims to provide a stable semantic substrate where generated or human-written ideas can be clarified, constrained, edited, and accumulated over time.

## Current Status

Nomi is a working prototype, not a stable language. It can parse and run selected Nomi and Python-like programs through a Python-based runner. The project already includes a custom parser, AST lowering, interpreter, environment model, binding semantics, constraints, and resumable control machinery.

The implementation is intentionally experimental. Some parts are robust enough to test and iterate on; others are exploratory and expected to change substantially.

## Long-Term Direction

The long-term direction is to move from Python-hosted prototyping toward a more independent language substrate. Possible future steps include:

- A clearer informal language specification.
- More systematic syntax and semantics documents.
- Stronger regression and unit coverage.
- Better tooling, including editor support and diagnostics.
- A reduced core implementation that can eventually be ported or self-hosted.
- A VM, bytecode, or stack-machine execution model if the current AST-walking interpreter becomes limiting.

The near-term strategy remains conservative: keep Python as the reference and host while replacing pieces only when the language design demands it.

## Risks

Nomi's risks are both technical and social.

Technical risks include the complexity of resumable control, the challenge of preserving clarity while adding expressive power, and the eventual need to decouple from Python without losing a practical development path.

Social risks are larger. Programming languages rarely succeed on semantic merit alone. Tooling, documentation, education, ecosystem fit, and institutional trust often matter more than elegance. Nomi's success should therefore be judged partly by whether its ideas become clear, useful, and transmissible, even if the language itself changes direction.

## Working Thesis

Nomi is an attempt to build a language that is minimal without being impoverished, expressive without being opaque, and practical without surrendering conceptual coherence.

The guiding thesis is simple:

> Sophistication should grow from small primitives in controlled, inspectable layers.

That thesis shapes the project's syntax, interpreter, documentation, and long-term ambition.

---

<a id="documentation-design-review-archive-proposed-language-feature-design-plan-md"></a>

# Source: `documentation/design_review_archive/proposed_language_feature_design_plan.md`

# Proposed Language Feature Design Plan

> Status: design proposal, not implementation guidance.
>
> This document captures proposed Nomi language features at the level of user-facing
> semantics. The goal is to make sample code fragments meaningful and implementable
> later, while keeping the design centered on usability and Python-like readability.
>
> Companion documents:
>
> - [Proposed Syntax Samples](proposed_syntax_samples.md) is the sample-heavy
>   syntax catalog.
> - [Language Syntax Synthesis](language_syntax_synthesis.md) explains the
>   small-core philosophy and cross-language reductions behind the catalog.
> - [Cross-Language Feature Synthesis Examples](cross_language_feature_synthesis.md)
>   compares similar features across several languages before proposing Nomi
>   forms.
> - [Nomi Language Revision Report](nomi_language_revision_report.md) records a
>   report-style proposed language revision.
> - [Radical Language Feature Ideas](radical_language_feature_ideas.md) collects
>   more speculative ideas such as calculational blocks, relations, proof-carrying
>   code, live values, worlds, semantic holes, and counterfactual execution.
> - [Everyday Radical Language Ideas](everyday_radical_language_ideas.md)
>   focuses on radical-but-common features for daily coding: validation,
>   cleanup, defaults, collection transforms, retry/timeout, logging, config,
>   forms, CLI commands, small parallel blocks, caching, patches, and undo.

## Purpose

Nomi should feel close enough to Python that a Python programmer can read small
programs immediately, but the meaning of the core constructs should be cleaner,
more uniform, and less accidental.

The design priority is not ease of implementation. It is the shape of the
language as experienced by the programmer:

- Can the code be read locally?
- Does syntax say what kind of thing is being introduced?
- Do constraints and blocks mean the same thing across contexts?
- Can a simple fragment be explained without referring to parser internals?
- Does a feature reduce mental overhead compared with ordinary Python?

Implementation can come later. This plan defines the semantic target.

## Cross-Language Syntax Synthesis

This section lists coherent proposed syntax families for Nomi. The intent is not
to copy any one language, but to synthesize useful ideas from Python,
Mathematica, ALGOL, APL, Lisp, Ruby, Scala, Kotlin, and related language
families into a small Python-readable surface.

The proposed direction:

- Python supplies indentation, plain reading order, ordinary calls, and everyday
  approachability.
- ALGOL supplies block structure, lexical scope, and procedural clarity.
- Lisp supplies the idea that code has a regular underlying structure and that
  programs can manipulate program-shaped values.
- Mathematica supplies symbolic transformation, rules, and expression rewriting.
- APL supplies concise array-oriented thinking and whole-collection operations.
- Ruby supplies caller-side blocks as ergonomic control abstractions.
- Scala supplies expression orientation, pattern matching, and typed functional
  composition.
- Kotlin supplies null-safety, trailing functional arguments, extension-style
  usability, and lightweight data modeling.

Nomi should borrow the ideas, not the visual noise. The syntax should remain
readable as ordinary text.

### Syntax Tiers

Not every idea should enter the core language at the same level.

**Core syntax** should be small and stable:

- `func` definitions,
- arrow functions,
- binding constraints,
- pattern binding,
- block calls,
- `yield` to attached blocks,
- expression-oriented conditionals and matching.

**Candidate syntax** should be designed but held until examples justify it:

- pipe and composition operators,
- symbolic rewrite rules,
- array rank/map shorthand,
- null-safe access,
- extension declarations,
- lightweight data/type declarations.

**Library-led syntax** should start as ordinary functions and blocks before it
becomes language syntax:

- concurrency scopes,
- transactions,
- resources,
- tests,
- parsers,
- symbolic algebra,
- dataframes and tensor operations.

### Coherent Proposed Syntax List

| Idea | Proposed syntax | Main influence | Meaning |
| --- | --- | --- | --- |
| Named function | `func f(x): ...` | Python, ALGOL | Bind `f` to a function with block body. |
| Function value | `(x) => x + 1` | Scala, Kotlin | Create an expression-level function value. |
| Constrained binding | `x:int, x > 0 = 3` | Python hints, contracts | Bind only if all constraints pass. |
| Pattern binding | `(x, y) = point` | Python, ML, Scala | Destructure a value into names. |
| Block call | `retry(3): ...` | Ruby, Python blocks | Pass caller-side code into callee-owned control. |
| Yield to block | `yield value` | Python generators, Ruby | Invoke the attached block with a value. |
| Block parameter | `each(xs) -> x: ...` | Ruby, Kotlin | Name values yielded by the callee. |
| Match expression | `match value: case ...` | Python, Scala, ML | Choose by structural pattern. |
| Pipe forward | `value |> f(_)` | F#, Elixir, Mathematica | Pass a value through a readable transformation chain. |
| Composition | `f >> g` | APL, functional languages | Build a function that applies `f`, then `g`. |
| Rewrite rule | `expr /. pattern -> replacement` | Mathematica | Transform expression-shaped data by rule. |
| Quoted form | `quote: ...` or `'expr` | Lisp, Mathematica | Treat code-shaped syntax as data. |
| Null-safe access | `user?.name` | Kotlin | Access only if the receiver is not empty/null. |
| Defaulting | `name ?: "guest"` | Kotlin | Use fallback when left side is empty/null. |
| Range | `1..10` | Kotlin, Ruby | Inclusive range value. |
| Half-open range | `1..<10` | Kotlin, Swift | Range excluding the end. |
| Spread | `f(*xs, **opts)` | Python | Expand sequence or mapping into arguments. |
| Data declaration | `data Point(x:int, y:int)` | Kotlin, Scala | Declare a lightweight structured value. |
| Extension function | `func String.words(self): ...` | Kotlin, Scala | Add callable behavior to an existing type's interface. |
| Resource block | `using resource: ...` | Python, C#, Ruby blocks | Scoped setup and cleanup, possibly library-defined. |

This table is a proposal map, not a final grammar.

### Function And Call Syntax

Nomi should keep ordinary Python-style calls:

```python
total = add(2, 3)
```

Named functions use `func`:

```python
func add(x:int, y:int):
    return x + y
```

Function values use arrows:

```python
add = (x:int, y:int) => x + y
```

These two forms should have the same function semantics. The distinction is
surface usability:

- `func` is for named, block-shaped definitions.
- `=>` is for expression-shaped function values.

### Pipeline Syntax

Python reads well for nested calls until transformations become too deeply
nested:

```python
result = summarize(normalize(parse(text)))
```

A pipeline form can expose left-to-right data flow:

```python
result = text |> parse(_) |> normalize(_) |> summarize(_)
```

Meaning:

- start with `text`,
- substitute it into `_` in the next stage,
- pass each stage result forward.

For single-argument calls, a shorthand may be allowed:

```python
result = text |> parse |> normalize |> summarize
```

This borrows from functional pipeline languages and Mathematica's postfix style,
but keeps a Python-like reading order. The placeholder `_` should mean "the
value flowing through this pipeline position" only in syntactic contexts that
make that meaning obvious.

### Function Composition

Composition creates a function instead of immediately applying values:

```python
clean = strip >> lower >> normalize_space
```

Meaning:

```python
clean(x) == normalize_space(lower(strip(x)))
```

This is APL-like and functional, but expressed with ASCII operators. It should be
used for reusable transformation functions, not for ordinary imperative steps.

Pipeline applies now. Composition builds a later callable.

```python
value |> clean      # apply now
clean = f >> g      # define composed function
```

### Pattern Binding And Matching

Binding should support patterns consistently:

```python
(x, y) = point
{"name": name, "age": age} = user
```

The same pattern idea should appear in `match`:

```python
match response:
    case {"status": 200, "body": body}:
        body
    case {"status": code} if code >= 400:
        raise RequestError(code)
```

Meaning:

- patterns bind names,
- guards refine cases,
- failed patterns do not partially bind names,
- successful patterns expose their bindings in the case body.

This synthesis draws from Python pattern matching, ML/Scala destructuring, and
Lisp's long tradition of structural code/data manipulation.

### Symbolic Rewrite Rules

Mathematica's strongest idea for Nomi is not its bracket syntax, but its rule
semantics: transform expression-shaped values by matching patterns.

Candidate syntax:

```python
simplified = expr /. x + 0 -> x
```

Meaning:

- treat `expr` as a structured expression value,
- find subexpressions matching `x + 0`,
- replace them with `x`,
- produce the transformed expression.

Multiple rules:

```python
simplified = expr /. [
    x + 0 -> x,
    x * 1 -> x,
    x * 0 -> 0,
]
```

Rules should operate on explicit expression values, not secretly rewrite normal
runtime code. This preserves local reasoning.

Open syntax question: `->` is also useful for block yielded values. If both
forms remain, context must make them visually unambiguous:

```python
each(xs) -> x:          # block value binding
expr /. pattern -> out  # rewrite rule
```

### Quoted Expressions

To support symbolic rewriting and code-shaped data, Nomi may need a quote form.
Lisp uses quote; Mathematica treats expressions uniformly.

Candidate forms:

```python
expr = quote:
    x + 0
```

or:

```python
expr = '(x + 0)
```

Meaning:

- do not evaluate `x + 0` as normal code,
- capture its structured expression form as data.

The block form is more readable for large expressions:

```python
rule_input = quote:
    if amount > 0:
        account.balance -= amount
```

This should remain an advanced feature. It is powerful, but it can easily harm
ordinary readability if used casually.

### Array And Collection Orientation

APL's lesson is that whole-array thinking can remove incidental loops. Nomi
should make collection operations readable before making them cryptic.

Candidate forms:

```python
xs.map((x) => x * 2)
xs.filter((x) => x > 0)
xs.reduce(0, (a, x) => a + x)
```

Possible pipeline form:

```python
result = (
    xs
    |> map(_, (x) => x * 2)
    |> filter(_, (x) => x > 0)
    |> sum
)
```

Possible array-lift shorthand:

```python
ys = xs.*2
zs = xs.+ys
```

Meaning:

- apply the scalar operation elementwise.

This shorthand is intentionally risky. It is compact, but Nomi should not become
APL-like in visual density by default. The safer baseline is named collection
operations plus pipelines.

### Ranges And Slices

Ranges are common enough to deserve clear syntax:

```python
1..10      # inclusive range
1..<10     # half-open range
```

Use cases:

```python
for i in 1..<10:
    print(i)

xs[1..<4]
```

The half-open range should be favored for indexing because it matches Python's
slice convention. Inclusive ranges are useful for human-facing domains.

### Null And Optional Values

Nomi should avoid making absence handling verbose in application code.

Candidate syntax:

```python
city = user?.address?.city
name = user.name ?: "guest"
```

Meaning:

- `?.` stops access when the receiver is empty/null and returns the empty/null
  value.
- `?:` provides a fallback when the left side is empty/null.

This comes from Kotlin and related languages. The design question is whether
Nomi should have a distinguished `None`-like value only, or a richer optional
value model.

### Data Declarations

For simple structured values, a Kotlin/Scala-like data declaration may be more
usable than a full class:

```python
data Point(x:int, y:int)
```

Meaning:

- declare a structured value type,
- create fields `x` and `y`,
- generate ordinary construction, equality, and readable representation.

Example:

```python
p = Point(2, 3)
print(p.x)
```

This should be a convenience for value-shaped data, not a replacement for a
full object system.

### Extension-Style Functions

Kotlin and Scala show that method-like usability can be separated from actual
class ownership.

Candidate syntax:

```python
func String.words(self):
    return self.split()
```

Use:

```python
"hello world".words()
```

Meaning:

- define a function whose first receiver is a `String`,
- allow method-call syntax as a convenience,
- do not mutate the original `String` type globally unless the module/import
  system makes that extension visible.

This is mainly a usability feature. It lets library authors create fluent APIs
without forcing all behavior into classes.

### Block-Based Resource And Policy Syntax

Ruby's blocks and Python's `with` suggest a broader Nomi direction:

```python
transaction(db):
    create_user()
    send_welcome()
```

```python
timeout(5):
    fetch(url)
```

```python
parallel():
    fetch_user()
    fetch_orders()
```

These should all be explainable as block calls. The syntax should not require a
new language keyword for every policy. The language supplies the block mechanism;
libraries supply the control patterns.

### Expression-Oriented Statements

Scala and Kotlin make many constructs expressions. Nomi should move in that
direction selectively.

Candidate:

```python
label = if score >= 90:
    "excellent"
else:
    "ok"
```

Candidate:

```python
kind = match value:
    case int:
        "number"
    case str:
        "text"
    case _:
        "other"
```

Meaning:

- the construct produces a value,
- the chosen branch's final expression is the value,
- statement-style layout is preserved for readability.

This avoids the common split where small expressions are composable but larger
control structures are trapped as statements.

### Keywords To Prefer

Nomi should prefer plain, semantic keywords:

| Concept | Candidate keyword |
| --- | --- |
| Function definition | `func` |
| Lightweight data value | `data` |
| Interface/protocol | `trait` or `protocol` |
| Explicit constant binding | `const` |
| Mutable cell or variable marker | possibly none by default |
| Symbolic quote | `quote` |
| Pattern matching | `match`, `case` |
| Local import/use | `use` or Python-compatible `import` |

Keyword growth should be conservative. A library-defined block call is often
better than a new keyword.

### Syntax To Avoid Or Treat Carefully

Some powerful ideas from the inspiration languages should be handled carefully:

- Avoid pervasive punctuation like APL unless confined to array libraries.
- Avoid Lisp-like parenthesis-first syntax at the surface, even if the internal
  representation is regular.
- Avoid Mathematica-style capitalized builtins and bracket-heavy calls.
- Avoid Ruby's highly implicit receiver conventions where they harm local
  clarity.
- Avoid Scala's tendency toward many equivalent spellings for the same idea.
- Avoid Kotlin-style annotation and modifier buildup unless it remains readable.

The synthesis should preserve a Python-like "one obvious reading" even when the
semantic model is more systematic than Python's.

## Guiding Usability Principles

### Stay Python-Readable

Nomi should preserve Python's strongest usability property: code is scanned as
plain procedural text. Indentation, familiar operators, ordinary function calls,
and statement sequencing remain central.

Nomi should avoid symbolic density unless the symbol has a clear, recurring
meaning. A feature should earn its syntax by making common code easier to read,
not merely shorter.

### Make Core Concepts Explicit

Python's `def` keyword says that something is being defined, but not what kind
of thing. Nomi uses `func` because the construct introduces a function.

This principle applies broadly:

- Function definition introduces callable behavior.
- Binding attaches a value to a name.
- Annotation constrains a binding.
- A block call passes caller-side code to a callable control abstraction.
- `yield` inside such an abstraction marks where the caller's block runs.

The same concept should keep the same meaning wherever it appears.

### Prefer One Mental Model Per Concept

Nomi should minimize avoidable splits such as:

- named function versus anonymous function,
- assignment annotation versus parameter annotation,
- context manager versus block control helper,
- loop body versus callback body.

The surface syntax can still differ when readability demands it, but the
underlying explanation should stay unified.

## Feature 1: `func` Definitions

### Surface Form

```python
func greet(name):
    print("Hello", name)
```

### Meaning

This binds the name `greet` to a function value. When called, the function maps
arguments to parameters, creates a local execution environment, runs its body,
and returns either an explicit `return` value or the default empty value.

The key semantic point is that `func` introduces a function, not a generic
definition. The binding of the name is still visible and Python-like, but the
keyword now matches the kind of value being created.

### Decorators

```python
@logged
func greet(name):
    print("Hello", name)
```

Decorators apply to the function value produced by the function definition and
then bind the decorated result to the function name. This preserves Python's
readable decorator flow.

Conceptually:

```python
greet = logged(func_value)
```

The block form remains preferred for named, decorated, annotated, or multi-step
functions.

## Feature 2: Arrow Function Literals

### Surface Form

```python
(x, y) => x + y
(x:int) => x * x
() => print("ready")
```

### Meaning

An arrow expression creates a function value directly. It is the expression-level
form of function creation.

```python
square = (x:int) => x * x
```

This means:

- create a function that accepts one parameter `x`,
- constrain `x` to `int`,
- evaluate `x * x` when called,
- return that expression result.

Arrow functions are not "lesser functions." They are ordinary function values
with concise syntax for expression-oriented cases.

### Usability Rule

Use `func` when the function has a name, decorators, several statements, or a
body that benefits from vertical structure.

Use `=>` when the function is best read inline as a value.

```python
numbers.map((x) => x * 2)
```

The readability goal is similar to Python's `lambda`, but without treating
inline functions as a special, restricted sub-language.

## Feature 3: Binding Constraints

### Surface Form

```python
age:int = 34
score: score >= 0 = 10
amount:int, amount > 0 = 25
```

### Meaning

A binding associates a name with a value. A constrained binding additionally
checks that the value satisfies the listed constraints.

```python
age:int = 34
```

This means:

- bind `34` to `age`,
- check that the value is an instance of `int`,
- allow the binding only if the check passes.

```python
score: score >= 0 = 10
```

This means:

- tentatively bind `10` to `score`,
- evaluate `score >= 0` in the binding context,
- keep the binding if the expression is true,
- otherwise raise `TypeError`.

### Multiple Constraints

```python
amount:int, amount > 0 = 25
```

This means that all constraints must pass. The binding is valid only if `amount`
is an `int` and is greater than zero.

Constraints are programmer-facing validation, not optional documentation.

### Rebinding

```python
amount:int = 25
amount = 30
amount:str = "paid"
```

Proposed semantics:

- A constrained binding records constraints on that name.
- A later plain rebinding must satisfy the active constraints.
- A later annotated rebinding replaces the old constraint set with the new one.

This gives constraints a stable meaning while still allowing the programmer to
change the intended domain explicitly.

## Feature 4: Parameter Constraints

### Surface Form

```python
func withdraw(account, amount:(int, amount > 0)):
    account.balance -= amount
```

### Meaning

Parameter binding is binding. When a function is called, arguments are first
mapped to parameters using normal Python-like call rules. After that mapping,
each parameter's constraints are checked.

```python
withdraw(my_account, 10)
```

This means:

- map `my_account` to `account`,
- map `10` to `amount`,
- check that `amount` is an `int`,
- check that `amount > 0`,
- run the function body if all checks pass.

The parentheses around `(int, amount > 0)` distinguish multiple constraints on
one parameter from multiple parameters.

### Usability Goal

The same annotation idea should work in assignment and function parameters.
Users should not have to learn a separate validation model for function calls.

## Feature 5: Block Calls

### Surface Form

```python
retry(3):
    send_request()
```

### Meaning

This calls `retry(3)` with an attached caller-side block. The block is not
ordinary function syntax and should not be mentally treated as a callback.

The block:

- is written in the caller's indentation flow,
- runs where the callee yields to it,
- sees the caller's surrounding names,
- is controlled by the callee's block-yield behavior.

The most useful mental model is:

> The callee owns the control pattern. The caller supplies the work to be placed
> inside that pattern.

### Defining a Block-Control Function

```python
func retry(max_times):
    for attempt in range(max_times):
        try:
            yield
            return
        except Exception:
            pass
```

Here, `yield` means "run the attached caller block here."

When used as:

```python
retry(3):
    send_request()
```

the `send_request()` block may be attempted up to three times, depending on the
control logic inside `retry`.

### Why This Is Not Just `with`

Python's `with` handles enter/exit resource patterns well. Nomi block calls are
intended to express broader control patterns:

- retry,
- timing,
- setup/cleanup,
- temporary policy changes,
- structured iteration,
- scoped error handling,
- eventually, concurrency or scheduling patterns.

The usability goal is to avoid forcing every control abstraction into the shape
of a context manager, callback, decorator, or loop.

## Feature 6: Yielding Values Into Blocks

### Surface Form

```python
each([1, 2, 3]) -> item:
    print(item)
```

### Meaning

The callee may yield values to the attached block. The caller names those yielded
values after `->`.

```python
func each(items):
    for item in items:
        yield item
```

Used as:

```python
each([1, 2, 3]) -> item:
    print(item)
```

This means:

- call `each` with the list,
- each time `each` yields a value, bind it to `item`,
- run the caller block with that binding,
- resume `each` after the block completes.

The user-facing behavior is close to a `for` loop, but the iteration policy is
owned by `each`.

### Multiple Yielded Values

```python
pairs(data) -> key, value:
    print(key, value)
```

This should behave like destructuring assignment at the block boundary. If the
yielded value cannot be bound to the declared names, the block call fails with a
clear binding error.

## Feature 7: Block Parameters With Constraints

### Surface Form

```python
each(users) -> user: User:
    print(user.name)
```

Alternative candidate:

```python
each(users) -> user(User):
    print(user.name)
```

### Proposed Meaning

The yielded value is bound to the block parameter and validated using the same
constraint model as assignment and function parameters.

The exact syntax needs further design. The semantic goal is clear:

- block parameters are bindings,
- bindings may have constraints,
- invalid yielded values fail at the boundary where they are received.

### Design Concern

The syntax must remain easy to scan. Block calls already use `:` for the block
body, so adding parameter constraints must not create a dense or confusing line.

This is a usability-first open question.

## Feature 8: Caller-Scope Blocks

### Sample

```python
message = "start"

once:
    message = "done"

print(message)
```

If `once` is a block-control abstraction that yields exactly once, the final
print should show:

```python
done
```

### Meaning

The attached block executes in the caller's environment, not in a fresh function
environment. This is the major semantic difference between a Nomi block and an
ordinary function callback.

This makes block calls feel like structured control flow rather than nested
function definitions.

### Usability Benefit

The programmer can write:

```python
transaction(db):
    user = create_user()
    send_welcome(user)
```

without wrapping the body in a separate function solely to pass it around.

The body reads as normal sequential code, while the callee supplies the control
frame around it.

## Feature 9: Expression-Oriented Growth

Nomi should gradually make more constructs expression-friendly, but not at the
cost of readability.

Candidate direction:

```python
result = retry(3):
    compute()
```

Possible meaning:

- the block call as a whole produces the value returned by the block-control
  function,
- yielded block results can be captured and transformed by the callee,
- failure behavior remains explicit through exceptions or declared alternatives.

This is intentionally left less settled than basic block statements. The
statement form should be designed first because it is easier to read and closer
to Python's current mental model.

## Feature 10: Unified Meaning of Sample Fragments

### Fragment A

```python
is_pos = (x) => x > 0
count:int, is_pos = 3
```

Meaning:

- `is_pos` is a function value.
- `count` is bound to `3`.
- `3` must be an `int`.
- `is_pos(3)` must be true.

### Fragment B

```python
func repeat(n:int, body):
    for i in range(n):
        yield i
```

Meaning:

- `repeat` is a block-control function when used with an attached block.
- `n` must be an `int`.
- every `yield i` invokes the caller block with `i`.

The explicit `body` parameter may not be needed in final syntax. It is included
here only to expose the concept that a block is supplied by the caller.

### Fragment C

```python
repeat(3) -> i:
    print(i)
```

Meaning:

- call `repeat(3)`,
- bind each yielded value to `i`,
- run the indented block once per yielded value.

### Fragment D

```python
func protect(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()

protect(my_lock):
    update_shared_state()
```

Meaning:

- the callee handles resource policy,
- the caller writes the protected work inline,
- cleanup is guaranteed by the control abstraction.

This reads like a context manager but is explained through the same block-yield
mechanism as retry and iteration.

## Open Design Questions

### Block Argument Syntax

Current candidate:

```python
each(items) -> item:
    ...
```

Questions:

- Should `->` always mean values flow from callee to block?
- Should zero-argument blocks omit `->` entirely?
- Should constrained block parameters reuse function parameter syntax exactly?

### Return Values From Blocks

If the caller block computes a value:

```python
measure:
    expensive_call()
```

Questions:

- Does the block implicitly return its last expression?
- Does the callee receive that value as the result of `yield`?
- Should statement blocks and expression blocks be separate forms?

### Exception Boundaries

When the caller block raises an exception, the callee should be able to catch it
around `yield`.

```python
func retry(n):
    for i in range(n):
        try:
            yield
            return
        except NetworkError:
            continue
```

This behavior is essential for retry-like control abstractions. The final design
must make exception ownership understandable from the code's visual structure.

### Name Binding in Blocks

Caller-scope execution is usable, but it raises questions:

- Does assignment inside a block always affect the caller scope?
- Are block parameters local to the block body?
- How do `nonlocal` and `global` interact with block calls?

The usability target is that block bodies behave like ordinary in-place code
unless a binding is explicitly introduced by the block boundary.

## Proposed Design Milestones

### Milestone 1: Stabilize Core Reading

Define the informal semantics of:

- `func`,
- arrow functions,
- constrained assignment,
- constrained parameters.

Success criterion: a Python user can read small Nomi snippets and correctly
explain name binding, validation, and function calls.

### Milestone 2: Stabilize Block Statement Semantics

Define:

- `call(...): block`,
- `call(...) -> names: block`,
- caller-scope execution,
- `yield` to attached block,
- exception flow around `yield`.

Success criterion: retry, resource protection, and simple iteration examples
all share one explanation.

### Milestone 3: Decide Constraint Syntax for Block Parameters

Pick the most readable form for constrained block inputs.

Success criterion: block parameter constraints are readable beside the block
colon and clearly reuse the normal binding model.

### Milestone 4: Explore Expression-Level Block Calls

Only after statement blocks feel stable, explore block calls that produce values
directly inside expressions.

Success criterion: expression block calls improve clarity in real examples and
do not make ordinary control flow harder to scan.

## Non-Goals For This Document

This document does not specify:

- parser grammar,
- AST representation,
- bytecode or interpreter strategy,
- performance model,
- full type system,
- complete exception lifecycle,
- module/package semantics.

Those belong in implementation and specification documents after the user-facing
semantics settle.

## Working Thesis

Nomi's proposed feature set should make Python-like code more semantically
regular without making it feel foreign.

The language should let programmers write ordinary-looking code whose deeper
meaning is cleaner:

- functions are functions,
- bindings may validate,
- parameters are bindings,
- blocks are caller-side code placed into callee-owned control patterns,
- `yield` is the bridge between the two.

If these meanings remain stable, later implementation work can proceed against a
clear semantic target rather than a collection of isolated syntax experiments.

---

<a id="documentation-design-review-archive-language-syntax-synthesis-md"></a>

# Source: `documentation/design_review_archive/language_syntax_synthesis.md`

# Language Syntax Synthesis

> Status: design note.
>
> This document explains the ideas behind the proposed syntax catalog in
> [Proposed Syntax Samples](proposed_syntax_samples.md). It is concerned with
> usability, semantic coherence, and reducibility to a small core, not immediate
> implementation.

## Aim

Nomi should synthesize well-loved language ideas without becoming a museum of
syntax. The goal is not to combine Python, Lisp, Ruby, Mathematica, APL, Scala,
Kotlin, Rust, Swift, and ML mechanically. The goal is to identify the durable
ideas behind their syntax and express those ideas in a Python-readable form.

The result should feel like:

- Python in local readability,
- ALGOL in block structure,
- Lisp in regularity and code-as-data potential,
- Mathematica in symbolic transformation,
- APL in whole-collection thinking,
- Ruby in block ergonomics,
- Scala/ML in pattern and expression orientation,
- Kotlin/Swift in practical null-safety and lightweight modeling,
- Rust in explicit recoverable error flow where useful.

But Nomi should not inherit every surface habit from those languages.

## The Small Core

The proposed syntax should reduce to the following core.

### Values

Values are the things programs compute with:

```python
3
"hello"
[1, 2, 3]
Point(2, 3)
```

Most language features should either create values, transform values, or control
when value-producing code runs.

### Bindings

A binding gives a name to a value.

```python
x = 3
```

Binding is the common semantic operation behind:

- assignment,
- function parameters,
- loop variables,
- block parameters,
- pattern destructuring,
- imports,
- exception names,
- match-case names.

Unifying these reduces the number of rules a programmer has to remember.

### Constraints

Constraints refine bindings.

```python
x:int, x > 0 = 3
```

The same idea should apply in every binding position:

```python
func f(x:(int, x > 0)): ...

for x:int in xs:
    ...

each(xs) -> x:int:
    ...

case {"age": age:(int, age >= 0)}:
    ...
```

Reduction: bind first in a temporary context, validate, then commit or fail.

### Functions

Functions abstract value-producing or action-producing behavior.

```python
func add(x, y):
    return x + y
```

Arrow functions are the expression form of the same idea:

```python
(x, y) => x + y
```

Reduction: both create function values. `func` additionally binds a name and
supports block layout.

### Calls

Function application stays ordinary.

```python
f(x, y)
```

Most advanced syntax should reduce to calls:

```python
xs.map((x) => x * 2)
text |> normalize
transaction(db): ...
```

### Blocks

Blocks represent caller-side code supplied to a callee.

```python
retry(3):
    send_request()
```

The callee invokes the attached block with `yield`.

```python
func retry(n):
    for i in range(n):
        try:
            yield
            return
        except Exception:
            pass
```

This is the primitive that lets library-defined control structures exist without
adding a new keyword for each one.

### Patterns

Patterns describe the shape a value must have and the names to bind.

```python
(x, y) = point

match response:
    case {"status": 200, "body": body}:
        body
```

Pattern matching reduces to conditional shape tests plus binding.

### Explicit Expression Values

For symbolic programming and macro-like facilities, code-shaped syntax must be
captured explicitly.

```python
expr = quote:
    x + 0
```

Rewrite rules operate on these expression values.

```python
expr /. x + 0 -> x
```

This preserves normal local reasoning: ordinary code runs; quoted code is data.

## Design Rule: Syntax Must Desugar

A proposed syntax form should answer three questions:

1. What primitive does it reduce to?
2. What common human pattern does it make easier to express?
3. What ambiguity or hidden control does it introduce?

If the answers are weak, the syntax should remain a library pattern or be
dropped.

## Synthesis By Language Family

### Python: Readable Local Code

Python's central gift is ordinary readability:

```python
for user in users:
    if user.active:
        send(user.email)
```

Nomi should keep:

- indentation,
- plain names,
- ordinary calls,
- keyword arguments,
- exceptions,
- comprehensions where they remain readable,
- familiar data literals.

Nomi should refine Python where the semantics are uneven:

- `def` becomes `func`,
- type hints become runtime binding constraints where requested,
- `lambda` becomes ordinary arrow functions,
- context managers generalize into block calls,
- statement-only constructs can become expression-producing when readable.

### ALGOL: Blocks And Scope

ALGOL's durable idea is structured blocks. Nomi should treat block shape as a
semantic tool, not just formatting.

```python
if ready:
    run()

transaction(db):
    update()

scope:
    temp = compute()
```

Block syntax should communicate where control and names live. Caller-side blocks
should be explicit, and isolated scopes should be explicit too.

### Lisp: Regular Structure And Code As Data

Lisp shows that programs become more powerful when code has a regular structure.
Nomi should borrow this at the semantic layer without adopting Lisp's surface
parentheses.

```python
expr = quote:
    x + 0
```

Possible macro-like forms should be functions from expression values to
expression values:

```python
macro unless(cond, body):
    quote:
        if not {cond}:
            {body}
```

But macros should be rare, explicit, and import-scoped. Nomi should not allow
uncontrolled syntax mutation to undermine readability.

### Mathematica: Rules And Symbolic Transformation

Mathematica's key insight is expression transformation:

```python
simplified = expr /. [
    x + 0 -> x,
    x * 1 -> x,
]
```

In Nomi, this should reduce to:

- quoted expression values,
- pattern matching,
- replacement construction,
- repeated application when requested.

This can support symbolic algebra, AST transformations, query planners, and
domain-specific rewrites without making everyday code magical.

### APL: Whole-Collection Thinking

APL demonstrates how much incidental looping disappears when operations apply
to whole collections.

Nomi should prefer readable forms first:

```python
xs.map((x) => x * 2)
xs.filter((x) => x > 0)
```

and pipeline forms:

```python
result = xs |> filter(_, is_pos) |> map(_, square) |> sum
```

Elementwise symbolic shorthand is possible:

```python
ys = xs.*2
zs = xs.+ys
```

but this should remain candidate syntax. APL's power is real, but its visual
density is not aligned with Nomi's Python-readable goal.

### Ruby: Blocks As Control Abstractions

Ruby's block ergonomics are a major design source:

```python
each(users) -> user:
    print(user.name)

retry(3):
    send_request()
```

The crucial idea is not just callback syntax. It is that the caller writes code
in place while the callee owns the control pattern.

Reduction:

```python
callee(args):
    body
```

means:

```python
callee(args, block=<caller-scope body>)
```

and the callee invokes the block with `yield`.

### Scala, ML, And Haskell: Expressions, Patterns, And Composition

These languages show the value of expression orientation:

```python
kind = match value:
    case int:
        "number"
    case str:
        "text"
```

and compositional functions:

```python
clean = strip >> lower >> normalize_space
```

They also show the importance of pattern matching as a general way to process
structured values:

```python
match result:
    case Ok(value):
        value
    case Err(error):
        recover(error)
```

Nomi should borrow these ideas, but keep syntax less abstract than Scala and
less symbolic than Haskell.

### Kotlin And Swift: Practical Modeling And Null Safety

Modern application code benefits from lightweight value models:

```python
data User(id:int, name:str, email:str?)
```

and safe access:

```python
email = user?.profile?.email ?: "missing"
```

These forms reduce common boilerplate. The design risk is that `None`, optional
types, nullable types, and result types can become fragmented. Nomi needs one
coherent absence/error story before this syntax becomes final.

### Rust: Recoverable Errors And Explicit Propagation

Rust's `Result` flow is attractive because it makes recoverable errors explicit.

Candidate:

```python
config = read_config(path)?
```

Reduction:

```python
tmp = read_config(path)
match tmp:
    case Ok(value):
        config = value
    case Err(error):
        return Err(error)
```

This should not replace exceptions casually. It is useful when a function's
normal contract includes failure as a value.

## Coherent Surface Families

### Family 1: Definition Forms

```python
func f(x): ...
data Point(x:int, y:int)
trait Drawable: ...
protocol Reader: ...
```

All define named program concepts. Each should reduce to bindings and
constraints:

- `func` binds a function value,
- `data` binds a constructor and pattern shape,
- `trait` binds a behavioral constraint set,
- `protocol` binds a structural constraint set.

### Family 2: Expression Functions And Composition

```python
(x) => x + 1
f >> g
value |> f
```

Reduction:

- arrows create function values,
- composition creates function values,
- pipelines call functions with flowing values.

### Family 3: Binding And Pattern Forms

```python
x:int = 3
(x, y) = point
case Point(x, y):
for user:User in users:
each(users) -> user:User:
```

Reduction: each is binding plus optional validation.

### Family 4: Block Control Forms

```python
retry(3): ...
transaction(db): ...
timeout(5): ...
test "name": ...
```

Reduction: each is a call with an attached caller-side block. Some may become
keywords later, but they should begin as library-defined block calls.

### Family 5: Symbolic Forms

```python
quote: ...
expr /. pattern -> replacement
macro name(...): ...
```

Reduction: explicit expression values plus functions over those values.

## Sample Program: Data Processing

```python
data User(id:int, name:str, age:(int, age >= 0), email:str?)

func adult(user:User) -> bool:
    user.age >= 18

func normalized_email(user:User) -> str?:
    user.email?.lower()

emails = (
    users
    |> filter(_, adult)
    |> map(_, normalized_email)
    |> filter(_, (email) => email is not None)
    |> sort
)
```

Reduction:

- `data` creates a structured value constructor and pattern.
- `func` binds functions.
- `str?` is a constraint or optional type marker.
- `|>` rewrites nested calls left-to-right.
- `?.` rewrites guarded access.

## Sample Program: Control Abstraction

```python
func retry(times:int, on=Exception):
    for attempt in 1..times:
        try:
            yield attempt
            return
        except on as error:
            if attempt == times:
                raise error

retry(3, on=NetworkError) -> attempt:
    print(f"attempt {attempt}")
    send_request()
```

Reduction:

- the block call passes caller-side code to `retry`,
- `yield attempt` invokes the block with `attempt`,
- `attempt` is bound at the block boundary,
- exceptions from the block are visible around `yield`.

## Sample Program: Symbolic Rules

```python
expr = quote:
    (x + 0) * 1

simplified = expr //. [
    x + 0 -> x,
    0 + x -> x,
    x * 1 -> x,
    1 * x -> x,
]
```

Reduction:

- `quote` creates expression data,
- rules are pattern/replacement pairs,
- `//.` repeats rewrite until stable,
- no ordinary runtime code is rewritten implicitly.

## Sample Program: Testing

```python
test "withdraw reduces balance":
    account = Account(balance=100)
    account.withdraw(30)
    assert account.balance == 70

cases([(100, 30, 70), (50, 10, 40)]) -> start, amount, expected:
    test f"withdraw {amount} from {start}":
        account = Account(balance=start)
        account.withdraw(amount)
        assert account.balance == expected
```

Reduction:

- `test` is a block call registering a named block,
- `cases` yields values into a caller block,
- block parameters are bindings.

## Syntax Admission Criteria

A syntax proposal should be admitted only if it passes these tests.

### Readability

Can a Python programmer guess the basic meaning from the sample?

Good:

```python
retry(3):
    send_request()
```

Risky:

```python
send_request repeat_symbol 3
```

The second stands in for dense symbolic repetition. It may be elegant in an APL
context, but it does not fit Nomi's surface.

### Reducibility

Can the form be explained in terms of primitives?

Good:

```python
value |> f
```

reduces to:

```python
f(value)
```

Risky: syntax that requires a new invisible runtime model.

### Orthogonality

Does the form reuse existing concepts?

Good:

```python
each(users) -> user:User:
    ...
```

because block parameters are bindings, and bindings can have constraints.

Risky: a special validation system only for block parameters.

### Local Reasoning

Can the reader see where control flows and where names are bound?

Block calls should make control abstraction visible:

```python
transaction(db):
    update()
```

Symbolic rewriting should be explicit:

```python
expr /. rule
```

### Frequency

Does the feature serve common code?

High-frequency:

- constrained binding,
- data values,
- pattern matching,
- block calls,
- pipelines,
- null-safe access.

Lower-frequency:

- macros,
- repeated rewrite rules,
- array-rank shorthand,
- custom query syntax.

Lower-frequency features can still exist, but they should be library-led or
advanced.

## Features To Keep Library-First

Some ideas are attractive but should begin as libraries using the small core.

### Query Syntax

Prefer:

```python
users |> filter(_, active) |> map(_, name)
```

before:

```python
query users -> u:
    where u.active
    select u.name
```

### Concurrency Syntax

Prefer:

```python
scope() -> task:
    user = task.spawn(() => fetch_user())
```

before:

```python
async:
    user = spawn fetch_user()
```

### Macros

Prefer explicit `quote` and rewrite functions before open-ended macro syntax.

### Array Shorthand

Prefer named whole-collection operations before symbolic elementwise operators.

## Risks

### Too Many Spellings

Scala demonstrates the cost of too many equivalent forms. Nomi should avoid
adding syntax if an existing form is already clear.

### Too Much Implicitness

Ruby demonstrates the elegance and risk of implicit receivers and flexible
blocks. Nomi should keep caller-side blocks visible and avoid hidden receivers
except for controlled extension methods.

### Too Much Symbolism

APL and Mathematica demonstrate how notation can become a powerful private
language. Nomi should support symbolic domains without making ordinary programs
look symbolic by default.

### Too Much Magic

Lisp macros and Mathematica rewriting can change code meaning deeply. Nomi
should require explicit quote/rewrite/macro boundaries.

## Working Design Position

Nomi should be a small-core language with a rich but disciplined surface.

The core is:

```text
value
binding
constraint
function
call
block
yield
pattern
quote
```

The surface can then support:

```text
data values
pipelines
composition
pattern matching
block control
symbolic rewrites
null-safe access
extension functions
structured tests
structured concurrency
```

Each surface form should be explainable by peeling it back to the core. If that
peeling process is natural, the syntax is a candidate. If it feels like a
separate language hidden inside Nomi, it should remain outside the core.

The long-term design goal is not minimal syntax. It is tractable
sophistication: a language where advanced forms exist, but every advanced form
has a clear path back to simple primitives.

---

<a id="documentation-design-review-archive-proposed-syntax-samples-md"></a>

# Source: `documentation/design_review_archive/proposed_syntax_samples.md`

# Proposed Syntax Samples

> Status: exploratory syntax catalog.
>
> This document is intentionally sample-heavy. It sketches what Nomi code could
> look like if it synthesized well-loved syntax ideas from Python, Ruby,
> Mathematica, Lisp, ALGOL, APL, Scala, Kotlin, ML, Haskell, Rust, Swift, and
> related languages while remaining reducible to a small semantic core.

## Small Core Assumption

Every surface form in this document should reduce to a small set of primitives:

- values,
- names and bindings,
- constraints on bindings,
- functions,
- function calls,
- caller-side blocks,
- `yield` to blocks,
- patterns,
- explicit expression values for symbolic/code-shaped data.

If a syntax form cannot be explained through these ideas, it should stay out of
the language until its primitive meaning is clearer.

## 1. Binding

Basic binding should remain Python-readable.

```python
name = "Nomi"
count = 3
enabled = True
```

Constrained binding validates at the point of binding.

```python
age:int = 34
age:int, age >= 0 = 34
email:str, contains(email, "@") = "a@b.com"
```

Predicate functions are ordinary constraints.

```python
is_pos = (x) => x > 0
amount:int, is_pos = 25
```

Constant binding can be explicit if Nomi later distinguishes rebinding policy.

```python
const pi = 3.14159
const app_name:str = "Nomi"
```

Destructuring is binding through a pattern.

```python
(x, y) = point
[first, *rest] = items
{"id": id, "name": name} = user
```

Constrained destructuring should reuse the same binding idea.

```python
(x:int, y:int) = point
{"age": age:(int, age >= 0)} = user
```

Reduction:

```python
(x, y) = point
```

means:

```python
tmp = point
x = tmp[0]
y = tmp[1]
```

plus shape checks.

## 2. Functions

Named functions use `func`.

```python
func add(x, y):
    return x + y
```

Parameters are bindings, so constraints work there too.

```python
func withdraw(account, amount:(int, amount > 0)):
    account.balance -= amount
```

Expression functions use arrows.

```python
square = (x:int) => x * x
add = (x, y) => x + y
```

Multi-line expression functions can use a block when readability needs it.

```python
score_user = (user) =>:
    base = user.reputation
    bonus = user.completed_tasks * 2
    base + bonus
```

Reduction:

```python
score_user = (user) =>:
    base = user.reputation
    bonus = user.completed_tasks * 2
    base + bonus
```

means:

```python
func score_user(user):
    base = user.reputation
    bonus = user.completed_tasks * 2
    return base + bonus
```

Decorators remain Python-like.

```python
@logged
@timed
func fetch_user(id:int):
    return api.get_user(id)
```

Inline anonymous block parameters can use the same arrow syntax.

```python
users.map((u) => u.name)
users.filter((u) => u.active)
```

## 3. Calls

Ordinary calls remain ordinary.

```python
send(email, subject, body)
```

Keyword arguments stay readable.

```python
send(to=email, subject="Welcome", body=body)
```

Spread is Python-compatible.

```python
send(*args, **options)
```

Named argument shorthand can be considered for common object construction and
calls where the variable name matches the parameter name.

```python
send(:email, :subject, body)
```

Possible reduction:

```python
send(email=email, subject=subject, body=body)
```

This is useful but optional. It should be admitted only if it stays visually
clear.

## 4. Blocks

Ruby's strongest contribution is caller-side blocks. Nomi should make that idea
Python-readable.

```python
retry(3):
    send_request()
```

Zero-argument block call:

```python
transaction(db):
    create_user()
    send_welcome_email()
```

Yielded value block call:

```python
each(users) -> user:
    print(user.name)
```

Multiple yielded values:

```python
pairs(headers) -> key, value:
    print(key, value)
```

Constrained yielded values:

```python
each(users) -> user:User:
    print(user.name)
```

Alternative if the double colon reads poorly:

```python
each(users) -> user(User):
    print(user.name)
```

The block runs in caller scope.

```python
status = "pending"

once():
    status = "done"

print(status)  # "done"
```

Reduction:

```python
retry(3):
    send_request()
```

means:

```python
retry(3, block=<caller block containing send_request()>)
```

and inside `retry`, `yield` invokes that block.

## 5. Control As Library-Defined Blocks

The language should not need a new keyword for every control pattern.

```python
timeout(5):
    fetch(url)
```

```python
lock(my_lock):
    update_shared_state()
```

```python
measure("load users") -> elapsed:
    users = load_users()
```

```python
with_env(DEBUG=True):
    run_tests()
```

```python
capture_logs() -> logs:
    service.run()
print(logs)
```

Possible library-defined concurrency:

```python
parallel():
    fetch_user()
    fetch_orders()
    fetch_recommendations()
```

Possible structured tasks:

```python
scope() -> task:
    user = task.spawn(() => fetch_user())
    orders = task.spawn(() => fetch_orders())
    combine(user.await(), orders.await())
```

Reduction: all are calls with attached blocks. The callee decides when and how
often to `yield`.

## 6. Conditionals As Expressions

Statement style remains valid.

```python
if score >= 90:
    label = "excellent"
else:
    label = "ok"
```

Expression-oriented form:

```python
label = if score >= 90:
    "excellent"
else:
    "ok"
```

Guard-like early exit, inspired by Swift/Kotlin/Rust ergonomics:

```python
guard user is not None:
    return "missing user"

send_welcome(user)
```

Possible reduction:

```python
if not (user is not None):
    return "missing user"
send_welcome(user)
```

`unless` is Ruby-readable but should be used sparingly.

```python
return unless ready
```

Possible reduction:

```python
if not ready:
    return
```

This is concise, but it may hurt Python-like clarity. Candidate only.

## 7. Pattern Matching

Use Python's readable `match`, but allow expression orientation.

```python
match event:
    case {"type": "click", "x": x, "y": y}:
        handle_click(x, y)
    case {"type": "key", "key": key}:
        handle_key(key)
    case _:
        ignore(event)
```

As an expression:

```python
kind = match value:
    case int:
        "number"
    case str:
        "text"
    case [first, *rest]:
        "sequence"
    case _:
        "unknown"
```

Match with constraints:

```python
match user:
    case {"age": age:(int, age >= 18)}:
        allow()
    case _:
        deny()
```

Algebraic-data-like pattern:

```python
match result:
    case Ok(value):
        value
    case Err(error):
        raise error
```

Reduction: `match` is repeated pattern binding plus guards.

## 8. Data Values

Lightweight structured values:

```python
data Point(x:int, y:int)
data User(id:int, name:str, email:str?)
```

Construction:

```python
p = Point(2, 3)
u = User(id=1, name="Ada", email=None)
```

Pattern use:

```python
match p:
    case Point(x, y):
        x + y
```

Default values:

```python
data User(
    id:int,
    name:str,
    active:bool = True,
)
```

Derived fields could be library-level, not core syntax.

```python
data Invoice(items):
    total = items.sum((item) => item.price)
```

Reduction: `data` declares a constructor, named fields, equality, and pattern
shape. It is sugar over ordinary values plus bindings.

## 9. Traits, Protocols, And Interfaces

Scala/Rust/Kotlin suggest named behavioral contracts, but Nomi should keep them
plain.

```python
trait Drawable:
    func draw(self, canvas)
```

```python
trait Sized:
    func len(self) -> int
```

Implementation candidate:

```python
impl Drawable for Circle:
    func draw(self, canvas):
        canvas.circle(self.center, self.radius)
```

Duck-typed protocol candidate:

```python
protocol Reader:
    func read(self, n:int) -> bytes
```

Reduction: a trait/protocol is a named set of function constraints. It should
not require a heavy class hierarchy.

## 10. Extension-Style Functions

Kotlin/Scala-style extension functions improve method usability without forcing
ownership into classes.

```python
func String.words(self):
    return self.split()
```

Use:

```python
"hello world".words()
```

Pipeline-friendly:

```python
text |> String.words
```

Generic extension:

```python
func List[T].second(self) -> T:
    return self[1]
```

Reduction:

```python
"hello".words()
```

means:

```python
String.words("hello")
```

under module-visible extension lookup.

## 11. Pipelines

Nested calls:

```python
result = summarize(normalize(parse(text)))
```

Pipeline:

```python
result = text |> parse |> normalize |> summarize
```

Placeholder form:

```python
result = text |> parse(mode="loose", _) |> normalize(_) |> summarize(_)
```

Multi-line pipeline:

```python
result = (
    text
    |> parse
    |> normalize
    |> summarize
)
```

Pipelines with lambdas:

```python
names = users |> map(_, (u) => u.name) |> sort
```

Pipelines with blocks:

```python
report = users |> group_by(_, (u) => u.team) |> render:
    title = "Users by team"
```

The last example is speculative. The simple rule should be: `|>` rewrites into
a call where the left value is inserted into the next stage.

## 12. Function Composition

Composition builds a function.

```python
clean = strip >> lower >> normalize_space
```

Use:

```python
clean("  HELLO  ")
```

Backward composition may be allowed but is lower priority.

```python
clean = normalize_space << lower << strip
```

Reduction:

```python
(f >> g)(x) == g(f(x))
```

Composition should be for function values, while pipelines are for values now.

## 13. Collection And Array Operations

Readable whole-collection operations:

```python
xs.map((x) => x * 2)
xs.filter((x) => x > 0)
xs.sum()
```

Pipeline style:

```python
total = (
    xs
    |> filter(_, (x) => x > 0)
    |> map(_, (x) => x * 2)
    |> sum
)
```

Comprehension remains Python-like:

```python
doubles = [x * 2 for x in xs if x > 0]
```

Dictionary comprehension:

```python
by_id = {user.id: user for user in users}
```

APL-inspired elementwise shorthand is candidate-only.

```python
ys = xs.*2
zs = xs.+ys
mask = xs.>0
```

Reduction:

```python
xs.*2 == xs.map((x) => x * 2)
xs.+ys == zip(xs, ys).map((x, y) => x + y)
```

Rank-like operation may be library-first:

```python
matrix.each_row() -> row:
    print(row.sum())
```

Instead of dense symbolic rank operators, prefer named operations first.

## 14. Ranges, Slices, And Indexing

Human inclusive range:

```python
1..10
```

Index-friendly half-open range:

```python
0..<n
```

Slicing:

```python
xs[1..<4]
xs[..3]
xs[3..]
xs[..]
```

Step:

```python
xs[0..<10 by 2]
```

Reduction: ranges are values. Slices are indexing calls with range values.

```python
xs[1..<4] == xs.get(range(1, 4, end="open"))
```

## 15. Null, Option, And Result

Kotlin-style safe access:

```python
city = user?.address?.city
```

Fallback:

```python
name = user.name ?: "guest"
```

Required value:

```python
name = user.name!
```

`!` is risky. It should mean "fail here if empty" and should be visually
obvious in code review.

Option-style pattern:

```python
match user.email:
    case Some(email):
        send(email)
    case None:
        skip()
```

Result-style error handling:

```python
result = read_config(path)

match result:
    case Ok(config):
        start(config)
    case Err(error):
        report(error)
```

Try-like propagation candidate:

```python
config = read_config(path)?
start(config)
```

Reduction:

```python
tmp = read_config(path)
match tmp:
    case Ok(value):
        config = value
    case Err(error):
        return Err(error)
```

This is inspired by Rust. It should only exist if Nomi has a clear `Result`
model.

## 16. Errors And Recovery

Python-like exceptions remain familiar.

```python
try:
    load()
except FileNotFoundError as e:
    recover(e)
finally:
    cleanup()
```

Block-based recovery:

```python
retry(3, on=NetworkError):
    fetch(url)
```

Expression recovery:

```python
config = try:
    load_config()
except FileNotFoundError:
    default_config()
```

Reduction: expression `try` is statement `try` whose selected branch produces a
value.

## 17. Loops And Iteration

Keep Python loops.

```python
for user in users:
    print(user.name)
```

Ranges:

```python
for i in 0..<10:
    print(i)
```

Block-defined iteration:

```python
users.each() -> user:
    print(user.name)
```

Loop with destructuring:

```python
for key, value in pairs:
    print(key, value)
```

Loop with constraints:

```python
for user:User in users:
    print(user.name)
```

Reduction: loop variable binding is binding with optional constraints.

## 18. Modules And Use

Python-compatible imports should remain.

```python
import math
from pathlib import Path
```

Candidate `use` for bringing extension functions, traits, or rule sets into
scope:

```python
use text.words
use math.vector.*
```

Reduction: `use` is controlled import plus scope-visible capabilities.

Local alias:

```python
import numpy as np
use dataframe as df
```

The design should avoid hidden global mutation.

## 19. Symbolic Expressions

Quote expression-shaped code:

```python
expr = quote:
    x + 0
```

Short quote for small expressions:

```python
expr = '(x + 0)
```

Inspect:

```python
expr.head
expr.args
```

Evaluate explicitly:

```python
value = eval(expr, env={"x": 3})
```

Reduction: quoted syntax produces an explicit expression value. It does not run
as ordinary code until passed to an evaluator.

## 20. Rewrite Rules

Mathematica-style transformation:

```python
simplified = expr /. x + 0 -> x
```

Multiple rules:

```python
simplified = expr /. [
    x + 0 -> x,
    0 + x -> x,
    x * 1 -> x,
    1 * x -> x,
]
```

Repeated rewrite:

```python
normal = expr //. [
    x + 0 -> x,
    x * 1 -> x,
]
```

Conditional rule:

```python
expr /. n -> n * 2 if n:int
```

Function-backed rule:

```python
expr /. Call(name, args) -> lower_call(name, args)
```

Reduction: rewriting is pattern matching over explicit expression values plus
construction of replacement expression values.

## 21. Macros And Compile-Time Transformation

Lisp teaches that macros are powerful because code can be represented as data.
Nomi should be cautious here.

Candidate:

```python
macro assert_equal(left, right):
    quote:
        if {left} != {right}:
            raise AssertionError(f"{left} != {right}")
```

Use:

```python
assert_equal(user.name, "Ada")
```

Reduction: a macro is a function from quoted syntax to quoted syntax, expanded
before normal evaluation.

Restriction: macros should be explicit imports and should not silently change
the meaning of ordinary local syntax.

## 22. String And Template Syntax

Keep Python-like f-strings.

```python
message = f"Hello {user.name}"
```

Multi-line:

```python
sql = f"""
select *
from users
where team = {team_id}
"""
```

Safe template block candidate:

```python
query = sql():
    select *
    from users
    where team = {team_id}
```

Reduction: tagged blocks are function/block calls over raw text or quoted
syntax.

```python
sql:
    select * from users
```

means:

```python
sql(block_text)
```

or:

```python
sql(block_expression)
```

depending on the tag.

## 23. Object And Method Syntax

Class syntax can remain Python-like.

```python
class Account:
    func deposit(self, amount:(int, amount > 0)):
        self.balance += amount
```

Data values should cover many class use cases:

```python
data Account(id:int, balance:int)
```

Property-like computed members:

```python
class Circle:
    func area(self):
        return pi * self.radius * self.radius
```

Candidate property sugar:

```python
class Circle:
    prop area:
        pi * self.radius * self.radius
```

Reduction:

```python
prop area: expr
```

means a zero-argument method exposed as field-like access.

## 24. Query And Dataflow Syntax

LINQ/SQL-like readability is useful, but should probably be library-led.

Pipeline query:

```python
active_names = (
    users
    |> filter(_, (u) => u.active)
    |> map(_, (u) => u.name)
    |> sort
)
```

Query block candidate:

```python
query users -> u:
    where u.active
    select u.name
    order by u.name
```

Reduction: query blocks are quoted or block-structured calls to a query builder.

The pipeline form should be preferred until query syntax proves its value.

## 25. Tests And Assertions

Tests are good examples for block syntax.

```python
test "withdraw reduces balance":
    account = Account(balance=100)
    account.withdraw(30)
    assert account.balance == 70
```

Parameterized:

```python
cases([(1, 2, 3), (2, 3, 5)]) -> a, b, expected:
    test f"{a} + {b}":
        assert add(a, b) == expected
```

Reduction: `test` can be a block call that registers and runs a caller-side
block. It does not need to be a primitive keyword at first.

## 26. Effects And Actions

Nomi should distinguish value-shaped code from action-shaped code through usage,
not heavy ceremony.

Value:

```python
total = items.sum((x) => x.price)
```

Action:

```python
for item in items:
    save(item)
```

Action block:

```python
transaction(db):
    for item in items:
        save(item)
```

Possible effect annotation:

```python
func save_user(user) !io:
    db.save(user)
```

This is speculative. If effects enter the language, they should be constraints
on functions/actions, not a separate programming model.

## 27. Async And Concurrency

Python's `async` is familiar, but structured concurrency may be more usable.

```python
async func fetch_user(id):
    return await http.get(f"/users/{id}")
```

Block scope:

```python
async_scope() -> task:
    user = task.spawn(() => fetch_user(id))
    orders = task.spawn(() => fetch_orders(id))
    render(await user, await orders)
```

Candidate lighter syntax:

```python
async:
    user = spawn fetch_user(id)
    orders = spawn fetch_orders(id)
    render(await user, await orders)
```

The block-call version is more consistent with the small core. Dedicated syntax
should wait until the pattern is stable.

## 28. Defer And Cleanup

Go/Swift-style `defer` is useful but reducible to block cleanup.

```python
func write_file(path, text):
    f = open(path, "w")
    defer f.close()
    f.write(text)
```

Reduction:

```python
with open(path, "w") as f:
    f.write(text)
```

or a block-control cleanup stack. Candidate only, because block calls may cover
most cleanup use cases.

## 29. Named Blocks And Local Structure

ALGOL-like block structure can improve local organization.

```python
block:
    temp = compute()
    result = normalize(temp)
```

Scoped block candidate:

```python
scope:
    temp = compute()
    result = normalize(temp)
print(temp)  # error if scope is isolated
```

Nomi's default block calls use caller scope. Isolated scopes should be explicit.

```python
isolated:
    temp = compute()
```

Reduction: a scoped block is a function/block call with an explicit environment
policy.

## 30. Style Summary

Preferred Nomi syntax should look like this:

```python
data User(id:int, name:str, email:str?)

func active_email(user:User) -> str?:
    if user.active:
        user.email
    else:
        None

emails = (
    users
    |> filter(_, (u) => u.active)
    |> map(_, active_email)
    |> filter(_, (email) => email is not None)
)

retry(3, on=NetworkError):
    send_batch(emails)
```

The code is Python-readable, but it has:

- constrained bindings,
- expression-oriented functions,
- data declarations,
- pipeline flow,
- block-based retry control.

All of it reduces to the small core: values, bindings, functions, calls,
patterns, constraints, blocks, and explicit control around `yield`.

---

<a id="documentation-design-review-archive-cross-language-feature-synthesis-md"></a>

# Source: `documentation/design_review_archive/cross_language_feature_synthesis.md`

# Cross-Language Feature Synthesis Examples

> Status: comparative design study.
>
> This document compares similar but not identical language features across
> several well-loved languages, then proposes a Nomi synthesis for each family.
> The emphasis is surface usability plus reduction to a small core.

## Reading Guide

Each section follows the same pattern:

- the recurring programming need,
- representative syntax from existing languages,
- what each language gets right,
- what creates friction,
- proposed Nomi syntax,
- reduction to Nomi primitives.

The recurring primitives are:

```text
value
binding
constraint
function
call
block
yield
pattern
quote
rewrite
```

## 1. Naming Functions

### Recurring Need

Define reusable behavior and bind it to a name.

### Existing Forms

Python:

```python
def add(x, y):
    return x + y
```

Ruby:

```ruby
def add(x, y)
  x + y
end
```

Scala:

```scala
def add(x: Int, y: Int): Int =
  x + y
```

Kotlin:

```kotlin
fun add(x: Int, y: Int): Int {
    return x + y
}
```

Scheme:

```scheme
(define (add x y)
  (+ x y))
```

Mathematica:

```wolfram
add[x_, y_] := x + y
```

### Observations

Python and Ruby are readable but `def` is generic. Kotlin's `fun` is explicit
but informal. Scala separates expression-bodied and block-bodied definitions.
Scheme is semantically regular but visually foreign to Python readers.
Mathematica's pattern-based definition is powerful, but `_` patterns in the
definition head are not beginner-friendly.

### Nomi Synthesis

```python
func add(x:int, y:int) -> int:
    x + y
```

or, when an explicit return is clearer:

```python
func add(x:int, y:int) -> int:
    return x + y
```

Expression form:

```python
add = (x:int, y:int) => x + y
```

### Reduction

```python
func add(x:int, y:int) -> int:
    x + y
```

reduces to:

```text
bind name `add`
to function value with parameters x, y
validate x:int and y:int when called
evaluate body
validate return:int if return constraint is present
```

## 2. Anonymous Functions And Function Literals

### Existing Forms

Python:

```python
lambda x: x + 1
```

JavaScript:

```javascript
x => x + 1
(x, y) => x + y
```

Scala:

```scala
(x: Int) => x + 1
```

Kotlin:

```kotlin
{ x: Int -> x + 1 }
```

Ruby:

```ruby
->(x) { x + 1 }
```

Haskell:

```haskell
\x -> x + 1
```

APL:

```apl
{right + 1}
```

### Observations

JavaScript and Scala arrows are readable and familiar. Kotlin/Ruby blocks are
good in call positions, but less uniform with named functions. Python's
`lambda` is constrained and visually unlike `def`. Haskell and APL are compact
but not aligned with Nomi's readability goal.

### Nomi Synthesis

```python
(x) => x + 1
(x:int) => x + 1
(x:int, y:int) => x + y
```

Multi-line:

```python
(user) =>:
    base = user.score
    bonus = user.reviews * 2
    base + bonus
```

### Reduction

Arrow functions create ordinary function values. Multi-line arrows are sugar for
anonymous `func` values whose final expression is returned.

## 3. Binding, Declaration, And Mutation

### Existing Forms

Python:

```python
x = 1
x: int = 1
```

JavaScript:

```javascript
let x = 1
const y = 2
```

Kotlin:

```kotlin
var x = 1
val y = 2
```

Rust:

```rust
let x = 1;
let mut y = 2;
```

Scala:

```scala
var x = 1
val y = 2
```

Mathematica:

```wolfram
x = 1
x := RandomInteger[]
```

### Observations

Python is light but does not distinguish constant intent. Kotlin/Scala/Rust make
mutability explicit but add declaration ceremony. Mathematica distinguishes
immediate and delayed binding, an important symbolic/programming distinction.

### Nomi Synthesis

Default simple binding:

```python
x = 1
```

Constrained binding:

```python
x:int = 1
x:int, x > 0 = 1
```

Constant binding:

```python
const max_retries:int = 3
```

Delayed binding candidate:

```python
now := clock.time()
```

Possible meaning: `now` evaluates its right side each time it is used. This is
Mathematica-inspired and should remain candidate syntax because delayed
evaluation can harm local reasoning.

### Reduction

```python
const x:int = 1
```

reduces to:

```text
bind x to 1
validate int
mark binding as non-rebindable
```

```python
now := clock.time()
```

reduces to:

```text
bind now to a zero-argument delayed expression/function
evaluate on access
```

## 4. Type Hints, Contracts, And Guards

### Existing Forms

Python:

```python
def f(x: int) -> int:
    return x + 1
```

TypeScript:

```typescript
function f(x: number): number {
  return x + 1
}
```

Kotlin:

```kotlin
fun f(x: Int): Int = x + 1
```

Eiffel-style contract idea:

```text
require x > 0
ensure result > x
```

Rust:

```rust
fn f(x: i32) -> i32 { x + 1 }
```

Racket contracts:

```scheme
(-> integer? integer?)
```

### Observations

Type annotations are widely understood. Contracts are semantically valuable but
often syntactically heavy or external to the function signature.

### Nomi Synthesis

```python
func sqrt(x:(float, x >= 0)) -> float:
    ...
```

Named constraints:

```python
positive = (x) => x > 0

func charge(amount:(Money, positive)):
    ...
```

Postcondition candidate:

```python
func inc(x:int) -> result:(int, result > x):
    x + 1
```

Block contract candidate:

```python
func transfer(from, to, amount:(Money, amount > 0)):
    require from.balance >= amount
    ...
    ensure from.balance == old(from.balance) - amount
```

### Reduction

Constraints reduce to predicates checked at binding boundaries. Return
constraints are binding constraints on the implicit `result` binding.

## 5. Blocks, Closures, And Trailing Lambdas

### Existing Forms

Ruby:

```ruby
3.times do |i|
  puts i
end
```

Kotlin:

```kotlin
users.forEach { user ->
    println(user.name)
}
```

Scala:

```scala
users.foreach { user =>
  println(user.name)
}
```

JavaScript:

```javascript
users.forEach(user => {
  console.log(user.name)
})
```

Python:

```python
for user in users:
    print(user.name)
```

### Observations

Ruby/Kotlin/Scala are excellent at passing behavior into library calls. Python
is excellent at making loops visually explicit. Nomi should combine these:
library-defined control with Python-like indentation.

### Nomi Synthesis

```python
users.each() -> user:
    print(user.name)
```

```python
retry(3):
    send_request()
```

```python
transaction(db):
    create_user()
    send_email()
```

### Reduction

All reduce to calls with attached caller-side blocks. The block is invoked by
`yield` in the callee.

## 6. Context Managers, Resource Scope, And Cleanup

### Existing Forms

Python:

```python
with open(path) as f:
    data = f.read()
```

Ruby:

```ruby
File.open(path) do |f|
  data = f.read
end
```

C#:

```csharp
using var f = File.Open(path);
```

Go:

```go
defer file.Close()
```

Swift:

```swift
defer { cleanup() }
```

### Observations

Python's `with` is very readable but specialized. Ruby's block style generalizes
better. Go/Swift `defer` is useful inside functions, but can hide cleanup order.

### Nomi Synthesis

General block:

```python
using(open(path)) -> f:
    data = f.read()
```

Domain-specific helper:

```python
file(path) -> f:
    data = f.read()
```

Cleanup candidate:

```python
func write(path, text):
    f = open(path, "w")
    defer f.close()
    f.write(text)
```

### Reduction

`using(resource) -> x:` is a block call that yields the acquired value and
performs cleanup after the block returns or raises.

## 7. Pattern Matching And Destructuring

### Existing Forms

Python:

```python
match value:
    case {"name": name}:
        print(name)
```

Scala:

```scala
value match {
  case Some(x) => x
  case None => 0
}
```

Rust:

```rust
match result {
    Ok(value) => value,
    Err(error) => return Err(error),
}
```

Elixir:

```elixir
{:ok, value} = result
```

Haskell:

```haskell
case result of
  Just x -> x
  Nothing -> 0
```

Mathematica:

```wolfram
expr /. f[x_] -> x
```

### Observations

Pattern matching is one of the strongest cross-language ideas. The friction is
surface syntax: Python is readable but statement-oriented; Scala/Rust/Haskell
are powerful but visually less Python-like; Mathematica is extremely powerful
for symbolic expressions.

### Nomi Synthesis

Statement:

```python
match result:
    case Ok(value):
        use(value)
    case Err(error):
        report(error)
```

Expression:

```python
value = match result:
    case Ok(value):
        value
    case Err(error):
        default
```

Binding:

```python
Ok(value) = result
```

Constrained:

```python
case User(age:(int, age >= 18)):
    allow()
```

### Reduction

Patterns are shape tests plus binding. Match is ordered pattern testing with
optional guards.

## 8. Null, Option, Maybe, And Result

### Existing Forms

Python:

```python
if user is not None:
    city = user.address.city
```

Kotlin:

```kotlin
val city = user?.address?.city ?: "unknown"
```

Swift:

```swift
let city = user?.address?.city ?? "unknown"
```

Rust:

```rust
let city = user.and_then(|u| u.address).map(|a| a.city);
```

Haskell:

```haskell
case maybeUser of
  Just user -> ...
  Nothing -> ...
```

Scala:

```scala
user.map(_.address).map(_.city).getOrElse("unknown")
```

### Observations

Kotlin/Swift are best for everyday ergonomics. Rust/Haskell/Scala model absence
more explicitly. Python is readable but verbose and error-prone for nested
access.

### Nomi Synthesis

Everyday:

```python
city = user?.address?.city ?: "unknown"
```

Explicit:

```python
match user:
    case Some(user):
        user.address.city
    case None:
        "unknown"
```

Result:

```python
config = read_config(path)?
```

### Reduction

Safe access desugars to conditional match over empty/non-empty values. `?`
result propagation desugars to `match Ok/Err`.

## 9. Pipelines, Method Chains, And Postfix Application

### Existing Forms

Unix shell:

```sh
cat file | grep error | sort
```

F#:

```fsharp
text |> parse |> normalize |> summarize
```

Elixir:

```elixir
text |> parse() |> normalize() |> summarize()
```

Mathematica:

```wolfram
text // parse // normalize // summarize
```

Kotlin:

```kotlin
text.parse().normalize().summarize()
```

Python:

```python
summarize(normalize(parse(text)))
```

### Observations

Pipelines are best when the dataflow matters more than nesting. Method chains
are readable when operations naturally belong to the receiver. Python nested
calls become hard to scan.

### Nomi Synthesis

```python
summary = text |> parse |> normalize |> summarize
```

With placeholders:

```python
summary = text |> parse(mode="loose", _) |> summarize(style="short", _)
```

With collection operations:

```python
names = users |> filter(_, active) |> map(_, name) |> sort
```

### Reduction

`x |> f` becomes `f(x)`. `x |> f(_, y)` becomes `f(x, y)`.

## 10. Comprehensions, Maps, Queries, And Array Thinking

### Existing Forms

Python:

```python
[x * 2 for x in xs if x > 0]
```

Haskell:

```haskell
[x * 2 | x <- xs, x > 0]
```

Scala:

```scala
for x <- xs if x > 0 yield x * 2
```

LINQ:

```csharp
from x in xs
where x > 0
select x * 2
```

APL:

```apl
2 * xs
```

Mathematica:

```wolfram
Select[xs, # > 0 &] * 2
```

### Observations

Python comprehensions are compact and readable for simple cases. LINQ/query
syntax is excellent for tabular domains. APL is extremely concise for arrays but
not self-explanatory to broad audiences.

### Nomi Synthesis

Comprehension:

```python
doubles = [x * 2 for x in xs if x > 0]
```

Pipeline:

```python
doubles = xs |> filter(_, (x) => x > 0) |> map(_, (x) => x * 2)
```

Query candidate:

```python
query users -> u:
    where u.active
    select u.name
    order by u.name
```

Array shorthand candidate:

```python
ys = xs.*2
```

### Reduction

All reduce to iteration, binding, predicate calls, and result construction.

## 11. Data Modeling

### Existing Forms

Python dataclass:

```python
@dataclass
class User:
    id: int
    name: str
```

Kotlin:

```kotlin
data class User(val id: Int, val name: String)
```

Scala:

```scala
case class User(id: Int, name: String)
```

Rust:

```rust
struct User {
    id: i32,
    name: String,
}
```

Haskell:

```haskell
data User = User { id :: Int, name :: String }
```

### Observations

Kotlin/Scala are strongest for concise value data. Python dataclasses are useful
but decorator-plus-class is a workaround. Rust/Haskell are explicit but heavier
for everyday scripting.

### Nomi Synthesis

```python
data User(id:int, name:str, active:bool = True)
```

Pattern:

```python
case User(id, name, active=True):
    ...
```

Copy/update candidate:

```python
new_user = user with {active = False}
```

### Reduction

Data declarations bind a constructor, field accessors, equality, representation,
and pattern shape.

## 12. Traits, Protocols, Typeclasses, And Interfaces

### Existing Forms

Java/Kotlin:

```kotlin
interface Drawable {
    fun draw(canvas: Canvas)
}
```

Rust:

```rust
trait Drawable {
    fn draw(&self, canvas: Canvas);
}
```

Haskell:

```haskell
class Drawable a where
  draw :: a -> Canvas -> Canvas
```

Python:

```python
class Drawable(Protocol):
    def draw(self, canvas): ...
```

Scala:

```scala
trait Drawable {
  def draw(canvas: Canvas): Unit
}
```

### Observations

These features all express named behavioral expectations. The main difference is
nominal versus structural matching and whether implementation is attached to the
type or discovered externally.

### Nomi Synthesis

Nominal-ish:

```python
trait Drawable:
    func draw(self, canvas)

impl Drawable for Circle:
    func draw(self, canvas):
        canvas.circle(self.center, self.radius)
```

Structural:

```python
protocol Drawable:
    func draw(self, canvas)
```

### Reduction

Traits/protocols are named sets of function constraints. `impl` binds functions
into a dispatch table or capability scope.

## 13. Extension Methods And Open Functions

### Existing Forms

Kotlin:

```kotlin
fun String.words(): List<String> = split(" ")
```

Scala:

```scala
extension (s: String)
  def words = s.split(" ")
```

C#:

```csharp
public static Words(this string s) { ... }
```

Ruby:

```ruby
class String
  def words
    split(" ")
  end
end
```

### Observations

Extension methods improve fluent APIs. Ruby's monkey patching is powerful but
globally risky. Kotlin/Scala keep extensions more scoped.

### Nomi Synthesis

```python
func String.words(self):
    self.split(" ")
```

Use:

```python
"a b c".words()
```

Scoped import:

```python
use text.extensions.words
```

### Reduction

Method syntax reduces to a function call with receiver as first argument, using
module-visible extension lookup.

## 14. Macros, Templates, And Code Generation

### Existing Forms

Lisp:

```scheme
(define-syntax unless
  ...)
```

Rust:

```rust
println!("x = {}", x);
```

Template Haskell:

```haskell
$(deriveJSON ''User)
```

Scala:

```scala
inline def ...
```

Mathematica:

```wolfram
Hold[expr]
```

### Observations

Macros are useful when the language can represent code as data. They are also
one of the easiest ways to destroy local readability.

### Nomi Synthesis

```python
macro assert_equal(left, right):
    quote:
        if {left} != {right}:
            raise AssertionError(f"{left} != {right}")
```

Use:

```python
assert_equal(user.name, "Ada")
```

### Reduction

Macros are functions from quoted expression values to quoted expression values,
expanded in explicit macro scope.

## 15. Symbolic Rewrite And Rule-Based Programming

### Existing Forms

Mathematica:

```wolfram
expr /. x_ + 0 -> x
expr //. rules
```

Prolog:

```prolog
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
```

Stratego/rewrite systems:

```text
Plus(x, Zero) -> x
```

Lisp:

```scheme
(match expr
  [`(+ ,x 0) x])
```

### Observations

Rewrite systems are excellent for symbolic domains, compilers, optimizers, and
mathematics. They should operate over explicit expression data, not ordinary
runtime code invisibly.

### Nomi Synthesis

```python
expr = quote:
    (x + 0) * 1

normal = expr //. [
    x + 0 -> x,
    x * 1 -> x,
]
```

### Reduction

Rules are pattern functions over expression values. `/.` applies once; `//.`
applies until stable.

## 16. Error Handling

### Existing Forms

Python:

```python
try:
    work()
except Error as e:
    recover(e)
```

Go:

```go
value, err := work()
if err != nil { return err }
```

Rust:

```rust
let value = work()?;
```

Swift:

```swift
let value = try work()
```

Haskell:

```haskell
Either Error Value
```

### Observations

Exceptions are readable for exceptional control. Result values are better when
failure is part of the ordinary API contract. Go is explicit but repetitive.
Rust is concise because the `?` operator has a clear `Result` model.

### Nomi Synthesis

Exceptions:

```python
try:
    work()
except Error as e:
    recover(e)
```

Result:

```python
value = work()?
```

Pattern:

```python
match work():
    case Ok(value):
        use(value)
    case Err(error):
        recover(error)
```

### Reduction

`?` is syntax over `match Ok/Err` and early return from the current function.

## 17. Modules, Imports, And Capability Scope

### Existing Forms

Python:

```python
from math import sqrt
```

Rust:

```rust
use std::collections::HashMap;
```

Haskell:

```haskell
import qualified Data.Map as Map
```

JavaScript:

```javascript
import { sqrt } from "math"
```

### Observations

Imports do more than bring names into scope. They may also bring extension
methods, traits, macros, and rewrite rules. Nomi should make such capabilities
visible.

### Nomi Synthesis

```python
import math
from math import sqrt
use text.extensions.words
use symbolic.algebra.rules as algebra
```

### Reduction

`import` binds names. `use` brings scoped capabilities into the current module:
extensions, traits, macros, or rules.

## 18. Summary Matrix

| Need | Python | Ruby | Scala/Kotlin | Lisp/Mathematica/APL | Proposed Nomi |
| --- | --- | --- | --- | --- | --- |
| Function | `def` | `def` | `def` / `fun` | `define`, `f[x_] :=` | `func` |
| Function value | `lambda` | `-> {}` | `=>`, `{ -> }` | `lambda`, pure funcs | `(x) => expr` |
| Block control | `with`, loops | `do/end` blocks | trailing lambdas | higher-order funcs | `call(args): block` |
| Binding constraints | hints only | dynamic | types | predicates/patterns | `x:int, pred = v` |
| Pattern matching | `match` | limited | strong | symbolic patterns | `match`, pattern binding |
| Pipeline | nested calls | method chains | chains | `//`, array flow | `value |> f` |
| Data values | dataclass | Struct | data/case class | records/expressions | `data User(...)` |
| Null safety | manual | nil chaining | `?.`, `?:` | Maybe-like | `?.`, `?:`, match |
| Symbolic rewrite | AST libs | metaprogramming | macros/libs | native rules | `quote`, `/.`, `//.` |

The synthesis is intentionally conservative at the core and ambitious at the
surface. Each proposed surface form should remain peelable back to primitives.

---

<a id="documentation-design-review-archive-radical-language-feature-ideas-md"></a>

# Source: `documentation/design_review_archive/radical_language_feature_ideas.md`

# Radical Language Feature Ideas

> Status: wild design notebook.
>
> This document is intentionally more speculative than the other Nomi design
> documents. It explores language features that may be difficult, unfamiliar, or
> socially risky, but are at least theoretically implementable. The criterion is
> not contemporary implementation ease. The criterion is whether a feature could
> make programming radically easier to use while still having a possible semantic
> account.

## Spirit

This document takes inspiration from:

- Leibniz: a calculus of thought, symbolic notation that helps humans reason.
- Boole: algebraic manipulation of logic.
- Dijkstra: calculational program derivation, weakest preconditions, guarded
  commands, structured reasoning.
- Iverson/APL: notation as a tool of thought.
- Lisp: programs as manipulable symbolic objects.
- Mathematica: rules, symbolic forms, transformation, and evaluation control.
- Prolog: relations, search, and unification.
- Haskell/ML: algebraic structure, equations, types, and purity as leverage.
- Smalltalk/Ruby: message passing and blocks as humane control.
- Spreadsheets: live dependency graphs and approachable reactive computation.

The attitude:

> A program should be not only instructions for a machine, but a manipulable
> object of reasoning for a human.

## Radical Design Permission

The rest of Nomi should remain Python-readable and reducible to a small core.
This document permits more aggressive ideas, provided they can still be given a
semantics in terms of:

```text
value
binding
constraint
function
call
block
yield
pattern
quote
rewrite
relation
proof
time
world
```

The last four are new speculative primitives:

- `relation`: a predicate-like definition that can be queried in multiple
  directions.
- `proof`: a checkable justification object.
- `time`: versioned or evolving values.
- `world`: an explicit boundary for external effects.

## 1. Calculational Blocks

Dijkstra-style programming treats programs as things one can derive and
transform, not merely write.

### Sample

```python
calc:
    sum([1, 2, 3, 4])
== 1 + 2 + 3 + 4
== 3 + 3 + 4
== 6 + 4
== 10
```

Meaning: each step must be justified by equality, a known rewrite rule, or an
explicit named reason.

With reasons:

```python
calc:
    sum(xs + ys)
== sum(xs) + sum(ys)       by sum_concat
== total_x + total_y       where total_x = sum(xs), total_y = sum(ys)
```

### Function Derivation

```python
derive func triangle(n:int, n >= 0) -> int:
    goal:
        result == sum(1..n)

    calc:
        sum(1..n)
    == n * (n + 1) / 2     by arithmetic_series

    return n * (n + 1) / 2
```

### Reduction

A `calc` block is quoted expression syntax plus rewrite/proof checking. It can
be ignored at runtime after verification, or retained as metadata.

## 2. Guarded Commands

Dijkstra's guarded command language made nondeterminism and preconditions
explicit.

### Sample

```python
choose:
    when x >= y:
        max = x
    when y >= x:
        max = y
```

If multiple guards are true, any branch may be selected unless determinism is
requested.

Deterministic form:

```python
choose one:
    when status == 200:
        handle_ok()
    when status >= 400:
        handle_error()
    otherwise:
        handle_unknown()
```

Parallel guarded assignment:

```python
do:
    when x > 0:
        x -= 1
    when y > 0:
        y -= 1
until x == 0 and y == 0
```

### Why It Is Interesting

This gives algorithms a direct notation for "any enabled step is valid." It is
closer to specifications, distributed algorithms, and search problems than
ordinary sequential `if`.

### Reduction

Guarded commands reduce to a set of predicate/block pairs plus a scheduler
policy:

```text
evaluate guards
select enabled branch according to policy
run selected branch
```

## 3. Boolean Algebra As Code

Boole's insight: logic can be calculated.

### Sample

```python
logic:
    allowed = admin or (owner and not suspended)

minimize allowed:
    admin or owner and not suspended
```

Truth-table generation:

```python
truth allowed(admin, owner, suspended):
    admin or (owner and not suspended)
```

Possible output value:

```python
[
    {admin=False, owner=False, suspended=False, allowed=False},
    {admin=False, owner=True,  suspended=False, allowed=True},
    ...
]
```

Boolean proof:

```python
prove:
    not (a and b) == (not a) or (not b)
by boolean_algebra
```

### Use In Real Code

```python
policy can_delete(user, document):
    user.admin or (
        document.owner == user
        and not document.locked
        and not user.suspended
    )

explain can_delete(alice, report)
```

Possible explanation:

```text
can_delete = true because:
  document.owner == user
  document.locked == false
  user.suspended == false
```

### Reduction

Boolean policy syntax reduces to ordinary expressions plus quoted expression
trees that can be simplified, evaluated, and explained.

## 4. Relations Instead Of One-Way Functions

Functions compute in one direction. Relations describe constraints that may be
queried in multiple directions.

### Sample

```python
rel parent(parent, child)
rel ancestor(a, b):
    parent(a, b)
or:
    parent(a, x)
    ancestor(x, b)
```

Query:

```python
find x where ancestor("Ada", x)
```

Reverse query:

```python
find x where ancestor(x, "Grace")
```

### Arithmetic Relations

```python
rel add(x, y, z):
    x + y == z

find y where add(2, y, 10)   # y = 8
find x, y where add(x, y, 10), x > 0, y > 0
```

### User-Friendly Constraint Solving

```python
solve:
    monthly_payment * months == principal + interest
    principal == 10000
    months == 24
    interest == 1200
for monthly_payment
```

### Reduction

Relations reduce to predicates over values plus a search/unification engine.
This is not easy, but it is theoretically clean.

## 5. Bidirectional Functions

Some transformations are naturally reversible. Make that explicit.

### Sample

```python
bidir celsius_fahrenheit:
    f = c * 9 / 5 + 32
```

Use forward:

```python
fahrenheit = celsius_fahrenheit(c=100).f
```

Use backward:

```python
celsius = celsius_fahrenheit(f=212).c
```

### Structured Parser/Printer

```python
bidir iso_date:
    text = f"{year}-{month:02}-{day:02}"
```

```python
iso_date(year=2026, month=5, day=7).text
iso_date(text="2026-05-07").year
```

### Reduction

A bidirectional function is a relation with preferred projections and possibly
declared invertibility constraints.

## 6. Live Values And Time Travel

Spreadsheets are popular because values update when dependencies change.
Languages should be able to express this deliberately.

### Sample

```python
live subtotal = items.sum((item) => item.price)
live tax = subtotal * tax_rate
live total = subtotal + tax
```

When `items` changes, `subtotal`, `tax`, and `total` update.

### Timeline Values

```python
timeline balance:
    starts 0
    deposit(amount) => balance + amount
    withdraw(amount) if balance >= amount => balance - amount
```

Query:

```python
balance.at("2026-05-07")
balance.history()
balance.explain_change(at=event_id)
```

### Time Travel Debugging

```python
debug timeline:
    run program
    watch user.balance
    rewind to before failed_payment
```

### Reduction

`live` bindings form a dependency graph. `timeline` values are event-sourced
state with versioned bindings.

## 7. World-Passing Effects

Effects can be made explicit without making user code unbearable.

### Sample

```python
func save_user(user) using world:
    world.db.users.insert(user)
    world.log.info(f"saved {user.id}")
```

Call:

```python
save_user(user) in production_world
```

Test:

```python
test "save user":
    fake = world.memory()
    save_user(user) in fake
    assert fake.db.users.contains(user)
```

### Capability Slices

```python
func send_email(email) using world.mail, world.log:
    world.mail.send(email)
    world.log.info("sent")
```

### Reduction

Effects are explicit parameters. `world` is a structured value containing
capabilities. The syntax is sugar over dependency injection, but much more
pleasant.

## 8. Explainable Execution

Programs should be able to explain their own decisions.

### Sample

```python
explainable func approve(application):
    application.score >= 700
    and application.income > application.debt * 3
    and not application.flagged
```

Use:

```python
decision = approve(app)
print(decision.value)
print(decision.why)
```

Possible output:

```text
approved because:
  score >= 700                 true, 742 >= 700
  income > debt * 3            true, 9000 > 2000 * 3
  not flagged                  true
```

### Debuggable Branches

```python
if explain user.can_delete(document):
    delete(document)
else -> reason:
    show(reason)
```

### Reduction

An explainable function evaluates an expression while retaining a proof tree or
trace tree for predicates and branches.

## 9. Proof-Carrying Programs

Let programs carry small checkable proofs about their behavior.

### Sample

```python
func abs(x:int) -> result:(int, result >= 0):
    if x >= 0:
        x
    else:
        -x
proof:
    case x >= 0:
        result == x
        x >= 0
    case x < 0:
        result == -x
        -x > 0
```

### Loop Invariant

```python
func sum_to(n:int, n >= 0) -> int:
    total = 0
    i = 0

    while i <= n
    invariant total == sum(0..<i):
        total += i
        i += 1

    total
```

### Reduction

Proof blocks are quoted logical assertions checked by a verifier, theorem
prover, SMT solver, or runtime assertion system.

## 10. Intent Blocks

Sometimes the user knows the desired property better than the algorithm.

### Sample

```python
intent sort_users(users):
    produce result
    where:
        result.permutation_of(users)
        result.every_adjacent((a, b) => a.name <= b.name)
    prefer:
        stable
        O(n log n)
```

The implementation may be synthesized, selected from a library, or checked
against the intent.

Manual implementation with intent:

```python
func sort_users(users)
ensures:
    result.permutation_of(users)
    result.every_adjacent((a, b) => a.name <= b.name)
:
    merge_sort(users, by=(u) => u.name)
```

### Reduction

Intent blocks are constraints over input/output behavior. They can be checked,
used for synthesis, or used as executable tests.

## 11. Holes And Typed Questions

Let unfinished code be first-class.

### Sample

```python
func invoice_total(invoice):
    subtotal = invoice.items.sum((item) => item.price)
    tax = ?
    subtotal + tax
```

The environment can report:

```text
hole tax:
  expected: Money
  available:
    subtotal: Money
    invoice.tax_rate: Rate
  possible:
    subtotal * invoice.tax_rate
```

Named holes:

```python
tax = ?tax
```

Constraint hole:

```python
discount = ? where 0 <= discount <= subtotal
```

### Reduction

A hole is an explicit placeholder value with required constraints and available
context. It is not runtime `None`; it is an incomplete program marker.

## 12. Semantic Search In The Language

Search for code by what it does, not by its name.

### Sample

```python
use function where:
    input: list[int]
    output: int
    ensures result == input.max()
as max_int
```

Ask the environment:

```python
find function:
    takes User
    returns str
    mentions email
```

### Reduction

Semantic search queries metadata, types/constraints, tests, examples, and proof
objects. This is a language-integrated tooling feature, not magic execution.

## 13. Examples As Semantics

Examples can be more than tests; they can define intended behavior.

### Sample

```python
func slugify(text):
examples:
    "Hello World" => "hello-world"
    " Nomi  Lang " => "nomi-lang"
    "A+B" => "a-b"
:
    text.lower().strip().replace(non_word+, "-")
```

Example-driven hole:

```python
func slugify(text):
examples:
    "Hello World" => "hello-world"
    "A+B" => "a-b"
:
    ?
```

### Reduction

Examples are input/output constraints. They can run as tests, guide synthesis,
or document behavior.

## 14. Units And Dimensions As Bindings

Leibniz wanted notation to prevent error. Units are a practical case.

### Sample

```python
distance = 10 meter
time = 2 second
speed = distance / time
```

The language knows:

```python
speed : meter / second
```

Invalid:

```python
distance + time  # DimensionError
```

Conversions:

```python
height = 6 foot
height in meter
```

### Domain Units

```python
unit USD
unit EUR

price = 10 USD
tax = 2 USD
total = price + tax
```

### Reduction

Units are constraints attached to numeric values, with algebra over dimensions.

## 15. Algebraic Effects As Friendly Blocks

Effect systems are usually hard to use. Blocks can make them humane.

### Sample

```python
effect Ask[T]:
    ask(prompt:str) -> T

func signup():
    name = ask("name?")
    email = ask("email?")
    User(name, email)
```

Handle:

```python
handle Ask with form_answers:
    user = signup()
```

Test:

```python
handle Ask with ["Ada", "ada@example.com"]:
    assert signup().name == "Ada"
```

### Reduction

Effects are resumable operations. Handlers are block-control functions that
decide how to resume.

## 16. Conversations As Programs

Many programs are interaction protocols. Make the protocol explicit.

### Sample

```python
dialog checkout:
    ask shipping_address -> address
    ask payment_method -> payment
    confirm order(address, payment) -> ok
    when ok:
        submit_order()
    otherwise:
        cancel()
```

Type of protocol:

```python
checkout : Dialog[OrderResult]
```

Testing:

```python
simulate checkout:
    shipping_address <- fake_address
    payment_method <- fake_card
    confirm <- True
expect:
    OrderSubmitted
```

### Reduction

A dialog is a state machine plus effect handlers for user input.

## 17. State Machines As Values

### Sample

```python
machine Door:
    state Open
    state Closed
    state Locked

    Closed --open--> Open
    Open --close--> Closed
    Closed --lock--> Locked
    Locked --unlock--> Closed
```

Use:

```python
door = Door.Closed
door = door.open()
door = door.close().lock()
```

Invalid transition:

```python
Door.Open.lock()  # TransitionError
```

### With Actions

```python
machine Order:
    state Draft
    state Paid
    state Shipped

    Draft --pay(payment)--> Paid:
        charge(payment)

    Paid --ship(label)--> Shipped:
        carrier.send(label)
```

### Reduction

A machine is a data type plus constrained transition functions.

## 18. Dataflow Equations

Let some programs be equations, not sequences.

### Sample

```python
flow invoice:
    subtotal = sum(items.price)
    tax = subtotal * tax_rate
    total = subtotal + tax
```

Order does not matter:

```python
flow physics:
    velocity = distance / time
    distance = velocity * time
```

Query:

```python
solve physics where distance=100, time=5 for velocity
solve physics where velocity=20, time=5 for distance
```

### Reduction

Dataflow equations are relations plus dependency solving.

## 19. Multiple Worlds: Simulation And Reality

Programs often need to run against real, test, simulated, or hypothetical
worlds.

### Sample

```python
world production:
    db = Postgres(url)
    mail = Sendgrid(key)
    clock = SystemClock()

world simulation:
    db = MemoryDb()
    mail = Mailbox.capture()
    clock = FakeClock("2026-05-07")
```

Run:

```python
signup(user) in production
signup(user) in simulation
```

Compare:

```python
compare:
    signup(user) in production_shadow
    signup(user) in new_pipeline
expect same:
    db.users
    emitted_events
```

### Reduction

A world is an explicit value containing capabilities, state, clocks, and effect
handlers.

## 20. Typed Logs And Audit Trails

Logs should be queryable semantic events, not strings.

### Sample

```python
event UserCreated(user_id:int, email:str)
event PaymentFailed(user_id:int, reason:str)

emit UserCreated(user.id, user.email)
```

Query:

```python
audit:
    find PaymentFailed(user_id, reason)
    where reason == "card_declined"
```

Explain:

```python
why user.status == "suspended":
    trace events for user.id
```

### Reduction

Events are data values appended to an event stream. Audit queries are relations
over event histories.

## 21. Program Slices As First-Class Objects

Let users name and transform parts of programs.

### Sample

```python
slice payment_flow:
    from checkout()
    through charge_card()
    until receipt_sent()
```

Use:

```python
profile payment_flow
prove payment_flow does_not_log(CardNumber)
rewrite payment_flow with async_io_rules
```

### Reduction

A slice is a quoted graph of definitions, calls, and effects. Tools can analyze
or transform it.

## 22. Counterfactual Execution

Ask what would have happened.

### Sample

```python
actual = run order_pipeline(order)

counterfactual:
    assume order.shipping = "express"
    rerun from price_quote
compare:
    actual.total
    counterfactual.total
```

In business logic:

```python
what_if:
    user.plan = "enterprise"
then:
    quote(user)
```

### Reduction

Counterfactual execution is time-travel plus world snapshots plus changed
bindings.

## 23. Negotiated Types

Instead of a type being only a declaration, let the compiler/runtime negotiate
the most useful representation under constraints.

### Sample

```python
choose representation Matrix:
    operations:
        multiply
        transpose
        row_slice
    constraints:
        rows > 1_000_000
        sparsity > 0.95
    prefer:
        memory < 1GB
        fast multiply
```

Use:

```python
A:Matrix = load_matrix(path)
B = A.transpose().multiply(A)
```

### Reduction

Representation choice is a compile/runtime strategy selection constrained by
declared operations and costs. The program semantics remain value-level.

## 24. Ambiguous Notation With Required Resolution

Sometimes human intent is ambiguous. Let code admit ambiguity temporarily but
force resolution before execution.

### Sample

```python
rate = "5%"
amount = 100 USD
fee = amount * rate
```

The system reports:

```text
Ambiguous:
  "5%" may mean Percent(5) or Probability(0.05)
Resolve with:
  rate = 5 percent
```

Explicit ambiguity:

```python
rate = ambiguous:
    5 percent
    Probability(0.05)
```

### Reduction

Ambiguous values are sets of possible values with constraints. Execution
requires the set to collapse to one value.

## 25. Notation Definitions

Let libraries define small, scoped notation, but require desugaring.

### Sample

```python
notation finance:
    "{amount} USD" => Money(amount, "USD")
    "{a} percent" => Percent(a)
```

Use:

```python
use notation finance

price = 10 USD
tax_rate = 8 percent
```

### Guardrails

Every notation must expose its expansion:

```python
expand price = 10 USD
# price = Money(10, "USD")
```

### Reduction

Notation is scoped parsing sugar into ordinary expressions. It is macro-like,
but constrained to declared patterns.

## 26. Human-Centered Error Messages As Syntax

Let code specify what failure should mean to a user.

### Sample

```python
age:int, age >= 18
else message:
    "You must be at least 18 to create an account."
= form.age
```

Function:

```python
func signup(age:(int, age >= 18 else "Must be 18+")):
    ...
```

### Reduction

Constraint failures carry structured explanation values.

## 27. Programs As Legal/Policy Text

Policies are executable logic plus explanation.

### Sample

```python
policy refund_allowed(order):
    allow when:
        order.days_since_purchase <= 30
        and order.status != "final_sale"

    deny when:
        order.item.category == "perishable"
        because "Perishable goods are not refundable."

    otherwise review
```

Use:

```python
decision = refund_allowed(order)
match decision:
    case Allow:
        refund(order)
    case Deny(reason):
        show(reason)
    case Review:
        escalate(order)
```

### Reduction

Policy is ordered guarded commands returning structured decision values and
explanations.

## 28. Literate Execution

Documentation and execution should be able to live together without notebooks.

### Sample

```python
doc "Compute monthly payment":
    We use the standard amortization formula.

    Given:
        principal = 10000 USD
        annual_rate = 6 percent
        months = 24

    calc:
        monthly_rate = annual_rate / 12
        payment = amortize(principal, monthly_rate, months)

    expect:
        payment.round(2) == 443.21 USD
```

### Reduction

`doc` blocks contain markdown-like text plus executable code, examples, and
assertions as structured values.

## 29. Whole-System Contracts

Let a system declare global laws.

### Sample

```python
law money_conserved:
    for every transfer in ledger:
        transfer.from.balance_before - transfer.amount == transfer.from.balance_after
        transfer.to.balance_before + transfer.amount == transfer.to.balance_after
```

Runtime checking:

```python
check law money_conserved during:
    run_settlement()
```

Static/query checking:

```python
prove law money_conserved for payment_pipeline
```

### Reduction

Laws are quantified constraints over values, events, timelines, or program
slices.

## 30. A Radical Nomi Sample

This is intentionally dense, but every piece has a possible semantic story.

```python
use notation finance
use symbolic.boolean

data User(id:int, email:str?, score:int)
data Order(id:int, user:User, total:Money, status:str)

event OrderApproved(order_id:int, reason:Proof)
event OrderRejected(order_id:int, reason:Proof)

policy approve(order):
    allow when:
        order.user.score >= 700
        and order.total <= 5000 USD
        and order.user.email is not None
    deny when:
        order.user.email is None
        because "email required"
    otherwise review

world simulation:
    db = MemoryDb()
    mail = Mailbox.capture()
    clock = FakeClock("2026-05-07")

func process(order:Order) using world:
    decision = explain approve(order)

    choose one:
        when decision is Allow:
            world.db.orders.save(order with {status = "approved"})
            emit OrderApproved(order.id, decision.why)
        when decision is Deny(reason):
            world.db.orders.save(order with {status = "rejected"})
            emit OrderRejected(order.id, reason)
        otherwise:
            world.db.reviews.enqueue(order)

test "approval is explainable":
    order = Order(1, User(7, "ada@example.com", 742), 1200 USD, "new")
    process(order) in simulation

    audit:
        find OrderApproved(order_id, reason)
        where order_id == 1

    prove:
        reason implies order.user.score >= 700
```

What is radical here:

- money notation is scoped syntax,
- policy is executable guarded logic,
- approval produces proof/explanation,
- effects run through an explicit world,
- events are typed,
- audit is relational,
- tests can assert over proof objects.

All of it is theoretically reducible to values, bindings, constraints,
functions, blocks, relations, proof objects, and world-passing effects.

## 31. Admission Rules For Wild Features

Even radical features should pass these tests.

### Human Value

Does the syntax make a hard thing easy for a human?

### Semantic Account

Can the feature be explained without saying "the compiler just knows"?

### Inspectability

Can the system show the desugaring, proof, trace, or explanation?

### Scope Control

Can the feature be imported, enabled, disabled, or localized?

### Failure Clarity

When the feature fails, can it say why in domain language?

## 32. Features That Would Make Designers Pause

The strongest radical candidates are:

- calculational `calc` blocks,
- executable Boolean/policy algebra with explanations,
- relations and bidirectional functions,
- live/timeline values,
- explicit `world` effects,
- proof-carrying functions,
- holes as typed questions,
- semantic search inside the language,
- examples as semantic constraints,
- notation definitions with required expansion,
- typed audit events,
- counterfactual execution,
- whole-system laws.

These ideas are dangerous if mixed casually into the everyday language. They are
also the ideas most likely to make Nomi feel like more than a Python variant.

## 33. Closing Note

A radical language should not merely let programmers write shorter code. It
should let them ask better questions:

```python
why did this happen?
what would happen if this changed?
what laws does this system preserve?
what code satisfies these examples?
what proof explains this decision?
what relation connects these values?
what world did this action affect?
```

If Nomi can make even a few of these questions ordinary, it will have earned its
own identity.

---

<a id="documentation-design-review-archive-everyday-radical-language-ideas-md"></a>

# Source: `documentation/design_review_archive/everyday_radical_language_ideas.md`

# Everyday Radical Language Ideas

> Status: design notebook for widely useful features.
>
> This document is about radical ideas for ordinary programming. The target is
> not niche symbolic systems, expert concurrency, theorem proving, or exotic
> memory models. The target is the kind of feature that could become as normal as
> Python decorators, context managers, comprehensions, varargs, keyword
> arguments, `map`/`filter`, or pattern matching.

## Aim

The best radical feature is one that stops feeling radical after a week.

It should help with daily code:

- naming values,
- transforming collections,
- validating inputs,
- handling missing values,
- opening and closing resources,
- logging and debugging,
- retrying operations,
- shaping data,
- writing tests,
- composing small functions,
- explaining errors,
- avoiding boilerplate.

The bar is high: a feature should be simple at first contact, useful in small
scripts, and still meaningful in large systems.

## Design Filter

Every idea here should pass these tests.

### It Helps Tiny Code

The feature should improve a 20-line script, not only a 200k-line service.

### It Reads Locally

A reader should not need global compiler knowledge to understand the surface
meaning.

### It Desugars

The feature should reduce to ordinary primitives:

```text
binding
function
call
block
pattern
constraint
collection
context
```

### It Is Common Enough

The feature should plausibly appear in everyday code as often as decorators,
comprehensions, `with`, `try`, or keyword arguments.

## Everyday Concern Matrix

| Daily concern | Proposed syntax family | Reduces to |
| --- | --- | --- |
| Validate external input | constrained binding, form binding | binding + predicates |
| Explain validation failure | `else "message"` on constraints | structured errors |
| Avoid temporary variables leaking | `do:` expression blocks, `let` in pipelines | local block + final value |
| Cleanup resources | `using`, `cleanup`, `temporarily` | `try/finally` block |
| Apply cross-cutting behavior | function `with` policies | decorators/wrappers |
| Handle missing values | `?.`, `?:`, `??`, `?=` | optional match + fallback |
| Transform collections | transform blocks, comprehensions with `let` | loops + yield/build |
| Unpack structured data | pattern binding with `else` | match + binding |
| Propagate ordinary failures | `?`, `recover` | `Result` match or try/except |
| Retry or time-limit work | `retry`, `timeout`, `rate`, `cancel_after` | block policies |
| Log and trace | `log`, `trace` | structured event emission |
| Explain decisions | `explain`, `explainable` | expression trace tree |
| Write examples/tests | `examples`, `cases` | data + generated tests |
| Patch nested data | `with:` patch blocks | copy/update |
| Scope mutation | `mut` blocks | explicit receiver mutation |
| Inject dependencies | `needs`, `using services` | explicit environment parameters |
| Run independent work | `parallel`, `race`, `background` | task creation + join/handle |
| Save memory | `stream`, `keep last`, `temp` | representation/lifetime policy |
| Shape JSON/tables | `shape`, `table`, `config` | structural constraints |
| Handle time | duration literals, schedules | unit values + block policies |
| Protect secrets | `secret`, `reveal` | redacted value wrapper |
| Debug state changes | `snapshot`, `watch`, `tracked` | snapshots + diff |
| Encode project defaults | `convention` | scoped syntax/policy defaults |

The important point is that these are not special domains. They are the daily
texture of practical programming.

## Syntax Taste

The proposed forms should feel like small extensions of familiar Python:

```python
using file = open(path):
    text = file.read()

user = fetch_user(id)? else "missing user"

names = users.map -> user:
    user.name

parallel:
    user = fetch_user(id)
    orders = fetch_orders(id)
```

The syntax can be radical underneath, but the first read should be ordinary.

## 1. Binding With Built-In Validation

Python made assignment pleasant. Nomi can make validated assignment pleasant.

### Sample

```python
age:int, age >= 0 = form.age
email:str, contains(email, "@") = form.email
```

In function parameters:

```python
func signup(email:(str, contains(email, "@")), age:(int, age >= 13)):
    ...
```

In loop variables:

```python
for user:User in users:
    send(user.email)
```

### Why Everyday

Most programs validate incoming values. Today this is scattered across
frameworks, assertions, type hints, validators, dataclasses, schemas, and tests.
One binding model would make validation ordinary.

### Desugaring

```python
age:int, age >= 0 = form.age
```

means:

```python
tmp = form.age
if not isinstance(tmp, int): raise TypeError
age = tmp
if not age >= 0: raise TypeError
```

## 2. Human Error Messages On Constraints

Validation should explain itself.

### Sample

```python
age:int, age >= 18 else "Must be 18 or older" = form.age
```

Function parameter:

```python
func buy(amount:(Money, amount > 0 else "Amount must be positive")):
    ...
```

Structured error:

```python
email:str, contains(email, "@") else {
    field: "email",
    message: "Email must contain @",
} = form.email
```

### Why Everyday

Every web app, CLI, API, and data pipeline needs errors that humans can act on.
Current code repeats validation and message wiring everywhere.

### Desugaring

A constraint failure raises a structured validation error carrying the given
message or object.

## 3. Named Intermediate Values In Expressions

People often want expression flow without hiding intermediate names.

### Sample

```python
price = (
    base = item.price
    tax = base * tax_rate
    base + tax
)
```

Pipeline-local bindings:

```python
result = text
    |> parse
    |> let tokens = _
    |> normalize(tokens)
    |> summarize
```

Block expression:

```python
total = do:
    subtotal = items.sum((i) => i.price)
    tax = subtotal * rate
    subtotal + tax
```

### Why Everyday

This avoids the false choice between one large expression and several outer
scope temporary variables.

### Desugaring

`do:` creates a small expression block. The final expression becomes the value.

## 4. One-Line Scoped Cleanup

Context managers are everyday because cleanup is everyday.

### Sample

```python
file = open(path) cleanup file.close()
data = file.read()
```

Block form:

```python
using file = open(path):
    data = file.read()
```

Multiple resources:

```python
using db = connect(), lock = mutex.acquire():
    update(db)
```

### Why Everyday

People open files, acquire locks, create temp dirs, patch environments, and
start spans constantly. `with` is good; Nomi can generalize it while keeping it
plain.

### Desugaring

```python
using file = open(path):
    data = file.read()
```

means:

```python
file = open(path)
try:
    data = file.read()
finally:
    file.close()
```

for resources with a cleanup protocol.

## 5. Decorators With Parameters That Read Like Policy

Python decorators are widely useful, but stacked decorators can become visually
indirect.

### Sample

```python
func fetch_user(id)
with cache(ttl=60), retry(3), timeout(2):
    api.get_user(id)
```

Equivalent decorator-like form:

```python
@cache(ttl=60)
@retry(3)
@timeout(2)
func fetch_user(id):
    api.get_user(id)
```

### Why Everyday

Caching, retrying, timing, auth checks, validation, tracing, and logging are not
advanced. They are daily work.

### Desugaring

The `with policy` form wraps the function value with policy functions, just like
decorators, but keeps the policy close to the body.

## 6. Default-On Missing Values

Missing values are everyday. Handling them should be lightweight.

### Sample

```python
name = user.name ?: "guest"
city = user?.address?.city ?: "unknown"
```

Binding with default:

```python
email = form.email ?? fail("email required")
```

Default object:

```python
settings.theme ?= "light"
```

Meaning: assign default only if missing.

### Why Everyday

APIs, forms, JSON, configs, and optional fields produce missing values
constantly.

### Desugaring

```python
city = user?.address?.city ?: "unknown"
```

means guarded access plus fallback.

## 7. Collection Transform Blocks

Comprehensions are loved because they make collection transformation local.
Nomi can generalize without losing readability.

### Sample

```python
names = collect users -> user:
    if user.active:
        yield user.name
```

Map:

```python
names = users.map -> user:
    user.name
```

Filter:

```python
active = users.keep -> user:
    user.active
```

Group:

```python
by_team = users.group -> user:
    user.team
```

### Why Everyday

Most programs transform collections. `map/filter/reduce` are powerful but can
be noisy with lambdas. Comprehensions are compact but become awkward for
multi-step transformation.

### Desugaring

These are block calls where the collection operation controls iteration and the
caller supplies the body.

## 8. Multi-Step Comprehensions

Python comprehensions are excellent until the body needs names.

### Sample

```python
result = [
    final
    for user in users
    let email = user.email?.lower()
    let final = normalize(email)
    if final is not None
]
```

Dictionary:

```python
by_slug = {
    slug: user
    for user in users
    let slug = slugify(user.name)
    if slug not in blocked
}
```

### Why Everyday

Intermediate names make data transformations readable without forcing a loop.

### Desugaring

Comprehension `let` binds per iteration before later filters or result
expressions.

## 9. Everyday Pattern Binding

Pattern matching should not be only a `match` feature.

### Sample

```python
Point(x, y) = point
Ok(value) = result else return result
{"id": id, "name": name} = payload
```

Optional pattern:

```python
User(email=Some(email)) = user else:
    return "missing email"
```

### Why Everyday

People constantly unpack structured data. Pattern binding makes shape checks and
name extraction one operation.

### Desugaring

Pattern binding is match plus assignment, with atomic failure.

## 10. Result Handling Without Ceremony

Exceptions and result values are both useful. Everyday code needs simple
propagation.

### Sample

```python
config = read_config(path)?
db = connect(config.db)?
run(db)
```

With recovery:

```python
config = read_config(path) recover error:
    default_config()
```

With message:

```python
user = fetch_user(id)? else "Could not load user"
```

### Why Everyday

File IO, APIs, parsing, config, and database operations fail constantly. Boilerplate
error plumbing obscures the normal path.

### Desugaring

`?` matches `Ok/Err` or success/failure values and returns early on failure.
`recover` is expression-level `try/except` or `Result` recovery.

## 11. Inline Retry And Timeout Blocks

Retry and timeout are everyday, not advanced.

### Sample

```python
user = retry(3):
    fetch_user(id)
```

Timeout:

```python
response = timeout(2 seconds):
    http.get(url)
```

Fallback:

```python
avatar = timeout(500 ms) else default_avatar:
    fetch_avatar(user)
```

### Why Everyday

Network calls, file systems, subprocesses, locks, and services fail or hang.
Every app eventually reimplements this.

### Desugaring

These are block calls that run the block under policy and return the block's
result.

## 12. Logging Without String Soup

Logging should be common, structured, and low-friction.

### Sample

```python
log user_created(user.id, user.email)
```

Structured:

```python
log "payment failed":
    user_id = user.id
    reason = error.reason
    retryable = error.retryable
```

Around a block:

```python
trace "load dashboard":
    user = fetch_user(id)
    orders = fetch_orders(id)
```

### Why Everyday

Developers log constantly. String logs lose structure and are hard to query.

### Desugaring

`log` emits a structured event value. `trace` is a block call that records start,
end, duration, errors, and nested logs.

## 13. Automatic Local Explanation

Explain small decisions without requiring a proof system.

### Sample

```python
if explain can_refund(order) -> reason:
    refund(order)
else:
    show(reason)
```

Function:

```python
explainable func can_refund(order):
    order.age_days <= 30
    and order.status != "final_sale"
```

### Why Everyday

Users ask why forms are rejected, why access is denied, why a workflow is
blocked. Developers currently hand-write explanation paths separately from logic.

### Desugaring

An explainable Boolean expression returns `{value, reason}` rather than only
`bool`.

## 14. Test Cases As First-Class Data

Testing should be lighter than framework ceremony.

### Sample

```python
examples slugify:
    "Hello World" => "hello-world"
    " A+B " => "a-b"
```

Attached to function:

```python
func slugify(text):
examples:
    "Hello World" => "hello-world"
    " A+B " => "a-b"
:
    text.lower().strip().replace(non_word+, "-")
```

Table cases:

```python
cases:
    a  b  expected
    1  2  3
    2  3  5
run -> row:
    assert add(row.a, row.b) == row.expected
```

### Why Everyday

Examples are how programmers communicate behavior. They should be executable by
default.

### Desugaring

Examples are data plus generated tests.

## 15. Patch Blocks For Object Updates

Updating nested data is common and verbose.

### Sample

```python
updated = user with:
    name = "Ada"
    settings.theme = "dark"
    settings.notifications.email = True
```

Conditional patch:

```python
updated = user with:
    if form.name:
        name = form.name
    if form.theme:
        settings.theme = form.theme
```

### Why Everyday

APIs, forms, config, immutable data, and UI state all need structured updates.

### Desugaring

Patch blocks copy a value and apply field updates, producing a new value unless
the receiver is explicitly mutable.

## 16. Safe Mutation Blocks

Mutation is useful but should be visually scoped.

### Sample

```python
mut user:
    name = form.name
    email = form.email
```

Nested:

```python
mut cart:
    items.append(item)
    total = items.sum((i) => i.price)
```

### Why Everyday

Mutation is common. A visible mutation block makes side effects easier to review
without requiring a pure functional style.

### Desugaring

Inside `mut user`, bare field assignments target `user`. The block is syntax for
explicit receiver mutation.

## 17. Function Policies For Common Concerns

Make everyday wrappers first-class.

### Sample

```python
func get_user(id)
policy:
    cache ttl=60
    retry 3 on NetworkError
    timeout 2 seconds
    log slow if duration > 500 ms
:
    api.get_user(id)
```

Small form:

```python
func get_user(id) with cache(ttl=60), retry(3):
    api.get_user(id)
```

### Why Everyday

Caching, retries, timing, rate limits, auth, tracing, and validation are normal
application concerns.

### Desugaring

Policies are function decorators/wrappers with structured configuration.

## 18. Local Dependency Injection Without Frameworks

Passing dependencies should be easy but explicit.

### Sample

```python
func send_welcome(user) needs mail, templates:
    body = templates.render("welcome", user)
    mail.send(user.email, body)
```

Call with environment:

```python
send_welcome(user) using app_services
```

Test:

```python
send_welcome(user) using fake_services:
    mail = Mailbox.capture()
    templates = TestTemplates()
```

### Why Everyday

Dependency injection frameworks are common because the need is common. The
language can make the pattern smaller.

### Desugaring

`needs` adds explicit parameters resolved from a supplied environment object.

## 19. Tiny Concurrent Everyday Blocks

Concurrency should appear as "do these independent things together", not as a
framework.

### Sample

```python
parallel:
    user = fetch_user(id)
    orders = fetch_orders(id)
    recommendations = fetch_recommendations(id)

render(user, orders, recommendations)
```

With limits:

```python
parallel limit=5:
    for url in urls:
        pages[url] = fetch(url)
```

Race:

```python
winner = race:
    cache.get(key)
    db.get(key)
```

### Why Everyday

Fetching several independent values is common in web apps, CLIs, data scripts,
and UI code.

### Desugaring

`parallel` creates tasks for independent statements and joins at the end of the
block. Names assigned inside become available after successful join.

## 20. Lazy By Need

Laziness should be opt-in and local.

### Sample

```python
lazy report = build_large_report()
```

Use:

```python
if user.downloads:
    send(report)
```

Memoized:

```python
once expensive = compute()
```

### Why Everyday

People often want "do not compute this unless needed" or "compute this once."
Today this requires ad hoc closures, properties, caches, or decorators.

### Desugaring

`lazy` binds a suspended computation. `once` binds a memoized suspended
computation.

## 21. Everyday Memory Hints Without Ownership Ceremony

Memory optimization can be common if expressed as intent rather than mechanics.

### Sample

```python
stream lines = file.lines()
```

Meaning: do not load all lines into memory.

Bounded collection:

```python
recent = keep last 100 events
```

Borrow-like read block:

```python
read image.pixels -> pixels:
    histogram = pixels.histogram()
```

Temporary arena:

```python
temp:
    buffer = allocate(size)
    process(buffer)
```

### Why Everyday

Developers constantly choose between lists, iterators, caches, streaming, and
temporary buffers. The language can expose common intent without Rust-level
ownership complexity.

### Desugaring

These forms choose library-backed representations and lifetimes:

- `stream` means iterator/lazy sequence,
- `keep last n` means bounded queue,
- `read` means non-mutating access scope,
- `temp` means values released after block.

## 22. Built-In Shape For Data Tables

Tabular data is everyday now.

### Sample

```python
table users:
    id:int
    name:str
    email:str?
```

Use:

```python
active = users.where((u) => u.active)
names = users.select(name)
```

Inline:

```python
rows = table:
    name   age
    "Ada"  36
    "Alan" 41
```

### Why Everyday

CSV, JSON arrays, database rows, dataframes, and UI grids are everywhere.

### Desugaring

A table is a collection of records with column constraints and query helpers.

## 23. Better Defaults For Function Arguments

Varargs and keyword args were radical once. Nomi can smooth common cases.

### Sample

```python
func connect(
    host = "db.example",
    port:int = 5432,
    timeout = 2 seconds,
    **options,
):
    ...
```

Require keyword:

```python
func send(to, *, subject, body):
    ...
```

Forward unknown options:

```python
func wrapper(*args, **opts):
    target(*args, **opts)
```

Named shorthand:

```python
send(:to, :subject, body)
```

### Why Everyday

APIs evolve. Good argument syntax keeps calls readable and wrappers simple.

### Desugaring

Mostly Python-compatible argument binding plus optional shorthand expansion.

## 24. Everyday Format And Parse Pairs

Formatting and parsing should be paired when possible.

### Sample

```python
format iso_date(date):
    "{date.year}-{date.month:02}-{date.day:02}"
```

Use:

```python
text = iso_date(Date(2026, 5, 7))
date = iso_date.parse("2026-05-07")
```

Form binding:

```python
Date(year, month, day) = iso_date.parse(text)
```

### Why Everyday

Dates, IDs, slugs, paths, URLs, and messages are constantly formatted and
parsed. Defining both together reduces drift.

### Desugaring

A format definition is a function plus a generated or declared parser relation.

## 25. Small Queries Over Ordinary Collections

SQL-like ideas are useful outside databases.

### Sample

```python
result = from users -> u:
    where u.active
    group by u.team
    select {
        team: key,
        count: count(u),
    }
```

Smaller:

```python
active_names = users
    |> where(_, (u) => u.active)
    |> select(_, (u) => u.name)
```

### Why Everyday

Most programs query collections. A small query form can make common data work
clearer than nested loops.

### Desugaring

Queries are collection transformations: filter, group, map, sort, aggregate.

## 26. Local Undo Blocks

Make reversible local changes easy.

### Sample

```python
temporarily settings:
    theme = "dark"
    debug = True
:
    render_preview()
```

Environment:

```python
temporarily env:
    PATH = test_path
:
    run_tool()
```

### Why Everyday

Tests, previews, config overrides, environment changes, and mocks need temporary
state constantly.

### Desugaring

Save old values, apply changes, run block, restore in `finally`.

## 27. Built-In Snapshots For Debugging

Debugging daily code often means asking "what changed?"

### Sample

```python
before = snapshot cart
apply_coupon(cart, code)
diff before cart
```

Block:

```python
watch cart:
    apply_coupon(cart, code)
```

Possible output:

```text
cart.total: 100 -> 80
cart.discounts: [] -> [Coupon("SAVE20")]
```

### Why Everyday

State changes cause bugs. Snapshot/diff should not require custom tooling.

### Desugaring

Snapshots are structured copies or persistent-version handles. Diffs compare
values by fields.

## 28. Safe Indexing And Bounds Defaults

Index errors are common and often avoidable.

### Sample

```python
first = users[0] ?: guest_user
name = users[0]?.name ?: "guest"
```

Checked slice:

```python
page = users[page_start..<page_end] clamp
```

Meaning: clamp the requested range to available bounds instead of failing.

Named access:

```python
header = rows.first else fail("empty file")
last = rows.last ?: default_row
```

### Why Everyday

Empty lists and out-of-range indexes are routine. The code should show whether
failure, fallback, or clamping is intended.

### Desugaring

Safe indexing returns an optional/missing value. `clamp` rewrites the range
against the collection length before indexing.

## 29. String Cleanup Pipelines

String normalization is everywhere.

### Sample

```python
slug = text
    |> trim
    |> lower
    |> replace(non_word+, "-")
    |> strip("-")
```

Common cleanup profile:

```python
name = form.name clean:
    trim
    collapse_space
    title_case
```

Validation plus cleanup:

```python
email:str = form.email clean:
    trim
    lower
check:
    contains(email, "@") else "Invalid email"
```

### Why Everyday

Data from humans and APIs is messy. Cleanup code is usually repetitive and
split across helpers.

### Desugaring

`clean:` is a pipeline block applied to the value. `check:` is a constraint
block over the cleaned binding.

## 30. Form And JSON Binding

Parsing request bodies, JSON, CLI args, and forms should feel like binding, not
framework ceremony.

### Sample

```python
bind form Signup:
    email:str, contains(email, "@")
    age:int, age >= 13
    name:str clean trim
```

Use:

```python
signup = Signup.from(request.form)?
```

Inline:

```python
{
    "email": email:(str, contains(email, "@")),
    "age": age:(int, age >= 13),
} = request.json
else error ->:
    return bad_request(error)
```

### Why Everyday

Most applications bind external data into internal names. Today this requires
schemas, validators, serializers, DTOs, or manual parsing.

### Desugaring

`bind form` declares a data shape plus converters and constraints. Inline
binding is pattern binding plus validation.

## 31. CLI Arguments As Function Calls

CLIs should be ordinary functions with argument binding.

### Sample

```python
command resize(
    input:Path,
    output:Path,
    width:int = 800,
    height:int = 600,
    keep_aspect:bool = True,
):
    image = load(input)
    save(image.resize(width, height, keep_aspect), output)
```

Generated usage:

```text
resize input output --width 800 --height 600 --keep-aspect
```

Subcommands:

```python
command users:
    command create(email:str, admin:bool=False):
        ...

    command delete(id:int, force:bool=False):
        ...
```

### Why Everyday

Every project grows scripts. Argument parsing is useful but boilerplate-heavy.

### Desugaring

`command` is a function plus generated parser, help text, type conversion, and
validation from the function signature.

## 32. Configuration As Typed Data With Layers

Configuration is daily code, but current practice is scattered across env vars,
YAML, JSON, flags, secrets, and defaults.

### Sample

```python
config AppConfig:
    host:str = "app.example"
    port:int = 8000
    debug:bool = False
    database_url:str from env "DATABASE_URL"
```

Layering:

```python
settings = AppConfig load:
    defaults
    file "app.toml"
    env
    cli_args
```

Use:

```python
server.start(settings.host, settings.port)
```

### Why Everyday

Almost every application has config. The language can make precedence and
validation explicit.

### Desugaring

`config` is a data declaration plus loaders, defaulting, converters, and
constraint checks.

## 33. Small Batching Syntax

Batching is common in APIs, databases, logging, and UI updates.

### Sample

```python
batch size=100:
    for user in users:
        send_email(user)
```

Collect then flush:

```python
batch emails every 100 or 5 seconds:
    emails.add(message)
flush -> chunk:
    mail.send_bulk(chunk)
```

### Why Everyday

Developers often need "do this in chunks" but write loops and counters by hand.

### Desugaring

`batch` is a block-control helper that buffers values and yields chunks to a
flush block.

## 34. Rate Limit Blocks

Rate limiting should be as ordinary as retry.

### Sample

```python
rate 10 per second:
    for url in urls:
        fetch(url)
```

Per key:

```python
rate 100 per minute by user.id:
    send_notification(user)
```

### Why Everyday

APIs, email, notifications, jobs, and scraping all need rate control.

### Desugaring

`rate` is a block-control policy that schedules block execution according to a
token bucket or similar limiter.

## 35. Cancellation As A Block Policy

Everyday async code needs cancellation that is visible and scoped.

### Sample

```python
cancel_after 5 seconds:
    render_report()
```

Cancel when another block completes:

```python
cancel_rest when first_done:
    fast = fetch(cache)
    slow = fetch(database)
```

Manual scope:

```python
cancel_scope -> cancel:
    button.on_click(cancel)
    upload(file)
```

### Why Everyday

Users close pages, requests timeout, jobs are superseded. Cancellation should
not require expert async architecture.

### Desugaring

Cancellation blocks pass a cancellation token through a scoped context and
ensure cleanup when cancellation fires.

## 36. Background Work That Returns A Handle

Starting background work should be simple, but not invisible.

### Sample

```python
task = background:
    generate_report()

notify_when task.done:
    send(task.result)
```

Fire-and-track:

```python
background named "sync contacts":
    sync_contacts()
```

### Why Everyday

Apps often start work that outlives the current screen/request/script. The
language should make the handle explicit so errors are not lost.

### Desugaring

`background` creates a task value with result, error, cancellation, and status.

## 37. Progress As A Language-Level Convention

Long-running tasks should expose progress without custom callback plumbing.

### Sample

```python
progress "import users" -> step:
    for row in csv.rows():
        import_user(row)
        step()
```

Known total:

```python
progress total=len(files) -> step:
    for file in files:
        process(file)
        step(label=file.name)
```

Consumer:

```python
for update in task.progress:
    print(update.percent, update.label)
```

### Why Everyday

Imports, exports, uploads, batch jobs, reports, and migrations need progress.

### Desugaring

`progress` creates a structured progress reporter and passes it into a block.

## 38. Built-In Memo And Cache Bindings

Caching is often just binding with a retention policy.

### Sample

```python
memo user = fetch_user(id)
```

Keyed:

```python
memo fetch_user(id) ttl=60:
    api.get_user(id)
```

Invalidate:

```python
invalidate fetch_user(id)
```

### Why Everyday

Caching is not rare. Developers constantly memoize expensive calls, API
responses, file reads, and computed properties.

### Desugaring

`memo` is a binding/function wrapper backed by a cache keyed by arguments or
declared key expressions.

## 39. Dirty Tracking For Ordinary Values

Apps often need to know what changed.

### Sample

```python
tracked user = edit_user(original)

if user.changed:
    save(user.changes)
```

Field check:

```python
if user.email.changed:
    send_confirmation(user.email)
```

### Why Everyday

Forms, settings, editors, ORM objects, and UI state all need change tracking.

### Desugaring

`tracked` wraps a value with original/current snapshots and field-level diff.

## 40. Built-In Undo For User-Facing State

Undo is common but hard.

### Sample

```python
undoable document:
    title = "New title"
    body.replace(selection, text)
```

Use:

```python
document.undo()
document.redo()
```

Named action:

```python
undoable "format paragraph" on document:
    paragraph.style = "quote"
```

### Why Everyday

Editors, dashboards, admin tools, forms, and design tools need undo. The pattern
is not niche.

### Desugaring

`undoable` records inverse patches or before/after snapshots for a scoped
mutation block.

## 41. Declarative Loading States

UI and service code constantly handles loading/error/empty/success states.

### Sample

```python
load users = fetch_users()

view users:
    loading:
        spinner()
    error e:
        error_box(e)
    empty:
        empty_state("No users")
    ready users:
        user_table(users)
```

Non-UI:

```python
when users:
    ready value:
        process(value)
    error e:
        retry_later(e)
```

### Why Everyday

This pattern appears in web apps, CLIs, services, and data loading.

### Desugaring

`load` creates a state value: `Loading | Error(e) | Empty | Ready(value)`.
`view/when` is pattern matching over that state.

## 42. Shape-Aware Dictionaries

Dictionaries are everyday, but key mistakes are common.

### Sample

```python
shape UserPayload:
    id:int
    name:str
    email:str?

payload:UserPayload = request.json
```

Access:

```python
payload.name
payload["name"]
```

Partial:

```python
patch:partial UserPayload = request.json
```

### Why Everyday

JSON-like dictionaries dominate modern programming. Shape constraints should be
lightweight.

### Desugaring

Shapes are structural constraints over mapping values plus optional field access
sugar.

## 43. Everyday Data Migration Blocks

Changing data shape is common.

### Sample

```python
migrate UserPayload v1 -> v2:
    full_name = name
    email = email ?: None
    drop name
```

Use:

```python
payload = UserPayload.v2.from(raw)
```

### Why Everyday

APIs, configs, saved files, caches, and database records evolve.

### Desugaring

Migration blocks are named transformation functions between shaped data
versions.

## 44. Small Time Syntax For Durations And Schedules

Time is everyday but libraries make it verbose.

### Sample

```python
timeout(2 seconds):
    fetch(url)

retry every 500 ms up_to 5 seconds:
    connect()
```

Schedule:

```python
every 1 hour:
    sync()
```

Business time:

```python
due = today + 3 business_days
```

### Why Everyday

Timeouts, retries, schedules, cache TTLs, and due dates appear everywhere.

### Desugaring

Duration literals are unit-tagged values. Schedule forms are block-control
helpers over clocks.

## 45. Permission Checks As Ordinary Guards

Authorization is daily code and should not be scattered.

### Sample

```python
allow user can "delete" document:
    document.owner == user or user.admin
```

Use:

```python
require user can "delete" document:
    delete(document)
else reason:
    forbidden(reason)
```

### Why Everyday

Most apps check permissions. Policies should be readable, testable, and
explainable.

### Desugaring

Permission declarations are named predicates returning structured allow/deny
results.

## 46. Localized Data Redaction

Redacting sensitive values is ordinary in logs, errors, and UI.

### Sample

```python
secret password = form.password
token:secret str = request.headers["Authorization"]
```

Logging:

```python
log login_failed(user.email, password)
```

Output:

```text
login_failed email="a@b.com" password="[secret]"
```

Explicit reveal:

```python
reveal password in secure_world:
    verify(password)
```

### Why Everyday

Secrets leak through logs and errors. Redaction should be a value property, not
an afterthought.

### Desugaring

`secret` wraps a value with display/logging constraints and explicit reveal
requirements.

## 47. Built-In Sampling For Expensive Work

Instrumentation and validation often need sampling.

### Sample

```python
sample 1 percent:
    validate_full_payload(payload)
```

Log sampling:

```python
log slow_query(query) sample 10 percent
```

### Why Everyday

Production checks, logs, metrics, and traces often cannot run for every event.

### Desugaring

`sample` is a probabilistic guard around a block or event emission.

## 48. Assertions That Can Become Runtime Policies

Assertions are useful in development but often disappear in production.

### Sample

```python
assert user.email is not None
    else "User must have email before invite"
```

Policy:

```python
assert mode production:
    log and continue
mode test:
    raise
```

### Why Everyday

Teams want different assertion behavior in tests, staging, and production.

### Desugaring

Assertions emit structured failures handled by an assertion policy.

## 49. Importable Local Conventions

Projects develop conventions. Make them explicit and scoped.

### Sample

```python
convention web_app:
    default timeout = 2 seconds
    default retry = 2 on NetworkError
    log structured
    secret fields = ["password", "token"]
```

Use:

```python
use convention web_app
```

### Why Everyday

Projects have repeated defaults. Today these become framework magic or copied
boilerplate.

### Desugaring

Conventions are scoped defaults for policies, logging, validation, and
capabilities. Expansions must be inspectable.

## 50. Everyday Feature Priority

The most promising daily radical features are:

- validated binding with human messages,
- missing-value fallback and safe access,
- expression blocks with local names,
- generalized cleanup blocks,
- collection transform blocks and multi-step comprehensions,
- pattern binding with `else`,
- retry/timeout/rate/cancel blocks,
- structured log/trace,
- function policies,
- local dependency injection,
- tiny `parallel`, `race`, and `background`,
- stream/bounded/temp memory hints,
- config/CLI/form binding,
- patch/mutation/undo blocks,
- shape-aware dictionaries,
- durations and schedules,
- secrets/redaction,
- project conventions.

These are not niche. They are the texture of ordinary programs.

## 51. A Daily Nomi Example

This is the target flavor: radical only because many daily concerns become
first-class and small.

```python
data User(id:int, name:str, email:str?)

func load_dashboard(user_id:int)
with cache(ttl=30), timeout(2 seconds), retry(2):
    parallel:
        user = fetch_user(user_id)?
        orders = fetch_orders(user_id)?
        recommendations = fetch_recommendations(user_id) recover:
            []

    email = user.email ?: "missing"

    trace "dashboard loaded":
        log user_loaded(user.id, email)
        log order_count(len(orders))

    {
        user: user,
        orders: orders,
        recommendations: recommendations,
    }
```

None of this should feel advanced:

- policies wrap a function,
- parallel fetches independent values,
- `?` handles ordinary failures,
- `recover` supplies fallback,
- `?:` handles missing values,
- `trace` and `log` produce structured observability,
- final dictionary is the result.

## 52. Expanded Daily Example: CLI Script

```python
command import_users(
    file:Path,
    dry_run:bool = False,
    batch_size:int = 100,
):
    config AppConfig:
        database_url:str from env "DATABASE_URL"

    settings = AppConfig load env

    using db = connect(settings.database_url):
        stream rows = csv(file).rows()

        progress total=rows.count? -> step:
            batch size=batch_size:
                for row in rows:
                    user = User.from(row)? else error:
                        log invalid_user(row, error) sample 10 percent
                        continue

                    if dry_run:
                        log would_import(user.email)
                    else:
                        db.users.upsert(user)

                    step()
```

This is everyday code:

- CLI args,
- env config,
- scoped database cleanup,
- streaming file reads,
- progress,
- batching,
- validation,
- structured logs,
- dry-run behavior.

## 53. Expanded Daily Example: Web Handler

```python
shape SignupPayload:
    email:str
    age:int
    name:str?

func signup(request)
with timeout(2 seconds), trace("signup"):
    payload:SignupPayload = request.json
    else error:
        return bad_request(error)

    email:str, contains(email, "@") else "Invalid email" = payload.email clean:
        trim
        lower

    age:int, age >= 13 else "Must be at least 13" = payload.age
    name = payload.name ?: "friend"

    require not users.exists(email=email):
        user = User(email=email, age=age, name=name)
        users.insert(user)?
        send_welcome(user) background
        return created(user)
    else:
        return conflict("Email already registered")
```

The feature mix is routine:

- JSON shape,
- cleaning,
- validation messages,
- missing defaults,
- requirement guard,
- result propagation,
- background side task,
- tracing.

## 54. Expanded Daily Example: UI State Update

```python
data Settings(theme:str, email_alerts:bool, timezone:str?)

tracked settings = load_settings(user)

view settings:
    loading:
        spinner()
    error e:
        error_box(e)
    ready settings:
        form settings -> draft:
            field theme choices ["light", "dark", "system"]
            field email_alerts toggle
            field timezone optional

            preview = settings with:
                theme = draft.theme
                email_alerts = draft.email_alerts
                timezone = draft.timezone

            temporarily app.settings = preview:
                render_preview()

            if draft.changed:
                save(preview)?
```

This combines:

- load-state matching,
- forms,
- patch blocks,
- temporary overrides,
- tracked changes,
- result handling.

## 55. The Real Radical Move

The radical move is not adding exotic features. It is noticing that daily code
already contains hidden patterns:

- validate this,
- default that,
- clean this up,
- retry this,
- run these together,
- log this structurally,
- explain this decision,
- transform this collection,
- patch this object,
- temporarily override this state,
- do this only if needed.

Nomi should make those patterns ordinary syntax, while keeping each one
desugarable into simple primitives.

That is how a radical feature becomes commonplace.

---

<a id="documentation-design-review-archive-streamlined-programmer-experience-design-md"></a>

# Source: `documentation/design_review_archive/streamlined_programmer_experience_design.md`

# Streamlined Programmer Experience Design

> Status: synthesis proposal.
>
> This document reviews and condenses the current Nomi design notes into a
> user-facing language direction. It is not an implementation plan. The priority
> is the experience of the programmer: common tasks should become smaller,
> clearer, and more coherent, even when the implementation is difficult.

## 1. Purpose

Nomi should not be "Python plus more features." It should be a coherent
language that keeps Python's local readability while making the recurring
patterns of real programming feel first-class:

- validate incoming values,
- bind and reshape data,
- pass behavior into control patterns,
- clean up resources,
- transform collections and tables,
- handle missing values and ordinary failures,
- compose small functions,
- query structured data,
- attach policies such as retry, timeout, cache, trace, and permissions,
- explain what happened when something fails.

The design goal is:

> Make the common hidden patterns of programming visible, small, and reusable,
> without forcing the programmer to feel the machinery underneath.

Python already did this successfully with decorators, context managers, keyword
arguments, varargs, comprehensions, destructuring, `map`, `filter`, `reduce`,
generators, and pattern matching. Nomi should continue that direction, but with
a more unified semantic spine.

In an AI-assisted programming world, this matters even more. AI can generate
many possible programs quickly; a language should provide the durable,
inspectable structure where those programs can be understood, constrained,
edited, tested, and trusted.

## 2. Design Thesis

Nomi should have a small set of concepts that explain a large set of surface
features:

```text
value
binding
constraint
function
call
block
yield
pattern
collection
table
policy
quote
rewrite
```

The programmer should mostly experience these as ordinary code:

```python
user:User = request.json

retry(3, on=NetworkError):
    send_welcome(user)

names = users |> filter(_, active) |> map(_, name) |> sort
```

The language designer should be able to peel them back:

- `user:User = request.json` is binding plus validation.
- `retry(...):` is a call with an attached caller-side block.
- `|>` is ordinary function application written left-to-right.

The core discipline is:

> Surface richness is acceptable only when the desugaring remains explainable.

## 3. Programmer Promise

Nomi should make these promises to a working programmer.

1. Simple code should read like direct Python-like prose.
2. Repeated ceremony should become syntax only when the pattern is common.
3. The same idea should mean the same thing in every position.
4. Advanced features should have explicit boundaries.
5. Failure should be reported in the language of the feature that failed.
6. Powerful features should be scoped by imports or `use`, not hidden globally.
7. The language should be explainable by desugaring, tracing, or inspection.

This is more important than implementation simplicity. A feature may require a
hard parser, a custom interpreter, bytecode, continuations, symbolic data, or
query planning. That is acceptable if the programmer-facing model is simple and
the feature has a plausible semantic account.

## 4. Cross-Language Synthesis

Nomi should borrow ideas, not surface clutter.

| Source | What to keep | What to avoid |
| --- | --- | --- |
| Python | indentation, local readability, ordinary calls, keyword args, exceptions, comprehensions | fragmented special cases and non-enforced annotations |
| ALGOL | block structure, lexical scope, structured control | ceremony that separates specification from daily coding |
| Scheme/Lisp | regular core, functions as values, code as data | making everyday code visually alien |
| Mathematica | symbolic expressions, rewrite rules, delayed/evaluation control | implicit rewriting of normal runtime code |
| APL | whole-collection thinking, rank/shape awareness | dense symbolic notation as the default style |
| KDB/q | table-first and vector-first data work, temporal/data analytics fluency | terse glyph-heavy expert syntax |
| SQL | declarative filtering, projection, grouping, joining, aggregation | a separate string language with weak composition |
| Scala | expression orientation, pattern matching, compositional APIs | too many equivalent spellings |
| Kotlin | null-safety, data classes, extension functions, trailing lambdas | modifier and annotation buildup |
| Groovy | closures, builders, named-argument DSLs, configuration ergonomics | hidden dynamic magic and ambiguous receiver scope |
| Ruby | caller-side blocks as humane control abstraction | overly implicit receivers and control surprises |
| Rust | explicit recoverable failure with `Result` and `?` | making everyday code feel ownership-heavy |

If "Schema" means Scheme, the Lisp/Scheme line applies. If it means data schema,
the `shape`, `data`, `table`, and constraint sections below are the relevant
synthesis.

## 5. The Main Streamlining Move

The documents already point to a strong unification:

> Binding is the core operation for names. Blocks are the core operation for
> actions.

Many features become simpler when viewed through those two ideas.

Binding explains:

- assignment,
- function parameters,
- keyword and vararg mapping,
- destructuring,
- loop variables,
- match-case names,
- imports,
- exception aliases,
- table row/column projection,
- JSON/form/config/CLI binding.

Blocks explain:

- context managers,
- retry/timeout/rate-limit scopes,
- transactions,
- tests,
- cleanup,
- logging and tracing,
- small concurrency scopes,
- custom iteration,
- local policy application.

Nomi should make both uniform.

## 6. Feature Family 1: Binding With Constraints

Validated binding should be as natural as assignment.

```python
age:int, age >= 0 = payload.age
email:str, contains(email, "@") = payload.email
```

With human-facing failure messages:

```python
age:int, age >= 13 else "Must be at least 13" = payload.age
email:str, contains(email, "@") else "Invalid email" = payload.email
```

The same model applies to parameters:

```python
func charge(account:Account, amount:(Money, amount > 0)):
    account.debit(amount)
```

and block parameters:

```python
each(users) -> user:User:
    send(user.email)
```

and patterns:

```python
match payload:
    case {"age": age:(int, age >= 13), "email": email:str}:
        signup(age, email)
```

Desugaring:

```text
evaluate value
tentatively bind name or pattern
check all constraints in the binding context
commit if all pass
raise structured BindingError if any fail
```

This turns many ad hoc validation libraries into one language habit.

## 7. Feature Family 2: Data, Shape, And Pattern Binding

Nomi needs two related but distinct user-facing forms.

`data` is for values the program owns:

```python
data User(id:int, name:str, email:str?, active:bool = True)
```

`shape` is for external or structural data the program receives:

```python
shape SignupPayload:
    email:str
    age:int, age >= 13 else "Must be at least 13"
    name:str?
```

Usage:

```python
payload:SignupPayload = request.json
else error:
    return bad_request(error)

user = User(
    id=new_id(),
    name=payload.name ?: "friend",
    email=payload.email,
)
```

Pattern binding should be ordinary:

```python
{"email": email, "age": age} = request.json
Point(x, y) = point
[first, *rest] = items
```

Desugaring:

- `data` creates constructors, fields, equality, representation, and pattern
  shape.
- `shape` creates a structural validator and binder.
- pattern binding is atomic shape checking plus name binding.

This synthesizes Python dataclasses, Kotlin data classes, Scala case classes,
SQL schemas, JSON schema, and ML-style destructuring.

## 8. Feature Family 3: Functions, Calls, And Arguments

Named functions should be explicit:

```python
func normalize(text:str) -> str:
    text.strip().lower()
```

Function values should be light:

```python
normalize = (text:str) => text.strip().lower()
```

The gap between named and anonymous functions should stay small. Parameters are
bindings, return values may be constrained, and arrow functions are ordinary
function values.

Calls should keep Python's strengths:

```python
send(to=email, subject=subject, body=body)
send(*args, **options)
```

Named argument shorthand can be considered only if it stays obvious:

```python
send(:email, :subject, body)
```

Possible desugaring:

```python
send(email=email, subject=subject, body=body)
```

The principle is that call mapping, parameter binding, defaults, varargs, and
constraints should be one coherent operation.

## 9. Feature Family 4: Blocks As User-Defined Control

The most important control feature is the caller-side block:

```python
retry(3, on=NetworkError):
    send_request()
```

The callee owns the control pattern:

```python
func retry(times:int, on=Exception):
    for attempt in 1..times:
        try:
            yield attempt
            return
        except on as error:
            if attempt == times:
                raise error
```

The caller can receive yielded values:

```python
retry(3, on=NetworkError) -> attempt:
    log attempt_started(attempt)
    send_request()
```

This one form should cover many daily abstractions:

```python
using file = open(path):
    text = file.read()

transaction(db):
    save(user)
    send_welcome(user)

timeout(2 seconds):
    fetch(url)

test "withdraw reduces balance":
    account.withdraw(30)
    assert account.balance == 70
```

Desugaring:

```text
call function with attached caller-side block
callee invokes the block with yield
yielded values bind to block parameters
exceptions from the block are visible around yield
```

This synthesizes Ruby blocks, Groovy closures, Kotlin trailing lambdas, Python
context managers, decorators, generators, and coroutine ideas.

## 10. Feature Family 5: Policies On Functions And Blocks

Decorators are powerful because they make cross-cutting behavior small. Nomi
should generalize the idea into readable policy syntax.

```python
func load_dashboard(user_id:int)
with cache(ttl=30), timeout(2 seconds), retry(2), trace("dashboard"):
    user = fetch_user(user_id)?
    orders = fetch_orders(user_id)?
    {user: user, orders: orders}
```

Equivalent idea:

```python
@cache(ttl=30)
@timeout(2 seconds)
@retry(2)
@trace("dashboard")
func load_dashboard(user_id:int):
    ...
```

Policy syntax should not be a separate feature family. It should reduce to
function wrapping and/or block control:

```text
create function value
wrap it with cache
wrap it with timeout
wrap it with retry
wrap it with trace
bind the final function
```

This keeps decorators, context managers, dependency injection, tracing, retry,
permissions, rate limits, and transactions conceptually close.

## 11. Feature Family 6: Pipelines And Composition

Nested calls hide the flow:

```python
result = summarize(normalize(parse(text)))
```

Pipelines expose it:

```python
result = text |> parse |> normalize |> summarize
```

Placeholders support non-leading arguments:

```python
result = text |> parse(mode="loose", _) |> summarize(style="short", _)
```

Composition builds a function:

```python
clean = strip >> lower >> normalize_space
name = raw_name |> clean
```

Desugaring:

```text
x |> f          == f(x)
x |> f(_, y)    == f(x, y)
f >> g          == (x) => g(f(x))
```

This borrows from F#, Elixir, Mathematica postfix flow, Unix pipes, APL
composition, and method chaining, while keeping Python-like reading order.

## 12. Feature Family 7: Collections, Arrays, Tables, And Queries

Nomi should treat collections and tables as ordinary values with strong
transformation support.

For lists and streams:

```python
names = (
    users
    |> filter(_, (u) => u.active)
    |> map(_, (u) => u.name)
    |> sort
)
```

Block form for readability:

```python
names = users.map -> user:
    user.name
```

For tables, prefer composable operations first:

```python
summary = (
    orders
    |> where(_, (o) => o.status == "paid")
    |> derive(_, total = price * quantity)
    |> group(_, by=customer_id)
    |> summarize(_, revenue = sum(total), count = count())
    |> order(_, by=revenue, desc=True)
)
```

Inside table transformations, the final design may allow column names to bind
from the table shape, KDB/APL/SQL-style. When that would be ambiguous, an
explicit row alias or lambda should be required.

SQL-like query blocks may be admitted when the table use case proves common:

```python
summary = query orders -> o:
    where o.status == "paid"
    derive total = o.price * o.quantity
    group by o.customer_id
    select {
        customer_id: o.customer_id,
        revenue: sum(total),
        count: count(),
    }
    order by revenue desc
```

The table model should learn from SQL, KDB/q, APL, LINQ, Pandas, and relational
algebra:

- columns can behave like vectors,
- row binding should be readable,
- filtering/projection/grouping/joining should compose,
- queries should be inspectable,
- operations should be values, not stringly-typed fragments.

Desugaring:

```text
query/table forms reduce to relational operations:
where, select/project, derive, group, aggregate, join, order
```

This gives Nomi a path toward data fluency without embedding raw SQL strings as
the main abstraction.

## 13. Feature Family 8: Missing Values And Ordinary Failure

Nomi needs one coherent story for absence and failure.

Everyday missing values:

```python
city = user?.address?.city ?: "unknown"
```

Explicit match:

```python
city = match user:
    case Some(user):
        user.address.city
    case None:
        "unknown"
```

Ordinary recoverable failure:

```python
config = read_config(path)?
```

Fallback:

```python
recommendations = fetch_recommendations(user)? recover:
    []
```

Desugaring:

```text
safe access checks empty/non-empty before field access
fallback selects the right side when the left side is empty
? matches Ok/Err and returns Err from the current function
recover handles Err or selected exceptions with a local block
```

Exceptions should remain for exceptional control. `Result`-style values should
be used when failure is part of the normal API contract.

## 14. Feature Family 9: Local Configuration, CLI, Forms, And External Data

Many everyday programs begin by mapping outside data into internal shape.

CLI:

```python
command import_users(
    file:Path,
    dry_run:bool = False,
    batch_size:int = 100,
):
    ...
```

Config:

```python
config AppConfig:
    database_url:str from env "DATABASE_URL"
    batch_size:int = 100
```

Forms and JSON:

```python
payload:SignupPayload = request.json
else error:
    return bad_request(error)
```

This family should be built from binding, constraints, defaults, and structured
errors. It should feel like one habit whether the source is CLI args,
environment variables, JSON, forms, config files, or database rows.

## 15. Feature Family 10: Scoped Extensions And Capabilities

Extension-style functions are useful:

```python
func String.words(self):
    self.split()
```

Use:

```python
use text.extensions.words

"hello world".words()
```

The important rule is scope:

```text
import brings names
use brings capabilities
```

Capabilities may include:

- extension functions,
- traits/protocols,
- rewrite rules,
- macros,
- query dialects,
- domain policies.

This borrows from Kotlin/Scala extensions, Rust `use`, Haskell imports, Groovy
DSL ergonomics, and Mathematica rule libraries while avoiding global monkey
patching.

## 16. Feature Family 11: Explicit Symbolic Power

Nomi should support symbolic and meta-level programming, but only with visible
boundaries.

```python
expr = quote:
    (x + 0) * 1

normal = expr //. [
    x + 0 -> x,
    x * 1 -> x,
]
```

Macros are advanced functions over quoted code:

```python
macro assert_equal(left, right):
    quote:
        if {left} != {right}:
            raise AssertionError(f"{left} != {right}")
```

Rules:

- ordinary runtime code is not rewritten invisibly,
- quote/eval boundaries are explicit,
- macro and rule imports are scoped,
- the expanded form should be inspectable.

This captures the useful parts of Lisp and Mathematica without making normal
programs unpredictable.

## 17. Feature Family 12: Explanation, Trace, And Inspectability

If Nomi adds high-level features, it should also make them explainable.

```python
trace "signup":
    payload:SignupPayload = request.json
    user = create_user(payload)?
    send_welcome(user)
```

Constraint failures should say which binding failed:

```text
BindingError: age failed constraint age >= 13
value: 11
message: Must be at least 13
```

Pipelines and queries should be inspectable:

```python
explain summary
```

Possible output:

```text
orders
| where status == "paid"
| derive total = price * quantity
| group by customer_id
| summarize revenue = sum(total), count = count()
| order by revenue desc
```

This is especially important for SQL/KDB/APL/Mathematica-inspired power:
high-level transformation should come with high-level explanation.

## 18. Preferred Staging

### Stage 1: Everyday Coherence

Admit the features that reduce daily boilerplate most clearly:

- `func` and arrow functions,
- constrained binding with messages,
- constrained parameters and block parameters,
- pattern binding and `match`,
- caller-side block calls and `yield`,
- `data` and `shape`,
- safe access and fallback,
- pipelines,
- block-based cleanup/retry/timeout/test.

### Stage 2: Data Fluency

Add the surface needed for table-heavy and collection-heavy work:

- table values,
- `where`, `select`, `derive`, `group`, `join`, `summarize`, `order`,
- query blocks if pipeline syntax is not enough,
- column/vector operations,
- streaming and batching blocks.

### Stage 3: Scoped Power

Add advanced features with strict boundaries:

- scoped extension functions,
- traits/protocols,
- `use` capabilities,
- `quote`,
- rewrite rules,
- macros,
- explainable transformations.

### Stage 4: Radical But Inspectable

Explore only after the daily core is stable:

- calculational blocks,
- relations and bidirectional functions,
- live/timeline values,
- counterfactual execution,
- proof-carrying functions,
- explicit worlds/effects.

These may define Nomi's long-term identity, but they should not destabilize the
daily language.

## 19. Admission Test For Any New Feature

A proposed feature should answer yes to these questions:

1. Does it make a common task simpler at first read?
2. Does it reuse binding, function, call, block, pattern, table, policy, quote,
   or rewrite?
3. Can a programmer inspect the desugaring or explanation?
4. Is its scope visible?
5. Does failure produce a local, useful error?
6. Would a Python programmer recognize the rough intent?
7. Does it avoid becoming a second hidden language?

If not, keep it library-first.

## 20. A Target Daily Example

```python
data User(id:int, name:str, email:str?, active:bool = True)

shape SignupPayload:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"
    name:str?

func signup(request)
with timeout(2 seconds), trace("signup"), rate(limit=100/minute):
    payload:SignupPayload = request.json
    else error:
        return bad_request(error)

    email = payload.email |> strip |> lower
    name = payload.name ?: "friend"

    require not users.exists(email=email):
        user = User(id=new_id(), name=name, email=email)

        transaction(db):
            users.insert(user)?
            send_welcome(user) background

        return created(user)
    else:
        return conflict("Email already registered")
```

The programmer sees ordinary work:

- bind external JSON to a shape,
- validate with useful messages,
- clean and default values,
- require a condition,
- run a transaction,
- propagate ordinary failures,
- start background work,
- return a response.

The designer sees the small core:

- binding,
- constraints,
- functions,
- calls,
- blocks,
- policies,
- pattern/failure flow.

## 21. A Target Data Example

```python
summary = query orders -> o:
    where o.status == "paid"
    derive total = o.price * o.quantity
    group by o.customer_id
    select {
        customer_id: o.customer_id,
        revenue: sum(total),
        first_order: min(o.created_at),
        last_order: max(o.created_at),
    }
    order by revenue desc
```

This should feel like SQL when SQL is the right mental model, like KDB/APL when
columnar/vector operations matter, and like Python when embedded in ordinary
application code.

Desugaring is relational:

```text
orders
| filter status == paid
| derive total
| group customer_id
| aggregate revenue, first_order, last_order
| order
```

No string query language is required for the common case.

## 22. Closing Position

Nomi's opportunity is not to add every elegant idea from Mathematica, Scala,
Kotlin, Groovy, APL, ALGOL, Scheme, KDB, SQL, Ruby, Rust, and Python.

The opportunity is to compress their best lessons into a small number of habits:

- bind values with meaning,
- shape data at the boundary,
- pass blocks into control,
- compose transformations left-to-right,
- treat collections and tables as first-class,
- handle absence and failure deliberately,
- scope powerful extensions,
- expose symbolic power explicitly,
- explain high-level behavior when asked.

If those habits become ordinary, Nomi can drastically reduce the complexity of
typical programming tasks without making the programmer feel the complexity that
the language implementation absorbs.

## Appendix: Source Documents Reviewed

- [ai-codex_project_overview_vision.md](ai-codex_project_overview_vision.md)
- [artifacts_and_usage.md](../artifacts_and_usage.md)
- [cross_language_feature_synthesis.md](cross_language_feature_synthesis.md)
- [delta_on_python.md](../delta_on_python.md)
- [everyday_radical_language_ideas.md](everyday_radical_language_ideas.md)
- [Implementation_guideline.md](../Implementation_guideline.md)
- [language_syntax_synthesis.md](language_syntax_synthesis.md)
- [nomi_language_revision_report.md](nomi_language_revision_report.md)
- [positioning_ambition_risk.md](../positioning_ambition_risk.md)
- [proposed_language_feature_design_plan.md](proposed_language_feature_design_plan.md)
- [proposed_syntax_samples.md](proposed_syntax_samples.md)
- [radical_language_feature_ideas.md](radical_language_feature_ideas.md)
- [yield_to_block.md](../yield_to_block.md)
- [Notes/category_theory_detour.md](../Notes/category_theory_detour.md)
- [Notes/meta.md](../Notes/meta.md)
- [Notes/tractable_sophistication.md](../Notes/tractable_sophistication.md)

---

<a id="documentation-design-review-archive-nomi-language-revision-report-md"></a>

# Source: `documentation/design_review_archive/nomi_language_revision_report.md`

# Nomi Language Revision Report

> Status: provisional design report.
>
> This document is modeled in spirit after language reports such as the Haskell
> Report, Scheme reports, and the ALGOL 68 report. It is not yet a formal
> specification. It records a coherent proposed revision of Nomi's surface
> language and semantic core so later implementation work has a stable target.

## 0. Scope

This report describes Nomi as a small-core, Python-readable language with a rich
surface syntax. The design emphasizes:

- semantic reducibility,
- local readability,
- explicit binding,
- block-structured control,
- expression orientation where readable,
- symbolic/code-shaped data as an explicit advanced facility.

The report does not define a parser, bytecode format, object layout, package
manager, optimizer, standard library, or foreign function interface.

## 1. Design Thesis

Nomi is organized around a small set of semantic primitives:

```text
value
binding
constraint
function
call
block
yield
pattern
quote
rewrite
```

Every surface feature admitted into the language should reduce to these
primitives.

The design follows this rule:

> Surface richness is acceptable only when the desugaring path remains obvious.

This lets Nomi borrow ideas from many languages without becoming a patchwork of
unrelated features.

## 2. Notational Conventions

Examples use proposed Nomi syntax. Some syntax is established in the current
prototype, while other syntax is proposed.

Status labels:

- **Core**: intended to be part of the central language.
- **Candidate**: promising, but needs more design pressure.
- **Library-first**: should be expressible through core features before becoming
  syntax.
- **Advanced**: powerful but should remain explicit and scoped.

## 3. Lexical And Layout Structure

### 3.1 Indentation

Nomi uses indentation for block structure.

```python
if ready:
    run()
else:
    wait()
```

Indentation is semantic. This follows Python and the broader off-side rule
tradition.

### 3.2 Comments

Line comments use `#`.

```python
# Load and normalize records.
records = load(path)
```

Block comments are not required in the core. Documentation strings and
editor-supported region comments are preferred.

### 3.3 Identifiers

Identifiers are plain names:

```python
user
total_count
normalize_space
```

The core style favors lowercase names for values/functions and capitalized names
for data constructors/types, but that is a convention rather than a semantic
requirement.

### 3.4 Keywords

Core proposed keywords:

```text
func
if
else
for
in
while
break
continue
return
yield
try
except
finally
raise
match
case
class
import
from
as
const
data
trait
protocol
impl
quote
macro
```

Not all keywords should necessarily enter the first implementation. `data`,
`trait`, `protocol`, `impl`, `quote`, and `macro` may be staged.

## 4. Values

A value is any runtime entity that can be bound to a name, passed to a function,
returned, stored in a structure, or matched by a pattern.

Examples:

```python
1
3.14
"hello"
True
None
[1, 2, 3]
{"name": "Ada"}
Point(2, 3)
(x) => x + 1
```

Functions are values. Data constructors produce values. Quoted expressions
produce expression values.

## 5. Bindings

### 5.1 Simple Binding

```python
x = 1
name = "Ada"
```

Meaning:

```text
evaluate right-hand side
bind resulting value to left-hand name or pattern
```

### 5.2 Constrained Binding

```python
x:int = 1
x:int, x > 0 = 1
```

Meaning:

```text
evaluate right-hand side
tentatively bind value
evaluate constraints in binding context
commit binding if all constraints pass
raise TypeError or BindingError otherwise
```

### 5.3 Constant Binding

```python
const max_retries:int = 3
```

Meaning:

```text
bind max_retries once
reject later rebinding in the same scope
```

Status: candidate core.

### 5.4 Pattern Binding

```python
(x, y) = point
[first, *rest] = items
{"id": id, "name": name} = user
```

Meaning:

```text
match the right-hand value against the left-hand pattern
bind names introduced by the pattern
fail atomically if the pattern does not match
```

## 6. Constraints

Constraints are predicates attached to bindings.

```python
age:(int, age >= 0) = 34
```

A constraint may be:

- a type/class-like value,
- a predicate function,
- an expression evaluated in the binding context.

Examples:

```python
age:int = 34
amount:positive = 10
score: score >= 0 = 5
```

All binding positions may support constraints:

```python
func f(x:(int, x > 0)): ...
for user:User in users: ...
each(users) -> user:User: ...
case User(age:(int, age >= 18)): ...
```

## 7. Functions

### 7.1 Function Definition

```python
func add(x:int, y:int) -> int:
    x + y
```

Meaning:

```text
create function value
bind it to add
on call, bind arguments to parameters
validate parameter constraints
execute body
validate return constraint if present
return result
```

### 7.2 Explicit Return

```python
func add(x, y):
    return x + y
```

`return` exits the current function and supplies a result value.

### 7.3 Final Expression Return

Candidate:

```python
func add(x, y):
    x + y
```

In expression-oriented function bodies, the final expression may be the result.
This should be admitted only if it does not make action-heavy functions
ambiguous.

### 7.4 Arrow Functions

```python
(x) => x + 1
(x:int, y:int) => x + y
```

Arrow functions create function values. They do not introduce a name unless
bound.

```python
inc = (x:int) => x + 1
```

### 7.5 Multi-Line Arrow Functions

Candidate:

```python
score = (user) =>:
    base = user.score
    bonus = user.rank * 10
    base + bonus
```

This desugars to an anonymous block-bodied function.

## 8. Calls

### 8.1 Positional And Keyword Calls

```python
move(point, dx=1, dy=2)
```

Calls map arguments to parameters, then perform parameter binding.

### 8.2 Spread

```python
f(*args, **kwargs)
```

Spread expands values into positional and keyword arguments.

### 8.3 Pipeline Application

Candidate:

```python
result = text |> parse |> normalize |> summarize
```

Desugaring:

```python
summarize(normalize(parse(text)))
```

Placeholder:

```python
result = text |> parse(mode="loose", _)
```

Desugaring:

```python
parse(mode="loose", text)
```

## 9. Blocks

### 9.1 Ordinary Statement Blocks

```python
if ready:
    run()
```

Blocks group statements under a control construct.

### 9.2 Caller-Side Blocks

```python
retry(3):
    send_request()
```

Meaning:

```text
call retry(3) with an attached caller-side block
the callee may invoke the block with yield
```

### 9.3 Block Parameters

```python
each(users) -> user:
    print(user.name)
```

Meaning:

```text
callee yields values
block boundary binds yielded values to user
body executes in caller scope with that binding
```

### 9.4 Constrained Block Parameters

Candidate syntax:

```python
each(users) -> user:User:
    print(user.name)
```

Alternative:

```python
each(users) -> user(User):
    print(user.name)
```

The report records the semantic requirement but does not choose the final
surface form.

### 9.5 Yield To Block

Inside a block-control function:

```python
func each(items):
    for item in items:
        yield item
```

`yield item` invokes the attached block with `item`. Exceptions raised by the
block are visible around the `yield` expression.

## 10. Control

### 10.1 Conditional Statement

```python
if condition:
    consequent()
else:
    alternative()
```

### 10.2 Conditional Expression Block

Candidate:

```python
label = if score >= 90:
    "excellent"
else:
    "ok"
```

The selected branch's final expression becomes the conditional value.

### 10.3 Loops

```python
for item in items:
    print(item)

while ready:
    step()
```

Loop variables are bindings and may be constrained:

```python
for user:User in users:
    print(user.name)
```

### 10.4 Library-Defined Control

Block calls make control abstraction library-definable:

```python
timeout(5):
    fetch(url)

transaction(db):
    save(record)

test "record saves":
    assert save(record).ok
```

These forms reduce to calls with attached blocks.

## 11. Pattern Matching

### 11.1 Match Statement

```python
match value:
    case Point(x, y):
        print(x, y)
    case _:
        print("unknown")
```

### 11.2 Match Expression

Candidate:

```python
kind = match value:
    case int:
        "number"
    case str:
        "text"
    case _:
        "other"
```

### 11.3 Guards

```python
match user:
    case User(age) if age >= 18:
        allow()
    case _:
        deny()
```

### 11.4 Constraint Patterns

```python
match user:
    case User(age:(int, age >= 18)):
        allow()
```

Patterns are binding forms with shape checks.

## 12. Data Declarations

Candidate core:

```python
data Point(x:int, y:int)
```

Meaning:

```text
bind constructor Point
define fields x and y
define pattern Point(x, y)
define equality and representation unless overridden
```

Defaults:

```python
data User(id:int, name:str, active:bool = True)
```

Copy/update candidate:

```python
inactive = user with {active = False}
```

## 13. Classes And Objects

Class syntax may remain Python-like:

```python
class Account:
    func deposit(self, amount:(int, amount > 0)):
        self.balance += amount
```

Classes are for identity, mutation, inheritance, or behavior-rich entities.
`data` is preferred for plain structured values.

Extension-style functions are candidate syntax:

```python
func String.words(self):
    self.split()
```

Use:

```python
"hello world".words()
```

Desugaring:

```python
String.words("hello world")
```

under scoped extension lookup.

## 14. Traits And Protocols

Candidate:

```python
trait Drawable:
    func draw(self, canvas)
```

Implementation:

```python
impl Drawable for Circle:
    func draw(self, canvas):
        canvas.circle(self.center, self.radius)
```

Structural protocol:

```python
protocol Reader:
    func read(self, n:int) -> bytes
```

Traits and protocols are named constraint sets over available functions.

## 15. Absence And Failure

### 15.1 None

Nomi may retain Python's `None` as the empty value.

### 15.2 Optional Marker

Candidate:

```python
email:str?
```

Meaning: `email` may be a `str` or empty.

### 15.3 Safe Access

Candidate:

```python
city = user?.address?.city
name = user.name ?: "guest"
```

Desugaring:

```text
if receiver is empty, return empty
otherwise perform access
```

### 15.4 Result Values

Candidate:

```python
config = read_config(path)?
```

Desugaring:

```python
match read_config(path):
    case Ok(value):
        config = value
    case Err(error):
        return Err(error)
```

The `?` operator requires a coherent `Result` model.

## 16. Exceptions

Nomi retains Python-like exceptions:

```python
try:
    work()
except NetworkError as error:
    retry_later(error)
finally:
    cleanup()
```

Expression `try` is candidate syntax:

```python
config = try:
    load_config()
except FileNotFoundError:
    default_config()
```

## 17. Symbolic Expressions

### 17.1 Quote

Advanced:

```python
expr = quote:
    x + 0
```

Meaning: capture syntax as an expression value rather than evaluating it.

Short quote candidate:

```python
expr = '(x + 0)
```

### 17.2 Evaluation

```python
value = eval(expr, env={"x": 3})
```

Evaluation is explicit.

## 18. Rewrite Rules

Advanced:

```python
simplified = expr /. x + 0 -> x
```

Multiple:

```python
simplified = expr /. [
    x + 0 -> x,
    x * 1 -> x,
]
```

Repeated:

```python
normal = expr //. [
    x + 0 -> x,
    x * 1 -> x,
]
```

Meaning:

```text
match expression value against pattern
construct replacement expression
return transformed expression value
```

No unquoted runtime code is rewritten.

## 19. Macros

Advanced and explicit:

```python
macro assert_equal(left, right):
    quote:
        if {left} != {right}:
            raise AssertionError(f"{left} != {right}")
```

Macros are functions from expression values to expression values. Macro use must
be scoped and visible through imports or `use`.

## 20. Modules And Imports

### 20.1 Imports

```python
import math
from pathlib import Path
```

Imports bind names.

### 20.2 Use

Candidate:

```python
use text.extensions.words
use symbolic.algebra.rules as algebra
```

`use` brings capabilities into scope:

- extension functions,
- traits,
- protocols,
- macros,
- rewrite rules.

The purpose is to avoid hidden global mutation.

## 21. Standard Surface Libraries

The language should prefer library-defined block abstractions before adding
keywords.

Examples:

```python
retry(3): ...
timeout(5): ...
transaction(db): ...
test "name": ...
cases(data) -> row: ...
scope() -> task: ...
```

These all reduce to calls and blocks.

## 22. Desugaring Summary

| Surface form | Desugars to |
| --- | --- |
| `func f(x): body` | bind `f` to function value |
| `(x) => expr` | function value returning `expr` |
| `x:T = v` | bind then validate `T` |
| `(x, y) = v` | pattern match then bind |
| `call(args): block` | call with attached caller block |
| `yield v` | invoke attached block with `v` |
| `each(xs) -> x: block` | block call plus yielded-value binding |
| `value |> f` | `f(value)` |
| `f >> g` | `(x) => g(f(x))` |
| `data Point(x, y)` | constructor, fields, pattern shape |
| `user?.name` | guarded access over empty/non-empty value |
| `expr /. rule` | rewrite quoted expression value |
| `quote: body` | expression value, not evaluated code |

## 23. Revision Staging

### Revision 0: Current Prototype Direction

- `func`
- arrow functions
- constrained binding
- constrained parameters
- block calls
- `yield` to block

### Revision 1: Coherent Usability Layer

- pattern binding everywhere
- expression `if` and `match`
- data declarations
- pipelines
- extension functions
- optional/null-safe syntax after absence semantics are settled

### Revision 2: Symbolic And Meta Layer

- `quote`
- rewrite rules
- scoped macros
- tagged syntax blocks
- rule libraries

### Revision 3: Capability And Effect Layer

- traits/protocols
- result propagation
- structured concurrency blocks
- effect constraints if justified by real examples

## 24. Design Risks

### 24.1 Syntax Accumulation

Nomi must avoid collecting syntax because it is attractive in other languages.
Each form needs a clear primitive reduction.

### 24.2 Hidden Control

Block calls and macros can obscure control flow. Nomi should keep block
boundaries visually explicit and macro capabilities import-scoped.

### 24.3 Symbolic Density

APL and Mathematica show the value and danger of dense notation. Nomi should
support symbolic and array-heavy domains while keeping ordinary code readable.

### 24.4 Fragmented Error Semantics

Exceptions, `None`, optional values, and `Result` can conflict. The language
needs a coherent story before adding `?`, `?.`, `?:`, and `str?` together.

## 25. Conformance For Future Implementations

A future implementation conforming to this report should:

1. Preserve the small-core reductions.
2. Provide deterministic binding and constraint behavior.
3. Make block invocation and exception flow around `yield` explicit.
4. Keep symbolic rewriting limited to explicit expression values.
5. Avoid global hidden changes from imports, extensions, macros, or rules.

This conformance definition is intentionally semantic rather than mechanical.

## 26. Concluding Position

Nomi should be rich enough to express modern programming patterns directly, but
small enough that each pattern can be explained by reduction.

The core should remain compact:

```text
values, bindings, constraints, functions, calls, blocks, yield, patterns, quote
```

The surface may grow:

```text
data, traits, protocols, pipelines, rewrite rules, macros, optional syntax,
structured concurrency
```

but every addition must preserve the ability to peel code back to primitives.
That is the central discipline of this revision.
