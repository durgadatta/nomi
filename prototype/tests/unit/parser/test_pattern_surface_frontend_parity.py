import json
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from prototype.parser.nomi.frontend import get_pattern_surface_frontends
from prototype.syntax.pattern_surface import (
    PATTERN_SURFACE_SCHEMA,
    PATTERN_SURFACE_VERSION,
    RESERVED_PATTERN_NAMES,
    PatternSurfaceDocument,
    capture_names,
    node_kinds,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_PATH = REPO_ROOT / "prototype/tests/data/pattern_surface/v1.json"
SCHEMA_PATH = REPO_ROOT / "docs/design/schemas/pattern_surface.schema.json"
FIXTURES = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
SCHEMA_VALIDATOR = Draft202012Validator(SCHEMA)


pytestmark = pytest.mark.skipif(
    shutil.which("cargo") is None,
    reason="Pattern Surface frontend parity requires Cargo",
)


@pytest.mark.parametrize(
    "case",
    FIXTURES["positive"],
    ids=lambda case: case["id"],
)
def test_pattern_surface_frontends_emit_equivalent_positive_fixtures(case):
    payload = _equivalent_payload(case["source"])
    expected = case["expected"]
    document = PatternSurfaceDocument.from_dict(payload)

    SCHEMA_VALIDATOR.validate(payload)
    assert payload["schema"] == FIXTURES["pattern_surface_schema"]
    assert payload["version"] == FIXTURES["pattern_surface_version"]
    assert payload["source"] == case["source"]
    assert payload["diagnostics"] == []
    assert payload["root"]["kind"] == expected["kind"]
    assert payload["root"]["span"] == expected["span"]
    assert list(capture_names(document.root)) == expected["captures"]
    assert list(node_kinds(document.root)) == expected["node_kinds"]
    for path, value in expected.get("checks", {}).items():
        assert _lookup(payload, path) == value
    _assert_utf8_spans(payload, case["source"])


@pytest.mark.parametrize(
    "case",
    FIXTURES["negative"],
    ids=lambda case: case["id"],
)
def test_pattern_surface_frontends_emit_equivalent_diagnostics(case):
    payload = _equivalent_payload(case["source"])
    document = PatternSurfaceDocument.from_dict(payload)

    SCHEMA_VALIDATOR.validate(payload)
    assert payload["source"] == case["source"]
    assert payload["root"] is None
    assert payload["diagnostics"] == [case["expected"]]
    assert document.root is None
    assert document.to_dict() == payload
    _assert_utf8_spans(payload, case["source"])


def test_pattern_surface_schema_and_fixture_versions_are_pinned():
    Draft202012Validator.check_schema(SCHEMA)

    assert FIXTURES["schema"] == "nomi.pattern-surface-fixtures"
    assert FIXTURES["version"] == 1
    assert SCHEMA["x-nomi-status"] == "experimental"
    assert SCHEMA["properties"]["schema"]["const"] == PATTERN_SURFACE_SCHEMA
    assert SCHEMA["properties"]["version"]["const"] == PATTERN_SURFACE_VERSION
    assert set(SCHEMA["required"]) == {
        "schema",
        "version",
        "source",
        "root",
        "diagnostics",
    }
    assert {
        item["$ref"] for item in SCHEMA["$defs"]["Pattern"]["oneOf"]
    } == {
        f"#/$defs/{kind}"
        for kind in {
            "WildcardPattern",
            "CapturePattern",
            "LiteralPattern",
            "NominalPattern",
            "TuplePattern",
            "ListPattern",
            "MapPattern",
            "OrPattern",
            "AsPattern",
        }
    }


def test_pattern_surface_frontends_are_capability_registered():
    assert tuple(
        frontend.spec.name for frontend in get_pattern_surface_frontends()
    ) == ("lark-lalr", "rust-fast-ast")


def test_reserved_vocabulary_cannot_become_pattern_captures():
    schema_reserved = set(
        SCHEMA["$defs"]["CaptureName"]["allOf"][1]["not"]["enum"]
    )
    assert schema_reserved == RESERVED_PATTERN_NAMES

    for name in sorted(RESERVED_PATTERN_NAMES):
        source = f"value as {name}"
        payload = _equivalent_payload(source)
        assert payload["root"] is None
        assert payload["diagnostics"][0]["code"] == "InvalidPatternSyntax"
        assert payload["diagnostics"][0]["span"] == {
            "start": len("value as "),
            "end": len(source),
        }


def _equivalent_payload(source: str):
    payloads = {
        frontend.spec.name: frontend.pattern_surface_payload(code=source)
        for frontend in get_pattern_surface_frontends()
    }
    assert payloads["lark-lalr"] == payloads["rust-fast-ast"]
    return payloads["lark-lalr"]


def _lookup(payload, path: str):
    value = payload
    for part in path.split("."):
        value = value[int(part)] if part.isdigit() else value[part]
    return value


def _assert_utf8_spans(payload, source: str) -> None:
    encoded = source.encode("utf-8")
    for span in _walk_spans(payload):
        assert 0 <= span["start"] <= span["end"] <= len(encoded)
        encoded[span["start"] : span["end"]].decode("utf-8")


def _walk_spans(value):
    if isinstance(value, dict):
        if set(value) == {"start", "end"}:
            yield value
        for child in value.values():
            yield from _walk_spans(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_spans(child)
