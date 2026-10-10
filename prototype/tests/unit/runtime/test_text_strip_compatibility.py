"""Prototype text trimming compatibility; not admission of the target Text API."""

import shutil

import pytest

from prototype.runtime import execute
from scripts.check_guide_examples import Example, run_example

ROUTES = ["nomi", "reduced", "core-runtime", "js-core-runtime", "wasm-js"]
VECTORS = [
    (" 3 ", ()),
    ("\t\r\nAda\v\f ", ()),
    ("", ()),
    (" \t", ()),
    ("a b", ()),
    ("\x85\x1cAda\u3000", ()),
    ("\ufeffAda\ufeff", ()),
    ("xyAdaxy", ("xy",)),
    ("\U0001f600Ada\U0001f600", ("\U0001f600",)),
    (" x ", ("",)),
    (" Ada ", (None,)),
]
VECTORS += [(chr(code) + "Ada" + chr(code), ()) for code in range(0x3100) if chr(code).isspace()]


def run_source(source, route):
    if route in {"wasm-js", "js-core-runtime"} and not shutil.which("node"):
        pytest.skip("Node is not installed")
    if route == "wasm-js":
        return run_example(Example("strip compatibility", source, ""), route)
    options = {"mode": route} if route in {"nomi", "reduced"} else {"eval_backend": route}
    result = execute(source=source, raise_on_error=False, **options)
    if not result.ok:
        raise RuntimeError("; ".join(item.message for item in result.diagnostics))
    return result.stdout


def text_literal(text):
    # Exercise text values independently of the optional Python escape spellings.
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return '"' + escaped + '"'


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("text,arguments", VECTORS)
def test_strip_matches_the_declared_prototype_text_operation(text, arguments, route):
    arguments_source = ", ".join(text_literal(item) if isinstance(item, str) else "None" for item in arguments)
    source = f"value = {text_literal(text)}.strip({arguments_source})\nprint('[' + value + ']')\n"
    assert run_source(source, route) == "[" + text.strip(*arguments) + "]\n"


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("arguments", ["3", "'x', 'y'"])
def test_invalid_strip_arguments_fail_instead_of_being_ignored(route, arguments):
    source = f"value = 'xxAdaxx'.strip({arguments})\nprint('after')\n"
    with pytest.raises(RuntimeError):
        run_source(source, route)
