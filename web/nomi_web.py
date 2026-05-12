"""
Nomi browser runtime — loads the prototype source tree into Pyodide
and provides a run_nomi(code) entry point.
"""

import ast
import io
import json
import os
import sys

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


def _base_url():
    from js import location
    return location.origin + location.pathname.replace("/web/", "/")


async def _ensure_prototype_loaded():
    if not PYODIDE:
        return

    _log("Loading manifest...")
    base = _base_url()
    resp = await pyfetch(base + "web/manifest.json")
    manifest = json.loads(await resp.string())
    files = manifest["files"]
    _log(f"Manifest: {len(files)} files")

    missing = []
    ok = 0
    for path in files:
        dir_path = os.path.dirname(path)
        if dir_path:
            try:
                os.makedirs(dir_path)
            except OSError:
                pass
        if os.path.isfile(path):
            ok += 1
            continue
        try:
            resp = await pyfetch(base + path)
            if resp.status == 200:
                with open(path, "wb") as f:
                    f.write(await resp.bytes())
                ok += 1
            else:
                missing.append(f"{path} ({resp.status})")
        except Exception as e:
            missing.append(f"{path}: {e}")

    _log(f"Loaded {ok}/{len(files)} files")
    if missing:
        for m in missing[:5]:
            _log(f"  MISSING: {m}")
        if len(missing) > 5:
            _log(f"  ... and {len(missing) - 5} more")


async def init_nomi():
    await _ensure_prototype_loaded()


async def run_nomi(code: str) -> dict:
    from prototype.interpreter.nomi.usage import run_eval_loop as _run_nomi
    if not code.endswith("\n"):
        code += "\n"
    stdout = io.StringIO()
    try:
        import contextlib
        with contextlib.redirect_stdout(stdout):
            bindings = _run_nomi(code=code)
        raw = stdout.getvalue()
        clean = {}
        for k, v in bindings.items():
            if k.startswith("_"):
                continue
            try:
                clean[k] = repr(v)
            except Exception:
                clean[k] = str(type(v).__name__)
        return {"output": raw, "bindings": clean}
    except Exception as e:
        return {"error": str(e), "output": stdout.getvalue()}
