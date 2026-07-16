---
name: nomi-parse
description: Modify the Nomi parser — grammar rules, AST lowering, desugar pipeline.
compatibility: deepseek
---

Before adding new syntax, check the `nomi-language-design` skill,
`docs/design/syntax.md`, and `docs/design/decisions.md`. Consult
`docs/research/convergences.md` and `open_questions.md` only when the target
choice remains open. Syntax changes should be driven by design decisions, not
the other way around.

For a registered feature, run `python3 -m tools.design_passes show <id>` and
read its focused target plus bridge before editing grammar. Treat accepted and
rejected packet fixtures as the frontend contract; update pass status and
validation when parser capability changes.

For core/sugar separation, read `docs/design/README.md` and
`docs/orientation/implementation_guideline.md`. Every syntax feature should
declare whether it is core surface, standard convenience, library/protocol, or
scoped language tool. Convenience syntax needs an inspectable reduction target
and should not require a final evaluator hook.

Because Nomi is still exploratory, parser work should preserve optionality.
Prefer declarative feature metadata, versioned payload/schema contracts, and
inspectable surface/core artifacts over hardcoded parser/lowering branches.
Read `docs/orientation/exploratory_implementation_doctrine.md` before broad
parser or frontend changes.

## Feature Work Contract

Before implementing or extending syntax, record the feature owner in
`prototype/syntax/features.py` and the target decision in `docs/design/`.
Name its layer/status, normal form or core target, docs/spec surface, focused
tests, and inspection command (`tools.syntax.inspect`, parse snapshots,
expansions, or capability matrix). If any of those are intentionally missing,
say why before writing parser code.

## Key files
- `prototype/grammar/layers/*.lark` — layered Lark grammar (assembled at runtime)
- `prototype/parser/nomi/ast_.py` — NomiToPythonAST transformer
- `prototype/parser/nomi/functions.py` — FunctionsMixin (func_expr, block_call_stmt)
- `prototype/parser/nomi/usage.py` — generate_ast() entry point
- `prototype/parser/nomi/desugar/` — AST reduction passes
- `docs/orientation/performance_notes.md` — parser performance history,
  LALR migration notes, known ambiguity traps, and parser frontend benchmarking
  tooling (`tools/perf/bench_parsers.py`, `scripts/profile_parsers.py`).

## Architecture
```
.nomi source → Lark parser (LALR + NomiPostLexer) → Lark parse tree
    → NomiToPythonAST.transform() → Python ast.Module
    → desugar_module() [reduced only] → simplified ast.Module
    → Interpreter.eval()
```

With opt-in Core IR path (`NOMI_USE_CORE_IR=1`):
```
.nomi source → ... → Python ast.Module
    → lower_python_ast_to_core() → Core IR
    → verify_core(strict=True)
    → backend.evaluate()  (python-ast, core-runtime, or js-core-runtime)
```

Target architecture for new work:
```
.nomi source → feature-selected parser/profile → raw/transformed tree
    → Nomi-owned Surface AST with SourceSpan
    → name/type/constraint/effect analysis and typed Surface
    → Core IR
    → Python AST compatibility backend or direct runtime backend
```

Parser frontend work must stay parser-family neutral. Lark, Rust fast AST,
future PEG grammars, parser combinators, Tree-sitter, or LR frontends should
all join the same `ParserFrontendSpec` registry and shared parse/AST/runtime
equivalence matrices. Do not let a new parser candidate define a dialect of
Nomi; internal CSTs can differ, observable accepted source and lowered
artifacts cannot.

Before adding broad syntax, read:
- `docs/design/syntax.md` - target source forms and punctuation discipline.
- `docs/design/semantics.md` - source-level control and behavior.
- `docs/design/decisions.md` - rejected forms and open experiments.
- `docs/design/industrial.md` - target artifacts and conformance.
- `docs/orientation/implementation_guideline.md` - current migration road.
- `docs/orientation/performance_notes.md` - current parser constraints.
- `docs/research/open_questions.md` - whether the syntax question is actually
  open.

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
- Identify the user act and confirm the target status in
  `docs/design/decisions.md`.
- Check consolidated research only when the decision is still open.
- Prefer a feature-owned manifest/profile plan (`prototype/syntax/features.py`)
  when the syntax is more than a small Python-parity extension.
- Check soft-keyword and ambiguity implications before editing grammar layers.
- Update `docs/orientation/implementation_guideline.md` only when the change
  exposes a reusable architectural seam.
