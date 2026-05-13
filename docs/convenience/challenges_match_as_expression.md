# Match as Expression — Challenges & Progress

> Status: **partially implemented**.  Inline `match` expressions using
> `=>`-separated cases are implemented.  Indented statement-style `match`
> blocks in expression position remain deferred for the reasons captured here.

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
- `match` guard evaluation was fixed (see commit `ca94916`)
- The IIFE-transformer logic exists in the codebase (was written then
  reverted; see commit history around `match_expr` in `functions.py`)
- `if_let_stmt` successfully uses pattern-matching-as-expression via
  desugaring to `match`

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

**Next attempt if inline is insufficient:** Approach 2 with a grammar
change that teaches Lark's indenter about `match` in expression context.
This requires modifying the Lark-based `PythonIndenter` or switching to
a different indentation strategy.

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
