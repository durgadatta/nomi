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
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lark import Lark
from lark.lexer import PatternRE

from ...grammar.assemble import assemble_grammar, get_layer_pipeline
from ...syntax.features import get_extra_grammar_layers
from .postlexer import NomiPostLexer
from .rust_payload import python_ast_from_rust_payload


GRAMMAR_VERSION = "builtin-features-v1"
DEFAULT_FRONTEND = "lark-lalr"
_REPO_ROOT = Path(__file__).resolve().parents[3]
_TREE_SITTER_NOMI_DIR = _REPO_ROOT / "tools" / "parser_spikes" / "tree_sitter_nomi"
_RUST_FAST_AST_DIR = _REPO_ROOT / "tools" / "parser_spikes" / "rust_fast_ast"
_PEST_READABLE_CST_DIR = _REPO_ROOT / "tools" / "parser_spikes" / "pest_readable_cst"


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
    """Describes a parser technology or candidate frontend.

    Parser specs are deliberately family-neutral: handwritten, PEG, LR,
    Tree-sitter, parser-combinator, and bootstrap Lark frontends all graduate
    through the same capability gates and shared equivalence tests.
    """

    name: str
    status: str
    grammar_format: str
    implementation: str
    cst_artifact: str
    output_contract: str
    capabilities: ParserFrontendCapabilities = ParserFrontendCapabilities()
    experiment_roles: tuple[str, ...] = ()
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
    experiment_roles=("readable-bootstrap", "current-default"),
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
        experiment_roles=("fast", "tooling", "generated-c"),
        notes=(
            "participates in parser-frontend acceptance tests",
            "needs structural grammar, indentation contract, and Python AST adapter",
        ),
    ),
    ParserFrontendSpec(
        name="rust-fast-ast",
        status="python-ast-parity",
        grammar_format="handwritten Rust Pratt parser",
        implementation="Rust CLI emitting Nomi-owned JSON AST payload",
        cst_artifact="JSON AST payload",
        output_contract="Python ast.Module adapter",
        capabilities=ParserFrontendCapabilities(
            parse_current_grammar=True,
            lower_to_python_ast=True,
        ),
        experiment_roles=("fast", "direct-ast", "rust"),
        notes=(
            "passes parser frontend acceptance for sample files and snippets",
            "matches Lark Python AST text for the shared sample/snippet matrix",
            "not selectable for execution until wider runtime parity is proven",
        ),
    ),
    ParserFrontendSpec(
        name="pest-readable-cst",
        status="research-candidate",
        grammar_format="pest PEG grammar",
        implementation="Rust pest parser crate exposed through serialized CST",
        cst_artifact="Nomi-owned CST or Surface IR payload",
        output_contract="Nomi Surface IR, then Python AST backend",
        experiment_roles=("readable", "grammar-file", "rust"),
        notes=(
            "candidate for the most readable non-Lark grammar",
            "must join acceptance tests before parse_current_grammar=True",
        ),
    ),
    ParserFrontendSpec(
        name="winnow-fast-cst",
        status="research-candidate",
        grammar_format="Rust parser combinators",
        implementation="Rust winnow parser crate exposed through serialized CST",
        cst_artifact="Nomi-owned CST or Surface IR payload",
        output_contract="Nomi Surface IR, then Python AST backend",
        experiment_roles=("fast", "handwritten", "rust"),
        notes=(
            "candidate for the fastest non-Lark parser",
            "must join acceptance tests before parse_current_grammar=True",
        ),
    ),
    ParserFrontendSpec(
        name="chumsky-readable-cst",
        status="research-candidate",
        grammar_format="Rust parser combinators",
        implementation="Rust chumsky parser crate exposed through serialized CST",
        cst_artifact="Nomi-owned CST or Surface IR payload",
        output_contract="Nomi Surface IR, then Python AST backend",
        experiment_roles=("readable", "diagnostics", "rust"),
        notes=(
            "candidate for readable parser code and recovery diagnostics",
            "must join acceptance tests before parse_current_grammar=True",
        ),
    ),
    ParserFrontendSpec(
        name="lalrpop-lr-cst",
        status="research-candidate",
        grammar_format="LALRPOP LR grammar",
        implementation="Rust LALRPOP parser crate exposed through serialized CST",
        cst_artifact="Nomi-owned CST or Surface IR payload",
        output_contract="Nomi Surface IR, then Python AST backend",
        experiment_roles=("generated-lr", "rust"),
        notes=(
            "candidate for a Rust LR parser comparable to current LALR shape",
            "must join acceptance tests before parse_current_grammar=True",
        ),
    ),
    ParserFrontendSpec(
        name="antlr4-cst",
        status="fallback-candidate",
        grammar_format="ANTLR4 grammar",
        implementation="generated parser with Python3 target available",
        cst_artifact="ANTLR parse tree",
        output_contract="Nomi Surface IR, then Python AST backend",
        experiment_roles=("portable", "generated"),
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

    def generate_python_ast(self, *, code=None, filename=None) -> ast.Module:
        from .ast_ import NomiToPythonAST
        from ...syntax.surface import lower_surface_to_python

        if code is None:
            code = Path(filename).read_text(encoding="utf-8")
        tree = self.parse_transformed_tree(code=code, filename=filename)
        node = NomiToPythonAST().transform(tree)
        lower_surface_to_python(node)
        return node

    def python_ast_text(self, *, code=None, filename=None) -> str:
        return ast.dump(
            self.generate_python_ast(code=code, filename=filename),
            include_attributes=False,
            indent=2,
        )


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
        if code is None:
            if filename is not None:
                return _run_tree_sitter_parse(tree_sitter, Path(filename))
            raise ValueError("code or filename is required")
        with tempfile.TemporaryDirectory(prefix="nomi-ts-source-") as temp_dir:
            path = Path(temp_dir) / "inline.nomi"
            path.write_text(code, encoding="utf-8")
            return _run_tree_sitter_parse(tree_sitter, path)


class JsonPayloadParserFrontend:
    """Reusable boundary for frontends that emit a JSON parser payload.

    This is intentionally not Rust-specific. A future PEG or generated parser
    can reuse this runner/adapter shape if its CLI emits the same kind of
    serialized Nomi-owned parser artifact.
    """

    inline_source_prefix = "nomi-json-parser-source-"

    def parse_raw_tree(
        self,
        *,
        code=None,
        filename=None,
        preserve_positions=None,
    ) -> dict[str, Any]:
        return self._parse_payload(code=code, filename=filename)

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
        self._parse_payload(code=code, filename=filename)

    def generate_python_ast(self, *, code=None, filename=None) -> ast.Module:
        payload = self._parse_payload(code=code, filename=filename)
        return self._python_ast_from_payload(payload)

    def python_ast_text(self, *, code=None, filename=None) -> str:
        return ast.dump(
            self.generate_python_ast(code=code, filename=filename),
            include_attributes=False,
            indent=2,
        )

    def _parse_payload(self, *, code=None, filename=None) -> dict[str, Any]:
        if code is None:
            if filename is not None:
                return self._parse_payload_file(Path(filename))
            raise ValueError("code or filename is required")
        with tempfile.TemporaryDirectory(prefix=self.inline_source_prefix) as temp_dir:
            path = Path(temp_dir) / "inline.nomi"
            path.write_text(code, encoding="utf-8")
            return self._parse_payload_file(path)

    def _parse_payload_file(self, source_path: Path) -> dict[str, Any]:
        raise NotImplementedError

    def _python_ast_from_payload(self, payload: dict[str, Any]) -> ast.Module:
        raise NotImplementedError


class RustFastAstParserFrontend(JsonPayloadParserFrontend):
    """Rust parser spike that directly emits a Python-AST-adaptable payload."""

    spec = next(
        spec
        for spec in PARSER_FRONTEND_CANDIDATES
        if spec.name == "rust-fast-ast"
    )
    inline_source_prefix = "nomi-rust-fast-source-"

    def _parse_payload_file(self, source_path: Path) -> dict[str, Any]:
        return _run_cargo_json_parser(
            crate_dir=_RUST_FAST_AST_DIR,
            command="ast-json",
            source_path=source_path,
            target_name="rust-fast-ast",
        )

    def _python_ast_from_payload(self, payload: dict[str, Any]) -> ast.Module:
        return python_ast_from_rust_payload(payload)


class PestReadableCstParserFrontend(JsonPayloadParserFrontend):
    """PEG parser scaffold that emits a serialized CST/debug payload."""

    spec = next(
        spec
        for spec in PARSER_FRONTEND_CANDIDATES
        if spec.name == "pest-readable-cst"
    )
    inline_source_prefix = "nomi-pest-readable-source-"

    def _parse_payload_file(self, source_path: Path) -> dict[str, Any]:
        return _run_cargo_json_parser(
            crate_dir=_PEST_READABLE_CST_DIR,
            command="cst-json",
            source_path=source_path,
            target_name="pest-readable-cst",
        )


_FRONTENDS = {
    DEFAULT_FRONTEND: LarkParserFrontend(),
    "tree-sitter-cst": TreeSitterParserFrontend(),
    "rust-fast-ast": RustFastAstParserFrontend(),
    "pest-readable-cst": PestReadableCstParserFrontend(),
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
        "roles | grammar | implementation | artifact | output |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for spec in specs:
        capabilities = spec.capabilities
        rows.append(
            (
                "| {name} | {status} | {full} | {python_ast} | "
                "{selectable} | {roles} | {grammar} | {implementation} | "
                "{artifact} | {output} |"
            ).format(
                name=spec.name,
                status=spec.status,
                full=_mark(capabilities.parse_current_grammar),
                python_ast=_mark(capabilities.lower_to_python_ast),
                selectable=_mark(capabilities.selectable_for_execution),
                roles=", ".join(spec.experiment_roles) or "-",
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


def get_functional_replacement_frontends(
    specs: tuple[ParserFrontendSpec, ...] = PARSER_FRONTEND_CANDIDATES,
) -> tuple[str, ...]:
    """Return non-Lark frontends that can replace the current default parser."""
    return tuple(
        spec.name
        for spec in specs
        if spec.name != DEFAULT_FRONTEND
        and spec.capabilities.parse_current_grammar
        and spec.capabilities.lower_to_python_ast
        and spec.capabilities.selectable_for_execution
    )


def get_parse_acceptance_frontends():
    """Return registered frontends that must pass parse acceptance tests."""
    return tuple(
        frontend
        for frontend in _FRONTENDS.values()
        if frontend.spec.capabilities.parse_current_grammar
    )


def get_python_ast_frontends():
    """Return frontends that must match the Python AST backend artifact."""
    return tuple(
        frontend
        for frontend in _FRONTENDS.values()
        if frontend.spec.capabilities.lower_to_python_ast
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
    source_path = source_path.resolve()
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


def _run_cargo_json_parser(
    *,
    crate_dir: Path,
    command: str,
    source_path: Path,
    target_name: str,
) -> dict[str, Any]:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise RuntimeError(f"cargo is required for {target_name} parsing")
    source_path = source_path.resolve()
    target_dir = (
        Path(tempfile.gettempdir())
        / f"nomi-{target_name}-target"
        / os.environ.get("PYTEST_XDIST_WORKER", "local")
    )
    result = subprocess.run(
        [
            cargo,
            "run",
            "--quiet",
            "--manifest-path",
            str(crate_dir / "Cargo.toml"),
            "--target-dir",
            str(target_dir),
            "--",
            command,
            str(source_path),
        ],
        cwd=crate_dir,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise SyntaxError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)
