# Performance Notes

Tracking file for parsing pipeline optimization attempts, findings, and
current status.  The pipeline is ~99% parse time; interpreter/eval time
is negligible for typical source files.

## Profiling Tooling

- **Profiler**: `tools/perf/profiler.py` — self-contained HTML report generator.
  Run with `python3 -O tools/perf/profiler.py --file samples/demo.nomi`.
- **Convenience script**: `scripts/profile.py` — defaults to `samples/demo.nomi`,
  opens browser.  Uses subprocess to avoid stdlib `profile` module name conflict.
- **Output**: `reports/profile/profile_{stem}.html` (gitignored).
- **cProfile caveat**: cProfile adds ~4x overhead for Earley parsing
  (function-call-heavy).  The profiler separates accurate `time.perf_counter()`
  wall-clock timing from cProfile stats.

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

## Current State

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Earley items | 1,670,000 | 1,464,202 | -12.6% |
| Parse time (demo.nomi) | ~1129ms | ~974ms | -13.7% |
| Test suite | 626 pass | 626 pass | — |

## Remaining Earley Item Breakdown (demo.nomi)

| Items | % | Rule | Notes |
|-------:|--:|------|-------|
| 231,760 | 15.8% | atom | 12 alternatives remaining |
| 174,509 | 11.9% | atom_expr | 7 alternatives (6 recursive + atom) |
| 155,706 | 10.6% | name | 7 keyword alternatives — needs lexer work |
| 119,198 | 8.1% | number | — |
| 56,843 | 3.9% | range_expr | — |
| 42,140 | 2.9% | string | — |
| 41,588 | 2.8% | _unary_op | — |
| 40,774 | 2.8% | test | — |

## Active Investigation: LALR Migration

Switching from Earley to LALR would be ~50x faster but currently blocked on
**103 reduce/reduce conflicts**.  Main conflict categories:

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

### Potential LALR resolution paths (not yet attempted)

1. **Lexer-level distinction**: Use context-aware lexing (ContextualLexer or
   postlexer) to emit different tokens for unary vs binary `+`/`-`.

2. **Grammar restructuring**: Separate expression and pattern grammars more
   aggressively so shared terminals resolve unambiguously.

3. **Lark ambiguity resolution**: Use `priority` or custom ambiguity handlers
   if available in the Lark version.

4. **Separate `+`/`-` from `*`/`/` etc. in `_binary_op`**: Keep `+`/`-` only
   in `_unary_op`, define `_binary_op` without them, and handle binary `+`/`-`
   through a higher-level rule that references the same terminals without
   creating a separate reduce target.

## Pipeline Stage Timings (demo.nomi, post-optimization)

| Stage | Wall time | % |
|-------|----------:|--:|
| Grammar assembly | 0.2ms | 0.0% |
| Raw parse (lex + Earley) | 1013.9ms | 49.9% |
| Layer transforms | 1.0ms | 0.0% |
| NomiToPythonAST | 6.9ms | 0.3% |
| Surface lowering | 0.4ms | 0.0% |
| Desugar (10 passes) | 5.4ms | 0.3% |
| Full pipeline | 998.8ms | 49.2% |
| Python compile + exec | 4.1ms | 0.2% |

Parse is 99.3% of total pipeline time.  Post-parse stages are negligible.
