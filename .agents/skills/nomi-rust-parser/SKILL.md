---
name: nomi-rust-parser
description: Work on Nomi Rust parser frontends and parser-spike infrastructure. Use for rust-fast-ast, future Rust parser candidates, JSON parser payload contracts, parse-acceptance promotion, and plug-and-play parser frontend boundaries.
compatibility: deepseek
---

Pair this with `nomi-parse` for language syntax decisions and with
`nomi-test` when changing acceptance or parity coverage.

## Current Rust Spike

- `tools/parser_spikes/rust_fast_ast/src/main.rs` — CLI glue only.
- `src/error.rs` — parse diagnostics.
- `src/token.rs` — token model and display helpers.
- `src/lexer.rs` — indentation-aware lexer.
- `src/ast.rs` — Rust-side structural AST and JSON emission.
- `src/parser.rs` — parser state, statements, Pratt expressions, raw fallback.
- `prototype/parser/nomi/frontend.py` — Python registration and payload adapter.
- `prototype/tests/unit/parser/test_rust_fast_ast_frontend.py` — Rust-specific
  parity and fixture coverage.
- `prototype/tests/unit/parser/test_parser_frontend_acceptance.py` — shared
  parse-acceptance gate.

## Contract

Keep Rust parser candidates plug-and-play behind a small external contract:

```text
binary ast-json path/to/source.nomi -> JSON payload on stdout
nonzero exit -> syntax/parse error on stderr
```

The Python frontend should know how to run the candidate and adapt its payload.
Do not tie parser internals to `rust-fast-ast`; future Rust parsers may be
handwritten, generated, CST-first, or direct-AST.

## Promotion Gates

Advance capabilities independently:

1. `parse_current_grammar=True` only after `parse_accepts()` handles the shared
   sample/snippet matrix accepted by Lark.
2. `lower_to_python_ast=True` only after exact `ast.dump(...,
   include_attributes=False, indent=2)` parity for shared Python-AST frontend
   tests.
3. `selectable_for_execution=True` only after parser, functional, regression,
   CLI, and downstream runtime behavior match the Lark path.

Never promote execution because a tolerant/raw payload parses files. Raw
payloads are useful for acceptance, not semantic parity.

## Workflow

1. Start with `git status --short`.
2. Run the focused Rust crate check:
   `cargo test --manifest-path tools/parser_spikes/rust_fast_ast/Cargo.toml`.
3. Run parser frontend tests:
   `pytest prototype/tests/unit/parser/test_rust_fast_ast_frontend.py prototype/tests/unit/parser/test_parser_frontend_acceptance.py prototype/tests/unit/parser/test_parser_frontend.py`.
4. For full parse-acceptance sweeps, compare Rust against files Lark accepts;
   ignore aspirational/scratch files that Lark rejects unless the user names
   them directly.
5. Commit in small milestones: structural refactor, capability promotion,
   parity slice, fixture hardening.

## Design Rules

- Keep `main.rs` thin. Add parser behavior in `parser.rs`, token behavior in
  `token.rs`, lexer behavior in `lexer.rs`, and payload shape in `ast.rs`.
- Prefer exact AST parity for mature slices. Use `Raw` only as a temporary
  parse-acceptance bridge.
- Preserve byte offsets in tokens; future spans and diagnostics depend on them.
- Avoid changing `frontend.py` in a way that assumes only one Rust parser can
  exist.
- If adding a second Rust parser, add a new frontend spec and runner path rather
  than overloading `rust-fast-ast`.

## Environment Note

If `cargo fmt` fails because `rustfmt` is missing, report it instead of
installing toolchain components unless the user asks.
