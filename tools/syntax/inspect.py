"""Inspect intermediate pipeline stages for a Nomi source file.

Usage::

    python3 -m tools.syntax.inspect FILE          # python-ast (default)
    python3 -m tools.syntax.inspect FILE --stage raw-tree
    python3 -m tools.syntax.inspect FILE --stage transformed-tree
    python3 -m tools.syntax.inspect FILE --stage surface-ast
    python3 -m tools.syntax.inspect FILE --stage core
    python3 -m tools.syntax.inspect FILE --stage python-ast
    python3 -m tools.syntax.inspect --stage features
"""

import sys
from pathlib import Path

from prototype.parser.nomi.usage import (
    generate_ast,
    parse_raw_tree,
    parse_transformed_tree,
)
from prototype.syntax.core import dump_core, lower_python_ast_to_core
from prototype.syntax.features import render_feature_layer_table


def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        return

    filename = None
    stage = "python-ast"
    args = sys.argv[1:]

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--stage" and i + 1 < len(args):
            stage = args[i + 1]
            i += 2
            continue
        if filename is None:
            filename = arg
        i += 1

    if stage == "features":
        print(render_feature_layer_table())
        return

    if filename is None:
        print(__doc__)
        sys.exit(1)

    code = Path(filename).read_text(encoding="utf-8")

    if stage == "raw-tree":
        tree = parse_raw_tree(code=code)
        print(tree.pretty())
    elif stage == "transformed-tree":
        tree = parse_transformed_tree(code=code)
        print(tree.pretty())
    elif stage == "surface-ast":
        print(generate_ast(code=code, dump=True, keep_surface=True))
    elif stage == "core":
        print(dump_core(lower_python_ast_to_core(generate_ast(code=code))))
    elif stage == "python-ast":
        print(generate_ast(code=code, dump=True))
    else:
        print(f"Unknown stage: {stage!r}. "
              f"Valid: raw-tree, transformed-tree, surface-ast, core, python-ast, features")
        sys.exit(1)


if __name__ == "__main__":
    main()
