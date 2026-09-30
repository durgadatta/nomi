"""Inspect current Nomi pipeline artifacts without executing the program.

Usage: python3 -m tools.syntax.inspect [FILE] --stage STAGE
"""

import argparse
import sys
from pathlib import Path

RUNTIME_STAGES = {
    "python-ast": "python_ast",
    "core": "core",
    "core-json": "core_json",
    "core_json": "core_json",
    "core-verify": "core_verify",
    "core_verify": "core_verify",
    "core-to-python": "core_to_python",
    "core_to_python": "core_to_python",
    "backend-lowered": "backend_lowered",
    "backend_lowered": "backend_lowered",
    "runtime-cache-key": "runtime_cache_key",
    "runtime_cache_key": "runtime_cache_key",
    "cache-key": "runtime_cache_key",
    "features": "features",
    "capabilities": "capabilities",
    "capability-matrix": "capabilities",
    "capability_matrix": "capabilities",
    "target-alignment": "target_alignment",
    "target_alignment": "target_alignment",
    "parser-frontends": "parser_frontends",
    "parser_frontends": "parser_frontends",
    "frontends": "parser_frontends",
    "eval-backends": "eval_backends",
    "eval_backends": "eval_backends",
    "host-capabilities": "host_capabilities",
    "host_capabilities": "host_capabilities",
    "resolved-pipelines": "resolved_pipelines",
    "resolved_pipelines": "resolved_pipelines",
    "pipelines": "resolved_pipelines",
    "passes": "passes",
    "desugar-passes": "passes",
    "desugar_passes": "passes",
    "expansions": "expansions",
    "desugar-expansions": "expansions",
    "desugar_expansions": "expansions",
}
PARSER_DEBUG_STAGES = ("raw-tree", "transformed-tree", "surface-ast")
METADATA_STAGES = {
    "features",
    "capabilities",
    "target_alignment",
    "parser_frontends",
    "eval_backends",
    "host_capabilities",
    "resolved_pipelines",
    "passes",
}


def main(argv=None):
    if __package__ in {None, ""}:
        # Avoid shadowing stdlib inspect when invoked as a source script.
        script_dir = Path(__file__).resolve().parent
        sys.path = [str(script_dir.parents[1])] + [
            entry for entry in sys.path if Path(entry).resolve() != script_dir
        ]

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "filename", nargs="?", help="Nomi source file for artifact inspection"
    )
    parser.add_argument(
        "--stage",
        default="python-ast",
        choices=tuple(RUNTIME_STAGES) + PARSER_DEBUG_STAGES,
    )
    args = parser.parse_args(argv)
    runtime_stage = RUNTIME_STAGES.get(args.stage)
    if args.filename is None and runtime_stage not in METADATA_STAGES:
        parser.error(f"a source file is required for {args.stage}")

    if runtime_stage is not None:
        from prototype.runtime import inspect

        # The original inspection CLI showed the complete reduction inventory.
        mode = "reduced" if runtime_stage in {"passes", "expansions"} else "nomi"
        source = (
            Path(args.filename).read_text(encoding="utf-8") if args.filename else None
        )
        result = inspect(
            source=source,
            filename=args.filename,
            mode=mode,
            stage=runtime_stage,
        )
        print(result.output)
        return

    from prototype.parser.nomi.usage import (
        generate_ast,
        parse_raw_tree,
        parse_transformed_tree,
    )

    source = Path(args.filename).read_text(encoding="utf-8")
    if args.stage == "surface-ast":
        print(generate_ast(code=source, dump=True, keep_surface=True))
    else:
        parse_tree = (
            parse_raw_tree if args.stage == "raw-tree" else parse_transformed_tree
        )
        print(parse_tree(code=source).pretty())


if __name__ == "__main__":
    main()
