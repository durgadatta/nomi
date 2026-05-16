# Implementation Learnings & Special Cases

> Status: living reference for future sessions.
> Documents tricky grammar interactions, API trade-offs, and features
> that seemed simple but hit obstacles.

## Grammar: Lark Terminal Conflicts

### `"type"` as keyword → name rule

Adding `type_alias: "type" NAME "=" test` creates an implicit `"type"`
terminal in Lark.  This terminal **always wins** over `NAME`, so
`type(x)` in expression context fails — `type` is no longer a valid
identifier.  **Fix**: add `"type"` to the `!name` rule so it remains
usable as a name in expression context.

### `"try"` in expression position

Adding `try_expr` to `?test` works because `"try"` is already a keyword
(not in `name`).  No terminal conflict.  The single-line form
(`try body except E: handler`) avoids the INDENT problem that killed
`match_expr`.

### Rule ordering matters for `small_stmt`

When adding alternatives like `type_alias` before `func_equation` in
`?small_stmt`, make sure the new rule comes first if it could be matched
by a later rule.  `func_equation_no_parens: name NAME "=" test` with
`name` including `"type"` would match `type X = expr`.  Putting
`type_alias` first in the list ensures it wins.

### `|` alternatives after string literals

After `"defer"`, using `(expr_stmt | assign_stmt)` works because Lark
parenthesized groups properly.  But `"defer" expr_stmt | assign_stmt`
(bare `|`) would be ambiguous.

## Grammar: INDENT/DEDENT Limitations

### `match_expr` in `test` (FAILED)

The `suite` production requires INDENT/DEDENT tokens from the postlexer.
When `match_expr` is inside `test` (expression context), the postlexer
doesn't emit INDENT tokens for the `:` → suite transition.  Root cause:
Lark's `PythonIndenter` only emits INDENT when the parser is in a
compound-statement state.  See the match-expression appendix in
`docs/convenience/patterns.md` for alternatives.

### Single-line workaround

For `try_expr`, using a single-line form (`try body except E: handler`)
avoids INDENT entirely.  The `except` clauses use `:` between exception
type and handler expression, which doesn't require indentation.

The same workaround is used for inline `match` expressions:

```nomi
result = match value: case 1 => "one"; case _ => "many"
```

Cases use `=>` so the match delimiter can remain `:` without colliding with
case bodies.  The transformer lowers each case body to `return expr` inside
an immediately-invoked anonymous function.

Indented `match` expressions work when each case body is a single expression:

```nomi
result = match value:
    case 1: "one"
    case _: "many"
```

This form deliberately does not use `suite` for case bodies.  It parses a
block of expression-valued case lines and lowers them to the same IIFE shape.
Because the inner block consumes the final newline before `_DEDENT`, assignment
and return positions need statement-level grammar entries such as
`target = match_block_expr` and `return match_block_expr`.

Nested match values need a specific case alternative:

```lark
case_block_expr: "case" pattern ["if" test] ":" match_block_expr
               | "case" pattern ["if" test] ":" test _NEWLINE
```

Without the first alternative, an indented nested match consumes its own final
newline before `_DEDENT`, then the outer case still expects another `_NEWLINE`
before the next outer `case`.

## AST: Variable Name Shadowing in Loops

### `name` reassigned in `func_equation` loop

When implementing defaults in equation args, the loop variable `name`
was reused:
```python
for i, arg in enumerate(eq_args):
    if isinstance(arg, tuple):
        name, default = arg    # BUG: overwrites the function name!
```
**Fix**: use distinct variable names (`arg_name`, `arg_default`).

## AST: `_nomi_*` Custom Attributes Break `isinstance` Checks

Storing custom attributes like `_nomi_eq_args`, `_nomi_eq_guard`,
`_nomi_where_body`, `_nomi_defer` on `ast.AST` nodes **does not affect**
`isinstance(node, ast.stmt)` checks.  Safe to use.

However, if a method inadvertently returns `None` or a non-`ast.stmt`
from a handler, the `file_input` transformer silently drops it from
the module body (no error, empty Module).

### `_nomi_defer` must be stripped before re-evaluation

When a deferred statement is evaluated during function exit, the
`_nomi_defer` attribute is still present.  The `eval_Expr`/`eval_Assign`
check re-triggers defer registration (infinite loop).  **Fix**: strip
the attribute in the finally block before executing the deferred stmt.

## Interpreter: `eval_List` / `eval_Tuple` and `Starred`

The interpreter's `eval_List` and `eval_Tuple` originally just collected
evaluated elements.  When a `Starred` element appeared, it evaluated to
a value (e.g., `[1, 2]`) but was **not spread** into the list.  **Fix**:
check `isinstance(elt, ast.Starred)` and `extend` instead of `append`.

## Interpreter: `match_case` Ignored Guards

The `match_case` method only checked pattern matching, ignoring
`case.guard` entirely.  This was a latent bug — guards in `case n if
n > 0:` were silently ignored.  **Fix**: after pattern match succeeds,
check `case.guard` and evaluate it; return False if guard fails.

## Desugar: Order of Passes Matters

`UnderscoreLambda` runs before `PositionalHole`.  Both wrap expressions
in anonymous `FunctionDef` nodes.  If a single expression uses both `_`
and `$1`, the result is nested lambdas (starts at outermost).  Avoid
mixing hole types in one expression.

## Features That Failed / Deferred

| Feature | Blocker | Doc |
|---------|---------|-----|
| Full-suite match as expression | Lark INDENT/suite in `test` context | see match-expression appendix in `patterns.md` |
| Elvis `?? return/raise` | `ast.IfExp` can't hold statements | Below |
| Postfix `if` on expr | Conflicts with ternary `if` | Below |
| Postfix `unless` on expr | Conflicts with expression grammar | Below |

### Elvis `?? return`

`x ?? return` needs `if x is None: return` — but `ast.IfExp(orelse=ast.Return())`
is invalid AST (`orelse` must be expression, not statement).  Requires
statement-level transformation (multiple output stmts from one expression).

### Postfix `if`/`unless` on expressions

`x = 'a' if True` is ambiguous: the parser tries ternary `'a' if True`
(missing `else`) before the statement-level postfix rule.  Solution
options: use different keyword (`when`), or change expression grammar
to not greedily consume `if` without `else`.

## Desugar: Invariant Checks for `removed_node_types`

After each desugar pass runs, the pipeline validates that any AST node
types listed in the pass's `removed_node_types` are genuinely absent from
the tree.  A pass that claims to remove `ast.Break` but misses a case is
caught immediately.  See `_check_pass_invariants` in `pipeline.py`.

**Lesson:** Declare `removed_node_types` on every pass that removes a node
type.  The invariant check catches incomplete passes and incorrect metadata.
Passes that transform without removing any type should leave it empty.

## Source Spans: Lark's `visit_wrapper` Mechanism

Lark's `Transformer._call_userfunc` dispatches to named methods with just
`children` — the tree `meta` (source location) is lost.  However, if a
method has a `visit_wrapper` attribute, Lark calls it as
`wrapper(method, data, children, meta)` — meta IS available.

The `captures_span` decorator in `prototype/syntax/surface.py` uses this
mechanism: it sets `method.visit_wrapper` to a function that extracts
`SourceSpan` from `meta` and attaches it to any `SurfaceNode` result.

**Key constraint:** Lark's `meta` only carries line/column when the parser
is created with `propagate_positions=True`.  The default execution parser keeps
that off for speed; use `NOMI_PARSER_SPANS=1` or `preserve_positions=True` when
testing source-span behavior.  Without it, `meta.empty` is always `True` and no
position data is available.

**Lesson:** Use `@captures_span` on any lowering method that produces a
`SurfaceNode`.  The decorator is a one-line addition that wires source
location through the pipeline.

## Dead Code: Duplicate Parse-Tree and AST-Level Passes

`prototype/parser/nomi/desugar/precedence.py` contained a `Precedence` class
that restructured flat `BinOp` chains at the Python AST level.  It was never
registered in `BUILTIN_FEATURES` and never imported.  The actual precedence
restructuring runs at the Lark parse-tree level via `ExpressionLayer` in
`parse_tree_precedence.py`.

**Pattern to watch for:** When a transform exists at both the parse-tree
level (Lark `LayerTransform`) and the AST level (`BaseDesugarer`), only one
should be active.  The parse-tree version is preferred for precedence because
it runs before AST lowering, keeping the AST transformer simpler.

**Lesson:** Audit `prototype/parser/nomi/desugar/` for other unregistered
classes that duplicate parse-tree-level transforms.  A scan for classes
extending `BaseDesugarer` or `NomiDesugarer` that are not in `BUILTIN_FEATURES`
would catch this pattern.

## Desugar: Feature Registry as Single Source of Truth

The `BUILTIN_FEATURES` list in `prototype/syntax/features.py` now drives
four registries that were previously hardcoded:

1. Layer transforms (`get_layer_transforms()`)
2. Lowering mixin composition (`get_lowering_mixins()`)
3. Extra grammar layers (`get_extra_grammar_layers()`)
4. Desugar passes (`get_desugar_passes()`)

Adding a new syntax feature means adding one entry to `BUILTIN_FEATURES`
plus the implementation module.  No editing `assemble.py`, `functions.py`,
or `pipeline.py`.

**Lesson:** When adding infrastructure that derives configuration from
feature declarations, validate at import time (like `_validate_pipeline` does
for `depends_on`).  Silent misconfiguration is worse than a loud error.
