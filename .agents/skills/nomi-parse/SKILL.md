---
name: nomi-parse
description: Modify the Nomi parser — grammar rules, AST lowering, desugar pipeline.
compatibility: deepseek
---

Before adding new syntax, check the `nomi-language-design` skill and the
research corpus (`docs/research/language_family_coverage_map.md`) for design
rationale and cross-language precedent. Syntax changes should be driven by
design decisions, not the other way around.

## Key files
- `prototype/grammar/layers/*.lark` — layered Lark grammar (assembled at runtime)
- `prototype/parser/nomi/ast_.py` — NomiToPythonAST transformer
- `prototype/parser/nomi/functions.py` — FunctionsMixin (func_expr, block_call_stmt)
- `prototype/parser/nomi/usage.py` — generate_ast() entry point
- `prototype/parser/nomi/desugar/` — AST reduction passes

## Architecture
```
.nomi source → Lark parser (Earley) → Lark parse tree
    → NomiToPythonAST.transform() → Python ast.Module
    → desugar_module() [reduced only] → simplified ast.Module
    → Interpreter.eval()
```

Target architecture for new work:
```
.nomi source → feature-selected parser/profile → raw/transformed tree
    → Nomi-owned surface AST with SourceSpan
    → core normal forms
    → Python AST backend or direct runtime backend
```

Before adding broad syntax, read:
- `docs/language/language_foundation.md` — the design target.
- `docs/language/language_degrees_of_freedom.md` — core/sugar/library/scoped/rejected framework.
- `docs/language/flexible_syntax_substrate_plan.md`
- `docs/language/syntax_substrate_todo_audit.md`
- `docs/language/architecture_refactoring_plan.md` when the syntax work also
  changes public runtime APIs, inspection tools, web, notebook, or package
  boundaries.
- `docs/research/language_family_coverage_map.md` — check if cross-language
  research already covers the syntax domain.

## Grammar rules
- Uses Lark Earley parser with PythonIndenter postlexer
- Nomi diffs from Python grammar: `func` keyword, `=>` arrow functions, compound annotation, `block_call_stmt`
- Reserved words in spec but not grammar: data, const, module, export, effect, shape, trait

## AST lowering
- NomiToPythonAST extends PythonASTTransformer + FunctionsMixin
- `func_expr`: `(x)=>expr` lowered to FunctionDef with Return body
- `block_call_stmt`: `call(args) -> target: body` lowered to Expr(Call(..., keywords=[keyword('__block__', value=(body, params))]))

## Adding syntax

Follow the current extension path (5 steps, documented in `CLAUDE.md`):

1. **Grammar** — add a rule to the appropriate layer in
   `prototype/grammar/layers/`. Verify with `tools.syntax.inspect --stage raw-tree`.
2. **Lowering** — create a module in `prototype/parser/nomi/lowering/`
   with a mixin class. Mix it into `FunctionsMixin`.
3. **Desugar** (optional) — create a pass in `prototype/parser/nomi/desugar/`
   and add to `BUILTIN_FEATURES` in `prototype/syntax/features.py`.
4. **Surface node** (optional) — define a `SurfaceNode` subclass in
   `prototype/syntax/surface.py` when Python AST cannot represent it.
5. **Tests** — parser unit tests, functional tests, regression snapshots.

Before starting any syntax addition:
- Identify the Nomi normal form and confirm the feature status in
  `docs/convenience/review_and_roadmap.md`.
- Check the research corpus for cross-language precedent on this syntax domain.
- Prefer a feature-owned manifest/profile plan (`prototype/syntax/features.py`)
  when the syntax is more than a small Python-parity extension.
- Check soft-keyword and ambiguity implications before editing grammar layers.
- Update `docs/language/syntax_substrate_todo_audit.md` when the change exposes
  a new architectural seam.
