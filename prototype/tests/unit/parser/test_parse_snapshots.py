from pathlib import Path
from textwrap import indent

import pytest

from prototype.parser.nomi.usage import parse_raw_tree, parse_transformed_tree


SNAPSHOTS_DIR = Path(__file__).with_name("snapshots")

PARSE_SNAPSHOT_SNIPPETS = {
    "pipeline": "result = 1..5 |> list |> sum\n",
    "match": "label = match value: case 1 => 'one'; case _ => 'many'\n",
    "where": "result = x + y where:\n    x = 1\n    y = 2\n",
    "block_call": "retry(3):\n    value = compute()\n",
    "underscore_lambda": "inc = _ + 1\n",
}


def _snapshot_text(name: str, code: str) -> str:
    raw_tree = parse_raw_tree(code=code).pretty()
    transformed_tree = parse_transformed_tree(code=code).pretty()
    return "\n".join(
        (
            f"# {name}",
            "source:",
            indent(code.rstrip(), "  "),
            "",
            "raw-tree:",
            indent(raw_tree.rstrip(), "  "),
            "",
            "transformed-tree:",
            indent(transformed_tree.rstrip(), "  "),
            "",
        )
    )


@pytest.mark.parametrize("name", tuple(PARSE_SNAPSHOT_SNIPPETS), ids=tuple(PARSE_SNAPSHOT_SNIPPETS))
def test_representative_parse_shapes_are_snapshotted(name, file_regression):
    file_regression.check(
        _snapshot_text(name, PARSE_SNAPSHOT_SNIPPETS[name]),
        fullpath=SNAPSHOTS_DIR / f"{name}.txt",
    )
