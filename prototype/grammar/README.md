# Nomi Grammar

## Quick Reference

```
Source text
    ↓
ParserFrontendSpec          ← Lark is the implemented frontend today
    ↓
assemble_grammar()          ← reads all layer .lark files, returns one grammar string
    ↓
Lark LALR parser            ← parses source into raw Lark Tree
    ↓
LayerPipeline               ← each LayerTransform restructures/annotates the tree
    ↓
NomiToPythonAST.transform() ← converts final tree to Python AST
    ↓
Desugar pipeline            ← AST-level reductions
    ↓
Interpreter                 ← eval
```

## Where Is the Grammar?

The current **Lark grammar** lives in `prototype/grammar/layers/`.  Each
`.lark` file covers one syntactic concern:

| File | Concern | ~Lines |
|------|---------|--------|
| `terminals.lark` | `%ignore`, `%declare`, `NAME`, `NUMBER`, `STRING`, … | 36 |
| `expressions.lark` | `test`, `or_test`, `comparison`, `bin_expr`, `factor`, `power`, `atom` | 76 |
| `statements.lark` | `stmt`, `funcdef`, `if`/`for`/`while`/`try`/`match`, `block_call_stmt`, imports | 69 |
| `patterns.lark` | `match`/`case` pattern sub-grammar | 39 |
| `bindings.lark` | `assign`, `annassign`, `augassign`, `parameters` | 36 |
| `calls.lark` | `atom_expr`, `funccall`, comprehensions | 19 |

The file `nomi.ref.lark` at this level is a **full assembled grammar**
(regenerated from the layers below).  It is not read by the parser at
runtime — the parser calls ``assemble_grammar()`` directly.  It exists
for:

* **Reference** — see the complete grammar in one file
* **Tooling** — IDEs, linters, syntax highlighters can consume it
* **Debugging** — compare against what the layered assembly produces

Regenerate it with::

    from prototype.grammar.assemble import assemble_grammar
    text = assemble_grammar()
    Path("prototype/grammar/nomi.ref.lark").write_text(text)

## Parse-Tree vs AST Transforms

Two categories of transforms, operating at different levels:

| Level | Location | Base class |
|-------|----------|------------|
| **Lark parse tree** | `parser/nomi/desugar/parse_tree_precedence.py` | `LayerTransform` (in `grammar/layer.py`) |
| **Python AST** | `parser/nomi/desugar/*.py` | `BaseDesugarer` |

Parse-tree transforms run **before** ``NomiToPythonAST``.
AST desugar passes run **after**, before the interpreter.

## How Expressions Work

Binary operators (`+`, `-`, `*`, `/`, `&`, `|`, `<<`, …) all live in a
single flat rule `bin_expr` inside `expressions.lark`:

```lark
?bin_expr: factor ((_binary_op) factor)*
```

The parser produces a **flat left-to-right** tree.  Precedence and
associativity are handled by `ExpressionLayer`
(`layers/expression_transform.py`), a `LayerTransform` that restructures
`bin_expr` subtrees using a shunting-yard algorithm driven by this table:

```python
_PRECEDENCE = {
    '|':  (2, True),  '^':  (4, True),  '&':  (6, True),
    '<<': (8, True),  '>>': (8, True),
    '+':  (10, True), '-':  (10, True),
    '*':  (12, True), '/':  (12, True), '%': (12, True),
    '//': (12, True), '@':  (12, True),
}
```

This table lives next to the grammar (same layer file's companion
transform), so adding an operator touches one location.

## Adding New Syntax

### Step 1 — Grammar rule

Add the new rule to the most relevant `.lark` layer file.  For example,
to add a `repeat` loop, edit `statements.lark`:

```lark
repeat_stmt: "repeat" test ":" suite
```

### Step 2 — Wire into a disjunction

Find the appropriate disjunction in the same or a nearby layer and add
the new rule name.  For `repeat_stmt`:

```lark
?compound_stmt: if_stmt | while_stmt | for_stmt | repeat_stmt | ...
```

If the disjunction lives in a different layer, edit that layer file.

### Step 3 — Optional: parse-tree transform

If the grammar rule needs structural refinement before the AST
transform (like precedence restructuring), create a `LayerTransform`
subclass alongside the layer and register it in `assemble.py`:

```python
# grammar/layers/my_transform.py
from prototype.grammar.layer import LayerTransform

class MyLayer(LayerTransform):
    def repeat_stmt(self, children):
        # restructure children if needed
        return Tree('repeat_stmt', children)
```

Then in `assemble.py`:
```python
from .layers.my_transform import MyLayer

_LAYER_TRANSFORMS = [
    ExpressionLayer(),
    MyLayer(),           # ← add here in order
]
```

### Step 4 — AST lowering

Add the corresponding method to the parser transformer in
`prototype/parser/nomi/` (either in an existing mixin or a new one).
The method name must match the grammar rule name:

```python
# In some transformer mixin
def repeat_stmt(self, items):
    return ast.While(...)  # or desugar to existing AST
```

### Step 5 — Interpreter

Add `eval_Repeat` (or the desugared form's handler) to the relevant
interpreter mixin in `prototype/interpreter/`.

### When NOT to add a transform

Most syntax does **not** need a `LayerTransform`.  Only add one if the
grammar rule **intentionally produces a flat or intermediate structure**
that needs restructuring before the AST transform can consume it.
Precedence is the canonical example.

## Layer Transform Pipeline

Each layer transform receives the **output tree of the previous layer**
and returns a new tree.  The chain is defined in `assemble.py`:

```python
_LAYER_TRANSFORMS = [ExpressionLayer()]
```

Base classes live in `grammar/layer.py`:
- `LayerTransform(lark.Transformer)` — override `visit_<rule>` or
  `<rule>` methods to restructure the tree.
- `LayerPipeline` — runs transforms in sequence.

## Grammar Assembly

`assemble.py` provides grammar text and layer-transform construction for the
current Lark frontend. `prototype/parser/nomi/frontend.py` owns the parser
frontend boundary so future Tree-sitter or Rust parsers can emit Nomi-owned
CST/Surface IR before the Python AST backend.

`assemble.py` provides two functions:

| Function | Returns | Used by |
|----------|---------|---------|
| `assemble_grammar(extra_layers=None)` | grammar string | `usage.py` → `Lark()` |
| `get_layer_pipeline()` | `LayerPipeline` | `usage.py` → `pipeline.run()` |

To load **experimental** syntax without modifying the built-in layers,
pass `extra_layers` file names:

```python
parser = get_parser(extra_layers=["my_experiment.lark"])
```

These files are looked up in `prototype/grammar/layers/`.

## Python Parser (Separate)

The **Python-compatible parser** (`prototype/parser/python/`) uses
Lark's built-in `python.lark` (LALR) via `Lark.open_from_package`.
It is **not** layered — it exists to exercise the interpreter on
standard Python syntax.  Changes to the Nomi grammar do not affect it.
