import ast
import io
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
    else:
        print(f"[nomi] {msg}")


async def _ensure_prototype_loaded():
    if not PYODIDE:
        return

    _log("Discovering modules...")
    from js import location
    base = location.origin + location.pathname.replace("/web/", "/")
    _log(f"Base URL: {base}")

    # --- discover all needed .py files from the import chain ---
    urls_to_try = set()

    # Start with the core modules
    core = [
        "prototype/__init__.py",
        "prototype/interpreter/__init__.py",
        "prototype/interpreter/constants.py",
        "prototype/interpreter/runner.py",
        "prototype/interpreter/helpers.py",
        "prototype/interpreter/python/__init__.py",
        "prototype/interpreter/python/signals.py",
        "prototype/interpreter/python/env.py",
        "prototype/interpreter/python/generator_state.py",
        "prototype/interpreter/python/binding.py",
        "prototype/interpreter/python/expressions.py",
        "prototype/interpreter/python/ds.py",
        "prototype/interpreter/python/control.py",
        "prototype/interpreter/python/patterns.py",
        "prototype/interpreter/python/class_.py",
        "prototype/interpreter/python/context_managers.py",
        "prototype/interpreter/python/exceptions.py",
        "prototype/interpreter/python/function_call.py",
        "prototype/interpreter/python/function.py",
        "prototype/interpreter/python/others.py",
        "prototype/interpreter/python/interpreter.py",
        "prototype/interpreter/python/usage.py",
        "prototype/interpreter/nomi/__init__.py",
        "prototype/interpreter/nomi/env.py",
        "prototype/interpreter/nomi/generator_state.py",
        "prototype/interpreter/nomi/binding.py",
        "prototype/interpreter/nomi/functions.py",
        "prototype/interpreter/nomi/interpreter.py",
        "prototype/interpreter/nomi/usage.py",
        "prototype/parser/__init__.py",
        "prototype/parser/python/__init__.py",
        "prototype/parser/python/binding.py",
        "prototype/parser/python/expressions.py",
        "prototype/parser/python/simple.py",
        "prototype/parser/python/literals.py",
        "prototype/parser/python/functions.py",
        "prototype/parser/python/sequences.py",
        "prototype/parser/python/control.py",
        "prototype/parser/python/ds.py",
        "prototype/parser/python/module.py",
        "prototype/parser/python/context_managers.py",
        "prototype/parser/python/exception.py",
        "prototype/parser/python/class_.py",
        "prototype/parser/python/patterns.py",
        "prototype/parser/python/others.py",
        "prototype/parser/python/ast_.py",
        "prototype/parser/python/utils.py",
        "prototype/parser/python/statements.py",
        "prototype/parser/nomi/__init__.py",
        "prototype/parser/nomi/functions.py",
        "prototype/parser/nomi/ast_.py",
        "prototype/parser/nomi/usage.py",
        "prototype/grammar/__init__.py",
        "prototype/grammar/nomi.lark",
    ]

    failed = []
    ok = 0
    for module_path in core:
        dir_path = os.path.dirname(module_path)
        if dir_path:
            try:
                os.makedirs(dir_path)
            except OSError:
                pass
        if os.path.isfile(module_path):
            ok += 1
            continue

        url = base + module_path
        try:
            resp = await pyfetch(url)
            if resp.status == 200:
                content = await resp.bytes()
                with open(module_path, "wb") as f:
                    f.write(content)
                ok += 1
            else:
                _log(f"  {module_path} → HTTP {resp.status}")
                failed.append(module_path)
        except Exception as e:
            _log(f"  {module_path} → {e}")
            failed.append(module_path)

    _log(f"Loaded {ok}/{len(core)} modules")
    if failed:
        _log(f"MISSING: {', '.join(failed[:5])}")
        if len(failed) > 5:
            _log(f"  ... and {len(failed) - 5} more")


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
        raw_output = stdout.getvalue()
        clean_bindings = {}
        for k, v in bindings.items():
            if k.startswith("_"):
                continue
            try:
                clean_bindings[k] = repr(v)
            except Exception:
                clean_bindings[k] = str(type(v).__name__)
        return {"output": raw_output, "bindings": clean_bindings}
    except Exception as e:
        return {"error": str(e), "output": stdout.getvalue()}
