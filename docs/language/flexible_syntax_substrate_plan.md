# Flexible Syntax Substrate Plan

> Status: active implementation architecture plan.
>
> Scope: parser, grammar, lowering, desugaring, and interpreter structure. This
> document is about making Nomi easy to change while preserving coherence. It
> intentionally deprioritizes performance until the language surface is easier
> to evolve.

## Purpose

The target language docs now describe a large, pleasant future Nomi surface:
data, decode, constraints, result values, table flow, block policies, tests,
explanation, scoped notation, and symbolic structure. To reach that surface,
Nomi needs a grammar and parsing substrate where adding syntax is routine,
inspectable, and reversible.

For the detailed critique and stable TODO list that points into code, see
[Syntax Substrate TODO Audit](syntax_substrate_todo_audit.md).

The current pipeline is already a useful laboratory:

```text
source
-> assembled Lark grammar
-> raw Lark tree
-> parse-tree layer pipeline
-> Python AST lowering
-> AST desugar pipeline
-> Python/Nomi/reduced interpreters
```

The problem is not that this is wrong. The problem is that each new feature can
still require hand coordination across many places:

```text
.lark rule
-> disjunction wiring
-> optional parse-tree transform
-> Python AST transformer method
-> custom AST attributes or Python AST encodings
-> desugar pass
-> interpreter eval method
-> reduced interpreter guard
-> tests, samples, docs
```

For fast language growth, Nomi should make that path explicit and mostly
mechanical.

## Design Goal

Optimize first for:

- ease of adding syntax;
- ease of removing syntax;
- local reasoning about one feature at a time;
- source spans and diagnostics;
- normal-form expansion that tools and humans can inspect;
- compatibility with the existing prototype while gradually escaping Python
  AST limitations.

Do not optimize first for:

- parser construction speed;
- smallest grammar;
- fastest interpreter dispatch;
- preserving Python AST as the only semantic representation.

Performance can be recovered later. A rigid substrate would cost more.

## Current Friction Points

| Friction | Current shape | Why it hurts syntax growth |
| --- | --- | --- |
| Layer registry is informal | `_LAYER_ORDER` and `_LAYER_TRANSFORMS` live in `prototype/grammar/assemble.py`. | A feature cannot bring its own grammar, transform, lowering, tests, and docs as one unit. |
| Parser cache needs feature-set discipline | `get_parser(extra_layers=...)` is now keyed by extra-layer tuple; future `features=[...]` should follow the same rule. | Experimental layers and syntax labs must never silently reuse a parser built for another feature set. |
| Python AST is the main IR | Nomi constructs often lower directly to Python AST or Python AST plus custom attributes. | Future syntax has to squeeze through Python forms such as IIFEs, `FunctionDef(name=None)`, or metadata on statements. |
| Source spans are not first-class | Lark tokens have position data, but lowering usually discards it. | Diagnostics and `explain` cannot reliably point to the user's surface form. |
| Desugar passes are ordered manually | `DESUGAR_PASSES` is a list of AST transformers. | Pass dependencies and input/output node contracts are not machine-checkable. |
| Feature admission is not executable | Docs define normal forms, but code does not require each feature to declare its normal-form reduction. | Syntax can slip in as one-off transformer logic. |
| Parse snapshots are not standard | Existing tests focus on behavior and desugar units. | Grammar changes can accidentally reshape unrelated syntax without an obvious review artifact. |
| Future syntax has no safe holding zone | Unsupported aspirational forms either fail parse or require premature semantics. | Design fixtures cannot be partially parsed for tooling, highlighting, or staged lowering. |

## Recommended Architecture

### 1. Introduce Feature Manifests

Make each syntax feature a small package with a manifest. A feature should be
able to declare:

```text
name
status
grammar fragments
soft keywords
parse-tree normalizers
surface node constructors
lowering/desugar passes
interpreter hooks, if any
normal forms used
fixtures/tests
docs links
```

Possible directory shape:

```text
prototype/syntax/features/
    pipeline/
        feature.py
        grammar.lark
        normalize.py
        lower.py
        tests/
    data/
        feature.py
        grammar.lark
        nodes.py
        lower.py
        diagnostics.md
    block_call/
        feature.py
        grammar.lark
        lower.py
```

Sketch:

```python
@syntax_feature(
    name="pipeline",
    status="prototype-ready",
    normal_forms=["flow", "function"],
    docs=[
        "docs/convenience/syntax_synthesis_matrix.md",
        "docs/language/target_language_tour.md",
    ],
)
class PipelineFeature:
    grammar = "grammar.lark"
    parse_transforms = [PipelineTreeNormalizer]
    surface_nodes = [PipeExpr]
    lower_passes = [LowerPipeToCall]
    fixtures = ["tests/fixtures/pipeline.nomi"]
```

The manifest is not about plugin glamour. It is about keeping syntax work
small, reviewable, and searchable.

### 2. Split Surface AST From Core AST

Add a Nomi-owned surface tree between Lark and Python AST:

```text
Lark tree
-> Nomi Surface AST
-> Nomi Core AST
-> Python AST backend and/or Core interpreter
```

The surface AST should preserve what the user wrote:

```python
@dataclass
class SourceSpan:
    file: str | None
    start_line: int
    start_col: int
    end_line: int
    end_col: int

@dataclass
class PipeExpr(SurfaceExpr):
    value: SurfaceExpr
    stages: list[SurfaceExpr]
    span: SourceSpan

@dataclass
class BlockCall(SurfaceStmt | SurfaceExpr):
    callee: SurfaceExpr
    args: list[SurfaceExpr]
    block_params: Pattern | None
    body: list[SurfaceStmt]
    span: SourceSpan
```

The core AST should contain only semantic anchors:

```text
Module
Binding
Function
Call
BlockCall
PatternMatch
DataValue
DecodeBoundary
ResultMatch
Trace
```

Most new syntax should lower to these. If a feature cannot lower to the core,
that is a signal that the language may need a new primitive, not just another
grammar rule.

### 3. Keep Python AST As A Backend, Not The Language IR

Python AST is useful for bootstrapping, but it should become one backend:

```text
Nomi Core AST -> Python AST backend -> existing interpreters
Nomi Core AST -> Core interpreter   -> future direct semantics
Nomi Core AST -> explain/trace view -> diagnostics and tooling
```

This lets Nomi keep working while gradually moving sensitive features away from
Python-shaped encodings.

Good candidates to move into Nomi-owned nodes early:

- block calls;
- binding constraints;
- match-as-expression;
- where clauses;
- data declarations;
- decode boundaries;
- result/absence operations;
- trace/explain.

These are exactly the features where Python AST encodings become awkward.

### 4. Make Lowering Passes Declarative

Replace the plain ordered `DESUGAR_PASSES` list over time with pass metadata:

```python
@lowering_pass(
    name="lower_pipeline",
    after=["resolve_names"],
    removes=[PipeExpr],
    produces=[CallExpr],
    normal_forms=["flow"],
)
class LowerPipeline:
    ...
```

The pass manager can then:

- sort passes by dependency;
- print the active pipeline;
- check that no removed surface nodes remain;
- expose `--explain-lowering` for one file;
- run one pass at a time in tests.

This is more important than speed. It makes syntax evolution boring.

### 5. Add A Parse And Lowering Snapshot Harness

Every feature should have snapshots at multiple levels:

```text
source
raw parse shape
surface AST
core AST
lowered Python AST, if applicable
runtime output, if implemented
diagnostic output, if failing
```

Suggested commands:

```bash
python3 -m tools.syntax.inspect samples/demo.nomi --stage parse
python3 -m tools.syntax.inspect samples/demo.nomi --stage surface
python3 -m tools.syntax.inspect samples/demo.nomi --stage core
python3 -m tools.syntax.inspect samples/demo.nomi --stage python-ast
```

This gives grammar changes a visible diff before behavior changes. For a
language-design-heavy project, that is gold.

### 6. Support Syntax Experiments Without Global Mutation

Keep the existing idea of extra grammar layers, but make it correct and more
powerful:

- cache parsers by feature set, not one global parser;
- allow `get_parser(features=[...])`;
- allow tests to parse with experimental feature bundles;
- keep feature status visible: `implemented`, `prototype-ready`,
  `design-needed`, `research-only`;
- prevent research-only features from entering default parsing accidentally.

Immediate improvement already started:

```text
prototype/parser/nomi/usage.py:get_parser(extra_layers=...)
```

now caches by `tuple(extra_layers or [])`. The same keying discipline should be
kept when `features=[...]` is added.

### 7. Use Soft Keywords By Default

To keep syntax addition easy, prefer soft keywords for new forms:

```text
data
match
case
trace
using
transaction
check
test
quote
rewrite
```

Soft keywords should be recognized only in specific grammar positions. This
lets old code continue to use ordinary names where possible and reduces the
cost of experimentation.

Rule of thumb:

```text
new everyday syntax -> soft keyword first
new global reserved word -> only after strong evidence
```

### 8. Add Island Parsing For Fenced Future Layers

For future layers such as `quote:`, `use units:`, symbolic rewrite, or dense
array notation, Nomi should support island parsing:

```text
ordinary Nomi parser
-> fenced block recognized
-> inner text preserved with source spans
-> optional domain parser handles it later
```

This lets the main parser accept and locate advanced regions without making
the first everyday grammar understand every future notation.

Example node:

```python
@dataclass
class SyntaxIsland(SurfaceExpr | SurfaceStmt):
    fence: str
    language: str | None
    text: str
    span: SourceSpan
```

This is how Nomi can grow power without turning every file into a private
dialect.

### 9. Put Diagnostics Into The Parser Contract

Every syntax feature should declare likely parse and lowering errors:

```text
missing block after `using(...) -> name:`
invalid pipeline stage
ambiguous placeholder scope
pattern used where binding target is required
constraint expression has no bound value
```

Do not wait for runtime errors to explain syntax. The parser/lowering layer
should produce Nomi vocabulary:

```text
This block call needs a body.
This pipeline stage is not callable.
This `_` placeholder would capture two different scopes.
This decode field failed at config.toml:12:5.
```

This requires source spans to survive from Lark tokens into surface/core nodes.

## Concrete Implementation Sequence

### Phase A: Make The Current Pipeline Inspectable

Small, low-risk changes:

1. Keep parser caching keyed so `extra_layers` and future feature sets get
   distinct parsers.
2. Add a `tools.syntax.inspect` command that prints raw Lark tree and current
   Python AST for a file.
3. Add parse snapshots for representative samples and target fixtures.
4. Regenerate `prototype/grammar/nomi.ref.lark` through a command rather than
   manual Python snippets.

Exit gate:

```text
When a grammar rule changes, reviewers can see parse-shape diffs without
running the whole interpreter.
```

### Phase B: Add Source Spans

1. Define `SourceSpan`.
2. Teach transformer helpers to attach spans to lowered nodes or side tables.
3. Preserve spans through desugar passes.
4. Print spans in parse/lowering inspection.

Exit gate:

```text
At least bindings, functions, calls, block calls, and match cases can report
where they came from.
```

### Phase C: Introduce Surface Nodes For New Work Only

Do not rewrite everything at once. Start with features that hurt most:

1. `BlockCall`
2. `BindingTarget` / `Constraint`
3. `PipeExpr`
4. `MatchExpr`
5. `DataDecl`

Existing syntax can keep lowering directly to Python AST until touched.

Exit gate:

```text
New syntax no longer needs to pretend to be Python AST immediately.
```

### Phase D: Build A Core Lowering Layer

Define a small core AST aligned with Nomi normal forms:

```text
Binding
Function
Call
BlockCall
PatternMatch
Flow
DataConstruct
Decode
Trace
```

Then lower surface nodes into this core. Keep a Python AST backend for current
execution.

Exit gate:

```text
The phrase "this syntax reduces to a normal form" is true in code, not only in
docs.
```

### Phase E: Convert Features To Manifests

Move one feature at a time into manifest packages:

1. pipeline;
2. underscore/positional holes;
3. where;
4. block calls;
5. binding constraints;
6. data/decode.

Exit gate:

```text
A new feature can be reviewed by opening one feature directory plus its tests.
```

### Phase F: Add Syntax Labs

Create a safe experimental mode:

```text
nomi --features data,decode,trace file.nomi
pytest --nomi-features data,decode
```

Rules:

- default parser only includes implemented/prototype-ready features;
- design-needed features require explicit opt-in;
- research-only features can parse as syntax islands but cannot run.

Exit gate:

```text
Target-language experiments can be parsed, inspected, and discussed before
runtime semantics exist.
```

## Feature Addition Workflow

The eventual workflow for adding syntax should be:

1. Create or update a feature manifest.
2. Add grammar fragment and parser snapshot.
3. Add surface node with source spans.
4. Lower to core normal forms.
5. Add diagnostics for common mistakes.
6. Add or update target fixture/tour snippet.
7. Add runtime behavior only if the core needs it.
8. Commit docs, parse snapshots, and behavior tests together.

The important inversion:

```text
Old workflow: grammar first, semantics chased afterward.
New workflow: normal form first, feature package carries grammar to runtime.
```

## Experiment Contract

Before a broad syntax or semantics experiment enters the codebase, it should
answer the same small set of questions. This keeps experiments quick without
making the default language unstable.

| Question | Required answer |
| --- | --- |
| What is the user pressure? | One concrete task or readability problem, not a copied syntax wish. |
| What is the normal form? | Binding, function, pattern, flow, block, absence/result, data boundary, or explanation; otherwise propose the smallest new primitive. |
| What is the status? | `target-only`, `research-only`, `design-needed`, `prototype-ready`, `implemented`, or `rejected-for-now`. |
| What profile enables it? | `default`, `lab`, `target-tour`, `docs-only`, or a named feature bundle. |
| What code owns it? | Feature manifest, grammar fragments, surface/core nodes, lowering passes, runtime handlers, diagnostics, docs, and tests. |
| How is it inspected? | Raw tree, transformed tree, surface AST, core AST, Python AST backend, and normal-form expansion where applicable. |
| What can fail? | Parse errors, lowering errors, unsupported profile errors, runtime errors, and diagnostics in Nomi vocabulary. |
| What proves it? | Parse/lowering snapshots first; runtime, web, notebook, and regression tests only when behavior exists. |

The first implementation of this contract should be deliberately lightweight:
metadata next to existing code, no code generation, no dynamic plugin loading,
and no requirement to migrate stable old syntax before new experiments can
benefit from the structure.

## What Not To Do Yet

- Do not rewrite the whole parser from Lark unless Lark becomes the blocker.
- Do not build a macro system as the extensibility mechanism.
- Do not make every feature dynamically pluggable at runtime before the static
  feature-manifest workflow exists.
- Do not replace Python AST everywhere in one sweep.
- Do not optimize parser construction until feature-set caching and inspection
  are correct.
- Do not accept syntax that cannot produce a normal-form expansion.

## Near-Term Code Changes Worth Doing First

These are the highest leverage first patches:

1. **Parser cache keying**:
   extend the current extra-layer cache key to future feature manifests.
2. **Grammar manifest registry**:
   replace hardcoded `_LAYER_ORDER` with a small layer registry object that can
   list core layers plus opt-in experiment layers.
3. **Inspection CLI**:
   add a command that prints grammar text, raw tree, transformed tree, Python
   AST, and eventually surface/core AST.
4. **SourceSpan prototype**:
   attach spans to a few high-value nodes without changing semantics.
5. **Feature template**:
   add a `prototype/syntax/features/_template/` directory showing the expected
   files for a new syntax feature.
6. **BlockCall surface node**:
   stop representing block bodies only as custom values inside Python AST
   keywords; give block calls an explicit Nomi-owned node before lowering.
7. **DataDecl experiment**:
   implement future `data` first as parse + surface AST + diagnostics, even
   before full runtime semantics.

## Success Criteria

This architecture is working when:

- adding one syntax form usually touches one feature directory;
- parse/lowering snapshots show what changed before runtime tests run;
- diagnostics can point to source spans in user syntax;
- the reduced interpreter catches unlowered core forms;
- target fixtures and the target language tour can be partially parsed in
  explicit experimental modes;
- docs can say "this lowers to binding/block/flow" and code can show the same
  expansion.

That is the ground needed for the grand vision: not a huge grammar, but a
language workbench where pleasant syntax can be grown, compared, reverted, and
explained without fear.
