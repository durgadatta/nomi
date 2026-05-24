# Nomi Web Playground — Performance Notes

> Historical note: early sections describe the previous Pyodide worker path.
> The current browser default is the Rust/WASM parser plus JavaScript Core
> Runtime path. See `docs/orientation/wasm_js_runtime_review.md` for the latest
> architecture review and promotion risks.

## Current execution pipeline (per cell)

```
User types code → run_nomi(code)
  → _eval_in_session(code)
    → generate_ast(code)          # Lark parse + AST lift
    → desugar_module(tree)         # full desugar pipeline + fix_missing_locations
    → interp.eval(tree)            # AST-walk evaluation
```

## Implemented improvements

### 2026-05-14

#### 1. Stop returning full bindings to JavaScript

**File:** `web/nomi_web.py`

**Before:** every `run_nomi()` call returned a cleaned copy of the interpreter's
global bindings. The current UI only reads `output`, `error`, and `session`, so
Pyodide still had to stringify and marshal data the browser discarded.

**After:** `run_nomi()` returns only the execution output/error and session id.

**Expected win:** Lower per-cell latency, especially after running larger
programs that leave many values in the environment.

#### 2. Cache runtime entry points and keep modules warm on restart

**File:** `web/nomi_web.py`

**Before:** runtime helpers were imported inside hot execution paths, and
`reset_session()` deleted `prototype.*` modules from `sys.modules`, throwing
away parser/module caches on restart.

**After:** `init_nomi()` stores the parser, desugarer, and interpreter class in
module globals. `reset_session()` creates a fresh interpreter without evicting
loaded modules.

**Expected win:** Faster restart and less import/cache churn during browser
sessions.

#### 3. Load manifest files in batches

**File:** `web/nomi_web.py`

**Before:** prototype files listed in `manifest.json` were fetched one at a
time.

**After:** file loading uses bounded async batches.

**Expected win:** Faster Pyodide initialization once the Pyodide runtime and
packages are available.

#### 4. Reduce Run All UI churn

**File:** `web/runtime.js`

**Before:** every cell in Run All toggled global controls and status.

**After:** Run All holds global controls/status stable while each cell runs.

**Expected win:** Smoother notebook execution and less layout/UI work.

#### 5. Move Pyodide execution into a Web Worker

**Files:** `web/worker.js`, `web/app.js`, `web/runtime.js`,
`web/index.html`

**Before:** the main browser thread owned Monaco, layout, buttons, Pyodide,
Nomi parsing, desugaring, and evaluation.

**After:** the main thread owns the UI and sends `init`, `run`, and `reset`
messages to `web/worker.js`. The worker loads Pyodide, installs Lark, loads
`nomi_web.py`, runs Nomi code, and returns plain JavaScript result objects.

**Expected win:** The editor and controls stay more responsive while Nomi code
runs. Raw execution may not be faster, but UI hitches should be reduced.

#### 6. Add per-run timing and AST cache

**Files:** `web/nomi_web.py`, `web/runtime.js`

**Before:** browser runs reported only total wall time from JavaScript, so parse,
desugar, and eval costs were not visible. Re-running unchanged cells always
parsed and desugared again.

**After:** `run_nomi()` returns a `timing` object with parse/desugar/eval/total
or cache/eval/total timings. The runtime keeps a small source-text cache of
desugared ASTs and deep-copies cached trees before evaluation.

**Expected win:** Faster repeated runs of unchanged cells and visible evidence
for the next bottleneck.

#### 7. Initialize editor and worker in parallel

**File:** `web/app.js`

**Before:** the page initialized Pyodide/Nomi first, then loaded Monaco.

**After:** worker startup and Monaco initialization run concurrently.

**Expected win:** Lower startup wall time on cold loads, especially when CDN
assets are not already warm.

### 2026-05-13

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
after `desugar_module(tree)`, which already calls it internally.  Double
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
| Lark parse for changed cells | Medium | AST cache now handles exact reruns; measure grammar/parser options next |
| Lark is large (~1 MB) | Medium | Vendor a minimal Lark subset, or pre-compile grammar to LALR table |
| Pyodide/WASM execution overhead | Medium | Measure stage timing; reduce parse/desugar/eval work |

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

## Enhancement Roadmap

The noticeable pause after clicking Run is not solely Pyodide. Pyodide adds a
large baseline because Python runs through WebAssembly in the browser, but each
cell also pays for Nomi's current prototype pipeline:

```text
source text -> Lark parse -> AST lift -> Nomi desugar passes -> AST-walk eval
```

The highest-value improvements are below, in recommended order.

### 1. Add Timing Breakdown Per Run

Before changing the runtime again, measure the stages separately inside
`web/nomi_web.py`:

```text
parse_ms
desugar_ms
eval_ms
stdout_ms
total_ms
```

Return an optional `timing` object from `run_nomi()` and show it in the footer
or behind a small "details" affordance. This will tell us whether the slow part
is parsing, desugaring, interpretation, output transfer, or browser/UI work.

Implementation sketch:

```python
t0 = time.perf_counter()
tree = _generate_ast(...)
t1 = time.perf_counter()
tree = _desugar_fn(tree)
t2 = time.perf_counter()
interp.eval(tree)
t3 = time.perf_counter()
```

Then return:

```python
{
    "output": raw,
    "session": _get_counter(),
    "timing": {
        "parse_ms": ...,
        "desugar_ms": ...,
        "eval_ms": ...,
        "total_ms": ...,
    },
}
```

### 2. Cache Parsed/Desugared Cells

Most notebook work reruns the same cell repeatedly, sometimes after editing a
different cell. Cache the desugared AST by source hash:

```text
code hash -> desugared AST
```

When code has not changed, skip parsing and desugaring and go straight to
`interp.eval(tree)`.

Important caveats:

- Python AST nodes should not be mutated during evaluation. If the interpreter
  mutates AST nodes, cache a deep copy or cache a serializable/lowered form
  instead.
- Cache invalidation can be simple at first: exact code string hash only.
- Keep the cache per browser session and clear it on hard runtime reload, not
  necessarily on `reset_session()`.

Expected win: high for repeated execution of unchanged cells, especially when
parse/desugar dominate.

### 3. Keep Worker Execution Responsive

A Web Worker is a separate browser thread for JavaScript. In this playground,
Pyodide and the Nomi runtime now live in `web/worker.js` outside the main UI
thread.

Current shape:

```text
main thread:
  Monaco editor
  buttons/layout
  Pyodide
  Nomi parse/desugar/eval
```

Current worker shape:

```text
main thread:
  Monaco editor
  buttons/layout
  postMessage({ type: "run", code, requestId })

worker thread:
  load Pyodide
  load prototype files
  run init_nomi()
  run code
  postMessage({ type: "result", requestId, output, error, timing })
```

What this improves:

- The UI stays responsive while Python/WASM is parsing and evaluating.
- Buttons, cursor movement, scrolling, and progress UI do not hitch.
- Long-running cells can later support cancellation/restart boundaries.

What this does not automatically improve:

- Raw Python execution may not become faster. The worker mainly prevents the
  execution pause from blocking the interface.
- Startup may still take time because the worker still downloads Pyodide,
  installs/loads Lark, and loads prototype files.

Current files:

```text
web/worker.js       # owns Pyodide and request/response loop
web/runtime.js      # sends run/reset/init messages instead of calling _runFn
web/nomi_web.py     # stays mostly unchanged as the Python bridge
```

Minimal message protocol:

```javascript
// main -> worker
{ id, type: "init" }
{ id, type: "run", code }
{ id, type: "reset" }

// worker -> main
{ id, type: "ready" }
{ id, type: "result", output, error, session, timing }
{ id, type: "reset-done", session }
{ id, type: "log", message }
{ id, type: "error", error }
```

Follow-up work:

- Add a hard "Restart worker" path that terminates and recreates the worker
  when a cell hangs.
- Add cancellation policy for long-running cells. JavaScript cannot interrupt
  arbitrary Python in a worker cleanly without killing the worker.
- Forward structured timing details from the worker to the footer.
- Consider separate progress messages for parse/desugar/eval once timing is
  instrumented.

Risks:

- Pyodide in a worker needs correct asset paths and CORS-friendly CDN loading.
- Python stdout redirection already happens in `nomi_web.py`, which is good.
- The worker cannot directly touch DOM or Monaco; all UI updates must happen
  through messages.
- Some browsers may require careful handling for `SharedArrayBuffer` only if
  future threaded WASM is used. Basic Pyodide-in-worker does not require that
  design at first.

### 4. Prebundle Runtime Files

The current manifest path fetches many small Python and grammar files. Batching
helps, but many small requests still have overhead. A future build step could
generate one bundle:

```text
web/nomi_runtime_files.json
```

or a compressed archive that contains all prototype files. The Pyodide bridge
would fetch one file and write each entry into the virtual filesystem.

Expected win: faster startup, especially on high-latency networks.

Tradeoff: a generated bundle must stay fresh, similar to `manifest.json`.

### 5. Reduce Parser Cost

If timing shows parse/desugar is the main per-cell cost:

- try a LALR-compatible grammar path for browser execution;
- precompile grammar artifacts if Lark supports a usable standalone path for
  this grammar;
- cache AST/desugar outputs aggressively;
- consider a small browser-target parser for the implemented syntax subset.

This is more invasive than worker/caching work, so measure first.

### 6. Compile Or Lower The Interpreter Hot Path

If timing shows `interp.eval(tree)` dominates:

- compile repeated cells to a lower internal instruction form;
- reduce Python AST walking overhead;
- cache name lookups or dispatch tables;
- eventually consider a bytecode-like reduced interpreter for browser use.

This is the deepest runtime change. It should wait until the parser/desugar and
worker questions are measured.

## Recommended Next Slice

The next practical slice should be:

1. Add hard worker restart/cancel controls for hung cells.
2. Prebundle runtime files to reduce many small startup fetches.
3. Use timing data to decide whether parser, desugar, or eval deserves the next
   optimization.
4. If parse/desugar dominates changed cells, investigate browser-target parser
   options or precompiled grammar artifacts.

That order improves reliability first, then startup, then deeper runtime speed
based on measured evidence.

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
