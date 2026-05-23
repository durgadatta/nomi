---
name: nomi-rust-parser
description: Work on Nomi Rust parser frontends and parser-spike infrastructure. Use for rust-fast-ast, future Rust parser candidates, JSON parser payload contracts, parse-acceptance promotion, and plug-and-play parser frontend boundaries.
compatibility: deepseek
---

Pair this with `nomi-parse` for language syntax decisions and with
`nomi-test` when changing acceptance or parity coverage.

## Current Rust Spike

- `prototype/parser/backends/rust_fast_ast/README.md` — status, promotion gates, and
  the "Observed Improvement Notes" pickup list. Read/update that section when
  you notice follow-up work.
- `rust-toolchain.toml` — project Rust toolchain declaration. Keep required
  components such as `rustfmt` explicit here.
- `prototype/parser/backends/rust_fast_ast/src/main.rs` — CLI glue only.
- `src/error.rs` — parse diagnostics.
- `src/token.rs` — token model and display helpers.
- `src/lexer.rs` — indentation-aware lexer.
- `src/ast.rs` — Rust-side structural AST and JSON emission.
- `src/parser.rs` — parser state, statements, Pratt expressions, raw fallback.
- `prototype/parser/nomi/frontend.py` — Python registration and payload adapter.
- `prototype/parser/nomi/rust_payload.py` — Rust JSON payload to Python AST
  adapter. Keep parser-specific lowering here, not in `frontend.py`.
- `prototype/tests/unit/parser/test_rust_fast_ast_frontend.py` — Rust-specific
  parity and fixture coverage.
- `prototype/tests/unit/parser/test_rust_fast_ast_lowering_parity.py` — exact
  Rust-vs-Lark Python AST parity for the current lowered slice, including
  `scripts/demo.nomi`.
- `prototype/tests/functional/parser/test_rust_fast_ast_demo_execution.py` —
  downstream execution proof for the Rust-generated core demo AST.
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
handwritten, PEG-generated, LR-generated, parser-combinator-based, CST-first,
or direct-AST.

All parser candidates must be functionally equivalent at the frontend boundary:
same accepted source, same lowered artifact, same downstream runtime behavior.
Different parser families may expose different raw CST/debug payloads, but they
must graduate through the same parse-acceptance, Python-AST parity, and runtime
gates. A future PEG parser should be registered as its own frontend, not folded
into `rust-fast-ast`.

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

When a new parser frontend is registered in `_FRONTENDS`
(`prototype/parser/nomi/frontend.py`), also add its name to `BENCH_FRONTENDS`
in `tools/perf/bench_parsers.py` so it appears in the parser comparison
benchmark.  If it is a Rust subprocess, add its crate metadata to
`_RUST_CRATES` in the same file for optional peak-RSS measurement.

## Workflow

1. Start with `git status --short`.
2. Run the focused Rust crate check:
   `cargo test --manifest-path prototype/parser/backends/rust_fast_ast/Cargo.toml`.
3. Run parser frontend tests:
   `pytest prototype/tests/unit/parser/test_rust_fast_ast_frontend.py prototype/tests/unit/parser/test_rust_fast_ast_lowering_parity.py prototype/tests/unit/parser/test_parser_frontend_acceptance.py prototype/tests/unit/parser/test_parser_frontend.py`.
4. When changing suite/block lowering, also run:
   `pytest prototype/tests/functional/parser/test_rust_fast_ast_demo_execution.py`.
5. For full parse-acceptance sweeps, compare Rust against files Lark accepts;
   ignore aspirational/scratch files that Lark rejects unless the user names
   them directly.
6. Commit in small milestones: structural refactor, capability promotion,
   parity slice, fixture hardening.

## Design Rules

- Keep `main.rs` thin. Add parser behavior in `parser.rs`, token behavior in
  `token.rs`, lexer behavior in `lexer.rs`, and payload shape in `ast.rs`.
- Prefer exact AST parity for mature slices. Use `Raw` only as a temporary
  parse-acceptance bridge.
- `scripts/demo.nomi` is now a parity and downstream-eval milestone for
  `rust-fast-ast`; keep it exact before broadening to guided-tour samples.
- Do not promote `lower_to_python_ast=True` just because the core demo lowers:
  the shared sample/snippet AST matrix and `samples/demo.nomi` still define the
  broader gate.
- Preserve byte offsets in tokens; future spans and diagnostics depend on them.
- Avoid changing `frontend.py` in a way that assumes only one Rust parser can
  exist.
- If adding a second Rust parser, add a new frontend spec and runner path rather
  than overloading `rust-fast-ast`.
- For a PEG next step, prefer the existing `pest-readable-cst` candidate name
  unless there is a strong reason to choose another PEG implementation.
- Do not grow one massive frontend file. Put parser-specific payload/CST
  lowering in a focused module such as `rust_payload.py` or a future
  `pest_payload.py`, while `frontend.py` stays registry and runner glue.

## Environment Note

If `cargo fmt` fails because `rustfmt` is missing, report it instead of
installing toolchain components unless the user asks.
