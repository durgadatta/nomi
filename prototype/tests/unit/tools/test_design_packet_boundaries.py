"""Malformed packets must fail the gate, not pass vacuously or crash it."""

import json

import pytest

from prototype.tests.unit.tools.test_design_passes import make_registry
from tools import design_passes


def save_registry(root, registry):
    (root / "config/design_passes.json").write_text(
        json.dumps(registry), encoding="utf-8"
    )


@pytest.mark.parametrize("kind", design_passes.ARTIFACT_KEYS)
@pytest.mark.parametrize("value", [None, "", "   ", 12, [], {}])
def test_required_artifact_values_cannot_be_skipped(tmp_path, kind, value):
    registry = make_registry(tmp_path)
    registry["passes"][0]["artifacts"][kind] = value
    save_registry(tmp_path, registry)

    errors = design_passes.validate_registry(tmp_path)

    assert any(f"{kind} path" in error for error in errors)


@pytest.mark.parametrize("value", [None, [], {}, 1, True])
def test_status_type_is_reported_without_crashing(tmp_path, value):
    registry = make_registry(tmp_path)
    registry["passes"][0]["status"] = value
    save_registry(tmp_path, registry)

    assert any(
        "status must be" in error for error in design_passes.validate_registry(tmp_path)
    )


@pytest.mark.parametrize("value", [None, [], 1, True, "registry"])
def test_registry_requires_an_object(tmp_path, value):
    make_registry(tmp_path)
    save_registry(tmp_path, value)

    assert any("object" in error for error in design_passes.validate_registry(tmp_path))


@pytest.mark.parametrize("value", [True, 1.0, "1"])
def test_schema_version_is_an_exact_integer(tmp_path, value):
    registry = make_registry(tmp_path)
    registry["schema_version"] = value
    save_registry(tmp_path, registry)

    assert any(
        "schema_version" in error for error in design_passes.validate_registry(tmp_path)
    )


@pytest.mark.parametrize("value", ["2026-02-30", "2026-00-16", "2026-13-16"])
def test_review_date_must_exist(tmp_path, value):
    registry = make_registry(tmp_path)
    registry["passes"][0]["last_reviewed"] = value
    save_registry(tmp_path, registry)

    assert any(
        "last_reviewed" in error for error in design_passes.validate_registry(tmp_path)
    )


@pytest.mark.parametrize(
    "text",
    [
        '{"schema_version": 1, "schema_version": 2, "passes": []}',
        '{"schema_version": 1, "passes": [{"id": "one", "id": "two"}]}',
    ],
)
def test_duplicate_json_keys_are_not_silently_overwritten(tmp_path, text):
    make_registry(tmp_path)
    (tmp_path / "config/design_passes.json").write_text(text, encoding="utf-8")

    assert any(
        "duplicate" in error for error in design_passes.validate_registry(tmp_path)
    )


def test_invalid_utf8_artifact_is_a_validation_error(tmp_path):
    registry = make_registry(tmp_path)
    (tmp_path / registry["passes"][0]["artifacts"]["research"]).write_bytes(b"\xff")

    assert any(
        "cannot read" in error for error in design_passes.validate_registry(tmp_path)
    )


def test_rejected_artifact_path_is_not_read(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    registry = make_registry(root)
    outside = tmp_path / "outside.nomi"
    outside.write_text("private fixture", encoding="utf-8")
    registry["passes"][0]["artifacts"]["target"] = "../outside.nomi"
    save_registry(root, registry)
    original = type(outside).read_text

    def guarded_read(path, *args, **kwargs):
        assert path.resolve() != outside.resolve(), "rejected path must not be opened"
        return original(path, *args, **kwargs)

    monkeypatch.setattr(type(outside), "read_text", guarded_read)

    assert any("escapes" in error for error in design_passes.validate_registry(root))


@pytest.mark.parametrize("command", ["check", "list", "show"])
def test_cli_reports_invalid_packets_before_formatting(
    tmp_path, monkeypatch, capsys, command
):
    registry = make_registry(tmp_path)
    registry["passes"][0]["artifacts"]["target"] = None
    save_registry(tmp_path, registry)
    monkeypatch.setattr(design_passes, "ROOT", tmp_path)
    argv = ["design-passes", command] + (["topic"] if command == "show" else [])
    monkeypatch.setattr("sys.argv", argv)

    with pytest.raises(SystemExit) as exit_info:
        design_passes.main()

    assert exit_info.value.code == 1
    assert "FAIL" in capsys.readouterr().out
