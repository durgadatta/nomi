"""Command line helpers for the local Nomi RAG index."""

from __future__ import annotations

import argparse

from tools.rag_mcp.config import load_config
from tools.rag_mcp.index import RagIndex, build_and_save


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and query the local Nomi RAG index.")
    parser.add_argument("--config", default=None, help="Path to rag_sources.json.")

    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("build", help="Build the local retrieval index.")

    search = subcommands.add_parser("search", help="Search the local retrieval index.")
    search.add_argument("query", help="Query text.")
    search.add_argument("--limit", type=int, default=6, help="Maximum result count.")
    search.add_argument("--source", default=None, help="Optional source name filter.")

    args = parser.parse_args()

    if args.command == "build":
        config = load_config(args.config)
        index = build_and_save(args.config)
        print(f"Indexed {len(index.chunks)} chunks into {config.index_path}")
        return

    if args.command == "search":
        config = load_config(args.config)
        if config.index_path.exists():
            index = RagIndex.load(config.index_path)
        else:
            index = build_and_save(args.config)

        for result in index.search(args.query, limit=args.limit, source=args.source):
            print(f"{result.score:.2f} {result.chunk.source} {result.chunk.ref}")
            for highlight in result.highlights:
                print(f"  {highlight}")


if __name__ == "__main__":
    main()
