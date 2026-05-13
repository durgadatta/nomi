# Match as Expression — Challenges & Progress

> Status: **partially implemented**.  Inline `match` expressions using
> `=>`-separated cases are implemented.  Indented expression-valued case
> lines are also implemented for assignment and return positions.  Full
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
  `result = match value:\n    case 1: "one"\n    case _: "many"`
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
