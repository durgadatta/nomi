# Parser Frontends

Parser implementations for Nomi. Each subdirectory is a self-contained parser
crate or grammar that can be registered as a frontend in
`prototype/parser/nomi/frontend.py`.

The bar for replacing the default parser is full current-grammar parity:

```text
parse current Nomi grammar
-> preserve source spans
-> lower to the same Python AST backend artifact
-> pass the existing parser/runtime suites
```

Partial parsers may live here as research artifacts, but they must not be wired
as session execution frontends until their
`ParserFrontendCapabilities.selectable_for_session_execution` flag can honestly
be set. Browser experiments use separate host-specific flags.

Parser frontends that claim current-grammar parsing support must implement
`parse_accepts()` and set `ParserFrontendCapabilities.parse_current_grammar`.
That enrolls them in
`prototype/tests/unit/parser/test_parser_frontend_acceptance.py`, the shared
parse matrix for sample files and parser feature snippets.

Parser frontends that claim Python AST backend support must implement
`python_ast_text()` and set `ParserFrontendCapabilities.lower_to_python_ast`.
The same test file then compares their text AST dump against `lark-lalr`
exactly. Parse success is not enough to call a parser functionally equivalent.

For quick local comparisons, run:

```bash
python3 -m prototype.parser.parse_matrix --iterations 5
```

This prints the same sample-file matrix for every parse-capable frontend, with
basic per-file timings. It is a smoke comparison, not a final benchmark.

Current local toolchain expectation:

```bash
rustc --version
cargo --version
tree-sitter --version
```

The first Rust-backed candidates should target these distinct experiment goals:

- `tree-sitter-cst`: full CST with an indentation/external-scanner contract,
  then Surface IR and Python AST backend lowering; or
- `winnow-fast-cst`: a Rust parser-combinator crate aimed at the fastest
  handwritten parser path;
- `pest-readable-cst`: a Rust PEG grammar-file parser aimed at readability;
- `chumsky-readable-cst`: a Rust parser-combinator path aimed at readable
  parser code and diagnostics;
- `lalrpop-lr-cst`: a generated Rust LR parser comparable to the current LALR
  shape.

Every candidate should emit a Nomi-owned CST/Surface payload first. Python AST
is the backend adapter target, not the grammar author's primary data model.

## Current Spike

`tree_sitter_nomi/` is the first non-Lark parser. It currently proves the
Tree-sitter toolchain can generate a parser and parse `samples/demo.nomi`
without errors. It is intentionally not selectable for execution yet because
its first grammar is line-oriented/token-preserving, not a full structural
replacement for the Lark grammar and lowering pipeline.

`rust_fast_ast/` is the first direct-AST Rust spike. It emits a Nomi-owned JSON
payload and the Python frontend adapts that payload into `ast.Module`. Its
current slice has exact Python AST parity for the shared parser snippet matrix
and selected demo/block/constraint fixtures, and it participates in the
Python-AST-capable frontend set. It remains intentionally not selectable for
normal execution until parser unit tests, functional behavior, regression
samples, CLI execution, and downstream runtime behavior match the Lark path.
See `rust_fast_ast/README.md` for the detailed completion handoff.

## Handoff Notes

For the next pass, keep the replacement gate strict:

- Read `prototype/parser/backends/rust_fast_ast/README.md` first. It contains the
  concrete syntax backlog, promotion checklist, parity workflow, and known
  traps for completing the Rust parser.
- Broaden `rust_fast_ast/src/main.rs` by syntax family, starting with expression
  parity before block statements.
- Add every newly supported Rust syntax slice to
  `prototype/tests/unit/parser/test_rust_fast_ast_frontend.py` and compare the
  exact text dump against `lark-lalr`.
- Do not set `selectable_for_execution=True` for `rust-fast-ast` until the
  runtime/regression/CLI promotion gate is genuinely met.
- Do not commit generated Cargo output. `target/` is intentionally ignored; the
  tracked Rust spike state should stay at `Cargo.toml`, `Cargo.lock`, and
  source files.

Useful checks:

```bash
cargo test --manifest-path prototype/parser/backends/rust_fast_ast/Cargo.toml
pytest prototype/tests/unit/parser/test_rust_fast_ast_frontend.py
pytest prototype/tests/unit/parser
python3 -m tools.syntax.inspect --stage parser-frontends
```
