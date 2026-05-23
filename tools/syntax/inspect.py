"""Inspect intermediate pipeline stages for a Nomi source file.

Usage::

    python3 -m tools.syntax.inspect FILE          # python-ast (default)
    python3 -m tools.syntax.inspect FILE --stage raw-tree
    python3 -m tools.syntax.inspect FILE --stage transformed-tree
    python3 -m tools.syntax.inspect FILE --stage surface-ast
    python3 -m tools.syntax.inspect FILE --stage core
    python3 -m tools.syntax.inspect FILE --stage core-json
    python3 -m tools.syntax.inspect FILE --stage python-ast
    python3 -m tools.syntax.inspect --stage features
    python3 -m tools.syntax.inspect --stage capabilities
    python3 -m tools.syntax.inspect --stage parser-frontends
    python3 -m tools.syntax.inspect --stage eval-backends
    python3 -m tools.syntax.inspect --stage passes
    python3 -m tools.syntax.inspect FILE --stage expansions
    python3 -m tools.syntax.inspect FILE --stage core-verify
    python3 -m tools.syntax.inspect FILE --stage core-to-python
    python3 -m tools.syntax.inspect FILE --stage backend-lowered
"""

import sys
from pathlib import Path

from prototype.parser.nomi.usage import (
    generate_ast,
    parse_raw_tree,
    parse_transformed_tree,
)
from prototype.parser.nomi.frontend import render_parser_frontend_table
from prototype.parser.nomi.desugar.pipeline import (
    render_desugar_expansion,
    render_desugar_pass_table,
)
from prototype.runtime.backends import render_eval_backend_table
from prototype.syntax.core import (
    core_to_python_ast,
    dump_core,
    lower_python_ast_to_core,
    verify_core,
)
from prototype.syntax.features import (
    render_feature_capability_table,
    render_feature_layer_table,
)


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
    if stage in {"capabilities", "capability-matrix", "capability_matrix"}:
        print(render_feature_capability_table())
        return
    if stage in {"parser-frontends", "parser_frontends", "frontends"}:
        print(render_parser_frontend_table())
        return
    if stage in {"passes", "desugar-passes", "desugar_passes"}:
        print(render_desugar_pass_table())
        return
    if stage in {"eval-backends", "eval_backends"}:
        print(render_eval_backend_table())
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
    elif stage in {"core-json", "core_json"}:
        from prototype.runtime import create_session

        print(create_session(mode="nomi").core_json(source=code))
    elif stage in {"core-verify", "core_verify"}:
        tree = generate_ast(code=code)
        core = lower_python_ast_to_core(tree)
        try:
            verify_core(core, strict=True)
            print(f"Core IR verification: PASS\n{dump_core(core)}")
        except Exception as exc:
            print(f"Core IR verification: FAIL\n{exc}")
    elif stage in {"core-to-python", "core_to_python"}:
        import ast as py_ast
        tree = generate_ast(code=code)
        core = lower_python_ast_to_core(tree)
        py_tree = core_to_python_ast(core)
        py_tree = py_ast.fix_missing_locations(py_tree)
        print(py_ast.dump(py_tree, include_attributes=False, indent=2))
    elif stage in {"backend-lowered", "backend_lowered"}:
        from prototype.runtime.backends.python_ast import make_python_ast_backend_for_mode
        from prototype.runtime.modes import get_mode_spec
        tree = generate_ast(code=code)
        core = lower_python_ast_to_core(tree)
        backend = make_python_ast_backend_for_mode(get_mode_spec("nomi"))
        print(backend.render_lowered(core))
    elif stage == "python-ast":
        print(generate_ast(code=code, dump=True))
    elif stage in {"expansions", "desugar-expansions", "desugar_expansions"}:
        print(render_desugar_expansion(generate_ast(code=code)))
    else:
        print(
            f"Unknown stage: {stage!r}. "
            f"Valid: raw-tree, transformed-tree, surface-ast, core, "
            f"core-json, core-verify, core-to-python, backend-lowered, "
            f"python-ast, features, capabilities, parser-frontends, "
            f"eval-backends, passes, expansions"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
