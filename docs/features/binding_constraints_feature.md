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
- explicit decoding for JSON, forms, config, and CLI values.

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

- `prototype/grammar/layers/bindings.lark` handles annotated assignment
  constraint lists and grouped parameter constraints.
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

Individual parameter constraints may carry the same user-facing message form as
assignment constraints:

```python
func signup(age:(int, age >= 13 else "Signup requires age 13+")):
    ...
```

Parameter constraints are checked after Python-compatible argument mapping:
positional arguments, keyword arguments, keyword-only arguments, defaults,
`*args`, and `**kwargs` are resolved first; then each resulting parameter
binding is validated. For `*args` and `**kwargs`, the constraint applies to the
collected tuple or mapping.

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

### External Data Boundary Binding

External request/config/form/CLI data should reuse binding constraints without
introducing a second field system. The first everyday spelling should be
explicit decode into owned `data`:

```python
data SignupPayload:
    email:str, contains(email, "@")
    age:int, age >= 13 else "Must be at least 13"
    name:str = "anonymous"
```

Usage:

```python
payload = SignupPayload.decode(request.json)
```

Structural patterns cover cases where the program only needs to recognize a
received value without constructing an owned domain value:

```python
match request.json:
    case {"email": email:str, "age": age:(int, age >= 13)}:
        signup(email, age)
```

Named structural contracts may be reconsidered later, but a future `shape`
keyword must mean a named structural pattern/constraint, not a second data
declaration.

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
parameterized constraints, algebraic data, and external data decoding.

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

Prototype status:

- Implemented for assignment constraints as executable syntax.
- The parser lowers the message-bearing constraint to a temporary metadata
  marker, and the current runtime includes the message in the raised
  `TypeError` text.
- The target remains a structured `BindingError` with explicit `message`
  metadata once the shared binding engine lands.

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

### Future Named Structural Contracts

If admitted, a named structural contract creates a validation/projection
boundary over external data. It must not create constructors, nominal variants,
or a second field validation system separate from binding constraints and
`data.decode`.

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
