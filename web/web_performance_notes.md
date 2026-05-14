# Nomi Web Playground — Performance Notes

## Current execution pipeline (per cell)

```
User types code → run_nomi(code)
  → _eval_in_session(code)
    → generate_ast(code)          # Lark parse + AST lift
    → _nomi_desugar(tree)          # 4 desugar passes + fix_missing_locations
    → interp.eval(tree)            # AST-walk evaluation
```

## Implemented improvements (2026-05-13)

### 1. Cache Lark parser instance
**File:** `prototype/parser/nomi/usage.py`
**Before:** `get_parser()` created a new `Lark(parser="earley")` on every
`generate_ast()` call — every single cell execution.  Earley parser
construction is O(n³) in grammar size; ~100+ ms in CPython, much worse
in Pyodide/WebAssembly.
**After:** `_PARSER_CACHE` stores the parser at module level.  Created
once on first parse, reused for all subsequent calls.
**Expected win:** 50-80% reduction in per-cell execution time for
typical small expressions.

### 2. Cache assembled grammar string
**File:** `prototype/grammar/assemble.py`
**Before:** `assemble_grammar()` re-read six `.lark` files from Pyodide's
virtual filesystem on every call.
**After:** `_GRAMMAR_CACHE` stores the concatenated grammar string.
**Expected win:** Smaller but multiplicative with parser caching —
saves disk I/O (which in Pyodide is in-memory but still has overhead).

### 3. Remove redundant `ast.fix_missing_locations`
**File:** `web/nomi_web.py`
**Before:** `_eval_in_session()` called `ast.fix_missing_locations(tree)`
after `_nomi_desugar(tree)`, which already calls it internally.  Double
traversal of the AST.
**After:** Removed the redundant call.
**Expected win:** Small (~5-10%) — `fix_missing_locations` is a single
AST walk but it visits every node.

### 4. Pre-warm parser and modules during init
**File:** `web/nomi_web.py`
**Before:** Parser construction and key module imports happened lazily
on the first user cell execution, making the first run feel slow.
**After:** `init_nomi()` parses a trivial expression (`x = 1`) to force
parser construction, module imports, and bytecode compilation before the
user types anything.  The loading spinner hides this latency.
**Expected win:** First-cell execution now matches subsequent-cell speed.

## Manifest regeneration

`web/manifest.json` is already dynamically regenerated on every
`launch_web` or `make_web` invocation:

- `launch_web.py` calls `regenerate_manifest()` (unless `--no-manifest`)
- `make_web.py` always regenerates `manifest.json`
- `make_web.py --check` exits 0/1 for CI freshness checks

No changes needed here — the manifest is always current when the server starts.

## Remaining bottlenecks (future work)

### Runtime

| Bottleneck | Severity | Approach |
|-----------|----------|----------|
| AST-walk evaluation (no JIT/compilation) | High | Consider bytecode compilation or tracing JIT |
| Lark parse for every cell | Medium | AST cache keyed by code hash |
| Lark is large (~1 MB) | Medium | Vendor a minimal Lark subset, or pre-compile grammar to LALR table |
| Module reload on reset_session | Low | Keep modules in sys.modules, just re-instantiate interpreter |
| Pyodide single-threaded | Medium | Move execution to a Web Worker |

### Loading

| Bottleneck | Severity | Approach |
|-----------|----------|----------|
| Pyodide ~8-12 MB download | High | CDN with better caching; minimal Pyodide build |
| lark install via micropip | Medium | Fast on warm cache; could vendor lark bytes directly |

### Editor

| Bottleneck | Severity | Approach |
|-----------|----------|----------|
| Monaco ~3 MB JS download | Low | CDN-cached; deferred until init |
| Multiple editor instances | Low | 1-6 editors; Monaco handles this well |

## How to measure

In the browser console after the playground loads:

```javascript
// Time a single cell execution
const t0 = performance.now();
await _runFn("x = 1 + 2\nprint(x)");
console.log("cell time:", performance.now() - t0, "ms");
```

For server-side profiling:

```bash
python3 -m cProfile -s cumulative scripts/cli.py samples/demo.nomi
```
