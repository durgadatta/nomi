# Performance Notes

Tracking file for parsing pipeline optimization attempts, findings, and
current status.  The pipeline is ~99% parse time; interpreter/eval time
is negligible for typical source files.

## Profiling Tooling

- **Profiler**: `tools/perf/profiler.py` — self-contained HTML report generator.
  Run with `python3 -O tools/perf/profiler.py --file samples/demo.nomi`.
  It does not open a browser unless passed `--open`.
- **Convenience script**: `scripts/profile.py` — defaults to `samples/demo.nomi`,
  opens browser.  Uses subprocess to avoid stdlib `profile` module name conflict.
- **Output**: `reports/profile/profile_{stem}.html` (gitignored).
- **Repeatable timing**: use `--iterations N` for min/median/average/max timing
  samples.  Use `--cprofile` only when you need function-level attribution;
  it adds substantial overhead.
- **Source spans**: default parser runs with Lark position propagation off for
  speed.  Set `NOMI_PARSER_SPANS=1` or pass `preserve_positions=True` to
  `get_parser()` / `generate_ast()` when testing diagnostics, inspection, or
  source-span plumbing.
- **cProfile caveat**: cProfile adds ~4x overhead for Earley parsing
  (function-call-heavy).  The profiler separates accurate `time.perf_counter()`
  wall-clock timing from cProfile stats.
- **LALR caveat**: the profiler still contains an Earley item-count panel.
  After the LALR migration this count is expected to be zero; use wall-clock
  parse and pipeline timings instead.

## Baseline (before optimization)

- **demo.nomi** (190 lines): ~1,670,000 Earley items, parse ~1129ms
- Top Earley item producers: `atom` ~443K (26.5%), `name` ~155K (9.3%)

## Completed Optimizations

### 1. Atom wrapper rules (COMMITTED `9c25430`)

**What**: Merged 5 `(` alternatives, 2 `[` alternatives, 4 `{` alternatives
from `atom` into `paren_expr`, `brack_expr`, `brace_expr` wrapper rules.

**Why it works**: Non-inline wrapper rules are predicted by Earley only when
their delimiter is scanned.  `atom` shrank from 20 to 12 alternatives.

**Impact**: -212K Earley items (-12.6%), parse time -13.7% (~1129ms → ~974ms).

### 2. Parse result cache (COMMITTED `3f9314a`)

**What**: Cache raw parse trees by source-content hash.  Second parse of
unchanged source is instant.

### 3. Desugar invariant checks gated on `__debug__` (COMMITTED `010a2d2`)

**What**: Skip `_check_pass_invariants()` when running with `python -O`.
Saves ~4.5ms per desugar pass.

### 4. LALR parser migration

**What**: Switched the Nomi parser in `prototype/parser/nomi/usage.py` from
Earley to LALR with the basic lexer and `NomiPostLexer`.

**Why it works**: The grammar now gives LALR distinct tokens at the places
where Earley previously relied on ambiguity resolution:

- explicit operator terminals replace `_unary_op` / `_binary_op` reductions;
- `SECTION_OP` is emitted only for operators inside standalone section
  parentheses, so `(+2)`, `(2*)`, and `(+)` do not collide with unary,
  binary, call-argument, or spread syntax;
- `_ARROW_LPAR` / `_ARROW_RPAR` are emitted only when a parenthesized parameter
  list is followed by `=>`, so arrow functions no longer steal ordinary
  parenthesized expressions or grouped constraints;
- `_CASE_COLON` separates match case separators from pattern-internal colons;
- `_CASE_IF` separates match guards from conditional expressions inside
  constrained captures;
- `_BLOCK_COLON` separates suite-introducing colons from expression colons;
- `_POSTFIX_IF` / `_POSTFIX_UNLESS` separate postfix flow guards from ternary
  `if ... else ...` expressions;
- function equations and block calls now use call-specific heads, preventing
  ordinary calls and annotations from being parsed as those statement forms.

**Impact**: On `samples/demo.nomi` under `python3 -O`, raw parse averages
~9.9ms and uncached `generate_ast()` averages ~12.2ms.  Compared with the
post-wrapper Earley parse baseline (~974ms), this is roughly a 100x raw parse
speedup.

### 5. Fast parser profile: source spans opt-in

**What**: Parser construction and raw-tree caching now key on
`preserve_positions`.  The default execution profile disables Lark
`propagate_positions`; diagnostics and tooling can opt in with
`NOMI_PARSER_SPANS=1` or an explicit `preserve_positions=True` call.

**Why it works**: Source position propagation attaches `meta` data throughout
the Lark tree.  That is essential for source-spanned diagnostics, but routine
execution does not currently consume those spans.

**Impact**: On `samples/demo.nomi`, direct raw-parse timing dropped from roughly
~10ms with spans to ~7.5-8.7ms without spans depending on run noise.  This is
not as dramatic as the LALR migration, but it is a cheap default-path win and
keeps the diagnostic path available.

### 6. Persistent LALR analysis cache

**What**: `get_parser()` passes `cache=True` to Lark.  `_PARSER_CACHE` already
keeps parsers hot inside one Python process; Lark's own cache persists the
expensive LALR grammar analysis for short-lived CLI processes.

**Why it works**: A full `python3 -O -m cProfile scripts/cli.py samples/demo.nomi`
run showed the next bottleneck had moved from parsing source to constructing
the LALR parser.  Fresh-process execution spent ~1.27s in `get_parser()` /
`Lark.__init__()`, almost entirely in LALR analysis, while interpreter
evaluation itself was only a few milliseconds.

**Impact**: First run after a grammar/options change still pays the analysis
cost and writes the cache.  Subsequent fresh-process CLI runs dropped from
~1.41s under cProfile to ~0.12s; direct suppressed-output CLI timing was
~83-92ms.  `get_parser()` fell from ~1.27s to ~29ms under cProfile, with
`Lark._load()` replacing `compute_lalr()` as the parser-construction cost.

### 7. Selected desugar passes for default Nomi execution

**What**: Default Nomi mode now runs only the desugar passes needed for
Nomi-only convenience syntax: piecewise equations, where clauses, underscore
holes, and positional/named dollar holes.  Reduced mode still runs the full
pipeline because its job is to enforce normal forms.

**Why it works**: The Nomi interpreter inherits Python-compatible evaluation
for `AugAssign`, `Assert`, `Pass`, `With`, decorators, and f-strings.  Running
those normal-form passes in default mode was pure tree-walk churn for
`demo.nomi`.

**Impact**: On `samples/demo.nomi` under `python3 -O`, full desugar median was
~5.97ms and selected default-Nomi desugar median was ~4.33ms in direct timing.
This is a modest but clean default-path win while preserving reduced-mode
checks.

### 8. RuntimeSession filename caching and direct AST reuse

**What**: `RuntimeSession` now reads filename sources into its source-keyed AST
cache, so repeated file runs in one long-lived session hit the cache.  Cache
hits reuse the fixed lowered AST directly instead of deep-copying it.

**Why it works**: In the current interpreter, evaluation does not mutate AST
nodes.  Deep-copying the cached Python AST was the dominant cost on repeated
session runs after parser/lowering were removed from the path.

**Impact**: Repeated `samples/demo.nomi` runs in one `RuntimeSession` dropped
from ~4-5ms to roughly ~0.9-1.3ms after the first run.  This is the best path
for web, notebook, REPL, and editor integrations where a process can stay hot.

## Attempted But Reverted

### Removing `?` prefix from `atom` and `atom_expr`

**Hypothesis**: Making inline rules non-inline would reduce Earley items by
preventing alternative expansion into parent rules.

**Result**: Zero change in Earley item counts.  The `?` prefix in Lark only
affects tree shaping, not Earley prediction.  The mechanism for item reduction
is moving alternatives to narrower context rules (the wrapper pattern), not
changing the `?` prefix.

### Inlining `_unary_op` into `factor`

**Hypothesis**: Removing the `_unary_op` rule would eliminate reduce/reduce
conflicts with `_binary_op` in LALR mode (both reduce `+`/`-` terminals).

**What was tried**: Changed `?factor: _unary_op factor | power` to
`?factor: "+" factor | "-" factor | "~" factor | power`.

**Result**: The `-` terminal is dropped from the parse tree because anonymous
terminals without the `!` rule modifier are filtered out during tree
construction.  Unary minus silently lost — `-5` parsed as `5`.

**Root cause**: `!_unary_op` uses the `!` prefix to preserve all tokens
in the tree.  Anonymous terminals (`"-"`) in inline rules don't get this
treatment.  The `!` prefix cannot be applied to individual terminals within
an inline rule.

### Soft-keyword removal from `name` rule

**Hypothesis**: Removing `"match"|"case"|"type"|"by"|"guard"|"data"` from
`!name` would reduce its 155K Earley items.

**Result**: 17 test failures.  Soft keywords (`data`, `case`, etc.) used as
variable names produced lexer errors because the lexer produces dedicated
keyword tokens that can't match `NAME`.

**Root cause**: Requires ContextualLexer or lexer priority changes to make
keywords conditionally match as `NAME`.  Deferred.

### Lark standalone parser for current transformer stack

**Hypothesis**: A generated Lark standalone parser could avoid the remaining
parser cache load and installed-Lark import cost in short-lived CLI runs.

**Result**: Deferred.  A generated standalone parser can parse `demo.nomi`, but
it returns the standalone module's own `Tree` class.  The current lowering stack
uses installed-Lark `Transformer` classes, so those transformers do not consume
standalone trees without an adapter.  A simple adapter works but largely turns
the change into a larger generated-parser/generated-transformer architecture
slice rather than a low-risk bottleneck fix.

## Current State

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Earley items | 1,670,000 | 0 | LALR does not create Earley items |
| Raw parse time (demo.nomi) | ~1129ms | ~7.5-9.9ms | ~99.1%+ faster |
| Full `generate_ast()` (demo.nomi, uncached) | ~998.8ms | ~12.2ms | ~98.8% faster |
| Fresh CLI run, cProfile | ~1.41s | ~0.12s | persistent LALR cache |
| Test suite | 626 pass | 626 pass | — |

## LALR Migration Notes

The migration initially failed on **103 reduce/reduce conflicts**.  Main
conflict categories:

1. **`_unary_op` vs `_binary_op`** (most frequent): Both rules match `+`/`-`/`~`
   terminals.  LALR can't distinguish unary from binary context.

2. **`string` vs `inner_literal_pattern`**: Same `STRING` terminal reduced to
   different rules in expression vs pattern context.

3. **`match_block_simple_stmt` vs `test`**: `match_block_expr` appears in both
   contexts.

### Merge `_unary_op` and `_binary_op` into `_op` (ATTEMPTED, REVERTED)

**What was tried**: Created a single `!_op` rule with all operators, used in
`factor`, `bin_expr`, and `section`.  This eliminates the fundamental RR
conflict since each `+`/`-` token has only one reduce target.

**Result**: Earley ambiguity — `*expr` in list spreads matches BOTH
`factor: _op factor` and `star_expr: "*" expr"`.  The ambiguity resolver
picks `factor`, which the transformer rejects (invalid unary op).  Star
spread breaks.

**Root cause**: `*` is valid as a binary operator but invalid as unary.
Merging the rules gives the parser no way to distinguish the contexts.

### Resolution paths that worked

1. **Postlexer-level distinction**: `NomiPostLexer` now emits virtual tokens
   for section operators, arrow-function parentheses, case colons, case guard
   `if`, postfix flow guards, and block colons.

2. **Grammar restructuring**: `func_equation` and `block_call_stmt` now use
   call-specific heads.  This avoids committing to those statement forms when
   parsing ordinary calls or annotations.

3. **Rule priorities**: Pattern, constraint, typed-parameter, and match-block
   rules use targeted priorities where LALR still had reduce/reduce overlap.

### Additional failed paths during migration

- **Direct operator terminals without section tokens**: built under LALR, but
  parsed `(+2)` as unary plus and failed on `(2*)`.
- **Contextual lexer with postlex implicit multiplication**: failed on `2x`
  because the contextual lexer rejected `NAME` before the postlexer could
  insert `STAR`.  The migration uses `lexer="basic"` so the postlexer sees the
  raw adjacent tokens.
- **Call-specific function equations without call-specific block calls**:
  fixed ordinary call parsing, but broad `block_call_stmt: atom_expr ":" suite`
  stole annotated assignments like `x: int = 1`.

## Pipeline Stage Timings (demo.nomi, post-optimization)

| Stage | Wall time | % |
|-------|----------:|--:|
| Grammar assembly | 0.2ms | 0.0% |
| Raw parse (lex + LALR) | ~9.9ms | dominant but small |
| Layer transforms | 1.0ms | 0.0% |
| NomiToPythonAST | 6.9ms | 0.3% |
| Surface lowering | 0.4ms | 0.0% |
| Desugar (10 passes) | 5.4ms | 0.3% |
| Full `generate_ast()` | ~12.2ms | — |
| Python compile + exec | 4.1ms | 0.2% |

Parse remains the largest stage, but it is no longer a second-scale bottleneck.
The profiler's cProfile totals can still be noisy; prefer direct
`time.perf_counter()` measurements for parser work.

## Next Max-Gain Directions

1. **Separate execution, diagnostics, and tooling parser profiles**.  Keep the
   execution parser span-free and benchmark whether inspection commands should
   use a span-preserving parser only at the last responsible moment.
2. **Inline parse-time transformation**.  Evaluate Lark's transformer-at-parse
   path or a smaller custom tree builder to reduce intermediate tree churn.
   Now that parsing is fast, allocation and lowering overhead will matter more.
3. **Lark standalone parser**.  Generate and benchmark a standalone LALR parser
   for CLI/web startup.  This may help Pyodide and short-lived CLI processes by
   reducing grammar analysis and parser construction work.
4. **Long-lived parser service for editor/web sessions**.  Treat parser reuse as
   a process architecture concern: keep the parser hot, cache per-buffer raw
   trees, and invalidate by content/version rather than rebuilding pipeline
   state per request.
5. **Nomi-owned surface/core AST**.  Python AST is convenient but not cheap or
   semantically native.  If lowering becomes dominant, a compact Nomi surface
   tree with explicit source-span side tables may be a larger win than shaving
   grammar rules.
6. **Tree-sitter or Rust parser later**.  Worth considering only after grammar
   semantics stabilize.  The current LALR result removes the urgent need, but a
   native parser could eventually give IDE-grade incremental parsing.
