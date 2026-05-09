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
