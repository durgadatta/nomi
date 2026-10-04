"""Release-facing fallback diagnostics; parsing is not typechecking."""

from pathlib import Path

import pytest

from prototype.runtime import create_session, execute


@pytest.mark.parametrize("backend", ["python-ast", "core-runtime", "js-core-runtime"])
@pytest.mark.parametrize("session", [False, True])
def test_parse_failure_produces_source_diagnostic(backend, session):
    options = dict(source="name = 'Ada'\nx =\n", raise_on_error=False)
    result = (
        create_session(eval_backend=backend).run(**options)
        if session
        else execute(eval_backend=backend, **options)
    )
    assert not result.ok
    assert result.exception is not None
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.phase == "parse"
    assert diagnostic.code == "NOMI-PARSE"
    assert diagnostic.span["line"] == 2
    assert diagnostic.span["column"] > 0
    assert diagnostic.source_excerpt == "x ="
    assert diagnostic.frontend == "lark-lalr"
    assert diagnostic.backend == backend


@pytest.mark.parametrize("session", [False, True])
def test_runtime_failure_preserves_output_and_original_exception(session):
    options = dict(
        source="print('before')\nmissing\n", raise_on_error=False, capture_output=True
    )
    result = create_session().run(**options) if session else execute(**options)
    assert result.stdout == "before\n"
    assert result.exception is not None
    assert result.diagnostics[0].phase == "eval"
    assert result.diagnostics[0].code == "NOMI-RUNTIME"
    assert "missing" in result.diagnostics[0].message
    # Do not invent source locations when the backend supplies none.
    assert result.diagnostics[0].span is None


def test_file_parse_failure_carries_filename_and_excerpt(tmp_path: Path):
    path = tmp_path / "broken.nomi"
    path.write_text("x =\n", encoding="utf-8")
    result = execute(filename=path, raise_on_error=False)
    assert result.diagnostics[0].span["filename"] == str(path)
    assert result.diagnostics[0].source_excerpt == "x ="


def test_binding_diagnostic_still_has_its_specific_semantic_code():
    result = execute(source="age: int, age > 0 = -1\n", raise_on_error=False)
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].code == "NOMI-BINDING-CONSTRAINT"
