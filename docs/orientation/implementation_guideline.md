# Implementation Guideline

> Status: implementation orientation.
>
> Scope: how to make code changes in the Python-hosted prototype while moving
> toward separated core layers, inspectable reductions, and future backends.

## Current Posture

Nomi is still intentionally Python-hosted. That is a productive bootstrap
choice, not the language boundary.

Current path:

```text
source
-> Lark grammar
-> parse-tree transforms
-> Nomi/Python AST lowering
-> optional SurfaceNode islands
-> Python AST backend
-> Python-hosted interpreter
```

Opt-in Core IR path (`NOMI_USE_CORE_IR=1`) or explicit eval backend
(`NOMI_EVAL_BACKEND=core-runtime`, `NOMI_EVAL_BACKEND=js-core-runtime`,
`execute(..., eval_backend="core-runtime")`):

```text
source
-> ... Python AST artifact
-> lower_python_ast_to_core() -> Core IR (registered L1 node types)
-> verify_core(strict=True)
-> eval backend dispatch (python-ast, core-direct, core-runtime, or js-core-runtime)
```

Target path:

```text
source
-> raw/transformed tree
-> surface nodes with SourceSpan
-> semantic core
-> implementation core IR
-> backend or direct core eval
```

Read before broad implementation work:

- [`core_layer_separation_plan.md`](../language/core_layer_separation_plan.md)
- [`architecture_refactoring_plan.md`](../language/architecture_refactoring_plan.md)
- [`flexible_syntax_substrate_plan.md`](../language/flexible_syntax_substrate_plan.md)
- [`python_independence_and_compiler_backend_plan.md`](../language/python_independence_and_compiler_backend_plan.md)
- [`core_runtime_backend_design.md`](../language/core_runtime_backend_design.md) —
  reference design for direct runtime backends; read before changing eval
  backend behavior.

## Layer Discipline

Use the L0-L7 vocabulary from the core layer plan.

| Layer | Implementation rule |
| --- | --- |
| L0 runtime substrate | Own frames, values, host capabilities, diagnostics, and ABI-shaped runtime records. |
| L1 implementation core IR | Small executable IR; direct eval and future backends target this. |
| L2 semantic core | User-facing meaning: binding, function, call, data, pattern, block, diagnostic. |
| L3 canonical surface | Syntax that teaches L2 concepts directly. |
| L4 sugar reductions | Pleasant spellings that must lower away before eval. |
| L5 library conventions | Ordinary functions and values; no grammar changes. |
| L6 scoped extensions | Fenced notation with inspectable expansion. |
| L7 backend targets | Python AST, direct runtime, Wasm, MLIR, LLVM, foreign bindings. |

The main implementation guardrail:

```text
Do not add permanent evaluator behavior for L4 sugar.
```

If a feature seems to need `eval_*`, first classify it:

- L4 sugar: add/repair lowering or desugar instead.
- L2/L3 semantic core: plan a core operation and temporary compatibility path.
- L6 extension: eval only the fenced expansion or an explicit extension node.
- L7 backend issue: put the workaround in backend code, not language meaning.

## Preparatory Implementation Work

The first implementation pass should be preparatory and low-risk.

### 1. Feature Layer Metadata

Extend `prototype/syntax/features.py` so each `SyntaxFeature` declares:

```text
layer
semantic_forms
reduces_to
runtime_hooks_allowed
backend_requirements
docs
tests
```

Initial contracts:

- every builtin feature declares a layer;
- L4 features declare a reduction target;
- L2/L3 features declare semantic forms;
- any feature that still needs an evaluator hook says whether that hook is
  temporary, semantic, or backend compatibility.

### 2. Core IR Skeleton

~~Add passive core artifacts before changing execution.~~ Done.

`prototype/syntax/core.py` — 17 passive frozen-dataclass CoreNode types
(Module, Literal, Load, Bind, Function, Call, Return, Branch, Diagnostic,
Loop, Match, PatternTest, ConstructData, GetField, Raise, Handle, Sequence).
Includes `verify_core(strict=...)`, `dump_core()`, `core_to_python_ast()`
(forward lowering), and `lower_python_ast_to_core()` (backward projection).

### 3. Inspection Stages

~~Grow `prototype.runtime.inspect()` and `tools.syntax.inspect`.~~ Done.

Current stages via CLI and API:
`raw_tree`, `transformed_tree`, `surface-ast`, `python-ast`, `core`,
`core-verify`, `core-to-python`, `backend-lowered`, `features`, `capabilities`,
`parser-frontends`, `eval-backends`, `passes`, `expansions`.

### 4. Reduced/Core Guardrails

Keep `prototype/interpreter/reduced/interpreter.py` aligned with declared
reductions. The Core IR verifier (`verify_core(strict=True)`) now provides an
additional guardrail via `NOMI_VERIFY_CORE=1`. The reduced interpreter and the
verifier should converge on the same set of rejected forms.

### 5. First Semantic Core Slice

Use constrained binding as the first semantic-core migration candidate.

Why:

- it is central to Nomi's identity;
- it crosses assignment, parameters, data fields, patterns, and diagnostics;
- it already has feature tests;
- it exposes the difference between L2 binding and L1 bind/check/commit ops.

Do not start here until metadata and passive Core IR exist.

### 6. First Sugar Slice

Use `unless` or postfix conditional return as the first sugar migration
candidate.

Goal:

- prove that an L4 form reduces to branch/return;
- prove no L4 node reaches core eval;
- keep diagnostics pointing at the original spelling.

## Working Rules

- Prefer facade-first changes over package moves.
- Keep old imports working while new APIs mature.
- Keep Python AST backend behavior green while adding new artifacts.
- Do not combine semantic changes with mechanical layer moves.
- Add focused contract tests before migrating frontends or public APIs.
- Preserve source spans whenever a new node shape is introduced.
- Update `.agents/skills/nomi-*` when the workflow changes.

## Useful Commands

```bash
# Full suite
pytest

# Core IR verification gate
NOMI_VERIFY_CORE=1 pytest
NOMI_USE_CORE_IR=1 pytest

# Feature and contract checks
pytest prototype/tests/features
pytest prototype/tests/contracts

# Reduced-mode pressure
pytest --interpreter-modes reduced

# Pipeline inspection
python3 -m tools.syntax.inspect samples/demo.nomi --stage raw-tree
python3 -m tools.syntax.inspect samples/demo.nomi --stage transformed-tree
python3 -m tools.syntax.inspect samples/demo.nomi --stage surface-ast
python3 -m tools.syntax.inspect samples/demo.nomi --stage python-ast
python3 -m tools.syntax.inspect samples/demo.nomi --stage core
python3 -m tools.syntax.inspect samples/demo.nomi --stage core-verify
python3 -m tools.syntax.inspect --stage eval-backends
python3 -m tools.syntax.inspect --stage parser-frontends

# Runtime facade from Python
python3 - <<'PY'
from prototype.runtime import execute
print(execute(source="x = 2\n", mode="nomi").bindings)
PY
```

## AI Tools Usage

Nomi has used ChatGPT, Grok, DeepSeek, Gemini, Claude, Codex, and other agents
for design critique, planning, and implementation pressure. Treat AI output as
design material until reconciled with:

- active docs;
- code;
- tests;
- samples;
- the current layer plan.

Agents should make implementation changes in small commits and leave notes in
the relevant plan when they discover a sharper boundary, stale assumption, or
new preparatory task.
