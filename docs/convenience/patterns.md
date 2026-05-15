# Pattern Convenience

> Status: active synthesis; prototype surface is partial but useful.
>
> Scope: `match`, destructuring, if-let, while-let, guard-let, piecewise
> dispatch, and future pattern captures. Detailed if-let edge cases and
> match-expression parser caveats are appendices at the end of this document.

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
See the match-expression appendix at the end of this document.

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
point: see the if-let appendix at the end of this document.

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

---

## Appendix: If-Let Detail

> Focused detail note. For the overall pattern family and admission decisions,
> start with [patterns.md](patterns.md).

## What It Is

If-let combines conditional branching with structural pattern matching.
Instead of testing a boolean:

```nomi
# regular if — tests truthiness
if x > 0:
    sign = "positive"
```

You test whether a value *matches a shape*:

```nomi
# if-let — tests pattern match, binds variables on success
if 42 = x:
    meaning = "found"
```

The form is `if PATTERN = EXPRESSION:` — pattern on the **left**,
expression on the **right**.  The body runs only when `EXPRESSION`
matches `PATTERN`.  If the pattern contains capture names (bare
identifiers), those names are bound to the matched values inside the
body.

## If-Let ≠ Regular If

| | Regular `if` | If-let `if pat = expr` |
|---|---|---|
| **What it tests** | Truthiness of an expression | Structural match of `expr` against `pat` |
| **Binding** | No new bindings | Captures in `pat` are bound in body |
| **Keyword** | `if`, `elif`, `else` | `if`, `else` (no `elif`) |
| **Desugars to** | `if cond: ...` (native) | `match expr: case pat: ...; case _: ...` |
| **Always matches?** | Truthy values only | Capture-only patterns match everything |

### Concrete Differences

#### 1. Regular `if` tests boolean expressions

```nomi
# regular: condition must be a boolean-ish expression
if x > 0:
    print("positive")

if x:                      # truthiness check (x is truthy/falsy)
    print("x is truthy")
```

#### 2. If-let tests structural patterns

```nomi
# if-let: does x equal the literal 42?
x = 42
if 42 = x:
    result = "yes"         # runs (x matches 42)

x = 5
if 42 = x:
    result = "yes"         # does NOT run (x is 5, not 42)
```

#### 3. If-let binds captured variables

```nomi
# capture pattern: val captures whatever value x holds
x = 99
if val = x:
    print(val)             # prints 99 (val bound to x's value)
```

This has **no regular-if equivalent** — a regular `if` cannot introduce
a new variable binding scoped to its body.

#### 4. Regular `if` has `elif`; if-let does not

```nomi
# regular if supports elif chains
if x > 100:
    label = "huge"
elif x > 10:
    label = "big"
else:
    label = "small"

# if-let: no elif — use multiple if-lets or match instead
if 0 = x:
    label = "zero"
if 1 = x:                  # second independent if-let
    label = "one"
```

For multi-pattern branching, use piecewise function guards or `match`
directly:

```nomi
label = describe(x) where:
    describe(n) when n > 100 = "huge"
    describe(n) when n > 10 = "big"
    describe(n) = "small"
```

#### 5. If-let with `else` catches non-matches

```nomi
x = 5
if 42 = x:
    label = "found"
else:
    label = "not found"    # runs (x doesn't match 42)
```

### Pattern Kinds That Work in If-Let

All `match` patterns work:

| Pattern | Example | When it matches |
|---------|---------|----------------|
| **Literal** | `if 42 = x:` | `x == 42` |
| **Capture** | `if val = x:` | Always; binds `val` to `x` |
| **Sequence** | `if [a, b] = xs:` | `xs` is a 2-element iterable |
| **Or** | `if 1 \| 2 = x:` | `x == 1 or x == 2` |
| **Class** | `if Some(v) = opt:` | Haskell/Rust-style variant check |

```nomi
# sequence destructuring
if [a, b, c] = triple:
    sum = a + b + c

# or-pattern
if 1 | 2 | 3 = roll:
    label = "small roll"

# class pattern (if classes with __match_args__ exist)
if Point(x, y) = origin:
    print(x, y)
```

## If-Let vs Match — When to Use Which

| Situation | Use |
|-----------|-----|
| One pattern to check, fallthrough to else | `if pat = val:` |
| Multiple patterns on same value | `match val:` |
| Need guards on patterns | `match val: case pat if cond:` |
| Want the result as an expression | Piecewise function with guards |

## Desugaring Detail

The transformer in `prototype/parser/nomi/functions.py:if_let_stmt`
converts:

```nomi
if pattern = expr:
    body
else:
    else_body
```

Into:

```nomi
match expr:
    case pattern: body
    case _: else_body      # (empty body if no else clause)
```

This means if-let inherits all of `match`'s semantics: guard evaluation,
variable scoping, and pattern-matching precedence.

## Edge Cases

### Pattern is a bare identifier (capture)

```nomi
if x = 42:
    result = x             # x is 42 here
```

`x` is a *new binding* inside the if-body, shadowing any outer `x`.  The
pattern `x` always matches, so this is effectively `x = 42; result = x`
but scoped to the if-body.

### Expression-side variable must be defined

```nomi
if 42 = x:                 # ERROR: name 'x' is not defined
    body
```

The expression on the right of `=` must be evaluable.  Unlike the
capture names on the left, it is not introduced by the if-let.

### Empty else clause

```nomi
if 42 = x:
    result = "yes"
else:
    pass                   # explicit no-op; or omit else entirely
```

Without `else`, a non-match simply does nothing (same as `match` without
a wildcard case).

## Related Features

| Feature | Relationship |
|---------|-------------|
| `match` statement | If-let desugars to it |
| Piecewise guards | Multi-branch alternative to if-let |
| `where` clause | Can host helper functions for complex matching |
| Guarded equations | `sign(n) when n > 0 = 1` — similar conditional spirit |

## Reference: Languages with If-Let

| Language | Syntax |
|----------|--------|
| Rust | `if let Some(v) = opt { ... }` |
| Swift | `if let v = opt { ... }` |
| Kotlin | `if (x is String) { val s = x; ... }` (smart-cast) |
| Scala 3 | `opt match { case Some(v) => ... }` (match preferred) |
| Nomi | `if Some(v) = opt: body` |

---

## Appendix: Match-as-Expression Challenges

> statement-suite case bodies in expression position remain deferred.

## What We Want

Nomi's `match` is currently a statement.  We want it usable in expression
position so it can appear on the RHS of assignments, in returns, as
arguments, etc.:

```nomi
result = match value:
    case 1: "one"
    case 2: "two"
    case _: "many"

func describe(n):
    return match n:
        case 0: "zero"
        case _: "nonzero"
```

This works in Rust (`let x = match v { ... }`), Haxe, ReasonML, and many
functional languages.  It avoids temporary mutable variables and keeps
control flow compositional.

## Approach 1: `match_expr` in `test` (failed)

**Idea.**  Add a new grammar rule `match_expr: "match" test ":" suite`
and place it in the `?test` alternative list alongside `func_expr`,
`pipe_expr`, etc.:

```lark
?test: func_expr | ... | match_expr
match_expr: "match" test ":" suite
```

The existing `match_stmt` lives in `?compound_stmt` (statement level).
Both start with `match`.  The Earley parser should try both paths and
disambiguate.

**Why it failed.**  The `suite` production (`simple_stmt | _NEWLINE
_INDENT stmt+ _DEDENT`) requires the INDENT/DEDENT postlexer.  When the
parser is inside a `test` (expression context, no indentation expected),
the postlexer does not send the INDENT token that `suite` expects.  The
result is a parse error at the first indented `case` line:

```
Unexpected token Token('DEC_NUMBER', '1') at line 2.
Expected: *, +, -, ==, etc.
```

The root cause: Lark's PythonIndenter postlexer only emits INDENT/DEDENT
tokens when the parser is in a state that expects them (i.e., inside a
compound statement context).  An expression-level rule like `match_expr`
inside `test` does not create the right parser state for the indenter.

## Approach 2: Post-parse IIFE wrapping (not attempted)

**Idea.**  Keep `match` as a statement only.  Write a desugar pass that
detects `ast.Match` nodes used as expression values and wraps them in
an Immediately-Invoked Function Expression:

```
Assign(targets=[x], value=Match(...))
```
→
```
Assign(targets=[x], value=Call(func=FunctionDef(name=None, body=[Match(...)])))
```

**Why not attempted.**  The grammar won't allow `match` in expression
position at all.  The parser must accept `x = match ...` before any
desugar pass can transform it.  So this approach requires grammar
support first.

## Approach 3: Sentinal-wrapper syntax (not attempted)

**Idea.**  Give match-expression a distinct syntactic marker so the
parser can recognize it without INDENT ambiguity.  Examples:

```nomi
# Option A: thin prefix
result = .match value:
    case 1: "one"
    case _: "many"

# Option B: expression-only keyword
result = when value:
    case 1: "one"
    case _: "many"

# Option C: block-style with curly/begin-end
result = match(value) { 1 => "one", _ => "many" }
```

**Trade-offs.**  Each option requires a new keyword or syntax that
diverges from the Rust/Python `match` look.  Option C is closest to
Rust but changes the block delimiter.  None were tried yet.

## Approach 4: Inline match with `;`-separated cases (not attempted)

**Idea.**  A single-line form that avoids INDENT entirely:

```nomi
result = match value: case 1 => "one"; case 2 => "two"; case _ => "many"
```

This keeps the parser in expression context (no indentation needed).
The cases use `=>` instead of `:` to avoid ambiguity with the match
delimiter.

**Trade-offs.**  Limited to short expressions.  Multi-line body blocks
would still need INDENT handling.  But it covers 80% of use cases.

## Approach 5: Pre-processor source rewrite (not attempted)

**Idea.**  Before parsing, scan the source for `match` in expression
position and rewrite it to a statement-level call:

```nomi
result = match value:            func __match_expr():
    case 1: "one"     →             match value:
    case _: "many"                      case 1: return "one"
                                        case _: return "many"
                                 result = __match_expr()
```

This requires source-level analysis (tracking paren/bracket depth,
knowing statement vs expression context) before Lark sees the source.

**Trade-offs.**  Adds complexity to the pipeline.  Fragile to edge cases
(nested matches, multi-line strings that contain `match`, etc.).  Error
messages would point to rewritten code, not original source.

## Current State

- `match_stmt` works correctly as a compound statement with INDENT/DEDENT
- Inline match expressions work in expression position:
  `result = match value: case 1 => "one"; case _ => "many"`
- Indented match expressions work for assignment and return positions when
  each case body is a single expression:
  `result = match value:
    case 1: "one"
    case _: "many"`
- `match` guard evaluation was fixed (see commit `ca94916`)
- The IIFE-transformer logic exists in the codebase (was written then
  reverted; see commit history around `match_expr` in `functions.py`)
- `if_let_stmt` successfully uses pattern-matching-as-expression via
  desugaring to `match`

## Known Unsupported Case

The current indented expression form supports one expression per case line.
That expression can itself be complex, including another match expression:

```nomi
result = match "json":
    case "json": match 200:
        case 200: "ok"
        case _: "bad"
    case _: "unknown"
```

It does **not** support full statement-suite case bodies:

Full-fledged desired example that does **not** work today:

```nomi
func describe_status(response):
    status = response["status"]

    return match status:
        case 200:
            body = response["body"].strip()
            print("successful response")
            "ok: " + body

        case code if code >= 500:
            print("server failure")
            "retry later: " + str(code)

        case code:
            print("non-success response")
            "failed: " + str(code)

result = describe_status({"status": 200, "body": " ready "})
```

The intended result would be:

```nomi
result == "ok: ready"
```

That example fails today at the first expression-style case suite:

```nomi
        case 200:
            body = response["body"].strip()
```

Current indented match expressions only accept this narrower shape:

```nomi
return match status:
    case 200: "ok"
    case code if code >= 500: "retry later"
    case code: "failed"
```

The key distinction is expression value vs. statement suite.  A nested
`match` is still one expression value, so it can be returned from the outer
case.  A body with local statements before the value, such as
`body = response["body"].strip(); print(...); "ok: " + body`, needs
value-producing block semantics that Nomi has not implemented yet.

Concrete reasons this does not work yet:

1. The implemented rule is intentionally narrow:
   `case_block_expr` accepts either one expression on the case line or a nested
   `match_block_expr`.  After `case 200:` it does not accept an arbitrary
   newline plus indented statement suite.
2. Reusing Python-style `suite` directly would parse statements, not a value.
   A case body like `print("matched one"); "one"` must define which statement
   produces the match expression's value.  Python AST has `ast.Match` as a
   statement, not an expression, so there is no built-in place to store that
   value.
3. The current lowering uses an IIFE:
   each expression-valued case becomes `case pattern: return expr`.  For a full
   suite, the transformer would need to convert the selected suite into
   statements that eventually `return` a value, while preserving ordinary
   control flow like `raise`, nested `return`, `break`/`continue` errors, and
   local bindings.
4. The statement grammar also matters.  The working assignment/return forms
   have special entries because the inner match block consumes the final
   newline before `_DEDENT`.  Full-suite bodies would add another indentation
   level and need careful statement termination so the outer assignment or
   return can complete cleanly.

What would be required to make it work:

1. Add a separate grammar rule for value-producing match suites, probably
   distinct from normal `suite`, so expression-position `match` can parse:
   `case pattern ":" _NEWLINE _INDENT stmt* value_stmt _DEDENT`.
2. Define Nomi's value-producing block rule.  Options include "last expression
   wins", explicit `yield`/`return` from expression blocks, or requiring every
   case body to end with an expression statement.  This must be specified
   before implementation so diagnostics are coherent.
3. Lower each selected case suite into IIFE function-body statements ending in
   `ast.Return(value=...)`.  For example, the first case above would lower to
   `print("matched one"); return "one"` inside the anonymous function.
4. Add validation and diagnostics for non-value-producing cases, mixed
   statement/value branches, and illegal control flow inside match-expression
   suites.
5. Add parser and interpreter tests covering full-suite case bodies,
   fallthrough, guards, captures, side effects before the returned value, and
   the no-match behavior.

## Concrete Next Steps

**Implemented first attempt:** Approach 4 (inline match with `=>`).
It avoids the INDENT problem entirely, covers most use cases, and is
backward-compatible (doesn't change existing `match_stmt`).  This
included:

1. Grammar: `match_inline: "match" test ":" case_expr (";" case_expr)*`
   with `case_expr: "case" pattern ["if" test] "=>" test`
2. Transformer: collect cases, return each case expression from an anonymous
   function, and call that function immediately
3. Tests for assignment, return position, call arguments, captures, and guards

**Implemented follow-up:** Indented expression-valued cases are supported
without using `suite` in the expression grammar:

```nomi
result = match value:
    case 1: "one"
    case _: "many"
```

This required special statement-level entries for assignment and return,
because the inner block consumes the terminating newline that ordinary
`simple_stmt` assignment/return expects.

**Next attempt if full block bodies are needed:** Approach 2 with a grammar
change that teaches Lark's indenter about full `suite` bodies in expression
context, or a deliberate source-level rewrite. This requires modifying the
Lark-based `PythonIndenter` strategy or switching to a different indentation
strategy.

**Investigate in parallel:** Whether the Lark `earley` parser can handle
`suite` inside a `test` if we tell the indenter to expect INDENT at that
point.  This may be a Lark configuration issue rather than a fundamental
limitation.

## Cross-Language Reference

| Language | Syntax | Expression? |
|----------|--------|-------------|
| Rust | `let x = match v { 1 => "one", _ => "many" }` | Yes |
| Haxe | `var x = switch v { case 1: "one"; case _: "many" }` | Yes |
| ReasonML | `let x = switch v { \| 1 => "one" \| _ => "many" }` | Yes |
| Scala 3 | `val x = v match { case 1 => "one"; case _ => "many" }` | Yes |
| Python 3.10+ | statement only (`match v: case ...`) | No |
| Kotlin | `val x = when(v) { 1 -> "one"; else -> "many" }` | Yes |
| Swift | `let x = switch v { case 1: "one"; default: "many" }` | No (stmt) |

## Design Context

This doc covers Nomi's **Pattern** normal form. For the broader picture:

- [Language Foundation §Coherence Contract](../language/language_foundation.md) —
  the One Pattern Story: patterns test structure and bind names; pattern failure
  and constraint failure are related but distinct.
- [Language Specification §11](../language/language_spec.md) — pattern forms,
  match, destructuring, pattern vs constraint failure, and pattern conveniences
  (if-let, guard-let, while-let).
- [Language Design Dimensions §2 (Level 4)](../language/language_design_dimensions.md) —
  how Choose + Contain + Bind compose into pattern matching.
- [Implementation Learnings](../convenience/implementation_learnings.md) —
  `match_expr` INDENT/DEDENT limitations, single-line `=>` workaround,
  `match_block_expr` for nested indented match, and `match_case` guard handling.
- [Binding Constraints Feature](../features/binding_constraints_feature.md) —
  how constraints compose with pattern captures.
