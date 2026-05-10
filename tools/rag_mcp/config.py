"""Configuration loading for the local Nomi RAG index."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT / "config" / "rag_sources.json"


@dataclass(frozen=True)
class SourceConfig:
    name: str
    kind: str
    path: Path
    include: tuple[str, ...] = field(default_factory=tuple)
    exclude: tuple[str, ...] = field(default_factory=tuple)


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

    with config_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    index_path = resolve_path(raw.get("index_path", ".nomi/rag_index.json"), project_root)
    sources = []
    for source in raw.get("sources", []):
        sources.append(
            SourceConfig(
                name=source["name"],
                kind=source.get("kind", "documents"),
                path=resolve_path(source["path"], project_root),
                include=tuple(source.get("include", ["**/*"])),
                exclude=tuple(source.get("exclude", [])),
            )
        )

    return RagConfig(root=project_root, index_path=index_path, sources=tuple(sources))
