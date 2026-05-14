---
name: nomi-parse
description: Modify the Nomi parser — grammar rules, AST lowering, desugar pipeline.
compatibility: deepseek
---

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
- `docs/language/flexible_syntax_substrate_plan.md`
- `docs/language/syntax_substrate_todo_audit.md`
- `docs/language/architecture_refactoring_plan.md` when the syntax work also
  changes public runtime APIs, inspection tools, web, notebook, or package
  boundaries.

## Grammar rules
- Uses Lark Earley parser with PythonIndenter postlexer
- Nomi diffs from Python grammar: `func` keyword, `=>` arrow functions, compound annotation, `block_call_stmt`
- Reserved words in spec but not grammar: data, const, module, export, effect, shape, trait

## AST lowering
- NomiToPythonAST extends PythonASTTransformer + FunctionsMixin
- `func_expr`: `(x)=>expr` lowered to FunctionDef with Return body
- `block_call_stmt`: `call(args) -> target: body` lowered to Expr(Call(..., keywords=[keyword('__block__', value=(body, params))]))

## Adding syntax
1. Identify the Nomi normal form and feature status before editing grammar.
2. Prefer a feature-owned manifest/profile plan when the syntax is more than a
   tiny Python-parity extension.
3. Add grammar rule to the appropriate layer file in `prototype/grammar/layers/`
   only after checking soft-keyword and ambiguity implications.
4. Add a surface/core node plan when Python AST cannot represent the syntax
   naturally. Direct Python AST lowering is acceptable for small current
   bootstrap forms, but not the target for major Nomi features.
5. Add AST lowering in `ast_.py` or create a new mixin.
6. Add parse/lowering snapshots or focused parser tests:
   `prototype/tests/unit/parser/`.
7. Update interpreter tests if behavior changes.
8. Update `docs/language/syntax_substrate_todo_audit.md` and inline
   `NOMI-SUBSTRATE-*` TODOs when the change exposes a new architectural seam.
