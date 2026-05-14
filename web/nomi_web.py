"""
Nomi browser runtime — loads the prototype source tree into Pyodide
and provides run_nomi(code) and reset_session() entry points.
"""

import asyncio
import copy
import contextlib
import io
import json
import os
import sys
import time

PYODIDE = False
try:
    import pyodide
    from pyodide.http import pyfetch
    PYODIDE = True
except ImportError:
    pass


def _log(msg):
    if PYODIDE:
        print(f"[nomi] {msg}", file=sys.stderr)


def _session_get(key, default=None):
    return getattr(_session_store, key, default)


def _session_set(key, value):
    setattr(_session_store, key, value)


class _Store:
    pass


_session_store = _Store()
_generate_ast = None
_nomi_desugar_fn = None
_Interpreter = None
_AST_CACHE = {}
_AST_CACHE_LIMIT = 64


def _get_interpreter():
    interp = _session_get("__nomi_interpreter__")
    _log(f"_get_interpreter -> {'found' if interp else 'None'}")
    return interp


def _set_interpreter(interp):
    _session_set("__nomi_interpreter__", interp)
    _log(f"_set_interpreter: new interpreter stored")


def _get_counter():
    return _session_get("__nomi_counter__", 0)


def _inc_counter():
    n = _get_counter() + 1
    _session_set("__nomi_counter__", n)
    return n


def _base_url():
    from js import location
    # Strip everything after (and including) "/web/" to get the repo root.
    # Works for both /user/repo/web/ and /user/repo/web/index.html.
    idx = location.pathname.index("/web/")
    return location.origin + location.pathname[:idx] + "/"


async def _fetch_manifest_file(base_url, path):
    dir_path = os.path.dirname(path)
    if dir_path:
        try:
            os.makedirs(dir_path)
        except OSError:
            pass

    try:
        resp = await pyfetch(base_url + path)
        if resp.status == 200:
            with open(path, "wb") as f:
                f.write(await resp.bytes())
            return (path, None)
        return (path, f"{path} ({resp.status})")
    except Exception as e:
        return (path, f"{path}: {e}")


async def _load_from_manifest(base_url, manifest):
    """Load prototype files individually from the manifest."""
    files = manifest["files"]
    _log(f"Loading {len(files)} files in batches...")

    missing = []
    ok = 0
    batch_size = 24
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        results = await asyncio.gather(*(_fetch_manifest_file(base_url, path) for path in batch))
        for _, error in results:
            if error:
                missing.append(error)
            else:
                ok += 1

    _log(f"Loaded {ok}/{len(files)} files")
    if missing:
        for m in missing[:5]:
            _log(f"  MISSING: {m}")
        if len(missing) > 5:
            _log(f"  ... and {len(missing) - 5} more")


async def _ensure_prototype_loaded():
    if not PYODIDE:
        return

    base = _base_url()

    # Fetch manifest first (small, needed for samples list anyway)
    _log("Loading manifest...")
    resp = await pyfetch(base + "web/manifest.json")
    manifest = json.loads(await resp.string())
    _log(f"Manifest: {len(manifest['files'])} files")

    await _load_from_manifest(base, manifest)


async def init_nomi():
    global _generate_ast, _nomi_desugar_fn, _Interpreter
    await _ensure_prototype_loaded()
    # ── pre-warm parser & modules ────────────────────────────────
    # Lark Earley parser construction is expensive (~100+ ms in
    # Pyodide).  Force parser creation and key module imports now
    # so the first user cell runs at full speed.
    from prototype.parser.nomi.usage import generate_ast
    from prototype.interpreter.nomi.interpreter import Interpreter
    from prototype.interpreter.nomi.usage import _nomi_desugar
    _generate_ast = generate_ast
    _nomi_desugar_fn = _nomi_desugar
    _Interpreter = Interpreter
    tree = generate_ast(code="x = 1\n")
    tree = _nomi_desugar(tree)
    reset_session()
    _log("Parser pre-warmed")



def reset_session() -> dict:
    global _Interpreter
    if _Interpreter is None:
        from prototype.interpreter.nomi.interpreter import Interpreter
        _Interpreter = Interpreter

    interp = _Interpreter()
    _set_interpreter(interp)
    sid = _inc_counter()
    _log(f"Session #{sid} created")
    return {"ok": True, "session": sid}


def _cache_ast(code, tree):
    if code in _AST_CACHE:
        _AST_CACHE[code] = tree
        return
    if len(_AST_CACHE) >= _AST_CACHE_LIMIT:
        oldest = next(iter(_AST_CACHE))
        del _AST_CACHE[oldest]
    _AST_CACHE[code] = tree


def _parse_and_desugar(code: str) -> tuple[object, dict]:
    global _generate_ast, _nomi_desugar_fn
    if _generate_ast is None or _nomi_desugar_fn is None:
        from prototype.interpreter.nomi.usage import _nomi_desugar
        from prototype.parser.nomi.usage import generate_ast
        _generate_ast = generate_ast
        _nomi_desugar_fn = _nomi_desugar

    timings = {}
    cached = _AST_CACHE.get(code)
    if cached is not None:
        t0 = time.perf_counter()
        tree = copy.deepcopy(cached)
        timings["cache_ms"] = (time.perf_counter() - t0) * 1000
        timings["cache_hit"] = True
        return tree, timings

    parse_start = time.perf_counter()
    tree = _generate_ast(code=code, dump=False)
    timings["parse_ms"] = (time.perf_counter() - parse_start) * 1000

    desugar_start = time.perf_counter()
    tree = _nomi_desugar_fn(tree)
    timings["desugar_ms"] = (time.perf_counter() - desugar_start) * 1000
    timings["cache_hit"] = False

    _cache_ast(code, copy.deepcopy(tree))
    return tree, timings


def _eval_in_session(code: str) -> dict:
    interp = _get_interpreter()
    if interp is None:
        reset_session()
        interp = _get_interpreter()

    tree, timings = _parse_and_desugar(code)
    # _nomi_desugar already calls ast.fix_missing_locations internally —
    # no need to call it again here.
    eval_start = time.perf_counter()
    interp.eval(tree)
    timings["eval_ms"] = (time.perf_counter() - eval_start) * 1000
    return timings


async def run_nomi(code: str) -> dict:
    if not code.endswith("\n"):
        code += "\n"
    stdout = io.StringIO()
    total_start = time.perf_counter()
    try:
        with contextlib.redirect_stdout(stdout):
            timings = _eval_in_session(code)
        raw = stdout.getvalue()
        timings["total_ms"] = (time.perf_counter() - total_start) * 1000
        return {"output": raw, "session": _get_counter(), "timing": timings}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        _log(f"Error in run_nomi: {e}\n{tb}")
        # Show last 5 traceback lines to pinpoint the source file
        lines = tb.strip().split("\n")
        short_tb = "\n".join(lines[-6:]) if len(lines) > 5 else tb
        return {
            "error": short_tb,
            "output": stdout.getvalue(),
            "session": _get_counter(),
            "timing": {"total_ms": (time.perf_counter() - total_start) * 1000},
        }
