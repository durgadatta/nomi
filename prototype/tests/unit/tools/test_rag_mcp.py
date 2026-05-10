from pathlib import Path

from tools.rag_mcp.config import RagConfig, SourceConfig
from tools.rag_mcp.index import RagIndex
from tools.rag_mcp.mcp_server import NomiRagMcpServer


def make_config(tmp_path: Path) -> RagConfig:
    docs = tmp_path / "docs"
    books = tmp_path / "Local_Programming_Books"
    docs.mkdir()
    books.mkdir()
    (docs / "language.md").write_text(
        "Binding constraints validate values at binding time.\n"
        "Yield to block models controlled resumable execution.\n",
        encoding="utf-8",
    )
    (books / "lambda.txt").write_text(
        "Lambda calculus treats functions and application as core primitives.\n",
        encoding="utf-8",
    )

    return RagConfig(
        root=tmp_path,
        index_path=tmp_path / ".nomi" / "rag_index.json",
        sources=(
            SourceConfig(
                name="nomi-codebase",
                kind="codebase",
                path=tmp_path,
                include=("docs/**/*.md",),
            ),
            SourceConfig(
                name="programming-books",
                kind="books",
                path=books,
                include=("**/*.txt",),
            ),
        ),
    )


def test_rag_index_searches_multiple_sources(tmp_path):
    config = make_config(tmp_path)
    index = RagIndex.build(config)

    code_results = index.search("binding constraints", source="nomi-codebase")
    book_results = index.search("lambda calculus", source="programming-books")

    assert code_results[0].chunk.path == "docs/language.md"
    assert code_results[0].chunk.source == "nomi-codebase"
    assert book_results[0].chunk.source == "programming-books"
    assert "Lambda calculus" in book_results[0].highlights[0]


def test_rag_index_round_trips_to_disk(tmp_path):
    config = make_config(tmp_path)
    index = RagIndex.build(config)

    index.save(config.index_path)
    loaded = RagIndex.load(config.index_path)

    assert loaded.search("resumable execution")[0].chunk.ref == "docs/language.md:1"


def test_mcp_server_lists_tools_and_sources(tmp_path):
    config_path = tmp_path / "rag_sources.json"
    books = tmp_path / "Local_Programming_Books"
    books.mkdir()
    config_path.write_text(
        """
        {
          "index_path": ".nomi/rag_index.json",
          "sources": [
            {
              "name": "programming-books",
              "kind": "books",
              "path": "Local_Programming_Books",
              "include": ["**/*.txt"],
              "exclude": []
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    server = NomiRagMcpServer(str(config_path))
    tools = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    sources = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "rag_sources", "arguments": {}},
        }
    )

    assert tools["result"]["tools"][0]["name"] == "rag_search"
    assert "programming-books" in sources["result"]["content"][0]["text"]
