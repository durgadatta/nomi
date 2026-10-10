#!/usr/bin/env python3
"""Check local file destinations in Nomi's user-facing Markdown documentation.

This is an offline file-link check, not a Markdown renderer, anchor validator,
or remote URL monitor. Code examples are ignored. The repository uses inline
links; reference-style link definitions are also supported.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = r'(<[^>\n]+>|(?:\\.|[^\s)\\])+)'
INLINE_LINK = re.compile(r'!?\[[^\]\n]*\]\(' + DESTINATION + r'(?:\s+"[^"]*")?\)')
REFERENCE_LINK = re.compile(r'^\s{0,3}\[[^\]]+\]:\s*' + DESTINATION)
INLINE_CODE = re.compile(r'(`+).*?\1')
FENCE = re.compile(r'^\s{0,3}(`{3,}|~{3,})')


def default_documents(root: Path = ROOT) -> list[Path]:
    return sorted({
        root / "README.md", root / "CHANGELOG.md",
        *root.glob("docs/**/*.md"),
        root / "tools/jupyter/README.md", root / "tools/vscode/nomi/README.md",
    })


def local_links(source: str):
    fence = None
    for number, line in enumerate(source.splitlines(), 1):
        marker = FENCE.match(line)
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        line = INLINE_CODE.sub("", line)
        matches = list(INLINE_LINK.finditer(line))
        definition = REFERENCE_LINK.match(line)
        if definition:
            matches.append(definition)
        for match in matches:
            destination = match[1].strip("<>")
            destination = re.sub(r'\\([\\() ])', r'\1', destination)
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            yield number, unquote(parsed.path)


def check_documents(documents: list[Path], root: Path = ROOT) -> tuple[int, list[str]]:
    checked = 0
    errors = []
    for document in documents:
        try:
            source = document.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"{document}: cannot read document: {error}")
            continue
        for line, destination in local_links(source):
            checked += 1
            target = root / destination.lstrip("/") if destination.startswith("/") else document.parent / destination
            if not target.exists():
                errors.append(f"{document}:{line}: missing local destination: {destination}")
    return checked, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("documents", nargs="*", type=Path, help="Markdown files to check (default: root, docs, Jupyter and VS Code guides)")
    args = parser.parse_args(argv)
    documents = args.documents or default_documents()
    checked, errors = check_documents(documents)
    for error in errors:
        print(error)
    if errors:
        return 1
    print(f"Checked {checked} local file links across {len(documents)} documents; no missing destinations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
