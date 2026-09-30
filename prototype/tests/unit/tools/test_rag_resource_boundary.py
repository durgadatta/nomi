import json

import pytest

from tools.rag_mcp.index import iter_source_files
from tools.rag_mcp.mcp_server import NomiRagMcpServer


@pytest.fixture
def server(tmp_path):
    project = tmp_path / "project"
    docs = project / "docs"
    docs.mkdir(parents=True)
    (docs / "guide.md").write_text("allowed guide")
    (docs / "private.md").write_text("excluded note")
    (project / "unselected.txt").write_text("not included")
    outside = tmp_path / "outside.md"
    outside.write_text("outside source")
    (docs / "external.md").symlink_to(outside)
    (docs / "alias.md").symlink_to(docs / "private.md")
    config = tmp_path / "rag.json"
    config.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "name": "project",
                        "path": "project",
                        "include": ["docs/**/*.md"],
                        "exclude": ["docs/private.md"],
                    }
                ],
            }
        )
    )
    return NomiRagMcpServer(str(config))


def test_subfolder_source_resources_round_trip(server):
    resources = server.resources()
    guide = next(item for item in resources if item["name"].endswith("guide.md"))
    assert server.read_resource(guide["uri"])["text"] == "allowed guide"


@pytest.mark.parametrize(
    "path",
    [
        "docs/private.md",
        "unselected.txt",
        "docs/alias.md",
        "docs/external.md",
        "../outside.md",
    ],
)
def test_resource_reads_cannot_bypass_source_selection(server, path):
    uri = server.resource_uri("project", path)
    with pytest.raises(ValueError, match="(outside configured source|not selected)"):
        server.read_resource(uri)


def test_index_and_resources_ignore_external_and_excluded_symlink_targets(server):
    source = server.config.sources[0]
    paths = list(iter_source_files(source, server.config.root))
    assert [path.name for path in paths] == ["guide.md"]
    assert len(server.resources()) == 1


def test_declared_source_outside_config_root_is_still_readable(tmp_path):
    books = tmp_path / "books"
    books.mkdir()
    (books / "guide.md").write_text("book content")
    settings = tmp_path / "settings"
    settings.mkdir()
    config = settings / "rag.json"
    config.write_text(
        json.dumps(
            {"sources": [{"name": "books", "path": str(books), "include": ["*.md"]}]}
        )
    )
    server = NomiRagMcpServer(str(config))
    resource = server.resources()[0]
    assert server.read_resource(resource["uri"])["text"] == "book content"
