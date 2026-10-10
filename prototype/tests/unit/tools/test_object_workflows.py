"""Multi-output reuse preserves identities, contracts and independent evidence."""

from pathlib import Path

import pytest

from tools.object_interface import (
    ContractError,
    Graph,
    Requirements,
    Workflow,
    Vocabulary,
    load_document,
)
from tools.object_interface.examples import lab_vocabulary, python_backend
from tools.object_interface.backend import Backend
from tools.object_interface.documentary import document_backend, document_vocabulary
from tools.object_replay import replay, replay_requirements

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def workflow():
    return Workflow.from_document(
        load_document(EXAMPLE / "workflow.json"), lab_vocabulary()
    )


def graph():
    return Graph.from_document(
        {
            "version": 1,
            "vocabulary": lab_vocabulary().fingerprint,
            "objects": [
                {
                    "id": "left_quantity",
                    "op": "exact.input",
                    "ports": {},
                    "attributes": {},
                },
                {
                    "id": "right_quantity",
                    "op": "exact.input",
                    "ports": {},
                    "attributes": {},
                },
                {"id": "left_name", "op": "text.input", "ports": {}, "attributes": {}},
                {"id": "right_name", "op": "text.input", "ports": {}, "attributes": {}},
            ],
            "outputs": ["left_quantity"],
        },
        lab_vocabulary(),
    )


def arguments(checked, side="left"):
    return {
        "quantity": checked.ref(side + "_quantity"),
        "name": checked.ref(side + "_name"),
    }


def pair():
    checked = graph()
    left = workflow().compose(checked, "left", arguments(checked))
    right = workflow().compose(left, "right", arguments(left.graph, "right"))
    return left, right


def selected(instance):
    return [
        instance.graph.ref(side + "." + suffix)
        for side in ("left", "right")
        for suffix in ("squared", "published")
    ]


BINDINGS = {
    "left_quantity": 3,
    "right_quantity": 4,
    "left_name": "Ada",
    "right_name": "Bo",
}


def test_one_workflow_expands_twice_without_aliasing_distinct_inputs():
    original = graph()
    before = original.document
    left = workflow().compose(original, "left", arguments(original))
    right = workflow().compose(left, "right", arguments(left.graph, "right"))
    assert original.document == before
    assert right.graph.compare("left.squared", "right.squared")["status"] == "unknown"
    assert right.graph.inspect("right.document")["ports"]["body"] == ["right.greeting"]
    result = (
        right.compile(python_backend(right.graph.vocabulary), selected(right))
        .bind(BINDINGS)
        .execute()
    )
    assert result.values == {
        "left.squared": 9,
        "left.published": "Hello, Ada",
        "right.squared": 16,
        "right.published": "Hello, Bo",
    }
    assert right.inspect()["realization"] == "unbound"
    assert left.requirements.check()["status"] == "pending"


def test_explicit_argument_sharing_is_distinct_from_implicit_input_aliasing():
    checked = graph()
    left = workflow().compose(checked, "left", arguments(checked))
    right = workflow().compose(left, "right", arguments(left.graph))
    assert (
        right.graph.compare("left.squared", "right.squared")["status"] == "equivalent"
    )
    assert right.graph.compare("left.document", "right.document")["status"] == "unknown"
    assert (
        replay(
            right.graph.vocabulary.document,
            right.graph.document,
            right.graph.compare("left.squared", "right.squared"),
        )["status"]
        == "verified"
    )


def test_carried_conditions_from_both_instances_gate_before_any_callback():
    _, combined = pair()
    ids = {r["id"] for r in combined.requirements.document["requirements"]}
    assert ids == {
        "left.positive_quantity",
        "left.name_has_content",
        "right.positive_quantity",
        "right.name_has_content",
    }
    compiled = combined.compile(
        python_backend(combined.graph.vocabulary), selected(combined)
    )
    for invalid in ({**BINDINGS, "left_quantity": 0}, {**BINDINGS, "right_name": ""}):
        with pytest.raises(ContractError, match="not satisfied"):
            compiled.bind(invalid)
    assert len(compiled.inspect()["requirements"]["requirements"]) == 4


def test_expanded_artifacts_restore_through_existing_loaders_and_independent_replay():
    _, instance = pair()
    document = instance.document
    restored = Graph.from_document(document["graph"], lab_vocabulary())
    required = Requirements.from_document(document["requirements"], restored)
    receipt = required.check(BINDINGS)
    assert (
        replay_requirements(
            restored.vocabulary.document,
            restored.document,
            required.document,
            receipt,
            BINDINGS,
        )["verdict"]
        == "satisfied"
    )
    result = (
        python_backend(restored.vocabulary)
        .compile(restored, [restored.ref(r.id) for r in selected(instance)])
        .require(required)
        .bind(BINDINGS)
        .execute()
    )
    assert result.get(restored.ref("right.squared")) == 16
    document["inspection"]["components"][0]["inputs"].clear()
    assert instance.inspect()["components"][0]["inputs"]


def test_outputs_and_source_condition_provenance_remain_inspectable():
    _, instance = pair()
    assert instance.outputs["square"].id == "right.squared"
    assert instance.outputs["greeting"].id == "right.published"
    components = instance.inspect()["components"]
    assert [c["namespace"] for c in components] == ["left", "right"]
    assert components[0]["workflow"] == workflow().context
    assert components[0]["requirement_source"]["owner"] == "example.input-contracts"
    detached = instance.outputs
    detached.clear()
    assert len(instance.outputs) == 2


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d.update(version=True),
        lambda d: d.update(inputs={"quantity": "quantity"}),
        lambda d: d.update(
            inputs={"quantity": "quantity", "again": "quantity", "name": "name"}
        ),
        lambda d: d.update(inputs={"quantity": "squared", "name": "name"}),
        lambda d: d.update(outputs={"square": "quantity"}),
        lambda d: d.update(outputs={}),
        lambda d: d.update(engine="discovered"),
        lambda d: d["requirements"].update(graph="stale"),
    ],
)
def test_invalid_template_interfaces_and_stale_requirements_are_refused(change):
    document = workflow().document
    change(document)
    with pytest.raises(ContractError):
        Workflow.from_document(document, lab_vocabulary())


def test_wrong_nominal_arguments_foreign_revisions_and_values_are_refused():
    checked, template = graph(), workflow()
    for supplied in (
        {"quantity": checked.ref("left_name"), "name": checked.ref("left_name")},
        arguments(graph()),
        {"quantity": 3, "name": "Ada"},
        {},
    ):
        with pytest.raises(ContractError):
            template.compose(checked, "one", supplied)


def test_namespace_collisions_and_old_reference_contexts_are_refused_atomically():
    checked = graph()
    first = workflow().compose(checked, "one", arguments(checked))
    original = first.document
    with pytest.raises(ContractError, match="already instantiated"):
        workflow().compose(first, "one", arguments(first.graph))
    with pytest.raises(ContractError, match="collision"):
        workflow().compose(first.graph, "one", arguments(first.graph))
    with pytest.raises(ContractError, match="exact graph"):
        workflow().compose(first, "two", arguments(checked))
    with pytest.raises(ContractError):
        workflow().compose(first, "x" * 128, arguments(first.graph))
    assert first.document == original


def test_projecting_away_a_carried_condition_requires_an_explicit_decision():
    _, instance = pair()
    with pytest.raises(ContractError, match="outside selected realization"):
        instance.compile(
            python_backend(instance.graph.vocabulary), [instance.outputs["square"]]
        )


def test_workflow_conditions_on_computed_arguments_stay_pending_and_unenforceable():
    checked = graph()
    checked = checked.compose(
        "calculated", "exact.double", {"value": checked.ref("left_quantity")}
    )
    supplied = arguments(checked)
    supplied["quantity"] = checked.ref("calculated")
    instance = workflow().compose(checked, "one", supplied)
    assert (
        instance.requirements.check({"left_quantity": 3, "left_name": "Ada"})["status"]
        == "pending"
    )
    with pytest.raises(ContractError, match="computed preconditions"):
        instance.compile(python_backend(instance.graph.vocabulary))


def test_no_new_value_codec_or_callback_is_needed_for_passive_multi_output_reuse():
    template = workflow()
    document = template.document
    document["requirements"] = None
    passive = Workflow.from_document(document, lab_vocabulary())
    checked = graph()
    instance = passive.compose(checked, "one", arguments(checked))
    assert instance.requirements is None
    assert instance.graph.check()["status"] == "composition-checked"
    with pytest.raises(AttributeError):
        template._context = "mutated"
    with pytest.raises(AttributeError):
        instance._graph = checked


def test_composition_checking_and_compilation_never_invoke_an_engine():
    checked, calls = graph(), []
    instance = workflow().compose(checked, "one", arguments(checked))
    backend = Backend(
        "observed",
        "v1",
        checked.vocabulary.fingerprint,
        {
            "exact.multiply": lambda p, a: (
                calls.append("multiply") or p["left"] * p["right"]
            ),
            "text.concat": lambda p, a: (
                calls.append("concat") or p["left"] + p["right"]
            ),
        },
    )
    compiled = instance.compile(backend, list(instance.outputs.values()))
    assert instance.requirements.check()["status"] == "pending"
    with pytest.raises(ContractError):
        compiled.bind({"left_quantity": 0, "left_name": "Ada"})
    bound = compiled.bind({"left_quantity": 3, "left_name": "Ada"})
    assert calls == []
    assert bound.execute().get(instance.outputs["square"]) == 9
    assert set(calls) == {"multiply", "concat"}


def test_documentary_workflow_preserves_nested_conditions_and_nominal_outputs():
    vocabulary = document_vocabulary()
    template = Workflow.from_document(
        {
            "version": 1,
            "id": "document",
            "revision": "v1",
            "graph": load_document(EXAMPLE / "document.json"),
            "inputs": {"draft": "draft"},
            "outputs": {"content": "published", "count": "paragraph_count"},
            "requirements": load_document(EXAMPLE / "document_requirements.json"),
        },
        vocabulary,
    )
    checked = Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": [
                {
                    "id": "draft",
                    "op": "document.spec.input",
                    "ports": {},
                    "attributes": {},
                }
            ],
            "outputs": ["draft"],
        },
        vocabulary,
    )
    instance = template.compose(checked, "report", {"draft": checked.ref("draft")})
    bindings = load_document(EXAMPLE / "document_bindings.json")
    result = (
        instance.compile(document_backend(vocabulary), list(instance.outputs.values()))
        .bind(bindings)
        .execute()
    )
    assert result.get(instance.outputs["count"]) == 3
    assert instance.requirements.inspect("report.first_heading_has_content")[
        "path"
    ] == ["sections", 0, "heading"]
    receipt = instance.requirements.check(bindings)
    assert (
        replay_requirements(
            vocabulary.document,
            instance.graph.document,
            instance.requirements.document,
            receipt,
            bindings,
        )["verdict"]
        == "satisfied"
    )
    with pytest.raises(ContractError, match="same checked vocabulary"):
        workflow().compose(checked, "bad", {})


def test_pass_through_parameters_and_duplicate_export_names_reuse_references_explicitly():
    checked = graph()
    source = Graph.from_document(
        {
            "version": 1,
            "vocabulary": lab_vocabulary().fingerprint,
            "objects": [
                {"id": "source", "op": "exact.input", "ports": {}, "attributes": {}}
            ],
            "outputs": ["source"],
        },
        lab_vocabulary(),
    )
    template = Workflow.from_document(
        {
            "version": 1,
            "id": "pass-through",
            "revision": "v1",
            "graph": source.document,
            "inputs": {"value": "source"},
            "outputs": {"first": "source", "second": "source"},
            "requirements": None,
        },
        lab_vocabulary(),
    )
    instance = template.compose(checked, "one", {"value": checked.ref("left_quantity")})
    assert instance.graph.document == checked.document
    assert (
        instance.outputs["first"].id == instance.outputs["second"].id == "left_quantity"
    )
    with pytest.raises(ContractError, match="already instantiated"):
        template.compose(
            instance, "one", {"value": instance.graph.ref("left_quantity")}
        )


def test_requirement_free_instances_do_not_erase_inherited_conditions():
    checked = graph()
    first = workflow().compose(checked, "one", arguments(checked))
    document = workflow().document
    document["requirements"] = None
    second = Workflow.from_document(document, lab_vocabulary()).compose(
        first, "two", arguments(first.graph, "right")
    )
    assert len(second.requirements.document["requirements"]) == 2
    assert second.requirements.document["graph"] == second.graph.context
    with pytest.raises(ContractError, match="different graph context"):
        Requirements.from_document(first.requirements.document, second.graph)


def test_literal_argument_refutation_survives_substitution():
    checked = graph()
    checked = checked.compose("zero", "exact.literal", {}, {"value": 0})
    supplied = arguments(checked)
    supplied["quantity"] = checked.ref("zero")
    instance = workflow().compose(checked, "one", supplied)
    assert instance.requirements.check()["status"] == "refuted"
    with pytest.raises(ContractError, match="literal condition is refuted"):
        instance.compile(python_backend(checked.vocabulary))


def test_workflow_reuse_remains_within_existing_graph_budgets():
    checked = graph()
    # A legal source graph must not bypass the aggregate graph limit by reuse.
    document = checked.document
    document["objects"].extend(
        [
            {
                "id": f"literal_{i}",
                "op": "exact.literal",
                "ports": {},
                "attributes": {"value": i},
            }
            for i in range(505)
        ]
    )
    checked = Graph.from_document(document, lab_vocabulary())
    before = checked.document
    with pytest.raises(ContractError):
        workflow().compose(checked, "one", arguments(checked))
    assert checked.document == before


def test_many_port_references_preserve_order_repetition_and_literal_attributes():
    manifest = lab_vocabulary().document
    manifest["operations"]["text.join"] = {
        "role": "apply",
        "ports": {"parts": {"accepts": ["Text"], "multiplicity": "many"}},
        "attributes": {"label": {"kind": "text"}},
        "result": "Text",
        "effects": [],
        "definition": None,
    }
    vocabulary = Vocabulary.from_document(manifest)
    source = Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": [
                {"id": "a", "op": "text.input", "ports": {}, "attributes": {}},
                {"id": "b", "op": "text.input", "ports": {}, "attributes": {}},
                {
                    "id": "joined",
                    "op": "text.join",
                    "ports": {"parts": ["b", "a", "b"]},
                    "attributes": {"label": "a"},
                },
            ],
            "outputs": ["joined"],
        },
        vocabulary,
    )
    template = Workflow.from_document(
        {
            "version": 1,
            "id": "join",
            "revision": "v1",
            "graph": source.document,
            "inputs": {"a": "a", "b": "b"},
            "outputs": {"joined": "joined"},
            "requirements": None,
        },
        vocabulary,
    )
    checked = Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": source.document["objects"][:2],
            "outputs": ["a"],
        },
        vocabulary,
    )
    instance = template.compose(
        checked, "one", {"a": checked.ref("a"), "b": checked.ref("b")}
    )
    observed = instance.graph.inspect("one.joined")
    assert observed["ports"]["parts"] == ["b", "a", "b"]
    assert observed["attributes"]["label"] == "a"


def test_parameter_free_workflow_has_no_phantom_inputs():
    source = Graph.from_document(
        {
            "version": 1,
            "vocabulary": lab_vocabulary().fingerprint,
            "objects": [
                {
                    "id": "answer",
                    "op": "exact.literal",
                    "ports": {},
                    "attributes": {"value": 42},
                }
            ],
            "outputs": ["answer"],
        },
        lab_vocabulary(),
    )
    template = Workflow.from_document(
        {
            "version": 1,
            "id": "answer",
            "revision": "v1",
            "graph": source.document,
            "inputs": {},
            "outputs": {"answer": "answer"},
            "requirements": None,
        },
        lab_vocabulary(),
    )
    instance = template.compose(source, "one", {})
    result = (
        instance.compile(
            python_backend(source.vocabulary), [instance.outputs["answer"]]
        )
        .bind({})
        .execute()
    )
    assert result.values == {"one.answer": 42}
