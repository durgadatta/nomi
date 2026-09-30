"""Minimal stdio MCP server for Nomi RAG context.

The server intentionally implements only the JSON-RPC pieces needed for the
initial tools. It can be replaced with the official MCP Python SDK later without
changing the retrieval layer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import quote, unquote, urlparse

from tools.rag_mcp.config import load_config
from tools.rag_mcp.index import RagIndex, build_and_save, iter_source_files, read_text


SUPPORTED_PROTOCOL_VERSIONS = {"2024-11-05", "2025-06-18"}
DEFAULT_PROTOCOL_VERSION = "2025-06-18"


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
                return self.result(request_id, self.initialize_result(request.get("params", {})))
            if method == "notifications/initialized":
                return None
            if method == "tools/list":
                return self.result(request_id, {"tools": self.tools()})
            if method == "tools/call":
                params = request.get("params", {})
                return self.result(request_id, self.call_tool(params.get("name"), params.get("arguments", {})))
            if method == "resources/list":
                return self.result(request_id, {"resources": self.resources()})
            if method == "resources/read":
                params = request.get("params", {})
                return self.result(request_id, {"contents": [self.read_resource(params.get("uri", ""))]})
            if method == "resources/templates/list":
                return self.result(request_id, {"resourceTemplates": self.resource_templates()})
            if method == "prompts/list":
                return self.result(request_id, {"prompts": self.prompts()})
            if method == "prompts/get":
                params = request.get("params", {})
                return self.result(
                    request_id,
                    self.get_prompt(params.get("name"), params.get("arguments", {})),
                )
            if request_id is None:
                return None
            return self.error(request_id, -32601, f"Unknown method: {method}")
        except Exception as exc:  # Keep MCP failures visible to the client.
            return self.error(request_id, -32000, str(exc))

    def initialize_result(self, params: dict[str, Any]) -> dict[str, Any]:
        requested_version = params.get("protocolVersion")
        protocol_version = (
            requested_version
            if requested_version in SUPPORTED_PROTOCOL_VERSIONS
            else DEFAULT_PROTOCOL_VERSION
        )
        return {
            "protocolVersion": protocol_version,
            "serverInfo": {"name": "nomi-rag", "version": "0.1.0"},
            "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
        }

    def tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "rag_search",
                "title": "Search Nomi RAG",
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
                "outputSchema": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "score": {"type": "number"},
                                    "source": {"type": "string"},
                                    "kind": {"type": "string"},
                                    "path": {"type": "string"},
                                    "ref": {"type": "string"},
                                    "line_start": {"type": "integer"},
                                    "line_end": {"type": "integer"},
                                    "highlights": {"type": "array", "items": {"type": "string"}},
                                    "snippet": {"type": "string"},
                                },
                                "required": ["score", "source", "kind", "path", "ref", "snippet"],
                            },
                        }
                    },
                    "required": ["results"],
                },
            },
            {
                "name": "rag_sources",
                "title": "List RAG Sources",
                "description": "List configured retrieval sources and the local index path.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "rag_rebuild",
                "title": "Rebuild RAG Index",
                "description": "Rebuild the local retrieval index from configured sources.",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "rag_search":
            text, structured = self.search(arguments)
            return self.tool_content(text, structured)
        if name == "rag_sources":
            return self.tool_content(self.sources())
        if name == "rag_rebuild":
            self.index = build_and_save(self.config_path)
            return self.tool_content(f"Indexed {len(self.index.chunks)} chunks into {self.config.index_path}")
        raise ValueError(f"Unknown tool: {name}")

    def search(self, arguments: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        query = arguments["query"]
        limit = max(1, min(int(arguments.get("limit", 6)), 20))
        source = arguments.get("source")
        index = self.get_index()
        results = index.search(query, limit=limit, source=source)
        structured = {"results": [result.as_dict() for result in results]}
        if not results:
            return "No local RAG results found.", structured

        sections = []
        for result in results:
            lines = [
                f"{result.chunk.source} {result.chunk.ref}",
                f"score={result.score:.2f}",
            ]
            if result.snippet:
                lines.append(result.snippet)
            sections.append("\n".join(lines))
        return "\n\n".join(sections), structured

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

    def resources(self) -> list[dict[str, Any]]:
        sources = {source.name: source for source in self.config.sources}
        selected = {
            source.name: {path.resolve() for path in iter_source_files(source, self.config.root)}
            for source in self.config.sources
        }
        seen: set[tuple[str, str]] = set()
        resources = []
        for chunk in self.get_index().chunks:
            source = sources.get(chunk.source)
            path = Path(chunk.path)
            if not path.is_absolute():
                path = self.config.root / path
            path = path.resolve()
            if source is None or path not in selected[source.name]:
                continue
            key = (chunk.source, chunk.path)
            if key in seen:
                continue
            seen.add(key)
            resources.append(
                {
                    "uri": self.resource_uri(
                        chunk.source, path.relative_to(source.path.resolve()).as_posix()
                    ),
                    "name": chunk.path,
                    "title": chunk.path,
                    "description": f"{chunk.source} {chunk.kind}",
                    "mimeType": mime_type_for_path(chunk.path),
                }
            )
        return resources

    def resource_templates(self) -> list[dict[str, Any]]:
        return [
            {
                "uriTemplate": self.resource_uri_template(source.name),
                "name": f"{source.name}-file",
                "title": f"{source.name} indexed file",
                "description": f"Read a text file from the configured {source.name} RAG source.",
                "mimeType": "text/plain",
            }
            for source in self.config.sources
        ]

    def read_resource(self, uri: str) -> dict[str, Any]:
        source_name, display_path = self.parse_resource_uri(uri)
        source = next((item for item in self.config.sources if item.name == source_name), None)
        if source is None:
            raise ValueError(f"Unknown RAG source: {source_name}")

        path = self.resolve_resource_path(source.path, display_path)
        if not any(
            candidate.resolve() == path
            for candidate in iter_source_files(source, self.config.root)
        ):
            raise ValueError(f"RAG resource not selected by source configuration: {display_path}")
        text = read_text(path)
        if text is None:
            raise ValueError(f"RAG resource is not readable text: {display_path}")
        return {
            "uri": uri,
            "mimeType": mime_type_for_path(display_path),
            "text": text,
        }

    def prompts(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "rag_grounded_answer",
                "title": "RAG-Grounded Nomi Answer",
                "description": "Answer a Nomi question by searching local RAG first and citing repository paths.",
                "arguments": [
                    {
                        "name": "question",
                        "description": "The Nomi design, implementation, or tooling question to answer.",
                        "required": True,
                    }
                ],
            }
        ]

    def get_prompt(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name != "rag_grounded_answer":
            raise ValueError(f"Unknown prompt: {name}")

        question = str(arguments.get("question") or "").strip()
        if not question:
            raise ValueError("rag_grounded_answer requires a non-empty question argument.")

        return {
            "description": "Use local Nomi RAG as source discovery before answering.",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": (
                            "Answer this Nomi question using local repository evidence.\n\n"
                            f"Question: {question}\n\n"
                            "Workflow:\n"
                            "1. Call `rag_search` with a narrow phrase from the question.\n"
                            "2. Read any returned repository files directly before relying on them.\n"
                            "3. Cite concrete paths or refs in the answer.\n"
                            "4. If the active docs and implementation disagree, name the drift instead of "
                            "treating current behavior as final language authority."
                        ),
                    },
                }
            ],
        }

    @staticmethod
    def tool_content(text: str, structured: dict[str, Any] | None = None) -> dict[str, Any]:
        result = {"content": [{"type": "text", "text": text}], "isError": False}
        if structured is not None:
            result["structuredContent"] = structured
        return result

    @staticmethod
    def result(request_id: Any, value: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": value}

    @staticmethod
    def error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    @staticmethod
    def resource_uri(source: str, display_path: str) -> str:
        return f"nomi-rag://{quote(source, safe='')}/{quote(display_path, safe='')}"

    @staticmethod
    def resource_uri_template(source: str) -> str:
        return f"nomi-rag://{quote(source, safe='')}/{{path}}"

    @staticmethod
    def parse_resource_uri(uri: str) -> tuple[str, str]:
        parsed = urlparse(uri)
        if parsed.scheme != "nomi-rag" or not parsed.netloc or not parsed.path:
            raise ValueError(f"Invalid Nomi RAG resource URI: {uri}")
        return unquote(parsed.netloc), unquote(parsed.path.lstrip("/"))

    @staticmethod
    def resolve_resource_path(source_root: Path, display_path: str) -> Path:
        path = Path(display_path)
        if not path.is_absolute():
            path = source_root / path
        path = path.resolve()
        if not path.exists() or not path.is_file():
            raise ValueError(f"RAG resource not found: {display_path}")
        if not path.is_relative_to(source_root.resolve()):
            raise ValueError(f"RAG resource is outside configured source: {display_path}")
        return path


def mime_type_for_path(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".md":
        return "text/markdown"
    if suffix == ".json":
        return "application/json"
    if suffix in {".py", ".lark", ".toml", ".yaml", ".yml", ".js", ".ts"}:
        return "text/plain"
    return "text/plain"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Nomi RAG MCP stdio server.")
    parser.add_argument("--config", default=None, help="Path to rag_sources.json.")
    args = parser.parse_args()
    NomiRagMcpServer(args.config).serve()


if __name__ == "__main__":
    main()
