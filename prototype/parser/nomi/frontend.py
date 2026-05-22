"""Parser frontend boundary for Nomi source.

This module is the first parser-side step toward treating Lark as one
frontend implementation instead of the definition of Nomi's grammar pipeline.
The current frontend still uses Lark and still feeds the Python AST backend,
but callers can now ask for named parser artifacts through a Nomi-owned
interface.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lark import Lark
from lark.lexer import PatternRE

from ...grammar.assemble import assemble_grammar, get_layer_pipeline
from ...syntax.features import get_extra_grammar_layers
from .postlexer import NomiPostLexer


GRAMMAR_VERSION = "builtin-features-v1"
DEFAULT_FRONTEND = "lark-lalr"
_REPO_ROOT = Path(__file__).resolve().parents[3]
_TREE_SITTER_NOMI_DIR = _REPO_ROOT / "tools" / "parser_spikes" / "tree_sitter_nomi"


@dataclass(frozen=True, slots=True)
class ParserCacheKey:
    """Identity for a constructed parser."""

    grammar_layers: tuple[str, ...]
    preserve_positions: bool
    grammar_version: str = GRAMMAR_VERSION
    feature_profile: str = "default"
    frontend: str = DEFAULT_FRONTEND


@dataclass(frozen=True, slots=True)
class RawTreeCacheKey:
    """Identity for a raw parse tree cache entry."""

    source_hash: int
    source_identity: str | None
    parser_key: ParserCacheKey


@dataclass(frozen=True, slots=True)
class ParserFrontendCapabilities:
    """Current support level for one parser frontend."""

    parse_current_grammar: bool = False
    lower_to_python_ast: bool = False
    source_spans: bool = False
    selectable_for_execution: bool = False


@dataclass(frozen=True, slots=True)
class ParserFrontendSpec:
    """Describes a parser technology or candidate frontend."""

    name: str
    status: str
    grammar_format: str
    implementation: str
    cst_artifact: str
    output_contract: str
    capabilities: ParserFrontendCapabilities = ParserFrontendCapabilities()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ParseArtifacts:
    """Artifacts produced by a parser frontend before Python AST lowering."""

    frontend: ParserFrontendSpec
    raw_tree: Any
    transformed_tree: Any
    source_identity: str | None = None


LARK_FRONTEND_SPEC = ParserFrontendSpec(
    name=DEFAULT_FRONTEND,
    status="implemented",
    grammar_format="layered Lark grammar",
    implementation="Python + Lark LALR + NomiPostLexer",
    cst_artifact="Lark Tree",
    output_contract="layer-transformed tree for NomiToPythonAST",
    capabilities=ParserFrontendCapabilities(
        parse_current_grammar=True,
        lower_to_python_ast=True,
        source_spans=True,
        selectable_for_execution=True,
    ),
    notes=(
        "bootstrap path",
        "keeps Python AST backend unchanged",
    ),
)


PARSER_FRONTEND_CANDIDATES: tuple[ParserFrontendSpec, ...] = (
    LARK_FRONTEND_SPEC,
    ParserFrontendSpec(
        name="tree-sitter-cst",
        status="parse-spike",
        grammar_format="Tree-sitter line-oriented token grammar",
        implementation="generated C parser with Rust Tree-sitter CLI",
        cst_artifact="Tree-sitter concrete syntax tree",
        output_contract="Nomi Surface IR, then Python AST backend",
        capabilities=ParserFrontendCapabilities(
            parse_current_grammar=True,
            source_spans=True,
        ),
        notes=(
            "participates in parser-frontend acceptance tests",
            "needs structural grammar, indentation contract, and Python AST adapter",
        ),
    ),
    ParserFrontendSpec(
        name="rust-peg-cst",
        status="research-candidate",
        grammar_format="PEG grammar, likely pest-style",
        implementation="Rust parser crate exposed through a serialized artifact",
        cst_artifact="Nomi-owned CST or Surface IR payload",
        output_contract="Nomi Surface IR, then Python AST backend",
        notes=(
            "useful if a Rust-native parser is needed before editor tooling",
            "must not emit Python AST as its primary semantic artifact",
        ),
    ),
    ParserFrontendSpec(
        name="antlr4-cst",
        status="fallback-candidate",
        grammar_format="ANTLR4 grammar",
        implementation="generated parser with Python3 target available",
        cst_artifact="ANTLR parse tree",
        output_contract="Nomi Surface IR, then Python AST backend",
        notes=(
            "broad target-language support",
            "less directly aligned with incremental editor parsing",
        ),
    ),
)


_PARSER_CACHE: dict[ParserCacheKey, Lark] = {}
_RAW_TREE_CACHE: dict[RawTreeCacheKey, object] = {}


def prefer_name_for_underscore_terminal(terminal):
    if terminal.name == "UNDERSCORE":
        terminal.pattern = PatternRE("(?!)_")


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").lower() in {"1", "true", "yes", "on"}


def preserve_positions_default() -> bool:
    return _truthy_env("NOMI_PARSER_SPANS")


class LarkParserFrontend:
    """Current parser frontend backed by Lark."""

    spec = LARK_FRONTEND_SPEC

    def parser_cache_key(
        self,
        *,
        extra_layers=None,
        preserve_positions=None,
    ) -> ParserCacheKey:
        if preserve_positions is None:
            preserve_positions = preserve_positions_default()
        resolved = tuple(get_extra_grammar_layers()) + (
            tuple(extra_layers) if extra_layers else ()
        )
        return ParserCacheKey(
            grammar_layers=resolved,
            preserve_positions=preserve_positions,
            frontend=self.spec.name,
        )

    def get_parser(self, *, extra_layers=None, preserve_positions=None) -> Lark:
        key = self.parser_cache_key(
            extra_layers=extra_layers,
            preserve_positions=preserve_positions,
        )
        preserve_positions = key.preserve_positions
        if key in _PARSER_CACHE:
            return _PARSER_CACHE[key]
        grammar = assemble_grammar(extra_layers=extra_layers)
        parser = Lark(
            grammar,
            parser="lalr",
            lexer="basic",
            postlex=NomiPostLexer(),
            start="file_input",
            edit_terminals=prefer_name_for_underscore_terminal,
            propagate_positions=preserve_positions,
            # Persist LALR analysis across short-lived CLI processes. In-process
            # reuse is handled by _PARSER_CACHE; this removes the cold-run
            # bottleneck for command-line and test invocations.
            cache=True,
        )
        _PARSER_CACHE[key] = parser
        return parser

    def parse_raw_tree(
        self,
        *,
        code=None,
        filename=None,
        preserve_positions=None,
    ):
        if code is None:
            code = Path(filename).read_text(encoding="utf-8")
        if preserve_positions is None:
            preserve_positions = preserve_positions_default()
        parser_key = self.parser_cache_key(preserve_positions=preserve_positions)
        source_identity = (
            str(Path(filename).resolve()) if filename is not None else None
        )
        key = RawTreeCacheKey(
            source_hash=hash(code),
            source_identity=source_identity,
            parser_key=parser_key,
        )
        cached = _RAW_TREE_CACHE.get(key)
        if cached is not None:
            return cached
        tree = self.get_parser(preserve_positions=preserve_positions).parse(code)
        _RAW_TREE_CACHE[key] = tree
        return tree

    def parse_transformed_tree(
        self,
        *,
        code=None,
        filename=None,
        preserve_positions=None,
    ):
        tree = self.parse_raw_tree(
            code=code,
            filename=filename,
            preserve_positions=preserve_positions,
        )
        pipeline = get_layer_pipeline()
        return pipeline.run(tree)

    def parse_artifacts(
        self,
        *,
        code=None,
        filename=None,
        preserve_positions=None,
    ) -> ParseArtifacts:
        raw_tree = self.parse_raw_tree(
            code=code,
            filename=filename,
            preserve_positions=preserve_positions,
        )
        transformed_tree = get_layer_pipeline().run(raw_tree)
        source_identity = (
            str(Path(filename).resolve()) if filename is not None else None
        )
        return ParseArtifacts(
            frontend=self.spec,
            raw_tree=raw_tree,
            transformed_tree=transformed_tree,
            source_identity=source_identity,
        )

    def parse_accepts(self, *, code=None, filename=None) -> None:
        """Raise if this frontend cannot parse the given source."""
        self.parse_raw_tree(code=code, filename=filename, preserve_positions=False)


class TreeSitterParserFrontend:
    """Tree-sitter parser spike for parse-acceptance parity."""

    spec = next(
        spec
        for spec in PARSER_FRONTEND_CANDIDATES
        if spec.name == "tree-sitter-cst"
    )

    def parser_cache_key(
        self,
        *,
        extra_layers=None,
        preserve_positions=None,
    ) -> ParserCacheKey:
        if extra_layers:
            raise ValueError("tree-sitter-cst does not support Lark layers")
        return ParserCacheKey(
            grammar_layers=("tree-sitter-nomi",),
            preserve_positions=bool(preserve_positions),
            frontend=self.spec.name,
        )

    def parse_raw_tree(
        self,
        *,
        code=None,
        filename=None,
        preserve_positions=None,
    ) -> dict[str, Any]:
        return self._parse_summary(code=code, filename=filename)

    def parse_transformed_tree(
        self,
        *,
        code=None,
        filename=None,
        preserve_positions=None,
    ) -> dict[str, Any]:
        return self.parse_raw_tree(code=code, filename=filename)

    def parse_artifacts(
        self,
        *,
        code=None,
        filename=None,
        preserve_positions=None,
    ) -> ParseArtifacts:
        raw_tree = self.parse_raw_tree(code=code, filename=filename)
        source_identity = (
            str(Path(filename).resolve()) if filename is not None else None
        )
        return ParseArtifacts(
            frontend=self.spec,
            raw_tree=raw_tree,
            transformed_tree=raw_tree,
            source_identity=source_identity,
        )

    def parse_accepts(self, *, code=None, filename=None) -> None:
        self._parse_summary(code=code, filename=filename)

    def _parse_summary(self, *, code=None, filename=None) -> dict[str, Any]:
        tree_sitter = _tree_sitter_binary()
        if tree_sitter is None:
            raise RuntimeError(
                "tree-sitter CLI is required for tree-sitter-cst parsing"
            )
        if filename is not None:
            return _run_tree_sitter_parse(tree_sitter, Path(filename))
        if code is None:
            raise ValueError("code or filename is required")
        with tempfile.TemporaryDirectory(prefix="nomi-ts-source-") as temp_dir:
            path = Path(temp_dir) / "inline.nomi"
            path.write_text(code, encoding="utf-8")
            return _run_tree_sitter_parse(tree_sitter, path)


_FRONTENDS = {
    DEFAULT_FRONTEND: LarkParserFrontend(),
    "tree-sitter-cst": TreeSitterParserFrontend(),
}


def get_parser_frontend(name: str = DEFAULT_FRONTEND):
    try:
        return _FRONTENDS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown parser frontend: {name!r}. "
            f"Valid frontends: {tuple(_FRONTENDS)}"
        ) from exc


def render_parser_frontend_table(
    specs: tuple[ParserFrontendSpec, ...] = PARSER_FRONTEND_CANDIDATES,
) -> str:
    rows = [
        "| frontend | status | full grammar | python AST | selectable | "
        "grammar | implementation | artifact | output |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for spec in specs:
        capabilities = spec.capabilities
        rows.append(
            (
                "| {name} | {status} | {full} | {python_ast} | "
                "{selectable} | {grammar} | {implementation} | "
                "{artifact} | {output} |"
            ).format(
                name=spec.name,
                status=spec.status,
                full=_mark(capabilities.parse_current_grammar),
                python_ast=_mark(capabilities.lower_to_python_ast),
                selectable=_mark(capabilities.selectable_for_execution),
                grammar=spec.grammar_format,
                implementation=spec.implementation,
                artifact=spec.cst_artifact,
                output=spec.output_contract,
            )
        )
    return "\n".join(rows)


def _mark(value: bool) -> str:
    return "yes" if value else "no"


def get_selectable_parser_frontends(
    specs: tuple[ParserFrontendSpec, ...] = PARSER_FRONTEND_CANDIDATES,
) -> tuple[str, ...]:
    """Return parser frontends safe to select for normal execution."""
    return tuple(
        spec.name
        for spec in specs
        if spec.capabilities.selectable_for_execution
    )


def get_parse_acceptance_frontends():
    """Return registered frontends that must pass parse acceptance tests."""
    return tuple(
        frontend
        for frontend in _FRONTENDS.values()
        if frontend.spec.capabilities.parse_current_grammar
    )


def _tree_sitter_binary() -> str | None:
    return (
        shutil.which("tree-sitter")
        or os.environ.get("TREE_SITTER_BIN")
        or _cargo_tree_sitter()
    )


def _cargo_tree_sitter() -> str | None:
    candidate = Path.home() / ".cargo" / "bin" / "tree-sitter"
    return str(candidate) if candidate.exists() else None


def _run_tree_sitter_parse(tree_sitter: str, source_path: Path) -> dict[str, Any]:
    env = os.environ.copy()
    with tempfile.TemporaryDirectory(prefix="nomi-tree-sitter-home-") as home:
        env["HOME"] = home
        result = subprocess.run(
            [
                tree_sitter,
                "parse",
                "--grammar-path",
                str(_TREE_SITTER_NOMI_DIR),
                str(source_path),
                "--json-summary",
            ],
            cwd=_TREE_SITTER_NOMI_DIR,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
    output_start = result.stdout.find("{")
    if output_start < 0:
        raise SyntaxError(result.stdout + result.stderr)
    summary = json.loads(result.stdout[output_start:])
    parse_summary = summary["parse_summaries"][0]
    if not parse_summary["successful"]:
        raise SyntaxError(result.stdout + result.stderr)
    return summary
