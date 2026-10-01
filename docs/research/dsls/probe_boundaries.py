"""Research probes; no Nomi, cloud, workflow, shell, or deployment execution.

Run from the repository root with Python, PyYAML and jsonschema available.
The JSON output records host-library observations, not DSL conformance.
"""

import argparse
import json
import platform
import re
import shlex
import sqlite3
import unicodedata
from importlib.metadata import version
from datetime import date

import yaml
from jsonschema import Draft202012Validator, FormatChecker


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

    print(
        json.dumps(
            {
                "observed_on": args.observed_on.isoformat(),
                "scope": "local host-library observations only",
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
