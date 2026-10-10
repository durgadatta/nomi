"""Configuration loading for the local Nomi RAG index."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT / "config" / "rag_sources.json"


class RagConfigError(ValueError):
    """Configuration cannot be used; no indexing should begin."""


@dataclass(frozen=True)
class SourceConfig:
    name: str
    kind: str
    path: Path
    include: tuple[str, ...] = field(default_factory=tuple)
    exclude: tuple[str, ...] = field(default_factory=tuple)
    path_boosts: tuple[tuple[str, float], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RagConfig:
    root: Path
    index_path: Path
    sources: tuple[SourceConfig, ...]


def resolve_path(path: str | Path, root: Path) -> Path:
    value = Path(path).expanduser()
    if not value.is_absolute():
        value = root / value
    return value.resolve()


def load_config(path: str | Path | None = None, root: Path | None = None) -> RagConfig:
    config_path = resolve_path(path or DEFAULT_CONFIG_PATH, root or ROOT)
    if root:
        project_root = root.resolve()
    elif config_path == DEFAULT_CONFIG_PATH:
        project_root = ROOT
    else:
        project_root = config_path.parent.resolve()

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as error:
        raise RagConfigError(
            f"RAG configuration not found: {config_path}. "
            "Provide --config /absolute/path/to/rag_sources.json. "
            "The default config belongs to the Nomi checkout and is not shipped in the wheel."
        ) from error
    except json.JSONDecodeError as error:
        raise RagConfigError(
            f"Invalid JSON in RAG configuration {config_path} at line {error.lineno}, column {error.colno}."
        ) from error

    if not isinstance(raw, dict) or not isinstance(raw.get("sources", []), list):
        raise RagConfigError(f"Invalid RAG configuration {config_path}: expected an object with a sources list.")
    index_value = raw.get("index_path", ".nomi/rag_index.json")
    if not isinstance(index_value, str) or not index_value.strip():
        raise RagConfigError(f"Invalid RAG configuration {config_path}: index_path must be nonempty text.")
    for source in raw.get("sources", []):
        if not isinstance(source, dict) or not all(
            isinstance(source.get(key), str) and source[key].strip() for key in ("name", "path")
        ):
            raise RagConfigError(f"Invalid RAG configuration {config_path}: each source needs a text name and path.")
        for key in ("include", "exclude"):
            if key in source and (
                not isinstance(source[key], list) or not all(isinstance(item, str) for item in source[key])
            ):
                raise RagConfigError(f"Invalid RAG configuration {config_path}: {key} must be a list of text patterns.")
        boosts = source.get("path_boosts", [])
        if not isinstance(boosts, list) or not all(
            isinstance(boost, dict) and isinstance(boost.get("pattern"), str)
            and isinstance(boost.get("boost"), (int, float))
            for boost in boosts
        ):
            raise RagConfigError(f"Invalid RAG configuration {config_path}: path_boosts need text patterns and numeric boosts.")

    index_path = resolve_path(index_value, project_root)
    sources = []
    for source in raw.get("sources", []):
        sources.append(
            SourceConfig(
                name=source["name"],
                kind=source.get("kind", "documents"),
                path=resolve_path(source["path"], project_root),
                include=tuple(source.get("include", ["**/*"])),
                exclude=tuple(source.get("exclude", [])),
                path_boosts=tuple(
                    (boost["pattern"], float(boost["boost"]))
                    for boost in source.get("path_boosts", [])
                ),
            )
        )

    return RagConfig(root=project_root, index_path=index_path, sources=tuple(sources))
