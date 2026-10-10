"""Definition provenance, execution cancellation and conservative laws."""

from copy import deepcopy

import pytest

from tools.object_interface import ContractError, Graph, Vocabulary
from tools.object_interface.backend import (
    Backend,
    BackendFailure,
    Cancellation,
    Cancelled,
)
from tools.object_interface.examples import lab_vocabulary


def node(identity, op, ports=None, attributes=None):
    return {
        "id": identity,
        "op": op,
        "ports": ports or {},
        "attributes": attributes or {},
    }


def checked(objects, outputs, vocabulary=None):
    vocabulary = vocabulary or lab_vocabulary()
    return Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": objects,
            "outputs": outputs,
        },
        vocabulary,
    )


def test_lowered_internal_failure_keeps_named_definition_origin():
    document = lab_vocabulary().document
    composed = deepcopy(document["operations"]["exact.square"])
    composed["definition"] = {
        "objects": [
            node(
                "internal_product",
                "exact.multiply",
                {"left": "$value", "right": "$value"},
            ),
            node("one", "exact.literal", attributes={"value": 1}),
            node("result", "exact.add", {"left": "internal_product", "right": "one"}),
        ],
        "output": "result",
    }
    document["operations"]["exact.square_plus_one"] = composed
    vocabulary = Vocabulary.from_document(document)
    graph = checked(
        [
            node("input", "exact.input"),
            node("calculation", "exact.square_plus_one", {"value": "input"}),
        ],
        ["calculation"],
        vocabulary,
    )

    def fail(ports, attributes):
        raise RuntimeError("physical operation failed")

    compiled = Backend(
        "test",
        "v1",
        vocabulary.fingerprint,
        {"exact.multiply": fail, "exact.add": lambda p, a: p["left"] + p["right"]},
    ).compile(graph)
    with pytest.raises(BackendFailure) as error:
        compiled.bind({"input": 3}).execute()
    assert error.value.object_ids == ("calculation",)
    assert error.value.operation == "exact.multiply"


def test_operation_mapping_snapshot_and_no_result_after_mid_operation_cancel():
    graph = checked(
        [
            node("input", "exact.input"),
            node("double", "exact.double", {"value": "input"}),
        ],
        ["double"],
    )
    token = Cancellation()

    def add(ports, attributes):
        token.cancel()
        return ports["left"] + ports["right"]

    implementations = {"exact.add": add}
    backend = Backend("test", "v1", graph.vocabulary.fingerprint, implementations)
    implementations["exact.add"] = lambda p, a: 999
    bound = backend.compile(graph).bind({"input": 3})
    with pytest.raises(Cancelled):
        bound.execute(token)
    assert graph.inspect("double")["realization"] == "unbound"


def test_undeclared_commutativity_and_distributivity_are_not_inferred():
    graph = checked(
        [
            node("a", "exact.input"),
            node("b", "exact.input"),
            node("forward", "exact.add", {"left": "a", "right": "b"}),
            node("reverse", "exact.add", {"left": "b", "right": "a"}),
        ],
        ["forward", "reverse"],
    )
    assert graph.compare("forward", "reverse")["status"] == "unknown"


def test_too_many_distinct_expanded_terms_refuse_even_small_source_graph():
    document = lab_vocabulary().document
    # Each source call uses fresh input identity, preventing accidental sharing
    # of an otherwise identical 20-operation pure definition.
    composed = deepcopy(document["operations"]["exact.double"])
    objects = []
    previous = "$value"
    for index in range(20):
        identity = f"s{index}"
        objects.append(
            node(identity, "exact.add", {"left": previous, "right": previous})
        )
        previous = identity
    composed["definition"] = {"objects": objects, "output": previous}
    document["operations"]["exact.big_definition"] = composed
    vocabulary = Vocabulary.from_document(document)
    sources = []
    outputs = []
    for index in range(25):
        sources.append(node(f"input{index}", "exact.input"))
        sources.append(
            node(f"result{index}", "exact.big_definition", {"value": f"input{index}"})
        )
        outputs.append(f"result{index}")
    with pytest.raises(ContractError, match="expanded composition exceeds node budget"):
        checked(sources, outputs, vocabulary)


def test_duplicate_selected_outputs_and_uncompiled_term_inspection_are_refused():
    graph = checked([node("input", "exact.input")], ["input"])
    backend = Backend("test", "v1", graph.vocabulary.fingerprint, {})
    with pytest.raises(ContractError, match="duplicate requested output"):
        backend.compile(graph, [graph.ref("input"), graph.ref("input")])
    with pytest.raises(ContractError, match="unknown compiled physical term"):
        backend.compile(graph).origins(99)
