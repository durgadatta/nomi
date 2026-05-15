# CLAUDE.md

See @AGENTS.md for the full project map, build commands, test commands, and
development posture.  This file adds Claude-specific orientation on top.

## Quick orientation

Nomi is an experimental programming language built as a Python-hosted
prototype (Lark grammar → desugar pipeline → layered interpreter).
The current focus is making syntax experimentation fast: the extension
path for new syntax is now 3-4 isolated steps instead of editing 5-7
files across the codebase.

## Adding new syntax (the current extension path)

1. **Grammar** — add a rule to the appropriate layer in
   `prototype/grammar/layers/`.  Use `python3 -m tools.syntax.inspect
   FILE --stage raw-tree` to verify the parse tree.

2. **Lowering** — create a module in `prototype/parser/nomi/lowering/`
   with a mixin class containing the Lark-transformer method.  Mix it
   into `FunctionsMixin` in `prototype/parser/nomi/functions.py`.

3. **Desugar** (optional) — if the syntax needs an AST-level transform,
   create a pass in `prototype/parser/nomi/desugar/` and add an entry
   to `BUILTIN_FEATURES` in `prototype/syntax/features.py`.

4. **Surface node** (optional) — if Python AST can't naturally represent
   the construct, define a `SurfaceNode` subclass in
   `prototype/syntax/surface.py` and emit it from the lowering step.
   The pipeline lowers it automatically before interpreter eval.

5. **Tests** — add parser unit tests, functional tests, and regenerate
   regression snapshots if sample output changes.

## Pipeline stages (for debugging)

```
Source → raw Lark tree → layer-transformed tree → surface AST (mixed)
      → Python AST (pure) → desugared Python AST → interpreter eval
```

Inspect any stage: `python3 -m tools.syntax.inspect FILE --stage <stage>`
Valid stages: `raw-tree`, `transformed-tree`, `surface-ast`, `python-ast`

## Key files Claude should know about

| File | Role |
|------|------|
| `prototype/syntax/features.py` | Feature manifest registry (single source of truth) |
| `prototype/syntax/surface.py` | Surface node base + `lower_surface_to_python` |
| `prototype/parser/nomi/lowering/` | Per-feature Lark→AST lowering modules |
| `prototype/parser/nomi/desugar/pipeline.py` | Desugar pass chain (derived from features) |
| `prototype/grammar/assemble.py` | Grammar assembly + layer transforms (derived from features) |
| `prototype/interpreter/runner.py` | Shared `make_runner` for all interpreter modes |
| `prototype/runtime/modes.py` | Mode registry (python, nomi, reduced) |
| `tools/syntax/inspect.py` | Pipeline stage inspection CLI |

## Commit style

- Short imperative subject: "Add X", "Fix Y", "Split Z"
- Body explains why, not what
- Co-Authored-By trailer for commits made in this session
- One logical change per commit

## Settings

Project-level Claude Code config is in `.claude/settings.json`.  Personal
overrides (model preference, local paths) go in `.claude/settings.local.json`
which is gitignored.
