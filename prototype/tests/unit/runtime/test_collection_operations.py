"""Operational library contracts, not static callback/effect conformance."""

import shutil

import pytest

from prototype.runtime import create_session
from prototype.runtime.collections import fold, scan


@pytest.mark.parametrize("backend", ["python-ast", "core-runtime", "js-core-runtime"])
@pytest.mark.parametrize("mode", ["nomi", "reduced"])
def test_seed_order_and_non_associative_state_match_across_backends(backend, mode):
    if backend == "js-core-runtime" and not shutil.which("node"):
        pytest.skip("node is not installed")
    source = """func subtract(state, item):
    print(item)
    return state - item

items = [1, 2, 3]
total = items |> fold(10, subtract)
history = scan(items, 10, subtract)
empty = fold([], 10, subtract)
empty_history = scan([], 10, subtract)
"""
    result = create_session(mode=mode, eval_backend=backend).run(
        source=source, capture_output=True
    )
    assert result.bindings["total"] == 4
    assert result.bindings["history"] == [10, 9, 7, 4]
    assert result.bindings["empty"] == 10
    assert result.bindings["empty_history"] == [10]
    assert result.stdout == "1\n2\n3\n1\n2\n3\n"


@pytest.mark.parametrize("backend", ["python-ast", "core-runtime", "js-core-runtime"])
@pytest.mark.parametrize("operation", ["fold", "scan"])
@pytest.mark.parametrize(
    "source",
    [
        "value = OP([], 0, 3)\n",
        "value = OP([1], 0)\n",
        "func combine(state, item):\n    return 1 / 0\nvalue = OP([1, 2], 0, combine)\n",
    ],
)
def test_bad_calls_or_callback_failure_do_not_return_success(
    backend, operation, source
):
    if backend == "js-core-runtime" and not shutil.which("node"):
        pytest.skip("node is not installed")
    result = create_session(eval_backend=backend).run(
        source=source.replace("OP", operation), raise_on_error=False
    )
    assert not result.ok
    assert result.diagnostics


def test_single_pass_and_callback_failure_stop_traversal():
    trace = []

    def items():
        for number in [1, 2, 3]:
            trace.append(("demand", number))
            yield number

    def combine(state, item):
        trace.append(("call", item))
        if item == 2:
            raise ValueError("stop")
        return state + item

    with pytest.raises(ValueError, match="stop"):
        fold(items(), 0, combine)
    assert trace == [("demand", 1), ("call", 1), ("demand", 2), ("call", 2)]


def test_scan_does_not_claim_mutable_reference_history_is_a_snapshot():
    seed = []

    def append(state, item):
        state.append(item)
        return state

    history = scan([1, 2], seed, append)
    assert len(history) == 3
    assert all(state is seed for state in history)
    assert history == [[1, 2], [1, 2], [1, 2]]


def test_plain_python_compatibility_does_not_gain_nomi_prelude():
    result = create_session(mode="python").run(
        source="fold([], 0, sum)\n", raise_on_error=False
    )
    assert not result.ok
    assert "fold" in str(result.exception)
