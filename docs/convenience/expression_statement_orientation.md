# Expression And Statement Orientation

> Status: active design doctrine.
>
> Scope: cross-cutting syntax guidance for constructs that may appear both as
> statements and as value-producing expressions: `if`, `match`, `try`, block
> calls, local blocks, loops, comprehensions, and recursion.
>
> Related docs: [syntax_design_rules.md](syntax_design_rules.md),
> [patterns.md](patterns.md), [functions.md](functions.md),
> [flow_and_collections.md](flow_and_collections.md),
> [design_lessons_and_integration.md](design_lessons_and_integration.md), and
> [language_spec.md](../language/language_spec.md).

## Core Position

Nomi should be **expression-capable and statement-friendly**.

That means:

- ordinary code can still read like Python: statements, indentation, names,
  effects, and clear long forms are welcome;
- value-oriented code can avoid temporary mutation: `if`, `match`, `try`, and
  selected blocks can produce values when every path clearly produces a value;
- the same construct may have statement and expression surfaces, but both must
  reduce to one semantic normal form;
- expression forms are admitted only when they improve local reasoning, not
  because "everything should be an expression."

The goal is not Rust/ML maximal expression orientation and not Python's strict
statement/expression split. The goal is a calm ladder:

```text
statement form for actions and control
expression form for local value selection
block/policy form for scoped effects and managed control
library/flow form for repetition and accumulation
```

## The Tension

Python keeps `if`, `for`, `while`, `with`, `try`, and `match` mostly as
statements. This keeps large control flow readable but creates friction:

- `lambda` is cramped because it cannot contain statements;
- `match` cannot directly produce a value;
- statement-only `if` often forces predeclared temporaries;
- loops produce side effects rather than values, so accumulation moves into
  mutation unless users reach for comprehensions or library helpers;
- parser and AST boundaries make value-producing blocks hard to retrofit.

Expression-oriented languages solve some of this:

- Rust, Scala, Kotlin, F#, Haskell, Elm, Gleam, and ML-family languages make
  `if`/`match`/`case` naturally produce values;
- Rust and ML-family languages make exhaustive `match` central to data design;
- Ruby blocks, Kotlin trailing lambdas, Swift result builders, F# computation
  expressions, and Gleam `use` show how statement-looking blocks can feed a
  value protocol;
- JavaScript expression syntax is flexible, but statement/expression drift
  remains visible in `if` vs ternary, `function` vs arrow, and block bodies.

The trap is making expression orientation too broad. If every statement can be
used anywhere as a value, users must learn hidden value rules for assignment,
loops, `return`, `break`, resource cleanup, exceptions, and partial control
flow. That is not pleasing; it is merely uniform.

## Nomi Rule: One Construct, Two Surfaces, One Core

When a control construct has both statement and expression forms, the forms
should differ in **position and value contract**, not in semantic meaning.

| Construct | Statement surface | Expression surface | Shared core |
|-----------|-------------------|--------------------|-------------|
| `if` | choose effects/statements by boolean | choose a value by boolean | boolean branch |
| `match` | choose effects/statements by pattern | choose a value by pattern | pattern dispatch |
| `try` | recover around an action | recover around a value | absence/result/error boundary |
| block call | attach caller-side code to a policy call | policy call returns yielded block values | block invocation with `yield` |
| loop | repeat effects | usually not an expression | flow over repetition |
| comprehension | compact collection expression | collection value | flow over collection |
| recursion | function calls itself for structure | function value result | function normal form |

Every expression form needs an ordinary statement expansion and a normal-form
owner. Every statement form should be explainable as the same choice, flow,
block, or function behavior without a value requirement.

## Value-Producing Blocks

A value-producing block is a block used where a value is required.

Design target:

```nomi
label =
    if age >= 18:
        "adult"
    else:
        "minor"

description =
    match response:
        case Ok(user):
            name = user.name.strip()
            "user: " + name
        case Err(problem):
            "error: " + problem.message
```

Rules:

- all reachable branches must produce a value;
- the block value is the last expression in the selected branch;
- support statements may appear before the final expression once full
  value-block suites are implemented;
- assignment, declaration, loop, `defer`, and effect statements produce `none`
  and cannot be the final value unless `none` is explicitly desired;
- branch diagnostics must say which branch did not produce a value;
- formatter and `explain` views must preserve the distinction between support
  statements and the branch value.

This is the design target. The current prototype may lower some expression
forms through hidden IIFE wrappers because Python AST lacks direct nodes. That
lowering is implementation residue, not the language model.

## Control Transfer Rule

Control-transfer keywords must never depend on hidden lowering artifacts.

Design target:

- `return` always returns from the nearest user-authored `func`;
- `break` and `continue` always target the nearest user-authored loop;
- `yield` belongs to block-call policy invocation, not to generic
  expression-block value production;
- `raise`/unexpected errors keep their ordinary propagation behavior;
- expression-block values come from the branch expression, not from `return`.

Therefore, a value-producing `match` branch should prefer:

```nomi
return match status:
    case 200: "ok"
    case _: "failed"
```

not:

```nomi
match status:
    case 200: return "ok"
    case _: return "failed"
```

The second form may remain legal as ordinary early return if the surrounding
construct is a statement, but it should not be the teaching path for producing
a value from an expression. In expression-position full-suite blocks, `return`,
`break`, and `continue` need explicit diagnostics before promotion from
prototype behavior.

## Construct Guidance

### `if`

`if` is the short form for boolean choice.

Statement form:

```nomi
if user.active:
    send(user.email)
else:
    skip(user)
```

Expression form:

```nomi
label =
    if user.active:
        "active"
    else:
        "inactive"
```

Rules:

- expression `if` must have an `else`;
- both branches must produce values;
- conditions must be boolean;
- use `match` when the condition is really shape, variant, absence, or result.

### `match`

`match` is the canonical elimination form for shape, variant, absence, and
result choice.

Statement form is best for effects, logging, mutation, and multi-step branch
actions. Expression form is best for local value selection.

```nomi
message =
    match parse_int(raw):
        case Ok(n) when n >= 0: "valid"
        case Ok(_): "negative"
        case Err(problem): problem.message
```

Rules:

- expression `match` should be exhaustive or have a default case;
- non-exhaustive expression `match` must have a specified failure value or
  diagnostic;
- guards are part of branch selection, not branch value production;
- full statement-suite branch bodies require value-producing block semantics;
- pattern diagnostics should distinguish non-match, guard failure, and
  constraint failure.

### `try` And Result Flow

`try` is a boundary around expected recovery. Statement `try` recovers around
actions. Expression `try` recovers around values.

```nomi
safe_age = try int(raw_age) except ValueError: 0
```

Rules:

- expression `try` must name the recovery value;
- result propagation syntax, if admitted, must state its target: enclosing
  function, block policy, or result-building expression;
- do not let `try` become a second `match` syntax for ordinary variant choice.

### Loops

Loops are primarily statement-oriented because they are about repeated action,
early exit, and local mutation.

```nomi
for item in items:
    process(item)
```

Value-oriented repetition should normally use the collection path:

```nomi
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> collect
```

Rules:

- `for` and `while` should stay statement-first;
- comprehensions, folds, scans, and pipelines are the value-producing path for
  collection accumulation;
- a future loop expression needs an explicit accumulator/yield protocol and
  should probably be a block policy or library helper, not first-layer syntax;
- `while-let` remains a pattern loop statement, not a value-oriented match.

### Recursion

Recursion belongs to the function path. It is the value-producing form of
structural repetition when the structure is clearer than an iterative loop.

```nomi
size(tree) =
    match tree:
        case Leaf(_): 1
        case Branch(left, right): size(left) + size(right)
```

Rules:

- use recursion for structural decomposition;
- use loops for procedural repetition;
- use collection verbs for one-to-many flow;
- keep fixed-point combinators and recursion schemes library-first.

### Block Calls

Block calls intentionally blur statement shape and value flow: the caller writes
an indented block, while the callee controls when it runs through `yield`.

```nomi
using(open(path)) -> file:
    file.read()
```

Rules:

- the attached block has a value: its last expression or `none`;
- the policy function owns how yielded block values are used;
- block calls are the right home for resource scope, retry, transaction,
  tracing, examples, fixtures, and future concurrency;
- do not create separate statement/expression versions of each policy keyword.

## Cross-Language Lessons

| Language family | Lesson for Nomi |
|-----------------|-----------------|
| Python | Readable statements are excellent; statement-only control creates value-friction and awkward temporaries. |
| Rust | `if`/`match` expressions work because exhaustiveness and block values are explicit. Avoid inheriting hidden IIFE semantics. |
| ML/F#/Elm/Gleam | Expression-oriented choice composes well with algebraic data and result types. |
| Kotlin/Scala/Swift | Expression-friendly blocks improve APIs, but implicit returns and builder protocols need clear scope rules. |
| Ruby | Blocks are ergonomic, but non-local return semantics show why control transfer must be specified early. |
| Go | Statement-first control is simple, but error handling and value construction can become repetitive. |
| JavaScript | Dual forms without a unifying doctrine produce drift: ternary vs `if`, expression arrows vs block arrows. |

## Admission Bar

Before allowing a construct in expression position, all answers must be yes:

- Does the expression form remove common temporary-variable or callback friction?
- Is there one normal-form owner and a clear statement-form expansion?
- Can all branches be checked for producing a value?
- Are `return`, `break`, `continue`, `yield`, `defer`, and `raise` rules clear?
- Can diagnostics point to the branch or path that failed to produce a value?
- Can `explain` show the selected branch, produced value, and any skipped cases?
- Does the expression form keep the same mental model as the statement form?

If not, keep the construct statement-only or library-first.

## Nomi Direction

Accepted direction:

- keep long statement forms calm and readable;
- support expression `if` and expression `match` for local value selection;
- keep expression `match` narrow until value-producing block suites are
  specified and implemented with Nomi-owned nodes;
- keep loops statement-first and use collection flow/comprehensions/folds for
  value-producing repetition;
- use block calls for scoped policies that need statement shape and value flow;
- treat hidden IIFE lowering as a prototype tactic, not source semantics.

Design-needed:

- a Nomi-owned surface/core representation for value-producing blocks;
- exact diagnostics for branch-without-value and no-match-in-expression;
- control-transfer validation inside expression-position full suites;
- formatter rules for branch final expressions;
- `explain` events for branch selection, skipped patterns, and block values;
- migration plan from Python-AST/IIFE lowering to explicit Core IR nodes.

Rejected-for-now:

- "everything is an expression" as a blanket rule;
- loop expressions without an explicit accumulator or yield protocol;
- using hidden functions to define user-visible `return` behavior;
- separate expression-only keywords for every statement construct;
- DSL-style block builders before block-call policy semantics are stable.
