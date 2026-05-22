"""Parser frontend boundary for Nomi source.

This module is the first parser-side step toward treating Lark as one
frontend implementation instead of the definition of Nomi's grammar pipeline.
The current frontend still uses Lark and still feeds the Python AST backend,
but callers can now ask for named parser artifacts through a Nomi-owned
interface.
"""

from __future__ import annotations

import os
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
class ParserFrontendSpec:
    """Describes a parser technology or candidate frontend."""

    name: str
    status: str
    grammar_format: str
    implementation: str
    cst_artifact: str
    output_contract: str
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
    notes=(
        "bootstrap path",
        "keeps Python AST backend unchanged",
    ),
)


PARSER_FRONTEND_CANDIDATES: tuple[ParserFrontendSpec, ...] = (
    LARK_FRONTEND_SPEC,
    ParserFrontendSpec(
        name="tree-sitter-cst",
        status="planned-spike",
        grammar_format="Tree-sitter grammar.js / grammar.json",
        implementation="generated C parser with Rust CLI and Python/Rust bindings",
        cst_artifact="Tree-sitter concrete syntax tree",
        output_contract="Nomi Surface IR, then Python AST backend",
        notes=(
            "best fit for editor CST, incremental parsing, and syntax tooling",
            "requires indentation/external-scanner contract",
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


_FRONTENDS = {
    DEFAULT_FRONTEND: LarkParserFrontend(),
}


def get_parser_frontend(name: str = DEFAULT_FRONTEND) -> LarkParserFrontend:
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
        "| frontend | status | grammar | implementation | artifact | output |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for spec in specs:
        rows.append(
            (
                "| {name} | {status} | {grammar} | {implementation} | "
                "{artifact} | {output} |"
            ).format(
                name=spec.name,
                status=spec.status,
                grammar=spec.grammar_format,
                implementation=spec.implementation,
                artifact=spec.cst_artifact,
                output=spec.output_contract,
            )
        )
    return "\n".join(rows)
