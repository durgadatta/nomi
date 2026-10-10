"""Explicit engine selection and isolated realizations of immutable objects."""

from copy import deepcopy
from pathlib import Path

import pytest

from tools.object_interface import ContractError, Graph, Vocabulary, load_document
from tools.object_interface.__main__ import main
from tools.object_interface.backend import (
    Backend,
    BackendFailure,
    Cancellation,
    Cancelled,
)
from tools.object_interface.examples import lab_vocabulary, python_backend

ROOT = Path(__file__).resolve().parents[4]


def graph():
    return Graph.from_document(
        load_document(ROOT / "docs/research/object_framework/composition.json"),
        lab_vocabulary(),
    )


def implementations():
    return {
        "exact.add": lambda ports, attrs: ports["left"] + ports["right"],
        "exact.multiply": lambda ports, attrs: ports["left"] * ports["right"],
        "text.concat": lambda ports, attrs: ports["left"] + ports["right"],
    }


def test_check_compile_and_bind_do_not_invoke_implementations():
    checked, calls = graph(), []

    def add(ports, attrs):
        calls.append("add")
        return ports["left"] + ports["right"]

    backend = Backend(
        "observed",
        "v1",
        checked.vocabulary.fingerprint,
        {**implementations(), "exact.add": add},
    )
    checked.check()
    checked.inspect("document")
    checked.compare("squared", "expanded_square")
    compiled = backend.compile(checked)
    bound = compiled.bind({"quantity": 3, "name": "Ada"})
    assert calls == []
    assert compiled.inspect()["execution"] == "not performed"
    assert bound.execute().values == {"doubled": 18, "published": "Hello, Ada"}
    assert calls == ["add"]


@pytest.mark.parametrize("quantity", [-31, -1, 0, 1, 7, 2**120])
def test_exact_realization_matches_independently_stated_results(quantity):
    checked = graph()
    result = (
        python_backend(checked.vocabulary)
        .compile(checked)
        .bind({"quantity": quantity, "name": "Ada"})
        .execute()
    )
    assert result.get(checked.ref("doubled")) == 2 * quantity**2
    assert result.get(checked.ref("published")) == "Hello, Ada"
    assert result.receipt["status"] == "realized"
    assert result.receipt["domain_validity"] == "not established"


def test_same_objects_can_have_two_explicit_backends():
    checked = graph()
    original = implementations()
    alternate = {
        "exact.add": lambda p, a: sum([p["left"], p["right"]]),
        "exact.multiply": lambda p, a: pow(p["left"], 1) * p["right"],
        "text.concat": lambda p, a: "".join([p["left"], p["right"]]),
    }
    first = Backend("first", "v1", checked.vocabulary.fingerprint, original)
    second = Backend("second", "v2", checked.vocabulary.fingerprint, alternate)
    assert (
        first.compile(checked).bind({"quantity": 3, "name": "Ada"}).execute().values
        == second.compile(checked).bind({"quantity": 3, "name": "Ada"}).execute().values
    )
    assert checked.inspect("doubled")["realization"] == "unbound"


def test_named_intermediate_can_be_selected_without_unrelated_bindings():
    checked = graph()
    compiled = python_backend(checked.vocabulary).compile(
        checked, [checked.ref("squared")]
    )
    assert compiled.inspect()["required_inputs"] == ["quantity"]
    result = compiled.bind({"quantity": 5}).execute()
    assert result.values == {"squared": 25}
    with pytest.raises(ContractError, match="not requested"):
        result.get(checked.ref("published"))


def test_every_phase_and_snapshot_remains_detached():
    checked = graph()
    supplied = {"quantity": 3, "name": "Ada"}
    compiled = python_backend(checked.vocabulary).compile(checked)
    bound = compiled.bind(supplied)
    supplied["quantity"] = 99
    result = bound.execute()
    exported = result.values
    exported["doubled"] = 999
    receipt = result.receipt
    receipt["logical_to_physical"].clear()
    assert result.values["doubled"] == 18
    assert result.receipt["logical_to_physical"]
    for target, key in (
        (compiled, "_outputs"),
        (bound, "_bindings"),
        (result, "_values"),
    ):
        with pytest.raises(AttributeError):
            setattr(target, key, "changed")


def test_foreign_or_stale_references_cannot_select_or_read_results():
    checked = graph()
    other = graph()
    backend = python_backend(checked.vocabulary)
    with pytest.raises(ContractError, match="exact graph revision"):
        backend.compile(checked, [other.ref("squared")])
    result = backend.compile(checked).bind({"quantity": 3, "name": "Ada"}).execute()
    with pytest.raises(ContractError, match="different graph revision"):
        result.get(other.ref("doubled"))
    revised = checked.compose(
        "later", "exact.double", {"value": checked.ref("quantity")}
    )
    with pytest.raises(ContractError, match="different graph revision"):
        result.get(revised.ref("doubled"))


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"quantity": True, "name": "Ada"},
        {"quantity": 3.0, "name": "Ada"},
        {"quantity": 3, "name": None},
        {"quantity": 3, "name": "Ada", "extra": 0},
    ],
)
def test_binding_refuses_missing_extra_and_wrong_values(values):
    checked = graph()
    compiled = python_backend(checked.vocabulary).compile(checked)
    with pytest.raises(ContractError):
        compiled.bind(values)


def test_unrealizable_description_and_unsupported_operation_fail_during_compile():
    checked = graph()
    with pytest.raises(ContractError, match="description has no realization"):
        python_backend(checked.vocabulary).compile(checked, [checked.ref("document")])
    with pytest.raises(ContractError, match="unsupported backend operation"):
        Backend("empty", "v1", checked.vocabulary.fingerprint, {}).compile(checked)
    with pytest.raises(ContractError, match="fingerprint"):
        Backend("wrong", "v1", "unrelated", implementations()).compile(checked)


def test_example_adapter_does_not_retag_changed_vocabulary():
    document = lab_vocabulary().document
    document["revision"] = "v2"
    changed = Vocabulary.from_document(document)
    with pytest.raises(ContractError, match="tracked lab vocabulary"):
        python_backend(changed)


def test_effectful_operations_are_declared_but_refused_by_pure_executor():
    vocabulary_document = lab_vocabulary().document
    operation = deepcopy(vocabulary_document["operations"]["text.concat"])
    operation["effects"] = ["Console"]
    vocabulary_document["operations"]["text.write"] = operation
    vocabulary = Vocabulary.from_document(vocabulary_document)
    document = graph().document
    document["vocabulary"] = vocabulary.fingerprint
    document["objects"].append(
        {
            "id": "write",
            "op": "text.write",
            "ports": {"left": "prefix", "right": "name"},
            "attributes": {},
        }
    )
    document["outputs"] = ["write"]
    checked = Graph.from_document(document, vocabulary)
    assert checked.check()["status"] == "composition-checked"
    with pytest.raises(ContractError, match="effectful"):
        Backend("declared", "v1", vocabulary.fingerprint, {}).compile(checked)


def test_cancellation_is_distinct_and_prevents_execution():
    checked, calls = graph(), []
    ops = implementations()
    ops["exact.add"] = lambda p, a: calls.append("invoked") or p["left"] + p["right"]
    bound = (
        Backend("watched", "v1", checked.vocabulary.fingerprint, ops)
        .compile(checked)
        .bind({"quantity": 3, "name": "Ada"})
    )
    token = Cancellation()
    token.cancel()
    with pytest.raises(Cancelled):
        bound.execute(token)
    assert not calls


def test_runtime_backend_failure_identifies_named_origin():
    checked = graph()

    def fail(ports, attributes):
        raise RuntimeError("private host error")

    backend = Backend(
        "broken",
        "v1",
        checked.vocabulary.fingerprint,
        {**implementations(), "exact.multiply": fail},
    )
    with pytest.raises(BackendFailure) as error:
        backend.compile(checked).bind({"quantity": 3, "name": "Ada"}).execute()
    assert "squared" in error.value.object_ids
    assert error.value.operation == "exact.multiply"
    assert "private host error" not in str(error.value)


def test_output_values_are_checked_but_semantic_conformance_is_not_assumed():
    checked = graph()
    invalid = Backend(
        "invalid",
        "v1",
        checked.vocabulary.fingerprint,
        {**implementations(), "exact.add": lambda p, a: True},
    )
    with pytest.raises(ContractError, match="expected int"):
        invalid.compile(checked).bind({"quantity": 3, "name": "Ada"}).execute()
    wrong = Backend(
        "wrong-law",
        "v1",
        checked.vocabulary.fingerprint,
        {**implementations(), "exact.add": lambda p, a: 0},
    )
    realization = wrong.compile(checked).bind({"quantity": 3, "name": "Ada"}).execute()
    assert realization.values["doubled"] == 0
    assert realization.receipt["authority"] == "trusted explicit backend implementation"
    assert realization.receipt["domain_validity"] == "not established"


def test_many_ports_preserve_order_and_repeated_references():
    vocabulary_document = lab_vocabulary().document
    vocabulary_document["types"]["IntList"] = {"value": {"kind": "array"}}
    vocabulary_document["operations"]["list.make"] = {
        "role": "apply",
        "result": "IntList",
        "effects": [],
        "definition": None,
        "ports": {"items": {"accepts": ["ExactInt"], "multiplicity": "many"}},
        "attributes": {},
    }
    vocabulary = Vocabulary.from_document(vocabulary_document)
    document = graph().document
    document["vocabulary"] = vocabulary.fingerprint
    document["objects"].append(
        {
            "id": "repeated",
            "op": "list.make",
            "ports": {"items": ["quantity", "squared", "quantity"]},
            "attributes": {},
        }
    )
    document["outputs"] = ["repeated"]
    checked = Graph.from_document(document, vocabulary)
    backend = Backend(
        "lists",
        "v1",
        vocabulary.fingerprint,
        {
            **implementations(),
            "list.make": lambda ports, attrs: ports["items"],
        },
    )
    result = backend.compile(checked).bind({"quantity": 3}).execute()
    assert result.values == {"repeated": [3, 9, 3]}


def test_trusted_backend_cannot_mutate_another_operation_argument_snapshot():
    vocabulary_document = lab_vocabulary().document
    vocabulary_document["types"]["Record"] = {"value": {"kind": "record"}}
    for op, role, ports in [
        ("record.input", "input", {}),
        (
            "record.mutate",
            "apply",
            {"value": {"accepts": ["Record"], "multiplicity": "one"}},
        ),
    ]:
        vocabulary_document["operations"][op] = {
            "role": role,
            "result": "Record",
            "effects": [],
            "definition": None,
            "ports": ports,
            "attributes": {},
        }
    vocabulary = Vocabulary.from_document(vocabulary_document)
    document = {
        "version": 1,
        "vocabulary": vocabulary.fingerprint,
        "objects": [
            {"id": "input", "op": "record.input", "ports": {}, "attributes": {}},
            {
                "id": "changed",
                "op": "record.mutate",
                "ports": {"value": "input"},
                "attributes": {},
            },
        ],
        "outputs": ["input", "changed"],
    }
    checked = Graph.from_document(document, vocabulary)

    def mutate(ports, attributes):
        ports["value"]["items"].append(2)
        return ports["value"]

    values = {"input": {"items": [1]}}
    result = (
        Backend("mutating", "v1", vocabulary.fingerprint, {"record.mutate": mutate})
        .compile(checked)
        .bind(values)
        .execute()
    )
    assert result.values == {"input": {"items": [1]}, "changed": {"items": [1, 2]}}
    assert values == {"input": {"items": [1]}}


def test_retained_value_and_integer_capacity_are_explicit_refusals():
    checked = graph()
    with pytest.raises(ContractError, match="retained-value"):
        python_backend(checked.vocabulary).compile(checked).bind(
            {"quantity": 3, "name": "x" * 600_000}
        ).execute()
    with pytest.raises(BackendFailure) as error:
        python_backend(checked.vocabulary).compile(checked).bind(
            {"quantity": 2**3000, "name": "Ada"}
        ).execute()
    assert error.value.operation == "exact.multiply"


def test_cli_requires_explicit_adapter_and_runs_fixture(capsys):
    path = str(ROOT / "docs/research/object_framework/composition.json")
    bindings = str(ROOT / "docs/research/object_framework/bindings.json")
    assert main(["compare", path, "squared", "expanded_square"]) == 0
    assert '"equivalent"' in capsys.readouterr().out
    assert main(["run", path, bindings, "--backend", "python-exact-text"]) == 0
    assert '"doubled": 18' in capsys.readouterr().out
    assert main(["compare", path, "quantity", "squared"]) == 1
    capsys.readouterr()
    with pytest.raises(SystemExit):
        main(["run", path, bindings])
