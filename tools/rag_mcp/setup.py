"""Build local retrieval, export client configuration and smoke-test stdio MCP."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from tools.rag_mcp.config import DEFAULT_CONFIG_PATH, ROOT, load_config
from tools.rag_mcp.index import build_and_save, iter_source_files
from tools.rag_mcp.mcp_server import NomiRagMcpServer


def server_command(config_path):
    return [
        sys.executable,
        str(ROOT / "tools/rag_mcp/launcher.py"),
        "--config",
        str(Path(config_path).resolve()),
    ]


def export_clients(config_path, directory):
    command = server_command(config_path)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    common = {"mcpServers": {"nomi-rag": {"command": command[0], "args": command[1:]}}}
    opencode = {
        "mcp": {"nomi-rag": {"type": "local", "command": command, "enabled": True}}
    }
    codex = (
        "[mcp_servers.nomi-rag]\ncommand = "
        + json.dumps(command[0])
        + "\nargs = "
        + json.dumps(command[1:])
        + "\n"
    )
    for filename, content in [
        ("stdio.json", json.dumps(common, indent=2) + "\n"),
        ("opencode.json", json.dumps(opencode, indent=2) + "\n"),
        ("codex.toml", codex),
    ]:
        (directory / filename).write_text(content, encoding="utf-8")
    return directory


def smoke(config_path, query="AI framework named axes"):
    config = load_config(config_path)
    selected = next(
        (
            (source, path)
            for source in config.sources
            for path in iter_source_files(source, config.root)
        ),
        None,
    )
    if selected is None:
        raise ValueError(
            "no selected source files; configure repository/docs before connecting MCP"
        )
    source, path = selected
    uri = NomiRagMcpServer.resource_uri(
        source.name, path.resolve().relative_to(source.path.resolve()).as_posix()
    )
    operations = [
        (
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "nomi-setup-smoke", "version": "1"},
            },
        ),
        ("ping", {}),
        ("tools/list", {}),
        ("tools/call", {"name": "rag_sources", "arguments": {}}),
        (
            "tools/call",
            {"name": "rag_search", "arguments": {"query": query, "limit": 3}},
        ),
        ("resources/templates/list", {}),
        ("resources/list", {}),
        ("resources/read", {"uri": uri}),
        ("prompts/list", {}),
        (
            "prompts/get",
            {"name": "rag_grounded_answer", "arguments": {"question": query}},
        ),
    ]
    project = next(
        (item for item in config.sources if item.name == "nomi-codebase"), None
    )
    if project and any(
        path.resolve() == (project.path / "config/design_passes.json").resolve()
        for path in iter_source_files(project, config.root)
    ):
        operations.append(
            ("tools/call", {"name": "nomi_design_passes", "arguments": {}})
        )
    frames = []
    for index, (method, params) in enumerate(operations, start=1):
        frames.append(
            {"jsonrpc": "2.0", "id": index, "method": method, "params": params}
        )
        if index == 1:
            frames.append({"jsonrpc": "2.0", "method": "notifications/initialized"})
    with tempfile.TemporaryDirectory(prefix="nomi-mcp-client-") as outside:
        process = subprocess.run(
            server_command(config_path),
            cwd=outside,
            input="".join(json.dumps(frame) + "\n" for frame in frames),
            text=True,
            capture_output=True,
            timeout=30,
        )
    if process.returncode:
        raise ValueError("MCP process failed: " + process.stderr.strip())
    replies = [json.loads(line) for line in process.stdout.splitlines()]
    if len(replies) != len(operations) or any(
        type(reply) is not dict
        or reply.get("jsonrpc") != "2.0"
        or reply.get("id") != index
        or "error" in reply
        or "result" not in reply
        or type(reply["result"]) is not dict
        or reply["result"].get("isError") is True
        for index, reply in enumerate(replies, start=1)
    ):
        raise ValueError(
            "MCP smoke exchange failed or stdout contains non-protocol output"
        )
    try:
        tools = [tool["name"] for tool in replies[2]["result"]["tools"]]
        protocol = replies[0]["result"]["protocolVersion"]
        contents = replies[7]["result"]["contents"]
        results = replies[4]["result"]["structuredContent"]["results"]
        if type(results) is not list or type(contents) is not list:
            raise ValueError("invalid MCP resource/search reply")
    except (KeyError, TypeError) as error:
        raise ValueError("missing MCP tool/resource/search reply fields") from error
    if not {"rag_search", "rag_sources", "rag_rebuild", "nomi_design_passes"} <= set(
        tools
    ):
        raise ValueError("missing MCP tool surface")
    if protocol != "2025-06-18" or not contents:
        raise ValueError("MCP initialization/resource read failed")
    return {
        "status": "checked",
        "transport": "stdio subprocess outside checkout",
        "exchanges": len(replies),
        "tools": tools,
        "retrieval_results": len(results),
        "scope": "bounded protocol smoke; not full MCP/client conformance",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument(
        "--check",
        action="store_true",
        help="Smoke-test without rebuilding or exporting configuration.",
    )
    args = parser.parse_args()
    try:
        config_path = str(Path(args.config).resolve())
        if not args.check:
            index = build_and_save(config_path)
            directory = export_clients(config_path, ROOT / ".nomi/mcp")
            print(f"Indexed {len(index.chunks)} chunks; client snippets: {directory}")
        print(json.dumps(smoke(config_path), indent=2))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        parser.exit(2, f"nomi-rag-setup: {error}\n")


if __name__ == "__main__":
    main()
