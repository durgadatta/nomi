"""Inspect intermediate pipeline stages for a Nomi source file.

Usage::

    python3 -m tools.syntax.inspect FILE          # python-ast (default)
    python3 -m tools.syntax.inspect FILE --stage raw-tree
    python3 -m tools.syntax.inspect FILE --stage transformed-tree
    python3 -m tools.syntax.inspect FILE --stage python-ast
"""

import sys
from pathlib import Path

from prototype.parser.nomi.usage import (
    generate_ast,
    parse_raw_tree,
    parse_transformed_tree,
)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return

    filename = sys.argv[1]
    stage = "python-ast"

    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == "--stage" and i + 1 < len(sys.argv):
            stage = sys.argv[i + 1]

    code = Path(filename).read_text(encoding="utf-8")

    if stage == "raw-tree":
        tree = parse_raw_tree(code=code)
        print(tree.pretty())
    elif stage == "transformed-tree":
        tree = parse_transformed_tree(code=code)
        print(tree.pretty())
    elif stage == "python-ast":
        print(generate_ast(code=code, dump=True))
    else:
        print(f"Unknown stage: {stage!r}. Valid: raw-tree, transformed-tree, python-ast")
        sys.exit(1)


if __name__ == "__main__":
    main()
