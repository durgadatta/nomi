---
name: nomi-parse
description: Modify the Nomi parser — grammar rules, AST lowering, desugar pipeline.
compatibility: deepseek
---

Before adding new syntax, check the `nomi-language-design` skill and the
research corpus (`docs/research/language_family_coverage_map.md`) for design
rationale and cross-language precedent. Syntax changes should be driven by
design decisions, not the other way around.

For core/sugar separation, read
`docs/language/core_layer_separation_plan.md`. Every syntax feature should
declare whether it is L2/L3 semantic core, L4 sugar, L5 library convention,
L6 scoped extension, or L7 backend-facing. L4 syntax must have an inspectable
reduction target and should not require a final evaluator hook.

## Key files
- `prototype/grammar/layers/*.lark` — layered Lark grammar (assembled at runtime)
- `prototype/parser/nomi/ast_.py` — NomiToPythonAST transformer
- `prototype/parser/nomi/functions.py` — FunctionsMixin (func_expr, block_call_stmt)
- `prototype/parser/nomi/usage.py` — generate_ast() entry point
- `prototype/parser/nomi/desugar/` — AST reduction passes
- `docs/orientation/performance_notes.md` — parser performance history,
  LALR migration notes, and known ambiguity traps

## Architecture
```
.nomi source → Lark parser (LALR + NomiPostLexer) → Lark parse tree
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
- `docs/language/core_layer_separation_plan.md` — layer vocabulary and eval
  separation rules.
- `docs/language/language_degrees_of_freedom.md` — core/sugar/library/scoped/rejected framework.
- `docs/language/flexible_syntax_substrate_plan.md`
- `docs/language/parser_frontend_decoupling_plan.md` when work touches Lark,
  Tree-sitter/Rust parser candidates, parser frontend selection, or the
  Python AST backend boundary.
- `docs/language/python_independence_and_compiler_backend_plan.md` when syntax
  work affects the future split between Surface IR, Core IR, Python AST, MLIR,
  LLVM, or Wasm backends.
- `docs/language/syntax_substrate_todo_audit.md`
- `docs/language/architecture_refactoring_plan.md` when the syntax work also
  changes public runtime APIs, inspection tools, web, notebook, or package
  boundaries.
- `docs/research/language_family_coverage_map.md` — check if cross-language
  research already covers the syntax domain.

## Grammar rules
- Uses Lark LALR parser with `NomiPostLexer`
- Default execution parsing disables Lark source-position propagation for speed.
  Use `NOMI_PARSER_SPANS=1` or `preserve_positions=True` when working on
  diagnostics, inspection, or source-span propagation.
- Nomi diffs from Python grammar: `func` keyword, `=>` arrow functions, compound annotation, `block_call_stmt`
- Reserved words in spec but not grammar: data, const, module, export, effect, shape, trait
- Before broad grammar rewrites, read `docs/orientation/performance_notes.md`.
  The LALR migration depends on postlexed virtual tokens for operator sections,
  arrow-function parens, match case colons/guards, postfix flow guards, and
  block colons.

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
5. **Layer metadata** — record the feature layer and reduction/core target in
   `SyntaxFeature` as soon as that metadata exists.
6. **Tests** — parser unit tests, feature tests, reduced/core invariant tests,
   and regression snapshots as appropriate.

Before starting any syntax addition:
- Identify the Nomi normal form and confirm the feature status in
  `docs/convenience/review_and_roadmap.md`.
- Check the research corpus for cross-language precedent on this syntax domain.
- Prefer a feature-owned manifest/profile plan (`prototype/syntax/features.py`)
  when the syntax is more than a small Python-parity extension.
- Check soft-keyword and ambiguity implications before editing grammar layers.
- Update `docs/language/syntax_substrate_todo_audit.md` when the change exposes
  a new architectural seam.
