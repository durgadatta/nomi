from pathlib import Path

import pytest

from prototype.parser.nomi.frontend import get_parser_frontend

REPO_ROOT = Path(__file__).resolve().parents[4]
DEMO = REPO_ROOT / "samples" / "demo.nomi"


def test_tree_sitter_spike_parses_demo_without_errors(tmp_path):
    frontend = get_parser_frontend("tree-sitter-cst")
    try:
        summary = frontend.parse_raw_tree(filename=DEMO)
    except RuntimeError as exc:
        if "tree-sitter CLI" in str(exc):
            pytest.skip(str(exc))
        raise

    parse_summary = summary["parse_summaries"][0]
    assert parse_summary["successful"] is True
    assert parse_summary["file"] == str(DEMO)
