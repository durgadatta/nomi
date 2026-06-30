# Binding, Data, And Pattern Integration Feature

> Status: active integration feature packet; design direction settled,
> implementation partial.
>
> Normal forms: binding, data boundary, pattern, absence/result, explanation.
>
> Canonical homes: this file owns the shared integration contract across
> binding, decode, and pattern capture. Detailed local semantics remain in
> [Binding Constraints Feature](binding_constraints_feature.md),
> [Data Decode Boundary Feature](data_decode_boundary_feature.md),
> [Failure Taxonomy Feature](failure_taxonomy_feature.md),
> [Explanation And Trace Feature](explanation_trace_feature.md), and
> [Pattern Convenience](../convenience/patterns.md).

## One Sentence

When a value enters a meaningful position, Nomi should use one machinery to
name it, judge it, commit it, or explain why it did not fit.

```text
incoming value -> BindingTarget -> tentative names -> constraints/patterns
-> commit, non-match, Result error, or diagnostic event
```

This packet exists because the same cognitive act appears in several places:

- assignment,
- function parameters,
- block parameters,
- destructuring,
- match captures,
- data field construction,
- external `decode`,
- future row/table scopes,
- future examples and generated tests.

If these surfaces grow separate validation or capture rules, Nomi will feel
like a pile of clever syntax. If they share one model, the language can feel
small while still competing with Python's ecosystem validation libraries,
Julia's data workflows, Ruby's block ergonomics, Mathematica's structural
power, and Scheme/Racket's explainable reduction style.

## Design Position

The primitive is not "type checking" and not "schema validation." The primitive
is checked receipt:

```text
receive -> tentatively bind -> judge -> commit or explain
```

That gives one family of surfaces:

| Surface | User question | Success | Non-success |
| --- | --- | --- | --- |
| Assignment | Can this value become this local meaning? | Commit name. | `BindingError` diagnostic. |
| Function parameter | Can this argument enter this call? | Enter body. | Call-boundary `BindingError`. |
| Block parameter | Can this yielded value enter this block? | Run block body. | Policy/binding diagnostic; body does not start. |
| Destructuring assignment | Does this shape fit and are captures valid? | Commit all captures. | `BindingError`; no leaked names. |
| Match case | Does this case shape and judgment fit? | Choose case body. | Case non-match with trace evidence. |
| Decode field | Can external field become owned data? | Construct field. | Accumulated `DecodeError` with field path. |
| Data constructor | Can constructor args satisfy fields? | Construct owned value. | Constructor-boundary `BindingError`. |

The user-facing outcomes differ, but the internal act should not.

## Shared Model

### `BindingTarget`

`BindingTarget` is the design name for every source location that introduces
one or more names.

Minimum target kinds:

| Kind | Example | Captures |
| --- | --- | --- |
| Name | `age:int = raw` | `age` |
| Tuple/list | `(x:int, y:int) = point` | `x`, `y` |
| Mapping | `{"age": age:int} = payload` | `age` |
| Data field | `age:int, age >= 13` in `data Signup` | `age` |
| Parameter | `func signup(age:(int, age >= 13)):` | `age` |
| Block parameter | `each(users) -> user:User:` | `user` |
| Pattern capture | `case {"age": age:(int, age >= 13)}:` | `age` |

Each target carries:

- target kind,
- capture names,
- structural pattern requirements,
- constraints,
- source span,
- binding scope,
- redaction policy,
- optional user-facing message.

### `Constraint`

A constraint is not just a callable. It should preserve enough evidence for
diagnostics, examples, and future generation.

Minimum fields:

| Field | Meaning |
| --- | --- |
| `source` | original expression or annotation spelling |
| `kind` | type, predicate, expression, message-bearing expression |
| `subject` | name or field path being judged |
| `span` | source location when known |
| `message` | optional `else "..."` message |
| `redaction` | whether the value may appear in diagnostics |

The current prototype can keep executable predicates as the runtime path, but
the design target should retain the source rule beside the executable check.

### Tentative Binding

Every target follows the same operational sequence:

```text
1. Evaluate the incoming value once.
2. Test structural shape, if any.
3. Bind captures into a temporary binding frame.
4. Evaluate constraints in that temporary frame.
5. On success, commit captures atomically.
6. On failure, discard captures and emit the outcome required by the surface.
```

This prevents half-bound destructuring, makes match explanations possible, and
lets decode accumulate field errors without committing an invalid owned value.

## Syntax Variations And Decisions

### Checked Assignment

Canonical:

```nomi
age:int, age >= 13 else "Signup requires age 13+" = raw_age
email:str, contains(email, "@") = raw_email
```

Verbose future sugar:

```nomi
age:int where age >= 13 else "Signup requires age 13+" = raw_age
```

Rejected as primary:

```nomi
age = raw_age as int where age >= 13
```

Decision:

- Keep the compact checked-binding form as canonical.
- Consider `where` only as pure sugar over the same target and constraints.
- Refuse cast-looking syntax as the primary surface because it makes binding
  look like conversion.

### Function And Block Parameters

Function parameters are bindings:

```nomi
func signup(email:str, age:(int, age >= 13)):
    save_signup(email, age)
```

Block parameters are bindings over values yielded by a policy call:

```nomi
each(users) -> user:User:
    send(user.email)

pairs(headers) -> key:str, value:str:
    print(key, value)
```

Decision:

- Resolve call arguments or yielded values first.
- Then validate each parameter through `BindingTarget`.
- If arrow functions cannot support constrained parameters immediately, reject
  the syntax intentionally instead of accepting weaker semantics.

### Data Decode

Owned data:

```nomi
data Signup:
    email:str, contains(email, "@")
    age:int, age >= 13 else "Signup requires age 13+"
    name:str = "anonymous"
```

External boundary:

```nomi
result = Signup.decode(request.json, source="POST /signup")

match result:
    case Ok(signup):
        save(signup)
    case Err(errors):
        explain(errors)
```

Decision:

- `data` owns program values.
- `decode` crosses from external representation to owned value.
- Decode field checks reuse binding constraints.
- Decode failure returns `Err(DecodeErrorList)` and accumulates field errors by
  default.
- A separate first-layer `shape` keyword remains refused until data/decode and
  structural patterns prove they need a named non-owning contract.

### Pattern Captures

Constrained capture:

```nomi
match payload:
    case {"email": email:str, "age": age:(int, age >= 13)}:
        signup(email, age)
    case _:
        reject(payload)
```

Guard-separated form:

```nomi
match payload:
    case {"email": email, "age": age} if age >= 13:
        signup(email, age)
```

One-case form:

```nomi
if {"email": email:str, "age": age:(int, age >= 13)} = payload:
    signup(email, age)
```

Decision:

- Treat pattern capture as tentative binding.
- Use constrained captures when the judgment belongs to the captured value.
- Use guards when the judgment relates multiple captures or outside state.
- Constraint failure inside `match` is case non-match before body entry, but
  trace events must preserve that it was a constraint failure, not a shape
  miss.

## Failure Semantics

The shared machinery reports different outcomes depending on the surface:

| Surface | Shape miss | Constraint failure | Body started? |
| --- | --- | --- | --- |
| Assignment | `BindingError` | `BindingError` | No |
| Destructuring assignment | `BindingError` | `BindingError` | No |
| Function call | call-boundary `BindingError` | call-boundary `BindingError` | No |
| Block parameter | block/policy diagnostic | block/policy diagnostic | No |
| Match case | case non-match | case non-match with constraint trace | No |
| Decode | `DecodeError` with path | `DecodeError` with rule | No owned value |

The important rule:

```text
no failed target leaks partial names
```

The explanation rule:

```text
user-facing outcome can differ, but event vocabulary stays shared
```

## Explanation Events

Each attempt should be representable as a semantic event compatible with
[Explanation And Trace Feature](explanation_trace_feature.md).

Minimum event fields for this packet:

| Field | Example |
| --- | --- |
| `kind` | `binding`, `decode`, `match` |
| `action` | `checked`, `matched`, `failed`, `skipped`, `committed` |
| `subject` | `age`, `Signup.age`, `payload.age`, `case 1` |
| `value` | redacted or summarized value |
| `rule` | `int`, `age >= 13`, mapping key `"age"` |
| `result` | success, non-match, constraint failure, decode failure |
| `span` | source span when available |
| `next` | repair hint or next inspectable artifact |
| `redactions` | fields or paths hidden by policy |

Example explanation:

```text
POST /signup: Signup.age failed constraint age >= 13
  value: 12
  field: age
  rule: age >= 13
  next: provide age 13 or greater
```

Example match trace:

```text
match payload: skipped case 1
  shape: mapping keys "email", "age" matched
  capture: age = 12
  rule: age >= 13 failed
  result: non-match before body entry
```

## Target Examples

### First-Hour Binding Error

```nomi
age:int, age >= 13 else "Signup requires age 13+" = 12
```

Desired diagnostic:

```text
age failed constraint age >= 13
  value: 12
  note: Signup requires age 13+
  next: choose a value 13 or greater
```

### API Payload Decode

```nomi
data Signup:
    email:str, contains(email, "@")
    age:int, age >= 13 else "Signup requires age 13+"

result = Signup.decode(request.json, source="POST /signup")
```

Desired outcome for `{"email": "x", "age": 12}`:

```text
Err([
  DecodeError(field="email", rule="contains(email, \"@\")"),
  DecodeError(field="age", rule="age >= 13", message="Signup requires age 13+")
])
```

### Constrained Match Capture

```nomi
match event:
    case {"type": "signup", "age": age:(int, age >= 13)}:
        allow(age)
    case {"type": "signup"}:
        reject("too young or missing age")
```

The first case may skip because the shape matched but the constraint failed.
`explain` must be able to show that distinction.

### Atomic Destructuring

```nomi
(x:int, y:int, y >= 0) = point
```

If `y` fails, neither `x` nor `y` is committed.

### Decode Before Table Flow

```nomi
people =
    read_csv(path)
    |> select(Person.decode)
    |> collect_results
```

Rows become owned data before domain logic. Field paths and row numbers remain
available to `explain`.

## Rejected Alternatives

| Alternative | Why not |
| --- | --- |
| Separate schema language for decode | Splits data fields from binding constraints before one story is stable. |
| Pattern-only validation syntax | Makes match captures more powerful than assignment and parameters. |
| Boolean-only validation | Loses field paths, source rules, redaction, and repair hints. |
| Exceptions for ordinary decode failure | Makes expected external-data failure harder to compose. |
| Commit captures before guard/constraint success | Leaks partial bindings and makes failed matches observable. |
| Silent match constraint failure with no trace | Hides why a visually matching case was skipped. |
| Cast-like checked assignment | Confuses validation, conversion, and naming. |

## Implementation Slices

1. Define passive `BindingTarget` records for assignment, data fields, and
   future pattern captures.
2. Define structured `Constraint` metadata beside the current executable
   predicate path.
3. Preserve source spans for constrained assignment, grouped parameters,
   data fields, and match cases.
4. Replace assignment and function-parameter checking with the shared
   tentative-bind/commit path.
5. Add `BindingError` metadata while retaining compatibility where old tests
   expect `TypeError`.
6. Route `data.decode` field checks through the same constraint representation.
7. Add mapping/destructuring targets with atomic commit/rollback.
8. Add constrained match captures and trace events that distinguish shape miss,
   guard failure, and constraint failure.
9. Add decode events with source identity, field path, raw value redaction, and
   repair hints.
10. Add target fixtures before executable samples; promote samples only after
    parser/runtime/web/notebook capability rows are honest.

## Test And Sample Gates

Before this packet is promoted beyond active design, the project should have:

- unit tests for `BindingTarget` and `Constraint` metadata;
- parser/lowering snapshots for checked assignment, grouped parameters,
  destructuring, data fields, and constrained match captures;
- runtime tests that failed assignment, parameter, block parameter, and
  destructuring targets do not leak names;
- match tests that constraint failure skips the case before body entry and
  records trace evidence;
- decode tests that accumulate field errors with paths, source identity,
  messages, and redaction;
- regression fixtures for first-hour examples and an API payload example;
- capability matrix rows that distinguish target-only, parse-only, lowerable,
  runnable, explainable, web-exposed, and notebook-exposed support.

## Promotion Rule

This packet becomes spec-ready only when one implementation path can show the
same target model across at least assignment, parameters, decode fields, and
match captures. Until then, local docs may describe their own implemented
subset, but they should cite this integration packet as the direction of
travel.
