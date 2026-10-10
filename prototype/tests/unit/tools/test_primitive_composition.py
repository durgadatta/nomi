"""Composition navigation cannot manufacture acceptance or silently lose targets."""

import copy

import pytest

from tools import primitive_composition as composition


def test_current_catalog_maps_all_target_files_and_preserves_open_gates():
    catalog = composition.load()
    report = composition.explain(catalog, "statistics")
    assert set(report["families"]) == {"value", "bind", "apply", "choose", "scope"}
    nodes = {node["id"]: node for layer in report["layers"] for node in layer["nodes"]}
    assert "numeric-profile" in nodes and "definition-proof" in nodes
    assert nodes["statistics"]["status"] == "experiment"
    assert (
        "missing" in nodes["statistics"]["law"].lower()
        or "mask" in nodes["statistics"]["law"].lower()
    )
    assert report["scope"].endswith("no semantic proof")
    composition.check_document(catalog, composition.DOCUMENT.read_text())


@pytest.mark.parametrize(
    "mutation",
    [
        lambda c: c.update(status="validated"),
        lambda c: c.update(version=True),
        lambda c: c["nodes"][0].update(status="target"),
        lambda c: c["nodes"][0].update(depends=["literal"]),
        lambda c: c["nodes"][6].update(depends=["missing"]),
        lambda c: c["nodes"][6].update(depends=["value", "value"]),
        lambda c: c["nodes"][6].update(depends=["binding"]),
        lambda c: c["nodes"][7].update(depends=["literal"]),
        lambda c: c["nodes"][6].update(gate=""),
        lambda c: c["nodes"][6].update(owner="docs/design/../research/README.md"),
        lambda c: c["nodes"][6].update(owner="/etc/passwd"),
        lambda c: c["nodes"][6].update(fixtures=["docs/design/targets/missing.nomi"]),
        lambda c: c["nodes"].append(copy.deepcopy(c["nodes"][0])),
    ],
)
def test_invalid_maps_cannot_claim_an_accepted_basis_or_hide_dependencies(mutation):
    catalog = composition.load()
    mutation(catalog)
    # The two directed-cycle cases need the opposite edge as well.
    if catalog["nodes"][6]["depends"] == ["binding"]:
        catalog["nodes"][7]["depends"] = ["literal"]
    if catalog["nodes"][7]["depends"] == ["literal"]:
        catalog["nodes"][6]["depends"] = ["binding"]
    with pytest.raises(composition.CompositionError):
        composition.validate(catalog)


def test_unmapped_target_navigation_fails_instead_of_reporting_full_coverage():
    catalog = composition.load()
    for node in catalog["nodes"]:
        node["fixtures"] = [
            f for f in node["fixtures"] if not f.endswith("/overall.nomi")
        ]
    with pytest.raises(composition.CompositionError, match="unmapped target"):
        composition.validate(catalog)


def test_owner_symlinks_cannot_escape_the_design_authority(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / "docs/design").mkdir(parents=True)
    (root / "docs/research").mkdir()
    foreign = root / "docs/research/reference.md"
    foreign.write_text("research evidence")
    (root / "docs/design/owner.md").symlink_to(foreign)
    monkeypatch.setattr(composition, "ROOT", root)
    with pytest.raises(composition.CompositionError, match="boundary"):
        composition._path("docs/design/owner.md", ".md", "docs/design")


def test_new_target_program_requires_a_declared_route(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    targets = root / "docs/design/targets"
    targets.mkdir(parents=True)
    (root / "docs/design/owner.md").write_text("design")
    (targets / "new_activity.nomi").write_text("# target-only")
    monkeypatch.setattr(composition, "ROOT", root)
    catalog = {
        "version": 1,
        "status": "designing",
        "nodes": [
            {
                "id": "value",
                "label": "Value",
                "kind": "family",
                "depends": [],
                "owner": "docs/design/owner.md",
                "law": "Explicit value meaning",
                "gate": "Unproven primitive model",
                "placement": "semantic-family",
                "status": "hypothesis",
                "fixtures": [],
            }
        ],
    }
    with pytest.raises(composition.CompositionError, match="new_activity"):
        composition.validate(catalog)


def test_stale_table_and_ignored_cli_selectors_are_refused(capsys):
    catalog = composition.load()
    document = composition.DOCUMENT.read_text()
    with pytest.raises(composition.CompositionError, match="stale"):
        composition.check_document(
            catalog, document.replace("Candidate root", "Accepted root", 1)
        )
    assert composition.main(["check", "statistics"]) == 2
    assert "only show" in capsys.readouterr().err
    assert composition.main(["show", "unknown"]) == 2
    assert "unknown composition" in capsys.readouterr().err


def test_duplicate_json_and_large_catalog_are_refused(tmp_path):
    artifact = tmp_path / "catalog.json"
    artifact.write_text('{"version":1,"version":2}')
    with pytest.raises(composition.CompositionError):
        composition.load(artifact)
    artifact.write_bytes(b" " * 1_000_001)
    with pytest.raises(composition.CompositionError, match="byte budget"):
        composition.load(artifact)
