"""A non-numeric domain keeps its shape, obligations and rendering separate."""

import json
from pathlib import Path

import pytest

from tools.object_interface import (
    ContractError,
    Graph,
    Requirements,
    Vocabulary,
    load_document,
)
from tools.object_interface.__main__ import main
from tools.object_interface.backend import Backend
from tools.object_interface.documentary import document_backend, document_vocabulary
from tools.object_interface.documents import ValueContractError

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def graph():
    return Graph.from_document(
        load_document(EXAMPLE / "document.json"), document_vocabulary()
    )


def conditions(checked):
    return Requirements.from_document(
        load_document(EXAMPLE / "document_requirements.json"), checked
    )


def requirement(checked, path, rule="text.nonempty-v1", subject="draft"):
    return Requirements.from_document(
        {
            "version": 2,
            "graph": checked.context,
            "owner": "test",
            "revision": "v1",
            "requirements": [
                {"id": "needed", "rule": rule, "subject": subject, "path": path}
            ],
        },
        checked,
    )


EXPECTED = (
    "Research plan\n\nPurpose\n\nKeep meaning separate from execution.\n\n"
    "Next\n\nCompose contracts.\n\nCompare implementations.\n"
)


@pytest.mark.parametrize("profile", ["blocks", "stream"])
def test_two_renderers_preserve_the_same_owned_document_contract(profile):
    checked = graph()
    original = checked.document
    bound = (
        document_backend(checked.vocabulary, profile)
        .compile(checked)
        .require(conditions(checked))
        .bind(load_document(EXAMPLE / "document_bindings.json"))
    )
    result = bound.execute()
    assert result.values == {"published": EXPECTED, "paragraph_count": 3}
    assert result.receipt["requirement_evidence"]["status"] == "satisfied"
    assert checked.document == original
    assert conditions(checked).check()["status"] == "pending"


@pytest.mark.parametrize(
    "spec,expected,count",
    [
        ({"title": "", "sections": []}, "\n", 0),
        (
            {
                "title": "é\nΩ",
                "sections": [{"heading": "", "paragraphs": ["", "a\nb"]}],
            },
            "é\nΩ\n\n\n\n\n\na\nb\n",
            2,
        ),
        (
            {"title": " x ", "sections": [{"heading": "h", "paragraphs": []}]},
            " x \n\nh\n",
            0,
        ),
    ],
)
def test_renderers_preserve_empty_parts_whitespace_unicode_and_item_order(
    spec, expected, count
):
    checked = graph()
    for profile in ("blocks", "stream"):
        result = (
            document_backend(checked.vocabulary, profile)
            .compile(checked)
            .bind({"draft": spec})
            .execute()
        )
        assert result.values == {"published": expected, "paragraph_count": count}


def test_description_remains_passive_and_each_intermediate_is_selectable():
    checked = graph()
    assert checked.inspect("description")["operation"] == "document.spec.describe"
    backend = document_backend(checked.vocabulary)
    with pytest.raises(ContractError):
        backend.compile(checked, [checked.ref("description")])
    result = (
        backend.compile(checked, [checked.ref("title"), checked.ref("rendered")])
        .bind(load_document(EXAMPLE / "document_bindings.json"))
        .execute()
    )
    assert result.values == {"title": "Research plan", "rendered": EXPECTED}


def test_shared_representation_does_not_erase_rendered_nominal_family():
    checked = graph()
    with pytest.raises(ContractError):
        checked.compose("bad", "text.alias", {"target": checked.ref("rendered")})
    assert checked.compare("content", "published")["status"] == "equivalent"


def test_nested_conditions_distinguish_static_binding_and_missing_item_evidence():
    checked = graph()
    needed = conditions(checked)
    assert {r["status"] for r in needed.check()["requirements"]} == {"pending"}
    receipt = needed.check({"draft": {"title": "", "sections": []}})
    assert receipt["status"] == "refuted"
    assert receipt["requirements"][2]["path"] == ["sections", 0, "heading"]
    assert receipt["requirements"][2]["basis"].endswith("missing path")
    assert (
        needed.check(load_document(EXAMPLE / "document_bindings.json"))["status"]
        == "satisfied"
    )


def test_nested_literal_alias_evidence_needs_no_engine_and_no_trim():
    checked = graph().compose(
        "literal",
        "document.spec.literal",
        {},
        {
            "value": {"title": " ", "sections": []},
        },
    )
    checked = checked.compose(
        "aliased", "document.spec.alias", {"target": checked.ref("literal")}
    )
    assert (
        requirement(checked, ["title"], subject="aliased").check()["status"]
        == "satisfied"
    )
    assert (
        requirement(checked, ["sections"], "array.nonempty-v1", "aliased").check()[
            "status"
        ]
        == "refuted"
    )


@pytest.mark.parametrize(
    "path,rule",
    [
        (["unknown"], "text.nonempty-v1"),
        (["title", 0], "text.nonempty-v1"),
        (["sections", True, "heading"], "text.nonempty-v1"),
        (["sections", -1, "heading"], "text.nonempty-v1"),
        (["sections", 0, "paragraphs"], "text.nonempty-v1"),
        (["title"], "array.nonempty-v1"),
        (["title"], "user.asserted"),
        ("title", "text.nonempty-v1"),
    ],
)
def test_path_obligations_must_follow_declared_shape_and_predicate_kind(path, rule):
    with pytest.raises(ContractError):
        requirement(graph(), path, rule)


def test_deep_shape_errors_accumulate_before_predicates_or_callbacks():
    checked, calls = graph(), []
    backend = Backend(
        "observed",
        "v1",
        checked.vocabulary.fingerprint,
        {
            "document.title": lambda p, a: calls.append("called") or p["spec"]["title"],
        },
    )
    compiled = backend.compile(checked, [checked.ref("title")]).require(
        conditions(checked)
    )
    with pytest.raises(ValueContractError) as failure:
        compiled.bind({"draft": {"title": None, "sections": [{"paragraphs": [False]}]}})
    assert {tuple(e["path"]) for e in failure.value.report["errors"]} == {
        ("title",),
        ("sections", 0, "heading"),
        ("sections", 0, "paragraphs", 0),
    }
    with pytest.raises(ContractError, match="not satisfied"):
        compiled.bind({"draft": {"title": "", "sections": []}})
    assert calls == []


def test_computed_nested_conditions_never_execute_to_create_evidence():
    checked = graph()
    needed = requirement(checked, [], subject="title")
    assert (
        needed.check(load_document(EXAMPLE / "document_bindings.json"))["status"]
        == "pending"
    )
    with pytest.raises(ContractError, match="computed preconditions"):
        document_backend(checked.vocabulary).compile(
            checked, [checked.ref("title")]
        ).require(needed)


def test_nested_receipts_are_detached_context_bound_and_not_supplied_truth():
    checked = graph()
    needed = conditions(checked)
    bindings = load_document(EXAMPLE / "document_bindings.json")
    receipt = needed.check(bindings)
    assert needed.verify(receipt, bindings)["verdict"] == "satisfied"
    receipt["requirements"][0]["path"] = ["sections"]
    with pytest.raises(ContractError):
        needed.verify(receipt, bindings)
    original = needed.document
    original["requirements"][0]["path"].clear()
    assert needed.inspect("title_has_content")["path"] == ["title"]


def test_document_adapter_refuses_unreviewed_vocabulary_and_profiles():
    manifest = document_vocabulary().document
    manifest["revision"] = "v2"
    with pytest.raises(ContractError):
        document_backend(Vocabulary.from_document(manifest))
    with pytest.raises(ContractError):
        document_backend(document_vocabulary(), "unknown")


def test_document_cli_selects_adapter_and_named_outputs_explicitly(capsys):
    args = ["--vocabulary", str(ROOT / "config/document_interface.json")]
    source = str(EXAMPLE / "document.json")
    bindings = str(EXAMPLE / "document_bindings.json")
    assert (
        main(
            args
            + [
                "run",
                source,
                bindings,
                "--backend",
                "document-stream",
                "--output",
                "title",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["values"] == {"title": "Research plan"}
    assert main(args + ["run", source, bindings, "--backend", "python-exact-text"]) == 2
    assert '"refused"' in capsys.readouterr().err
    assert (
        main(
            args
            + ["compile", source, "--backend", "document-blocks", "--output", "missing"]
        )
        == 2
    )
    capsys.readouterr()
