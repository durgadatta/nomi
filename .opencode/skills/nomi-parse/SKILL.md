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

## Grammar rules
- Uses Lark Earley parser with PythonIndenter postlexer
- Nomi diffs from Python grammar: `func` keyword, `=>` arrow functions, compound annotation, `block_call_stmt`
- Reserved words in spec but not grammar: data, const, module, export, effect, shape, trait

## AST lowering
- NomiToPythonAST extends PythonASTTransformer + FunctionsMixin
- `func_expr`: `(x)=>expr` lowered to FunctionDef with Return body
- `block_call_stmt`: `call(args) -> target: body` lowered to Expr(Call(..., keywords=[keyword('__block__', value=(body, params))]))

## Adding syntax
1. Add grammar rule to the appropriate layer file in `prototype/grammar/layers/`
2. Add AST lowering in `ast_.py` or create a new mixin
3. Update parser tests: `prototype/tests/unit/parser/test_nomi_ast_nodes.py`
4. Update interpreter tests if behavior changes
