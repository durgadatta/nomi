"""Read-only checking must remain independent of execution and authority."""

import hashlib

import pytest

from prototype import runtime


@pytest.mark.parametrize("mode", ["python", "nomi"])
def test_invoice_source_can_be_checked_without_running(mode, monkeypatch):
    monkeypatch.setenv("NOMI_EVAL_BACKEND", "deliberately-unavailable")
    source = "price = 1200\nquantity = 3\ntotal = price * quantity\n"
    result = runtime.check(source=source, mode=mode, requirements=("known-types", "pure"))
    record = result.to_record()
    assert result.ok
    assert record["source"]["sha256"] == hashlib.sha256(source.encode()).hexdigest()
    assert record["analysis"]["effects"] == []
    assert any(f["name"] == "total" and f["type"] == "Int" for f in record["analysis"]["facts"])


def test_check_never_imports_or_writes_user_code(tmp_path):
    target = tmp_path / "side-effect"
    source = f"open({str(target)!r}, 'w').write('executed')\n"
    result = runtime.check(source=source, mode="python", requirements=("pure",))
    assert not result.ok
    assert not target.exists()
    assert result.analysis.obligations


def test_syntax_error_is_a_structured_failed_check():
    result = runtime.check(source="func broken(:\n", mode="nomi")
    assert not result.ok
    assert result.analysis is None
    assert result.diagnostics[0].code == "NOMI-PARSE"
    assert result.to_record()["schema"] == "nomi.check"


def test_check_empty_source_is_explicit_not_packaged_demo():
    result = runtime.check(source="", requirements=("pure", "known-types"))
    assert result.ok
    assert result.analysis.facts == ()


def test_check_reads_utf8_source_and_keeps_original_digest(tmp_path):
    path = tmp_path / "invoice.nomi"
    source = 'label = "café"\nprice = 1200\n'
    path.write_text(source, encoding="utf-8")
    result = runtime.check(filename=path, requirements=("known-types",))
    assert result.ok
    assert result.to_record()["source"] == {
        "filename": str(path), "sha256": hashlib.sha256(source.encode()).hexdigest()
    }


def test_check_rejects_unsupported_frontend_without_fallback():
    with pytest.raises(ValueError, match="frontend"):
        runtime.check(source="x = 1\n", parser_frontend="rust-fast-ast")


def test_check_requires_unambiguous_source_input(tmp_path):
    with pytest.raises(ValueError, match="exactly one"):
        runtime.check()
    with pytest.raises(ValueError, match="exactly one"):
        runtime.check(source="x = 1\n", filename=tmp_path / "source.nomi")
