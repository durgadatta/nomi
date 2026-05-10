"""Minimal stdio MCP server for Nomi RAG context.

The server intentionally implements only the JSON-RPC pieces needed for the
initial tools. It can be replaced with the official MCP Python SDK later without
changing the retrieval layer.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from tools.rag_mcp.config import load_config
from tools.rag_mcp.index import RagIndex, build_and_save


class NomiRagMcpServer:
    def __init__(self, config_path: str | None = None):
        self.config_path = config_path
        self.config = load_config(config_path)
        self.index: RagIndex | None = None

    def serve(self) -> None:
        for line in sys.stdin:
            if not line.strip():
                continue
            request = json.loads(line)
            response = self.handle(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

    def handle(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        request_id = request.get("id")

        try:
            if method == "initialize":
                return self.result(request_id, self.initialize_result())
            if method == "notifications/initialized":
                return None
            if method == "tools/list":
                return self.result(request_id, {"tools": self.tools()})
            if method == "tools/call":
                params = request.get("params", {})
                return self.result(request_id, self.call_tool(params.get("name"), params.get("arguments", {})))
            if request_id is None:
                return None
            return self.error(request_id, -32601, f"Unknown method: {method}")
        except Exception as exc:  # Keep MCP failures visible to the client.
            return self.error(request_id, -32000, str(exc))

    def initialize_result(self) -> dict[str, Any]:
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "nomi-rag", "version": "0.1.0"},
            "capabilities": {"tools": {}},
        }

    def tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "rag_search",
                "description": "Search Nomi code/docs plus the configured programming books folder.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "default": 6},
                        "source": {"type": "string", "description": "Optional source name, e.g. nomi-codebase."},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "rag_sources",
                "description": "List configured retrieval sources and the local index path.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "rag_rebuild",
                "description": "Rebuild the local retrieval index from configured sources.",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "rag_search":
            return self.tool_content(self.search(arguments))
        if name == "rag_sources":
            return self.tool_content(self.sources())
        if name == "rag_rebuild":
            self.index = build_and_save(self.config_path)
            return self.tool_content(f"Indexed {len(self.index.chunks)} chunks into {self.config.index_path}")
        raise ValueError(f"Unknown tool: {name}")

    def search(self, arguments: dict[str, Any]) -> str:
        query = arguments["query"]
        limit = int(arguments.get("limit", 6))
        source = arguments.get("source")
        index = self.get_index()
        results = index.search(query, limit=limit, source=source)
        if not results:
            return "No local RAG results found."

        sections = []
        for result in results:
            lines = [
                f"{result.chunk.source} {result.chunk.ref}",
                f"score={result.score:.2f}",
            ]
            if result.highlights:
                lines.extend(f"- {highlight}" for highlight in result.highlights)
            sections.append("\n".join(lines))
        return "\n\n".join(sections)

    def sources(self) -> str:
        lines = [f"index: {self.config.index_path}"]
        for source in self.config.sources:
            status = "present" if source.path.exists() else "missing"
            lines.append(f"- {source.name} ({source.kind}, {status}): {source.path}")
        return "\n".join(lines)

    def get_index(self) -> RagIndex:
        if self.index is not None:
            return self.index
        if self.config.index_path.exists():
            self.index = RagIndex.load(self.config.index_path)
        else:
            self.index = build_and_save(self.config_path)
        return self.index

    @staticmethod
    def tool_content(text: str) -> dict[str, Any]:
        return {"content": [{"type": "text", "text": text}]}

    @staticmethod
    def result(request_id: Any, value: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": value}

    @staticmethod
    def error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Nomi RAG MCP stdio server.")
    parser.add_argument("--config", default=None, help="Path to rag_sources.json.")
    args = parser.parse_args()
    NomiRagMcpServer(args.config).serve()


if __name__ == "__main__":
    main()
