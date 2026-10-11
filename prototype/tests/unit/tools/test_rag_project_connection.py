"""Client wiring, source selection and project navigation without an AI call."""

import json
from pathlib import Path
import sys
import tomllib
from types import SimpleNamespace

import pytest

from tools.rag_mcp.config import DEFAULT_CONFIG_PATH, ROOT, load_config
from tools.rag_mcp.index import build_and_save, iter_source_files
from tools.rag_mcp.mcp_server import NomiRagMcpServer
from tools.rag_mcp.setup import export_clients, server_command, smoke


def test_checkout_index_selects_targets_registries_and_runtime_without_private_config():
    config = load_config()
    source = next(item for item in config.sources if item.name == "nomi-codebase")
    selected = {
        path.relative_to(ROOT).as_posix() for path in iter_source_files(source, ROOT)
    }
    assert {
        "docs/design/targets/research/scientific_model.nomi",
        "config/design_passes.json",
        "config/primitive_composition.json",
        "web/runtime.js",
    } <= selected
    assert ".codex/config.toml" not in selected
    assert ".mcp.json" not in selected
    assert not any(path.startswith((".nomi/", "local/", "PLAY/")) for path in selected)


def test_design_packets_expose_owned_paths_and_never_execute_declared_commands():
    server = NomiRagMcpServer()
    result = server.call_tool("nomi_design_passes", {"query": "AI frameworks"})
    packet = result["structuredContent"]["packets"][0]
    assert packet["id"] == "language-coherence"
    assert "docs/design/ai_frameworks.md" in packet["canonical_updates"]
    assert "commands not executed" in result["structuredContent"]["scope"]
    assert (
        server.design_passes({"pass_id": "language-coherence"})["packets"][0] == packet
    )
    assert server.design_passes({"query": "unmatchedword"})["packets"] == []
    with pytest.raises(ValueError, match="unknown design pass"):
        server.design_passes({"pass_id": "missing"})


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        {"query": True},
        {"query": "x" * 4097},
        {"query": "AI", "pass_id": "language-coherence"},
        {"command": "pytest"},
    ],
)
def test_project_navigation_refuses_unbounded_or_execution_arguments(arguments):
    with pytest.raises(ValueError):
        NomiRagMcpServer().design_passes(arguments)


def test_project_navigation_cannot_bypass_source_selection(tmp_path, monkeypatch):
    config = tmp_path / "rag.json"
    config.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "name": "nomi-codebase",
                        "path": str(ROOT),
                        "include": ["config/design_passes.json"],
                    }
                ]
            }
        )
    )
    opened = []
    original = Path.read_text

    def record(path, *args, **kwargs):
        opened.append(path.resolve())
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", record)
    with pytest.raises(ValueError, match="artifact is not selected"):
        NomiRagMcpServer(str(config)).design_passes({})
    assert ROOT / "config/design_passes.json" in opened
    assert not any(path.is_relative_to(ROOT / "docs") for path in opened)


def test_project_navigation_does_not_open_registry_when_it_is_excluded(tmp_path):
    config = tmp_path / "rag.json"
    config.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "name": "nomi-codebase",
                        "path": str(ROOT),
                        "include": ["docs/**/*.md"],
                    }
                ]
            }
        )
    )
    with pytest.raises(ValueError, match="registry is not selected"):
        NomiRagMcpServer(str(config)).design_passes({})


def test_exported_clients_use_exact_interpreter_and_absolute_checkout_paths(tmp_path):
    directory = export_clients(DEFAULT_CONFIG_PATH, tmp_path)
    common = json.loads((directory / "stdio.json").read_text())["mcpServers"][
        "nomi-rag"
    ]
    codex = tomllib.loads((directory / "codex.toml").read_text())["mcp_servers"][
        "nomi-rag"
    ]
    opencode = json.loads((directory / "opencode.json").read_text())["mcp"]["nomi-rag"]
    assert common == codex
    assert [common["command"], *common["args"]] == server_command(DEFAULT_CONFIG_PATH)
    assert common["command"] == sys.executable
    assert all(Path(common["args"][index]).is_absolute() for index in (0, 2))
    assert opencode["command"] == server_command(DEFAULT_CONFIG_PATH)
    assert opencode["enabled"] is True


def test_real_stdio_exchange_works_outside_checkout_without_model_or_network(tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "example.nomi").write_text(
        "# named axes support local reasoning\nanswer = 42\n"
    )
    config = tmp_path / "rag.json"
    config.write_text(
        json.dumps(
            {"sources": [{"name": "notes", "path": "notes", "include": ["**/*.nomi"]}]}
        )
    )
    build_and_save(config)
    result = smoke(config, "named axes")
    assert result["status"] == "checked"
    assert result["exchanges"] == 10
    assert result["retrieval_results"] == 1
    assert "outside checkout" in result["transport"]


def test_empty_source_has_actionable_setup_failure(tmp_path):
    config = tmp_path / "rag.json"
    config.write_text('{"sources": []}')
    with pytest.raises(ValueError, match="no selected source files"):
        smoke(config)


@pytest.mark.parametrize(
    "bad", [None, [], "logging on stdout", {"jsonrpc": "2.0", "id": 1, "result": None}]
)
def test_smoke_refuses_malformed_server_output_without_a_traceback(
    tmp_path, monkeypatch, bad
):
    config = tmp_path / "rag.json"
    (tmp_path / "note.md").write_text("local context")
    config.write_text(
        json.dumps(
            {"sources": [{"name": "notes", "path": ".", "include": ["note.md"]}]}
        )
    )
    monkeypatch.setattr(
        "tools.rag_mcp.setup.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stderr="",
            stdout="\n".join(json.dumps(bad) for _ in range(10)),
        ),
    )
    with pytest.raises(ValueError, match="MCP smoke exchange failed"):
        smoke(config)


def test_mcp_annotations_distinguish_reads_from_derived_cache_writes():
    tools = {tool["name"]: tool for tool in NomiRagMcpServer().tools()}
    for name in ("rag_search", "rag_sources", "nomi_design_passes"):
        assert tools[name]["annotations"]["readOnlyHint"] is True
    assert tools["rag_rebuild"]["annotations"]["readOnlyHint"] is False
    assert tools["rag_rebuild"]["annotations"]["destructiveHint"] is False


def test_tracked_claude_project_wiring_names_checkout_server():
    config = json.loads((ROOT / ".mcp.json").read_text())
    assert config["mcpServers"]["nomi-rag"] == {
        "command": "python3",
        "args": ["-m", "tools.rag_mcp.mcp_server"],
    }
