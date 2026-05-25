"""Regenerate or check the assembled Nomi grammar reference.

Usage::

    python3 -m tools.syntax.grammar_ref
    python3 -m tools.syntax.grammar_ref --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from prototype.grammar.assemble import assemble_grammar


DEFAULT_REFERENCE_PATH = Path("prototype/grammar/nomi.ref.lark")
HEADER = """// Nomi grammar - assembled from layers in prototype/grammar/layers/
// Not read at runtime. Regenerate: python3 -m tools.syntax.grammar_ref"""


def build_reference_text() -> str:
    return f"{HEADER}\n\n{assemble_grammar()}\n"


def write_reference_grammar(path: Path = DEFAULT_REFERENCE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_reference_text(), encoding="utf-8")


def is_reference_current(path: Path = DEFAULT_REFERENCE_PATH) -> bool:
    if not path.exists():
        return False
    return path.read_text(encoding="utf-8") == build_reference_text()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit with a non-zero status if the grammar reference is stale",
    )
    parser.add_argument(
        "--path",
        default=str(DEFAULT_REFERENCE_PATH),
        help="reference file to write or check",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = Path(args.path)

    if args.check:
        if is_reference_current(path):
            print(f"Grammar reference is up to date: {path}")
            return 0
        print(
            f"Grammar reference is stale: {path}\n"
            "Run: python3 -m tools.syntax.grammar_ref",
            file=sys.stderr,
        )
        return 1

    write_reference_grammar(path)
    print(f"Wrote grammar reference: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
