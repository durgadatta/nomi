# Parser Spikes

This directory is for parser-front-end experiments that are not yet selectable
for normal Nomi execution.

The bar for replacing the default parser is full current-grammar parity:

```text
parse current Nomi grammar
-> preserve source spans
-> lower to the same Python AST backend artifact
-> pass the existing parser/runtime suites
```

Partial parsers may live here as research artifacts, but they must not be wired
as selectable execution frontends until their
`ParserFrontendCapabilities.selectable_for_execution` flag can honestly be set.

Current local toolchain expectation:

```bash
rustc --version
cargo --version
tree-sitter --version
```

The first Rust-backed candidate should target either:

- `tree-sitter-cst`: full CST with an indentation/external-scanner contract,
  then Surface IR and Python AST backend lowering; or
- `rust-peg-cst`: a Rust parser crate that emits a Nomi-owned CST/Surface
  payload, then Python adapts that payload into the existing Python AST backend.
