# Rust Fast AST Parser Spike

This spike is the first non-Lark path that produces a Python-AST-compatible
artifact without routing through Lark. It is intentionally small today. Treat it
as real replacement machinery, not as the replacement itself.

## Current Status

`rust-fast-ast` currently supports exact `ast.dump(..., include_attributes=False,
indent=2)` parity with `lark-lalr` for:

- simple assignments: `x = 1`
- expression statements: `print("x")`
- positional calls: `f(a, 1)`
- arithmetic binary expressions: `+`, `-`, `*`, `/`, `**`
- parenthesized arithmetic precedence: `(1 + 2) * 3`
- unary minus, represented internally as `0 - expr` to match the current first
  slice only where tests require it
- function equations: `add(a, b) = a + b`
- arrow-function assignments: `double = x => x * 2`,
  `add = (a, b) => a + b`

It also has a broader parse-acceptance slice for both demo files:
`scripts/demo.nomi` and `samples/demo.nomi`. That slice emits a structural JSON
payload for indentation, `func` suites, `for`/`if`/`while` suites,
`try`/`except`, returns, yields, raises, augmented assignments, Nomi block
calls, constrained-binding targets, prefixed/triple strings, lists, attributes,
comparisons, boolean operators, conditional expressions, `where` suites,
guided-tour forms such as `unless`, `match`/`case`, `guard`, `data`
declarations, `$` holes, ranges, pipelines, null-safe tokens, and other
currently-raw expression forms.

The parse-acceptance slice is not exact Python AST parity. It is a
parser-frontier milestone only: `rust-fast-ast` is now enrolled in parser
frontend acceptance tests, but must not be made selectable for execution yet.
It also accepts the older Lark-accepted debug/interpreter fixtures covered by
`prototype/tests/unit/parser/test_rust_fast_ast_frontend.py`.

## Promotion Gate

Do not change these capability flags until the stated gate is genuinely met:

```python
ParserFrontendCapabilities(
    parse_current_grammar=False,
    lower_to_python_ast=False,
    selectable_for_execution=False,
)
```

Promotion sequence:

1. Keep `rust-fast-ast` out of `get_python_ast_frontends()` while it only emits
   a structural/tolerant payload.
2. Set `lower_to_python_ast=True` only when exact AST text parity passes for the
   shared sample/snippet matrix in
   `prototype/tests/unit/parser/test_parser_frontend_acceptance.py`.
3. `parse_current_grammar=True` is allowed once `parse_accepts()` handles every
   sample file and focused parser snippet accepted by Lark. This gate is now
   met for the parser frontend acceptance matrix.
4. Set `selectable_for_execution=True` only after parser unit tests, relevant
   functional tests, regression samples, CLI execution, and downstream runtime
   behavior all match the Lark path.

Full replacement means all three: parse current grammar, lower to the same
Python AST artifact, and be safe for normal execution.

## File Map

- `src/main.rs`: CLI argument handling only.
- `src/error.rs`: `ParseError` and diagnostics.
- `src/token.rs`: `TokenKind`, `Token`, token display helpers.
- `src/lexer.rs`: indentation-aware lexer and trivia handling.
- `src/ast.rs`: Rust-side `Stmt`, `Expr`, operators, and JSON emission.
- `src/parser.rs`: parser state, statement parsing, Pratt expression parser,
  and tolerant raw-form collection.
- `Cargo.toml`: standalone Rust spike package.
- `Cargo.lock`: tracked for reproducible local spike builds.
- `prototype/parser/nomi/frontend.py`: registers `rust-fast-ast`, runs the Rust
  CLI, and adapts the JSON payload to Python `ast.Module`.
- `prototype/tests/unit/parser/test_rust_fast_ast_frontend.py`: exact parity
  tests for the first supported slice plus demo parse-acceptance coverage.
- `prototype/tests/unit/parser/test_parser_frontend.py`: registry and promotion
  guard tests.

Generated build output belongs in `target/` and must not be committed.
`**/target/` is ignored at repo root.

## Current CLI Contract

The Rust binary accepts one command:

```bash
cargo run --quiet \
  --manifest-path tools/parser_spikes/rust_fast_ast/Cargo.toml \
  -- ast-json path/to/file.nomi
```

It prints a JSON payload shaped like:

```json
{
  "type": "Module",
  "body": [
    {
      "type": "Assign",
      "target": "x",
      "value": {"type": "Number", "value": "1"}
    }
  ]
}
```

The Python frontend then converts this payload to Python AST. The JSON payload
is the spike's public parser artifact for now; keep it stable enough to snapshot
and compare.

## Parser Architecture

The current Rust implementation is intentionally direct:

```text
source
-> lex()
-> Vec<Token>
-> Parser::parse_module()
-> Vec<Stmt> / Expr tree
-> module_json()
-> Python frontend JSON adapter
-> ast.Module
```

Important current parser choices:

- It uses a handwritten Pratt parser for expressions.
- `current_infix()` owns precedence and associativity.
- Function equations and assignments are parsed speculatively and rewind on
  mismatch.
- Calls are postfix forms parsed by `parse_postfix()`.
- Indentation is tokenized directly in Rust for the accepted demo slice.
- Comments are skipped as trivia.
- Source spans and Nomi surface nodes are not implemented yet.
- Keep future parser candidates plug-and-play by preserving the CLI payload
  contract (`ast-json <path>`) and adapting new internals behind that boundary.

## Exact AST Parity Rules

Every supported Rust syntax slice must compare against Lark using:

```python
ast.dump(module, include_attributes=False, indent=2)
```

Do not compare runtime output first. Runtime equality can hide AST shape drift
that will matter for the downstream desugar and interpreter layers.

When adding a syntax slice:

1. Add the smallest representative snippet to
   `RUST_FAST_AST_SNIPPETS`.
2. Run `pytest prototype/tests/unit/parser/test_rust_fast_ast_frontend.py`.
3. If the text AST differs, inspect Lark's current output with:

   ```bash
   python3 -c 'from prototype.parser.nomi.frontend import get_parser_frontend; f=get_parser_frontend(); print(f.python_ast_text(code="x = 1\n"))'
   ```

4. Adjust either Rust JSON shape or Python adapter mapping until the AST text is
   exactly the same.
5. Only then add broader samples.

## Next Implementation Order

Work from expressions outward. Expression parity unlocks most statements.

1. **Payload snapshots** (partially complete)
   - Add a small helper/test that snapshots or asserts the Rust JSON payload
     before Python AST adaptation.
   - This makes failures easier to locate: lexer/parser vs Python adapter.

2. **Lexer completeness for expressions** (partially complete)
   - Add tokens for `.`, `[`, `]`, `{`, `}`, `:`, `%`, `//`, `@`, bitwise ops,
     comparisons, `and`, `or`, `not`, `is`, `in`, `None`, `True`, `False`.
   - Add `$`, range, pipeline, and null-safe tokens.
   - Add string-prefix handling only after basic expression coverage is stable.
   - Preserve byte offsets in every token; later spans depend on them.

3. **Expression parity**
   - Constants: `None`, `True`, `False`, integers, floats, strings.
   - Unary: `+x`, `-x`, `~x`, `not x`.
   - Binary: `%`, `//`, `@`, bitwise ops, shifts.
   - Comparisons: chains like `a < b <= c`, `is not`, `not in`.
   - Boolean: `a and b`, `a or b`.
   - Conditional expression: `x if cond else y`.
   - Attributes and subscripts: `obj.name`, `items[0]`, slices.
   - Literals: tuples, lists, dicts, sets.
   - Calls: keyword args, starred args, `**kwargs`.

4. **Nomi expression forms**
   - Nullish: `a ?? b`.
   - Pipeline: `x |> f`.
   - Composition: `f >>> g`, `f <<< g`.
   - Ranges: `1..5`, `1..<5`, `1..10 by 2`.
   - Safe navigation: `data?.get("name")?.[0]`.
   - Operator sections: `(+1)`, `(2*)`, `(+)`.
   - Underscore and dollar-hole lambdas.
   - Inline `match`.
   - `try` expression.
   - `where` expression.
   - Current demo acceptance may keep these as `Raw` payloads. Exact parity and
     lowering remain future work.

5. **Simple statements**
   - Multiple assignment targets before annotated/augmented assignment.
   - `return`, `pass`, `break`, `continue`, `yield`.
   - `func name(...): suite`.
   - `if`/`elif`/`else`, `while`, `for`.
   - Imports only after basic control flow is stable.

6. **Indentation and suites**
   - Implement indentation tokens in Rust rather than relying on Python/Lark.
   - Match the current `NomiPostLexer` behavior closely.
   - Add tests for single-line suites and indented suites separately.

7. **Nomi statement forms**
   - `unless`.
   - `if-let`, `guard-let`, `while-let`.
   - `match` statement.
   - `data` declarations.
   - `type` aliases.
   - constrained bindings.
   - block calls: `callee(...): body` and `callee(...) -> params: body`.
   - `defer`.

8. **Surface/Core boundary**
   - Stop adding Python AST mappings directly when a Nomi form has no natural
     Python AST shape.
   - Prefer emitting a Surface payload that Python can lower through the same
     path as Lark.
   - This matters for `DataDecl`, `MatchExpr`, block calls, constraints, and
     other Nomi-native constructs.

## Observed Improvement Notes

These are explicit pickup notes from the current implementation review. Keep
them fresh as work lands.

### Correctness and Parity

- Replace `Raw` payloads feature by feature with structured nodes, starting
  with inline `match`, `where`, ranges, pipeline, nullish/safe navigation,
  operator sections, underscore lambdas, dollar holes, and constrained binding
  targets.
- Add exact Python AST parity tests beyond the first slice before setting
  `lower_to_python_ast=True`. Parse acceptance is already useful, but it is not
  semantic equivalence.
- Add payload-shape tests for Nomi-native forms before lowering them. This keeps
  failures attributable to lexer/parser vs Python adapter.
- Add source-span fields to tokens and payload nodes before improving
  diagnostics; byte offsets already exist, but the payload does not expose
  ranges yet.
- Decide whether keywords should remain `Name` tokens with parser checks or
  become distinct token variants. Distinct variants may simplify future grammar
  parity, but soft-keyword behavior needs care.

### Parser Structure

- Continue shrinking `parser.rs` by moving statement families into focused
  helpers/modules once behavior stabilizes: suites/control flow, assignments,
  function forms, and Nomi-native forms.
- Keep `main.rs` as CLI glue and keep parser behavior out of it.
- Preserve the `ast-json <path>` CLI contract for future parser candidates.
  New Rust parsers should plug in behind `JsonPayloadParserFrontend` instead of
  modifying `rust-fast-ast` assumptions into the frontend boundary.
- Avoid expanding tolerant parsing indefinitely. Each `Raw` fallback should have
  a named follow-up path to structured parse and eventual lowering.

### Payload and Adapter

- Keep using `src/payload.rs` helpers rather than manual JSON string assembly.
  If payload complexity grows, consider `serde_json`, but weigh that against the
  spike's intentionally tiny dependency surface.
- Move Python adapter support in `frontend.py` toward parser-neutral payload
  adapters. The current `_python_ast_from_rust_payload` name is still
  rust-fast-ast specific.
- Add a version or schema marker to JSON payloads before supporting multiple
  Rust parser candidates with different node sets.

### Testing and Tooling

- Add a deterministic Rust fixture sweep helper so the active Lark-accepted
  `.nomi` set is checked without ad hoc shell loops.
- Add timeout protection around Rust parser acceptance sweeps to catch parser
  loops quickly.
- Add tests that compare Rust parse acceptance against all files accepted by
  Lark, while explicitly excluding aspirational/scratch files Lark rejects.
- `cargo fmt` currently cannot run in this environment because `rustfmt` is not
  installed. Re-run formatting once the toolchain has the component.

### Performance

- Replace Python's `cargo run` invocation with cached binary resolution before
  measuring speed. Current timings mostly measure Cargo orchestration.
- Add a build helper or clear fallback error that tells developers how to build
  the Rust parser binary.
- Only add Rust to parser performance comparisons after the compared fixture set
  is identical across frontends.

## Performance Note

The Python frontend currently invokes Rust through `cargo run`, which measures
Cargo startup/build orchestration more than parser speed. Keep that during
early development because it is simple and robust.

Before doing speed comparisons:

- Add a `cargo build` helper or cached binary resolution.
- Have `RustFastAstParserFrontend` run the compiled binary directly.
- Keep a fallback error telling the developer how to build the binary.
- Then add `rust-fast-ast` to the parse/perf matrix only after it can parse the
  same fixtures being compared.

## Useful Commands

```bash
cargo test --manifest-path tools/parser_spikes/rust_fast_ast/Cargo.toml
pytest prototype/tests/unit/parser/test_rust_fast_ast_frontend.py
pytest prototype/tests/unit/parser/test_parser_frontend.py
pytest prototype/tests/unit/parser
python3 -m tools.syntax.inspect --stage parser-frontends
python3 -m tools.parser_spikes.parse_matrix --iterations 1
```

To inspect Lark's current AST text for a snippet:

```bash
python3 -c 'from prototype.parser.nomi.frontend import get_parser_frontend; f=get_parser_frontend(); print(f.python_ast_text(code="x = 1\n"))'
```

To inspect the Rust payload for a snippet:

```bash
printf 'x = 1\n' > /private/tmp/nomi-rust-slice.nomi
cargo run --quiet --manifest-path tools/parser_spikes/rust_fast_ast/Cargo.toml -- ast-json /private/tmp/nomi-rust-slice.nomi
```

## Do Not Do

- Do not call Lark from the Rust frontend to fake replacement parity.
- Do not mark `rust-fast-ast` as full grammar, Python-AST capable, or selectable
  until the shared contract tests prove it.
- Do not commit `target/`, debug binaries, timing output, local scratch files,
  or generated caches.
- Do not make runtime-output equality the primary success criterion.
- Do not let the Rust grammar become a different language from Lark while Lark
  remains the compatibility oracle.
