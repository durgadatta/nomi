"""Small local retrieval index used by the Nomi MCP server.

This is intentionally dependency-light. It gives the project a working RAG
surface today while leaving clear replacement points for embeddings, vector
stores, PDF extraction, or richer source metadata later.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fnmatch import fnmatch
import json
import math
from pathlib import Path
import re
from typing import Iterable

from tools.rag_mcp.config import RagConfig, SourceConfig, load_config


TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".rst",
    ".py",
    ".lark",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".js",
    ".ts",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


@dataclass(frozen=True)
class DocumentChunk:
    source: str
    kind: str
    path: str
    chunk_id: int
    line_start: int
    line_end: int
    text: str
    score_boost: float = 1.0

    @property
    def ref(self) -> str:
        return f"{self.path}:{self.line_start}"


@dataclass(frozen=True)
class SearchResult:
    score: float
    chunk: DocumentChunk
    highlights: tuple[str, ...]
    snippet: str

    def as_dict(self) -> dict[str, object]:
        return {
            "score": round(self.score, 4),
            "source": self.chunk.source,
            "kind": self.chunk.kind,
            "path": self.chunk.path,
            "ref": self.chunk.ref,
            "line_start": self.chunk.line_start,
            "line_end": self.chunk.line_end,
            "highlights": list(self.highlights),
            "snippet": self.snippet,
        }


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]+", text.lower())
        if token not in STOPWORDS and len(token) > 1
    ]


def is_excluded(relative_path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch(relative_path, pattern) for pattern in patterns)


def iter_source_files(source: SourceConfig, root: Path) -> Iterable[Path]:
    if not source.path.exists():
        return

    seen: set[Path] = set()
    for pattern in source.include:
        for path in source.path.glob(pattern):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            relative_to_source = path.relative_to(source.path).as_posix()
            relative_to_root = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
            if is_excluded(relative_to_source, source.exclude) or is_excluded(relative_to_root, source.exclude):
                continue
            if path.suffix.lower() in TEXT_SUFFIXES:
                yield path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except UnicodeDecodeError:
            return None


def relative_display_path(path: Path, root: Path) -> str:
    if path.is_relative_to(root):
        return path.relative_to(root).as_posix()
    return str(path)


def score_boost_for_path(source: SourceConfig, display_path: str) -> float:
    boost = 1.0
    for pattern, value in source.path_boosts:
        if fnmatch(display_path, pattern):
            boost *= value
    return boost


def chunk_text(
    source: SourceConfig,
    path: Path,
    root: Path,
    *,
    max_chars: int = 1800,
    overlap_lines: int = 4,
) -> Iterable[DocumentChunk]:
    text = read_text(path)
    if not text:
        return

    lines = text.splitlines()
    display_path = relative_display_path(path, root)
    score_boost = score_boost_for_path(source, display_path)
    start = 0
    chunk_id = 0
    while start < len(lines):
        size = 0
        end = start
        while end < len(lines) and (size + len(lines[end]) + 1 <= max_chars or end == start):
            size += len(lines[end]) + 1
            end += 1

        chunk_lines = lines[start:end]
        yield DocumentChunk(
            source=source.name,
            kind=source.kind,
            path=display_path,
            chunk_id=chunk_id,
            line_start=start + 1,
            line_end=end,
            text="\n".join(chunk_lines).strip(),
            score_boost=score_boost,
        )

        chunk_id += 1
        if end >= len(lines):
            break
        start = max(end - overlap_lines, start + 1)


class RagIndex:
    def __init__(self, chunks: Iterable[DocumentChunk]):
        self.chunks = list(chunks)
        self._tokens = [tokenize(chunk.text) for chunk in self.chunks]
        self._document_frequency = self._count_document_frequency()
        self._total_chunks = max(len(self.chunks), 1)

    @classmethod
    def build(cls, config: RagConfig) -> "RagIndex":
        chunks = []
        for source in config.sources:
            for path in iter_source_files(source, config.root):
                chunks.extend(chunk_text(source, path, config.root))
        return cls(chunks)

    @classmethod
    def load(cls, path: str | Path) -> "RagIndex":
        with Path(path).open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        chunks = [DocumentChunk(**chunk) for chunk in raw.get("chunks", [])]
        return cls(chunks)

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "chunks": [asdict(chunk) for chunk in self.chunks]}
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def search(self, query: str, *, limit: int = 6, source: str | None = None) -> list[SearchResult]:
        query_terms = tokenize(query)
        if not query_terms:
            return []

        results: list[SearchResult] = []
        for chunk, chunk_tokens in zip(self.chunks, self._tokens):
            if source and chunk.source != source:
                continue
            score = self._score(query_terms, chunk_tokens) * chunk.score_boost
            if score <= 0:
                continue
            results.append(
                SearchResult(
                    score=score,
                    chunk=chunk,
                    highlights=find_highlights(chunk.text, query_terms),
                    snippet=find_snippet(chunk.text, chunk.line_start, query_terms),
                )
            )

        return sorted(results, key=lambda result: result.score, reverse=True)[:limit]

    def _count_document_frequency(self) -> dict[str, int]:
        frequency: dict[str, int] = {}
        for tokens in self._tokens:
            for token in set(tokens):
                frequency[token] = frequency.get(token, 0) + 1
        return frequency

    def _score(self, query_terms: list[str], chunk_tokens: list[str]) -> float:
        if not chunk_tokens:
            return 0.0

        counts: dict[str, int] = {}
        for token in chunk_tokens:
            counts[token] = counts.get(token, 0) + 1

        score = 0.0
        for term in query_terms:
            term_count = counts.get(term, 0)
            if term_count == 0:
                continue
            idf = math.log((self._total_chunks + 1) / (1 + self._document_frequency.get(term, 0))) + 1
            score += (1 + math.log(term_count)) * idf
        return score


def find_highlights(text: str, query_terms: list[str], *, limit: int = 3) -> tuple[str, ...]:
    lower_terms = set(query_terms)
    highlights = []
    for line in text.splitlines():
        tokens = set(tokenize(line))
        if tokens & lower_terms:
            highlights.append(line.strip())
        if len(highlights) >= limit:
            break
    return tuple(highlights)


def find_snippet(
    text: str,
    line_start: int,
    query_terms: list[str],
    *,
    context_lines: int = 2,
) -> str:
    lines = text.splitlines()
    lower_terms = set(query_terms)
    match_index = 0
    for index, line in enumerate(lines):
        if set(tokenize(line)) & lower_terms:
            match_index = index
            break

    start = max(match_index - context_lines, 0)
    end = min(match_index + context_lines + 1, len(lines))
    return "\n".join(
        f"{line_start + index}: {lines[index].rstrip()}"
        for index in range(start, end)
    )


def build_and_save(config_path: str | Path | None = None) -> RagIndex:
    config = load_config(config_path)
    index = RagIndex.build(config)
    index.save(config.index_path)
    return index
