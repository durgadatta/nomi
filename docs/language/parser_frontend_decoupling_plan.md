# Parser Frontend Decoupling Plan

> Status: active implementation plan.
>
> Scope: move Nomi parsing from "Lark is the parser" to "Lark is the current
> parser frontend", while preserving the Python AST backend until downstream
> runtime layers are ready to move.

## Goal

Nomi should stop letting one Python parser library define the language
frontend. The near-term target is:

```text
source
-> parser frontend (Lark today, Tree-sitter/Rust spike next)
-> Nomi CST / Surface IR with spans
-> Nomi Core IR
-> Python AST backend
-> existing interpreters
```

This keeps the current execution path working while making it possible to swap
or compare parser technologies. Python AST remains a backend artifact, not the
semantic center of the language.

## First Code Boundary

`prototype/parser/nomi/frontend.py` now owns the parser frontend contract:

- `ParserFrontendSpec` describes one frontend technology.
- `ParserFrontendCapabilities` records whether that frontend parses the full
  current grammar, lowers to Python AST, preserves spans, and is selectable for
  execution.
- `ParseArtifacts` names the raw and transformed artifacts before Python AST
  lowering.
- `LarkParserFrontend` wraps the current Lark LALR parser, postlexer, parse
  caches, and layer-transform pipeline.
- `tools.syntax.inspect --stage parser-frontends` and
  `prototype.runtime.inspect(stage="parser_frontends")` print implemented and
  candidate parser frontends.

`prototype/parser/nomi/usage.py` still exposes the old functions:

```text
get_parser()
parse_raw_tree()
parse_transformed_tree()
generate_ast()
```

That compatibility layer is intentional. Existing tests, notebook tooling, web
playground paths, and interpreter modes should not need to change during the
first parser decoupling pass.

The execution-selection rule is strict: non-Lark frontends must stay
non-selectable until they can parse the full current grammar and lower to the
same Python AST backend artifact. This prevents a fast subset parser from
quietly becoming the language definition.

The parse-acceptance rule is shared: every registered frontend whose
`ParserFrontendCapabilities.parse_current_grammar` flag is true participates in
`prototype/tests/unit/parser/test_parser_frontend_acceptance.py`. That test
matrix runs the same sample files and feature snippets through Lark and the new
parser. Future frontends join by implementing `parse_accepts()` and setting the
capability flag; they do not get a separate, weaker parser test path.

The Python-AST equivalence rule is stricter: every registered frontend whose
`ParserFrontendCapabilities.lower_to_python_ast` flag is true must produce
exactly the same `ast.dump(..., include_attributes=False, indent=2)` text as
`lark-lalr` for the same sample files and feature snippets. A parser may parse
successfully before it can lower, but it cannot claim backend compatibility
until this text artifact matches.

This rule is parser-family neutral. A future PEG parser, LR parser,
parser-combinator frontend, Tree-sitter frontend, or handwritten parser should
join the same registry, same sample/snippet acceptance matrix, same AST
equivalence matrix, and same downstream runtime checks. Frontends may differ in
their internal CST, error recovery, generated code, or implementation language;
they must not define a different Nomi. Until Surface/Core IR is authoritative,
Lark remains the reference oracle for accepted source and Python AST backend
shape.

A non-Lark frontend is a functional replacement only when all of these are
true:

```text
parse_current_grammar
lower_to_python_ast
selectable_for_execution
```

`get_functional_replacement_frontends()` is intentionally empty until a
non-Lark parser satisfies that full contract.

## Parser Technology Direction

### Keep Lark As Bootstrap

Lark remains the default parser frontend until another frontend can produce
the same artifacts and pass the existing parser/runtime suite. It is still
useful for fast grammar iteration and Python-hosted testing.

### Compare Multiple Parser Families

Tree-sitter is useful, but it should not become the only parser experiment.
Nomi should compare parser families under one acceptance matrix and choose a
default only after both ergonomics and speed are visible.

Current experiment roles:

| Frontend | Role |
| --- | --- |
| `lark-lalr` | readable bootstrap and current default |
| `tree-sitter-cst` | fast generated C parser and tooling CST |
| `rust-fast-ast` | first direct Rust AST payload slice |
| `winnow-fast-cst` | fastest handwritten Rust parser candidate |
| `pest-readable-cst` | readable Rust PEG grammar-file candidate |
| `chumsky-readable-cst` | readable Rust parser-combinator and diagnostics candidate |
| `lalrpop-lr-cst` | generated Rust LR parser candidate |

For each implemented frontend, the rule is the same:

```text
same accepted source -> same Surface/Core/Python AST behavior
```

Speed and readability are selection criteria, not permission to accept a
different language.

When adding a new parser family, add a distinct `ParserFrontendSpec`, runner,
payload/CST adapter, and test enrollment. Do not special-case the shared
equivalence tests for that parser. If the parser is temporarily tolerant or
raw-preserving, keep it parse-acceptance-only until its lowered artifact is
identical to the reference path.

Keep the implementation modular as parser families accumulate. `frontend.py`
should remain the registry, capability, and process-runner boundary; each
parser-specific serialized artifact should live in a focused adapter module
such as `rust_payload.py` or a future PEG/CST payload adapter. A new parser
family should not append hundreds of lowering lines to the shared frontend
file.

### Tree-sitter Spike

Tree-sitter is still a useful candidate because it is designed around concrete
syntax trees, parser generation, editor embedding, and incremental parsing. Its
grammar DSL has explicit sequence, choice, repeat, precedence, alias, field,
keyword, conflict, and external-scanner concepts. Its implementation model is
also attractive for Nomi: the CLI reads a grammar and emits a generated C
parser, while the runtime library can be embedded from other languages.

Nomi-specific concern: indentation, virtual tokens, soft keywords, and
postfix/block-call disambiguation must become an explicit external-scanner and
grammar contract before Tree-sitter can replace Lark for execution parsing.

Current spike:

- `prototype/parser/backends/tree_sitter_nomi/` contains a generated Tree-sitter
  parser.
- The first acceptance fixture is `samples/demo.nomi`.
- The parser frontend acceptance matrix now also runs sample files and focused
  feature snippets through both `lark-lalr` and `tree-sitter-cst`.
- The current spike is line-oriented and token-preserving: it proves the
  non-Lark parser toolchain can consume the full demo file without parse
  errors, but it is not yet structural enough to lower to Python AST.

### Treat Rust PEG/LR Tools As Runtime Parser Candidates

Rust parser generators such as pest or LALRPOP are plausible if Nomi wants a
fast native parser crate before editor tooling is the main concern. pest uses
PEG grammar files compiled into Rust parser code; LALRPOP is a Rust parser
generator in the Yacc/ANTLR/Menhir family.

The next Rust parser spike may reasonably be a PEG grammar frontend, likely
`pest-readable-cst` if readability and grammar-file clarity are the goal. Its
first milestone should be parser acceptance against the shared sample/snippet
matrix; its second milestone should be a serialized CST/Surface payload that
can lower through the same Python AST backend contract as other frontends.

The rule for any Rust parser spike, including PEG: do not emit Python AST as
the primary artifact. Emit Nomi CST, Surface IR, or a stable serialized form,
then let the Python AST backend lower from that Nomi-owned representation.

`prototype/parser/backends/rust_fast_ast/` is the first direct-AST bridge slice. It
uses a Rust Pratt parser to emit a small JSON AST payload, and
`prototype/parser/nomi/frontend.py` adapts that payload to Python `ast.Module`.
Its tests compare exact AST dump text against Lark for simple assignments,
calls, binary expressions, function equations, and arrow-function assignments.
It is not a full grammar frontend yet, so its `lower_to_python_ast` capability
stays false until it can pass the shared all-fixture equivalence matrix.

### Keep ANTLR As A Portable Fallback

ANTLR4 is worth keeping in the comparison set because it has broad generated
target support, including Python3. It is less directly aligned with
incremental editor parsing than Tree-sitter, but it can validate whether Nomi's
grammar can live in a portable, non-Lark grammar family.

### Use MLIR After Core IR, Not As The Parser

MLIR belongs below the parser and Core IR boundary. Its value is extensible
operations, regions, blocks, traits, interfaces, verifiers, textual dumps, and
pass infrastructure. That is excellent for Nomi Core IR and later compiler
lowering, but it should not absorb source parsing before Nomi has a stable
Surface IR and Core IR contract.

## Nomi Grammar Contract

Every parser frontend must eventually prove these artifacts:

| Artifact | Purpose |
| --- | --- |
| Raw CST | Preserve source shape and trivia enough for tooling. |
| Normalized CST | Apply precedence, indentation, and virtual-token policy. |
| Surface IR | Preserve Nomi-specific syntax with `SourceSpan`. |
| Core IR | Lower to Nomi normal forms independent of Python AST. |
| Python AST | Backend compatibility target for the current interpreters. |

The compatibility rule:

```text
new parser frontend -> same Surface/Core/Python AST observable behavior
```

The strategic rule:

```text
Python AST is allowed after Surface/Core, never before them in new frontend work.
```

## Suggested Next Slices

1. Define a serialized CST/Surface IR debug format that both Lark and
   Tree-sitter/Rust spikes can emit.
2. Grow `prototype/parser/backends/rust_fast_ast/` from the first AST slice into
   suites, blocks, calls, literals, comparisons, and Nomi reductions until it
   can join the full Python-AST frontend matrix.
3. Grow `prototype/parser/backends/tree_sitter_nomi/` from the demo-parse grammar
   into structural rules plus an external scanner contract, but keep it
   non-selectable until it accepts the current grammar and lowers correctly.
4. Map the current parser samples through Lark and non-Lark frontends into the
   same Surface IR snapshot.
5. Move `DataDecl` and `MatchExpr` into Surface IR before any parser swap,
   because direct Python AST lowering would otherwise hide the very boundary
   the parser work is trying to create.

## Next Pass Checkpoint

Current implementation checkpoint:

- `lark-lalr` remains the only selectable execution frontend.
- `tree-sitter-cst` accepts the current sample/snippet parse matrix, but its
  grammar is still token-preserving rather than structural.
- `rust-fast-ast` is the first Rust direct-AST spike. It can emit a JSON payload
  and adapt that payload to Python `ast.Module` for an exact-parity slice that
  now includes the core `scripts/demo.nomi` file, `samples/block.nomi`,
  `samples/constraint.nomi`, and the shared parser feature snippets. That
  Rust-generated Python AST also executes successfully through the Nomi
  interpreter for the core demo.
- `rust-fast-ast` has `parse_current_grammar=True` because it passes the shared
  parse-acceptance matrix. It must not set `lower_to_python_ast` or
  `selectable_for_execution` until it passes the shared all-fixture AST
  equivalence and runtime behavior tests, including the broader guided-tour
  samples.
- `prototype/parser/backends/rust_fast_ast/README.md` is the detailed implementation
  handoff for finishing the Rust parser: current coverage, missing syntax,
  promotion gates, parity workflow, and performance cleanup.

Recommended next implementation order:

1. Add parser-neutral snapshot/debug tooling for serialized parser payloads so
   Rust fast AST, future PEG, and other frontends can compare payload/CST shape
   before Python AST adaptation.
2. Finish the expression layer beyond the current slice: slices, sets,
   keyword/starred call arguments, spread in literals, composition operators,
   bitwise/shift operators, and `is`/`in`.
3. Expand suite/block lowering beyond the current sample slice: `unless`,
   `elif`/`else`, defer statements, multiple assignment/pattern targets, and
   remaining guided-tour forms in `samples/demo*.nomi`.
4. Split `rust_payload.py` into smaller adapter modules before adding another
   large syntax family; likely boundaries are expressions, statements,
   patterns, and shared text-splitting helpers.
5. Once a meaningful subset passes exact AST parity, replace `cargo run` in
   `RustFastAstParserFrontend` with a cached binary path or a build helper so
   the parser matrix measures parser work instead of Cargo startup.
6. Keep the PEG candidate path explicit: when `pest-readable-cst` starts,
   register it as a separate frontend with parse-acceptance-only capability,
   then graduate it through the same payload, AST equivalence, and runtime
   gates.
7. Promote `rust-fast-ast` into `get_python_ast_frontends()` only when it can
   pass `prototype/tests/unit/parser/test_parser_frontend_acceptance.py` for
   the full sample/snippet AST dump matrix.

Do not commit Rust build products. `**/target/` is ignored, and only
`Cargo.toml`, `Cargo.lock`, and source files under `parser/` should
be tracked for this spike.

## Sources

- Tree-sitter grammar DSL: <https://tree-sitter.github.io/tree-sitter/creating-parsers/2-the-grammar-dsl.html>
- Tree-sitter implementation overview: <https://tree-sitter.github.io/tree-sitter/5-implementation.html>
- Tree-sitter grammar-writing guide: <https://tree-sitter.github.io/tree-sitter/creating-parsers/3-writing-the-grammar.html>
- pest parser overview: <https://pest.rs/>
- LALRPOP overview: <https://lalrpop.github.io/lalrpop/>
- ANTLR4 repository and target-language notes: <https://github.com/antlr/antlr4>
- MLIR overview: <https://mlir.llvm.org/>
- MLIR language reference: <https://mlir.llvm.org/docs/LangRef/>
