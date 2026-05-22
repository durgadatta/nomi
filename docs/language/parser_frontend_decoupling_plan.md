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

## Parser Technology Direction

### Keep Lark As Bootstrap

Lark remains the default parser frontend until another frontend can produce
the same artifacts and pass the existing parser/runtime suite. It is still
useful for fast grammar iteration and Python-hosted testing.

### Spike Tree-sitter Next

Tree-sitter is the best next parser frontend candidate because it is designed
around concrete syntax trees, parser generation, editor embedding, and
incremental parsing. Its grammar DSL has explicit sequence, choice, repeat,
precedence, alias, field, keyword, conflict, and external-scanner concepts.
Its implementation model is also attractive for Nomi: the CLI reads a grammar
and emits a generated C parser, while the runtime library can be embedded from
other languages.

Nomi-specific concern: indentation, virtual tokens, soft keywords, and
postfix/block-call disambiguation must become an explicit external-scanner and
grammar contract before Tree-sitter can replace Lark for execution parsing.

Current spike:

- `tools/parser_spikes/tree_sitter_nomi/` contains a generated Tree-sitter
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

The rule for any Rust parser spike: do not emit Python AST as the primary
artifact. Emit Nomi CST, Surface IR, or a stable serialized form, then let the
Python AST backend lower from that Nomi-owned representation.

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
   Tree-sitter spikes can emit.
2. Grow `tools/parser_spikes/tree_sitter_nomi/` from the demo-parse grammar
   into structural rules plus an external scanner contract, but keep it
   non-selectable until it accepts the current grammar and lowers correctly.
3. Map the current parser samples through both Lark and Tree-sitter into the same
   Surface IR snapshot.
4. Move `DataDecl` and `MatchExpr` into Surface IR before any parser swap,
   because direct Python AST lowering would otherwise hide the very boundary
   the parser work is trying to create.

## Sources

- Tree-sitter grammar DSL: <https://tree-sitter.github.io/tree-sitter/creating-parsers/2-the-grammar-dsl.html>
- Tree-sitter implementation overview: <https://tree-sitter.github.io/tree-sitter/5-implementation.html>
- Tree-sitter grammar-writing guide: <https://tree-sitter.github.io/tree-sitter/creating-parsers/3-writing-the-grammar.html>
- pest parser overview: <https://pest.rs/>
- LALRPOP overview: <https://lalrpop.github.io/lalrpop/>
- ANTLR4 repository and target-language notes: <https://github.com/antlr/antlr4>
- MLIR overview: <https://mlir.llvm.org/>
- MLIR language reference: <https://mlir.llvm.org/docs/LangRef/>
