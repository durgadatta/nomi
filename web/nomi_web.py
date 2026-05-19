"""
Nomi browser runtime — loads the prototype source tree into Pyodide
and provides run_nomi(code) and reset_session() entry points.
"""

import asyncio
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
_runtime_session = None
_SESSION_AST_CACHE_LIMIT = 64


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
    await _ensure_prototype_loaded()
    # ── pre-warm parser & modules ────────────────────────────────
    # Lark Earley parser construction is expensive (~100+ ms in
    # Pyodide).  Force parser creation and key module imports now
    # so the first user cell runs at full speed.
    from prototype.parser.nomi.usage import generate_ast
    from prototype.parser.nomi.desugar import desugar_module
    tree = generate_ast(code="x = 1\n")
    tree = desugar_module(tree)
    reset_session()
    _log("Parser pre-warmed")



def reset_session() -> dict:
    global _runtime_session

    from prototype.runtime import RuntimeSession

    if _runtime_session is None:
        _runtime_session = RuntimeSession(
            mode="nomi",
            cache_size=_SESSION_AST_CACHE_LIMIT,
        )
    else:
        _runtime_session.reset(clear_cache=True)
    _set_interpreter(_runtime_session.interpreter)
    sid = _inc_counter()
    _log(f"Session #{sid} created")
    return {"ok": True, "session": sid}


def _web_timing(runtime_timings: dict) -> dict:
    timings = {}
    if "cache" in runtime_timings:
        timings["cache_ms"] = runtime_timings["cache"] * 1000
        timings["cache_hit"] = True
    else:
        timings["cache_hit"] = False
    if "parse" in runtime_timings:
        timings["parse_ms"] = runtime_timings["parse"] * 1000
    if "lower" in runtime_timings:
        timings["desugar_ms"] = runtime_timings["lower"] * 1000
    if "eval" in runtime_timings:
        timings["eval_ms"] = runtime_timings["eval"] * 1000
    return timings


def _eval_in_session(code: str) -> dict:
    global _runtime_session
    if _runtime_session is None:
        reset_session()

    result = _runtime_session.run(
        source=code,
        raise_on_error=False,
        capture_output=True,
    )
    timings = _web_timing(result.timings)
    return {
        "result": result,
        "timing": timings,
    }


async def run_nomi(code: str) -> dict:
    if not code.endswith("\n"):
        code += "\n"
    total_start = time.perf_counter()
    execution = _eval_in_session(code)
    result = execution["result"]
    timings = execution["timing"]
    timings["total_ms"] = (time.perf_counter() - total_start) * 1000
    if result.ok:
        return {
            "output": result.stdout,
            "session": _get_counter(),
            "timing": timings,
        }

    try:
        raise result.exception
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        _log(f"Error in run_nomi: {e}\n{tb}")
        # Show last 5 traceback lines to pinpoint the source file
        lines = tb.strip().split("\n")
        short_tb = "\n".join(lines[-6:]) if len(lines) > 5 else tb
        return {
            "error": short_tb,
            "output": result.stdout,
            "session": _get_counter(),
            "timing": timings,
        }
