"""
Nomi browser runtime — loads the prototype source tree into Pyodide
and provides run_nomi(code) and reset_session() entry points.
"""

import ast
import contextlib
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


_SESSION_INTERPRETER = None
_SESSION_ID = 0


def reset_session() -> dict:
    global _SESSION_INTERPRETER, _SESSION_ID
    from prototype.interpreter.nomi.interpreter import Interpreter

    _SESSION_INTERPRETER = Interpreter()
    _SESSION_ID += 1
    _log(f"Session #{_SESSION_ID} created")
    return {"ok": True, "session": _SESSION_ID}


def _clean_bindings(bindings: dict) -> dict:
    clean = {}
    for k, v in bindings.items():
        if k.startswith("_"):
            continue
        try:
            clean[k] = repr(v)
        except Exception:
            clean[k] = str(type(v).__name__)
    return clean


def _eval_in_session(code: str) -> dict:
    global _SESSION_INTERPRETER, _SESSION_ID
    from prototype.interpreter.nomi.usage import _nomi_desugar
    from prototype.parser.nomi.usage import generate_ast

    if _SESSION_INTERPRETER is None:
        reset_session()
        _log(f"Auto-created session #{_SESSION_ID}")

    tree = generate_ast(code=code, dump=False)
    tree = _nomi_desugar(tree)
    tree = ast.fix_missing_locations(tree)
    _SESSION_INTERPRETER.eval(tree)
    return _SESSION_INTERPRETER.global_env.bindings


async def run_nomi(code: str) -> dict:
    global _SESSION_ID
    if not code.endswith("\n"):
        code += "\n"
    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            bindings = _eval_in_session(code)
        raw = stdout.getvalue()
        return {"output": raw, "bindings": _clean_bindings(bindings), "session": _SESSION_ID}
    except Exception as e:
        return {"error": str(e), "output": stdout.getvalue(), "session": _SESSION_ID}
