"""Research probes; no Nomi, cloud, workflow, shell, or deployment execution.

Run from the repository root with Python, PyYAML and jsonschema available.
The JSON output records host-library observations, not DSL conformance.
"""

import argparse
import html
import json
import platform
import re
import shlex
import sqlite3
import unicodedata
from datetime import date
from decimal import Decimal
from importlib.metadata import version

import yaml
from jsonschema import Draft202012Validator, FormatChecker


class RepresentationProbe:
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return "customer-facing"

    def __repr__(self):
        return f"RepresentationProbe(code={self.code})"

    def __format__(self, specification):
        if specification == "compact":
            return f"P{self.code}"
        if specification == "":
            return str(self)
        raise ValueError(f"unsupported format: {specification}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observed-on", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    cases = {}

    source = "on: [push]\n"
    loaded = yaml.safe_load(source)
    cases["yaml_key_resolution"] = {
        "source": source,
        "keys": [
            {"type": type(key).__name__, "repr": repr(key)} for key in loaded
        ],
        "quoted_key": list(yaml.safe_load('"on": [push]\n')),
    }

    cases["yaml_duplicates"] = {
        "source": "replicas: 1\nreplicas: 2\n",
        "value": yaml.safe_load("replicas: 1\nreplicas: 2\n"),
    }

    source = (
        "literal: |\n  alpha\n  beta\n"
        "folded: >\n  alpha\n  beta\n"
        "strip: |-\n  alpha\n  beta\n"
        "keep: |+\n  alpha\n  beta\n\n"
        'double: "alpha\\nbeta"\n'
        "single: 'alpha\\nbeta'\n"
    )
    cases["yaml_scalar_styles"] = {"source": source, "value": yaml.safe_load(source)}

    source = "base: &base\n  tags: [stable]\nalias: *base\n"
    loaded = yaml.safe_load(source)
    cases["yaml_alias_identity"] = {
        "source": source,
        "same_host_object": loaded["base"] is loaded["alias"],
    }

    payload = "plain\nextra: true"
    unsafe_source = "message: " + payload + "\n"
    structured_source = yaml.safe_dump({"message": payload}, sort_keys=False)
    structured_value = yaml.safe_load(structured_source)
    assert structured_value == {"message": payload}
    cases["yaml_text_vs_value"] = {
        "payload": payload,
        "text_substitution": unsafe_source,
        "text_substitution_value": yaml.safe_load(unsafe_source),
        "structured_encoding": structured_source,
        "structured_value": structured_value,
    }

    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE items (name TEXT)")
        connection.executemany("INSERT INTO items VALUES (?)", [("alpha",), ("beta",)])
        payload = "missing' OR 1=1 --"
        unsafe_query = "SELECT name FROM items WHERE name = '" + payload + "'"
        unsafe_rows = [row[0] for row in connection.execute(unsafe_query)]
        parameter_rows = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM items WHERE name = ?", (payload,)
            )
        ]
        assert unsafe_rows == ["alpha", "beta"] and parameter_rows == []
        cases["sql_text_vs_parameter"] = {
            "payload": payload,
            "text_query": unsafe_query,
            "text_query_rows": unsafe_rows,
            "parameter_query_rows": parameter_rows,
        }
    finally:
        connection.close()

    payload = "a.+"
    candidates = ["a.+", "abc", "a"]
    cases["regex_source_vs_literal"] = {
        "payload": payload,
        "source_matches": [value for value in candidates if re.fullmatch(payload, value)],
        "literal_matches": [
            value for value in candidates if re.fullmatch(re.escape(payload), value)
        ],
    }

    payload = 'two words; $(do_not_execute) "quote"'
    argv = ["tool", "--message", payload]
    serialized = shlex.join(argv)
    assert shlex.split(serialized) == argv
    cases["posix_argv_serialization"] = {
        "argv": argv,
        "serialized": serialized,
        "lexical_roundtrip": shlex.split(serialized),
        "executed": False,
    }

    schema = {"type": "string", "format": "date-time"}
    value = "not-a-timestamp"
    cases["json_schema_format"] = {
        "schema": schema,
        "value": value,
        "errors_without_format_checker": len(
            list(Draft202012Validator(schema).iter_errors(value))
        ),
        "errors_with_format_checker": len(
            list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value))
        ),
    }

    composed = "\u00e9"
    decomposed = "e\u0301"
    astral = "\U0001f600"
    cases["unicode_units"] = {
        "composed": composed,
        "decomposed": decomposed,
        "equal_before_normalization": composed == decomposed,
        "equal_after_nfc": unicodedata.normalize("NFC", composed)
        == unicodedata.normalize("NFC", decomposed),
        "composed_codepoints": len(composed),
        "decomposed_codepoints": len(decomposed),
        "astral_codepoints": len(astral),
        "astral_utf8_bytes": len(astral.encode("utf-8")),
        "astral_utf16_code_units": len(astral.encode("utf-16-le")) // 2,
    }

    represented = RepresentationProbe(7)
    representations = {
        "str": str(represented),
        "repr": repr(represented),
        "format_default": format(represented),
        "format_compact": format(represented, "compact"),
    }
    assert len(set(representations.values())) == 3
    cases["python_representation_channels"] = representations

    invalid_utf8 = b"\xffA"
    try:
        invalid_utf8.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        strict_error = {
            "start": error.start,
            "end": error.end,
            "reason": error.reason,
        }
    repaired = invalid_utf8.decode("utf-8", errors="replace")
    escaped = invalid_utf8.decode("utf-8", errors="surrogateescape")
    assert escaped.encode("utf-8", errors="surrogateescape") == invalid_utf8
    cases["text_decode_policies"] = {
        "input_hex": invalid_utf8.hex(),
        "strict_error": strict_error,
        "replacement": repaired,
        "surrogateescape_repr": repr(escaped),
        "surrogateescape_roundtrip_hex": escaped.encode(
            "utf-8", errors="surrogateescape"
        ).hex(),
    }

    mixed_lines = "alpha\r\nbeta\ngamma\r"
    kept_lines = mixed_lines.splitlines(keepends=True)
    assert "".join(kept_lines) == mixed_lines
    cases["line_boundary_preservation"] = {
        "source_repr": repr(mixed_lines),
        "splitlines": mixed_lines.splitlines(),
        "splitlines_keepends_repr": [repr(line) for line in kept_lines],
        "keepends_roundtrip": "".join(kept_lines) == mixed_lines,
        "plain_split_roundtrip": "\n".join(mixed_lines.splitlines()) == mixed_lines,
    }

    precise = Decimal("1.234")
    displayed = format(precise, ".2f")
    cases["presentation_is_not_a_codec"] = {
        "exact": str(precise),
        "displayed": displayed,
        "parsed_display": str(Decimal(displayed)),
        "roundtrip_equal": Decimal(displayed) == precise,
    }

    family = "👩‍👩‍👧‍👦"
    cases["unicode_visible_structure"] = {
        "text": family,
        "codepoints": len(family),
        "utf8_bytes": len(family.encode("utf-8")),
        "scalar_names": [unicodedata.name(character) for character in family],
        "grapheme_segmentation_performed": False,
    }

    directional = "allow # \u202e deny"
    cases["invisible_source_controls"] = {
        "source_repr": repr(directional),
        "non_ascii_or_control": [
            {
                "codepoint": f"U+{ord(character):04X}",
                "name": unicodedata.name(character, "UNKNOWN"),
                "category": unicodedata.category(character),
            }
            for character in directional
            if ord(character) > 127 or unicodedata.category(character).startswith("C")
        ],
        "visual_order_observed": False,
    }

    contextual_payload = '" $(touch never) <tag>&'
    contextual_encodings = {
        "json_string": json.dumps(contextual_payload),
        "html_text": html.escape(contextual_payload, quote=False),
        "posix_shell_word": shlex.quote(contextual_payload),
    }
    assert len(set(contextual_encodings.values())) == 3
    cases["destination_specific_encoding"] = {
        "payload": contextual_payload,
        **contextual_encodings,
        "executed": False,
    }

    delimiter_payload = "first\nEOF\nlast\n"
    fixed_delimiter = "EOF"
    suffix = 1
    selected_delimiter = f"NOMI_END_{suffix}"
    while selected_delimiter in delimiter_payload.splitlines():
        suffix += 1
        selected_delimiter = f"NOMI_END_{suffix}"
    assert fixed_delimiter in delimiter_payload.splitlines()
    assert selected_delimiter not in delimiter_payload.splitlines()
    framed = (
        f"VALUE<<{selected_delimiter}\n"
        f"{delimiter_payload}"
        f"{selected_delimiter}\n"
    )
    prefix = f"VALUE<<{selected_delimiter}\n"
    terminator = f"{selected_delimiter}\n"
    assert framed.startswith(prefix) and framed.endswith(terminator)
    recovered = framed[len(prefix) : -len(terminator)]
    assert recovered == delimiter_payload
    cases["delimiter_collision"] = {
        "payload_repr": repr(delimiter_payload),
        "fixed_delimiter": fixed_delimiter,
        "fixed_delimiter_collides": fixed_delimiter in delimiter_payload.splitlines(),
        "selected_delimiter": selected_delimiter,
        "model_roundtrip": recovered == delimiter_payload,
        "external_protocol_executed": False,
    }

    print(
        json.dumps(
            {
                "observed_on": args.observed_on.isoformat(),
                "scope": "local host-library and original finite-model observations only",
                "environment": {
                    "python": platform.python_version(),
                    "pyyaml": version("PyYAML"),
                    "jsonschema": version("jsonschema"),
                    "sqlite": sqlite3.sqlite_version,
                    "unicode_database": unicodedata.unidata_version,
                },
                "cases": cases,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
