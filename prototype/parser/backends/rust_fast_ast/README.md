# Rust Fast AST Parser Spike

This spike is the first non-Lark path that produces a Python-AST-compatible
artifact without routing through Lark. It is intentionally small today. Treat it
as real replacement machinery, not as the replacement itself.

## Current Status

The root `rust-toolchain.toml` pins the project Rust toolchain to stable and
declares `rustfmt` as a required component for this spike.

`rust-fast-ast` currently supports exact `ast.dump(..., include_attributes=False,
indent=2)` parity with `lark-lalr` for:

- simple assignments: `x = 1`
- expression statements: `print("x")`
- positional calls: `f(a, 1)`
- arithmetic binary expressions: `+`, `-`, `*`, `/`, `//`, `%`, `@`, `**`
- parenthesized arithmetic precedence: `(1 + 2) * 3`
- unary plus, unary minus, and `not`
- constants: `None`, `True`, `False`, numbers, strings, and f-strings
- comparisons, including chained comparisons such as `0 <= score <= 100`
- boolean `and`/`or`
- conditional expressions: `"Pass" if score >= 60 else "Fail"`
- list, tuple, and dict literals
- attributes and subscripts
- simple annotated assignment constraints:
  `age:int, is_positive = 25`
- constraint messages: `age >= 13 else "Too young"`
- function equations: `add(a, b) = a + b`
- arrow-function assignments: `double = x => x * 2`,
  `add = (a, b) => a + b`
- simple `func` suites, `return`, `yield`, `raise`, `pass`, augmented
  assignment, `for`, `if`, `while`, `guard`, `try`/`except`/`finally`,
  `match`, `data`, `where`, and Nomi block-call suites
- simple Nomi expressions: inline `match`, `(+2)` operator sections, ranges,
  pipelines, nullish `??`, and safe navigation

It also has a broader parse-acceptance slice for both demo files:
`scripts/demo.nomi` and `samples/demo.nomi`. That slice emits a structural JSON
payload for indentation, `func` suites, `for`/`if`/`while` suites,
`try`/`except`, returns, yields, raises, augmented assignments, Nomi block
calls, constrained-binding targets, prefixed/triple strings, lists, attributes,
comparisons, boolean operators, conditional expressions, `where` suites,
guided-tour forms such as `unless`, `match`/`case`, `guard`, `data`
declarations, `$` holes, ranges, pipelines, null-safe tokens, and other
currently-raw expression forms.

As of the current checkpoint, `scripts/demo.nomi`, `samples/block.nomi`,
`samples/constraint.nomi`, and every shared feature snippet in
`test_parser_frontend_acceptance.py` lower through `rust-fast-ast` to the exact
same Python AST dump as `lark-lalr`. The Rust-generated core demo AST also
executes successfully in the Nomi interpreter. This is still not a replacement
claim: the broader sample matrix has remaining guided-tour forms whose Rust
payload is parse-accepted but not fully lowered.

The parse-acceptance slice is not exact Python AST parity. It is a
parser-frontier milestone only: `rust-fast-ast` is now enrolled in parser
frontend acceptance tests, but must not be made selectable for execution yet.
It also accepts the older Lark-accepted debug/interpreter fixtures covered by
`prototype/tests/unit/parser/test_rust_fast_ast_frontend.py`.

The runtime can also use this frontend to produce the Python AST artifact before
handing it to the existing interpreter stack:

```bash
python3 scripts/cli.py --parser-frontend rust-fast-ast samples/demo.nomi
```

That proves the parser can feed downstream evaluation on the execution path.
The frontend now also matches the Lark Python AST text for the shared
sample/snippet matrix, but it is not a normal default/replacement until
`selectable_for_session_execution` is promoted. It is separately declared as
the browser playground experiment/default parser because that path lowers Rust
AST JSON through the JS Core lowerer instead of the Python session pipeline.

## Promotion Gate

Do not change these capability flags until the stated gate is genuinely met:

```python
ParserFrontendCapabilities(
    parse_current_grammar=True,
    lower_to_python_ast=True,
    emit_core_json=True,
    selectable_for_session_execution=False,
    selectable_for_browser_experiment=True,
    default_for_browser_playground=True,
)
```

Promotion sequence:

1. `parse_current_grammar=True` is allowed once `parse_accepts()` handles every
   sample file and focused parser snippet accepted by Lark. This gate is now
   met for the parser frontend acceptance matrix.
2. Set `lower_to_python_ast=True` only when exact AST text parity passes for the
   shared sample/snippet matrix in
   `prototype/tests/unit/parser/test_parser_frontend_acceptance.py`. This gate
   is now met; `rust-fast-ast` participates in `get_python_ast_frontends()`.
3. Set `selectable_for_session_execution=True` only after parser unit tests,
   relevant functional tests, regression samples, CLI execution, and downstream
   runtime behavior all match the Lark path when the Rust frontend is selected.

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
  CLI, and delegates JSON adaptation.
- `prototype/parser/nomi/rust_payload.py`: adapts the Rust JSON payload to
  Python AST. Keep parser-specific lowering out of `frontend.py` so future
  PEG/CST parser adapters can live beside it.
- `prototype/runtime/api.py`, `prototype/runtime/session.py`, and
  `scripts/cli.py`: expose parser-gated execution through the generic
  `parser_frontend` selector.
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
  --manifest-path prototype/parser/backends/rust_fast_ast/Cargo.toml \
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
   - Tokens exist for `.`, `[`, `]`, `{`, `}`, `:`, `%`, `//`, `@`,
     comparisons, `and`, `or`, `not`, constants, `$`, range, pipeline,
     null-safe forms, and prefixed strings.
   - Remaining: bitwise ops, shifts, `is`, `in`, starred forms, and keyword
     argument punctuation/shape.
   - Preserve byte offsets in every token; later spans depend on them.

3. **Expression parity** (partially complete)
   - Done: constants, strings/f-strings, unary `+`/`-`/`not`, arithmetic
     `+ - * / // % @ **`, chained comparisons, boolean `and`/`or`,
     conditional expressions, attributes, simple subscripts, lists, tuples,
     and dicts.
   - Remaining: `~x`, bitwise ops, shifts, `is not`, `not in`, slices,
     populated dicts/sets, keyword args, starred args, and `**kwargs`.

4. **Nomi expression forms**
   - Nullish: `a ?? b` (simple parity slice done).
   - Pipeline: `x |> f` (simple parity slice done).
   - Composition: `f >>> g`, `f <<< g`.
   - Ranges: `1..5`, `1..<5`, `1..10 by 2` (simple parity slice done).
   - Safe navigation: `data?.get("name")?.[0]` (simple parity slice done).
   - Operator sections: `(+1)` (simple parity slice done), `(2*)`, `(+)`.
   - Underscore and dollar-hole lambdas.
   - Inline `match` (simple parity slice done).
   - `try` expression.
   - `where` expression.
   - Remaining raw-expression work is mostly richer composition, spread,
     keyword/starred calls, slices, and less-common operators.

5. **Simple statements** (partially complete)
   - Done: simple and annotated assignment, augmented assignment,
     `return`, `pass`, `yield`, `raise`, simple `func`, simple `for`,
     simple `if`, `try`/`except`/`finally`, `while`/`guard` pattern forms,
     `match`, `data`, `where`, and block calls with/without params.
   - Remaining: multiple assignment targets, `break`, `continue` parity tests,
     `elif`/`else`, `while`, `finally`, decorators, defaults beyond the
     Python-compatible `func` head path, and imports.
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

- Replace remaining `Raw` payloads feature by feature with structured nodes.
  The Python adapter currently lowers the shared parity matrix, including
  inline `match`, `where`, ranges, pipeline, nullish/safe navigation, operator
  sections, underscore lambdas, dollar holes, `defer`, `unless`, try
  expressions, and function equations.
- Keep expanding exact Python AST parity beyond the shared matrix before
  promoting normal execution. AST parity is necessary but not sufficient for
  runtime equivalence.
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
- Keep Python adapter support parser-specific but modular: `frontend.py` should
  route to focused payload/CST adapter modules rather than growing a large
  lowering tail.
- Add a version or schema marker to JSON payloads before supporting multiple
  Rust parser candidates with different node sets.
- Keep parser-gated execution generic: runtime and CLI should call
  `get_parser_frontend(name).parse_accepts(...)` by name, not branch on
  `rust-fast-ast`. Future parsers should join by registration plus tests.
- Once a non-Lark frontend earns `lower_to_python_ast=True`, add a backend
  routing hook that can execute from that frontend's lowered artifact rather
  than using parser-gated Lark execution.

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
cargo test --manifest-path prototype/parser/backends/rust_fast_ast/Cargo.toml
pytest prototype/tests/unit/parser/test_rust_fast_ast_frontend.py
pytest prototype/tests/unit/parser/test_parser_frontend.py
pytest prototype/tests/unit/parser
python3 -m tools.syntax.inspect --stage parser-frontends
python3 -m prototype.parser.parse_matrix --iterations 1
python3 scripts/cli.py --parser-frontend rust-fast-ast samples/demo.nomi
```

To inspect Lark's current AST text for a snippet:

```bash
python3 -c 'from prototype.parser.nomi.frontend import get_parser_frontend; f=get_parser_frontend(); print(f.python_ast_text(code="x = 1\n"))'
```

To inspect the Rust payload for a snippet:

```bash
printf 'x = 1\n' > /private/tmp/nomi-rust-slice.nomi
cargo run --quiet --manifest-path prototype/parser/backends/rust_fast_ast/Cargo.toml -- ast-json /private/tmp/nomi-rust-slice.nomi
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
