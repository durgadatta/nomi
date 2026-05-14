# Pattern Convenience

> Status: active synthesis; prototype surface is partial but useful.
>
> Scope: `match`, destructuring, if-let, while-let, guard-let, piecewise
> dispatch, and future pattern captures. Detailed if-let edge cases live in
> [if_let_detail.md](if_let_detail.md). Match-expression parser caveats live in
> [challenges_match_as_expression.md](challenges_match_as_expression.md).

## Design Pressure

Pattern matching is the place where many attractive language features converge:

- Rust, Swift, Kotlin, Scala, OCaml, F#, Haskell, and Racket use `match` or
  `switch` to choose by shape.
- Elixir and Haskell put patterns directly in function clauses.
- Rust, Swift, Crystal, and Clojure use `if let`, `guard let`, `when-let`, or
  narrowing forms for one-pattern checks.
- Python now has structural `match`, but keeps it statement-oriented and
  conservative.

Nomi should not copy each surface separately. The durable need is:

```text
test whether a value has a shape, bind useful parts, check extra conditions,
then choose the body that runs
```

That gives one pattern normal form:

```text
test structure -> tentatively bind captures -> check constraints/guard ->
choose body or fail without committing captures
```

## One Pattern Family

| Surface | User story | Normal form |
| --- | --- | --- |
| `match value:` | Choose among several shapes. | Ordered pattern attempts. |
| `if pattern = value:` | Run one branch when a shape fits. | Single successful pattern branch. |
| `while pattern = value:` | Repeat while a shape fits. | Pattern attempt before each iteration. |
| `guard pattern = value:` | Continue only if a required shape fits. | Pattern attempt plus failure body. |
| Piecewise equation | Dispatch a function clause by argument shape. | Pattern attempts over parameters. |
| Destructuring assignment | Bind parts of a value. | Pattern attempt that must succeed. |
| Future decoder fields | Recognize external structure. | Pattern plus binding constraints at a boundary. |

This is the synthesis rule: if a new feature introduces names by recognizing a
shape, it should reuse pattern semantics. Do not create separate binding rules
for variants, lists, maps, data decoding, function clauses, or nullable checks.

## Implemented Core Surface

### Match Statements

```nomi
match value:
    case 1:
        label = "one"
    case 2 | 3:
        label = "two or three"
    case n if n > 10:
        label = "big"
    case _:
        label = "other"
```

Implemented and useful today:

- literal patterns;
- capture patterns;
- wildcard `_`;
- or-patterns such as `1 | 2 | 3`;
- sequence patterns with starred rest, such as `[head, *tail]`;
- guards with `if`;
- statement bodies.

### Match Expressions

Use match expressions when the branch itself produces a value.

```nomi
label = match n:
    case 0: "zero"
    case 1: "one"
    case _: "many"
```

Inline form is also supported:

```nomi
label = match n: case 0 => "zero"; case _ => "many"
```

Current caveat: indented match expressions support expression-valued case
lines, not full statement-suite case bodies. This works:

```nomi
return match status:
    case 200: "ok"
    case code if code >= 500: "retry later"
    case code: "failed: " + str(code)
```

This remains future work:

```nomi
return match status:
    case 200:
        body = response["body"].strip()
        "ok: " + body
```

That future form depends on Nomi's general value-producing block semantics.
See [challenges_match_as_expression.md](challenges_match_as_expression.md).

### If-Let

`if-let` is a one-pattern `match`.

```nomi
if [head, *tail] = items:
    print(head)
else:
    print("empty")
```

The left side is a pattern; the right side is the expression being tested. Bare
names on the left are captures, not reads from outer scope.

Use `if-let` for one local shape check. Use `match` when there are several
cases. Use the detailed reference when the distinction from normal `if` is the
point: [if_let_detail.md](if_let_detail.md).

### While-Let

`while-let` repeats while the pattern fits.

```nomi
items = [1, 2, 3]
total = 0

while [head, *tail] = items:
    total += head
    items = tail
```

This is useful when the loop both tests and destructures the next value.

### Guard-Let

`guard-let` means "this shape is required for the following code."

```nomi
func first(items):
    guard [head, *tail] = items:
        return "empty"
    return head
```

On match, captures are available after the guard. On non-match, the guard body
runs. The prototype does not yet enforce that the guard body exits; that should
become a diagnostic once control-flow checking is stronger.

## Pattern Kinds And Their Meaning

| Pattern | Example | Meaning |
| --- | --- | --- |
| Wildcard | `_` | Match anything and bind nothing. |
| Literal | `0`, `"ok"` | Match by value equality. |
| Capture | `name` | Match anything and bind `name`. |
| Or | `1 | 2 | 3` | Match any alternative. |
| Sequence | `[head, *tail]` | Match list-like structure and bind parts. |
| Class/constructor | `Some(value)` | Match constructor-like values. |
| Mapping | `{"email": email}` | Target design for structural maps and decode boundaries. |
| Constrained capture | `age:(int, age >= 13)` | Target design; reuse binding constraints. |

The last two are the important future synthesis point. They connect patterns to
data boundaries without inventing a separate schema language:

```nomi
match request.json:
    case {"email": email:str, "age": age:(int, age >= 13)}:
        signup(email, age)
```

If this is ever implemented, diagnostics should distinguish:

- pattern failure: the shape did not fit;
- constraint failure: the shape fit, but a captured value was unacceptable;
- guard failure: captures were available, but the `if` condition rejected the
  case.

In ordinary `match`, all three may skip the case. For decode, constraint
failure should usually become a diagnostic with a field path.

## Pattern Choice Versus Boolean Choice

Do not blur `if`, `match`, and pattern binding into one vague "condition"
story.

| Form | Reads as | Introduces captures? | Best use |
| --- | --- | --- | --- |
| `if condition:` | This boolean is true. | No | Numeric/string predicates, state checks. |
| `if pattern = value:` | This value has this shape. | Yes | One pattern plus optional else. |
| `guard pattern = value:` | The rest of this scope requires this shape. | Yes | Early exit from invalid input. |
| `match value:` | Choose the first matching shape. | Yes per case | Several alternatives. |
| `f(pattern) = expr` | This function clause applies to this shape. | Yes per clause | Compact classifiers and recursion. |

The syntax should make the question visible. `if user:` asks about truthiness;
`if Some(user) = maybe_user:` asks about shape.

## Cross-Language Synthesis

| Source form | What it contributes | What Nomi should keep | What Nomi should avoid |
| --- | --- | --- | --- |
| Rust `match`, `if let`, `let else` | Clear pattern attempts and exhaustiveness pressure. | Pattern attempts with bindings and future closed-data exhaustiveness. | Requiring Rust-like ownership or lifetime syntax. |
| Swift `if let`, `guard let`, `switch` | Pleasant early-exit style. | `guard pattern = value:` as a pattern guard. | Optional-only binding as a separate feature family. |
| Kotlin `when`, smart casts | Expression-oriented choice and type narrowing. | Match expressions once value blocks are settled. | Hidden type narrowing without visible pattern/binding semantics. |
| Elixir function clauses | Pattern dispatch as function definition. | Piecewise equations as ordered clauses. | Making every function definition depend on remote pattern magic. |
| OCaml/F#/Haskell | Algebraic data and exhaustive matches. | Variants plus exhaustiveness diagnostics later. | Dense symbolic syntax as the first teaching layer. |
| Racket `match` | Rich extensible patterns. | Long-term inspiration for structural and custom patterns. | Global macro-extensible pattern syntax before normal forms mature. |
| Python `match` | Familiar indentation and conservative structural matching. | Python-like visual shape where possible. | Statement-only limitation as the final design. |

## Recommended Teaching Order

1. Teach ordinary `if` and `match`.
2. Teach captures and `_`.
3. Teach sequence/or/guard patterns.
4. Teach `if pattern = value:` as a one-case match.
5. Teach `guard pattern = value:` for required shapes and early exits.
6. Teach piecewise equations as function-level pattern dispatch.
7. Teach match expressions after expression-valued blocks are explained.
8. Teach constrained captures and decode only after binding constraints are
   stable.

This order prevents users from seeing five unrelated constructs. They learn
one idea and then discover where it appears.

## Synthesis Decisions

| Candidate | Status | Decision |
| --- | --- | --- |
| Match statements | implemented | Keep as the canonical multi-case pattern form. |
| Match expression, one expression per case | partially implemented | Keep; document the value-block caveat. |
| Full statement-suite match expressions | design-needed | Wait for value-producing block semantics. |
| If-let | implemented | Keep as one-case pattern branch. |
| While-let | implemented | Keep as pattern loop. |
| Guard-let | implemented; exit diagnostic future | Keep, but require better non-exiting guard diagnostics later. |
| Or-patterns and guards | implemented | Keep; share semantics with piecewise guards. |
| Sequence destructuring | implemented | Keep; useful for list-like work. |
| Mapping patterns | design-needed | Prototype after shared binding target model exists. |
| Constrained pattern captures | prototype-ready after binding engine | High leverage for decode and data validation. |
| Exhaustiveness checking | design-needed | Future diagnostic for closed data variants. |
| Regex capture patterns | design-needed | Useful, but must not become a second pattern language. |
| Macro-extensible patterns | research-only | Too powerful before source spans and explanations mature. |

## Open Questions

- Should destructuring assignment be a pattern that must match, and what
  diagnostic should it produce on failure?
- How should match expressions report "no case matched" when used in value
  position?
- When constrained captures fail inside a `match`, should that always skip the
  case, or can users ask for diagnostic accumulation?
- What is the syntax for mapping patterns that stays readable next to data
  declarations and decode?
- Which data declarations are closed enough for exhaustiveness checking?
- How should pattern attempts appear in `explain` traces?

## Quality Bar For New Pattern Sugar

Add a new pattern convenience only if it:

- reuses tentative binding and capture scoping;
- distinguishes shape failure from constraint failure in diagnostics;
- composes with `match`, if-let, guard-let, piecewise equations, and decode;
- has an obvious expansion into existing pattern normal form;
- does not create a second validation, optional-binding, or schema syntax.

Patterns are one of Nomi's best chances to feel both friendly and deep. The
language should spend that power on one memorable family, not many near-miss
aliases.
