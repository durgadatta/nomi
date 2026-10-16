# Performance And Profiling

> Status: current profiling tools and measurement boundaries.

Measure the current workload and profile before selecting an optimization.
No parser speedup, startup budget or production capacity is implied by an older
measurement. Report source, host/tool versions, spans mode, cache state, warmup,
iterations, memory units and correctness/refusal behavior with each result.

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

### Parser Frontend Benchmark

- **Benchmark**: `tools/perf/bench_parsers.py` — compares all registered parser
  frontends on parse time, full-pipeline time, and memory.  Generates a
  self-contained HTML report with bar charts and detail tables.
- **Convenience script**: `scripts/profile_parsers.py` — defaults to
  `samples/demo.nomi`, opens browser.
- **Output**: `reports/bench/bench_{stem}.html` and `bench_{stem}.json`
  (gitignored).
- **Frontend list**: the benchmark iterates `BENCH_FRONTENDS` in
  `tools/perf/bench_parsers.py`.  **When you register a new parser frontend**
  (new entry in `_FRONTENDS` in `prototype/parser/nomi/frontend.py`), also add
  its name to `BENCH_FRONTENDS` so it appears in the benchmark.  If the new
  frontend is a Rust subprocess, add its crate metadata to `_RUST_CRATES` for
  optional RSS measurement (`--rss` flag).
- **Metrics**: parse acceptance wall-clock time (with Lark cache clearing for
  honest measurement), full pipeline parse+eval time (via `RuntimeSession`, only
  for frontends with `lower_to_python_ast=True`), Python heap memory via
  `tracemalloc`, and optional subprocess peak RSS via `/usr/bin/time -l`.


## Current Mechanisms And Gaps

The Python frontend uses LALR parsing, postlexer token distinctions and parser/
parse-result caches. Source positions are an explicit profile choice. Alternate
frontends publish parse/lowering/session capabilities separately; inspect their
actual fixtures before comparing performance. Core and host execution remain
replaceable layers.

An opt-in regression budget should cover construction/cache load, raw parse with
spans off/on, postlexing, lowering, reductions, runtime execution and session
cache hits. Establish a fresh baseline before choosing limits. Reassociation,
fusion, native code and caching must preserve values, failure order, authority,
completion and source diagnostics. Generated reports remain under ignored
`reports/`; project evolution is in HISTORY.md.
