"""Contracts for portable Core Runtime frames."""

import pytest

from prototype.runtime.backends.environment import Frame
from prototype.runtime.backends.values import IntValue, StrValue


def test_frame_lookup_reads_local_bindings():
    frame = Frame()

    frame.bind("x", IntValue(1))

    assert frame.lookup("x") == IntValue(1)


def test_frame_lookup_walks_parent_chain():
    root = Frame()
    child = root.extend()
    root.bind("x", IntValue(1))

    assert child.lookup("x") == IntValue(1)


def test_frame_assign_updates_nearest_existing_binding():
    root = Frame()
    child = root.extend()
    root.bind("x", IntValue(1))

    child.assign("x", IntValue(2))

    assert root.lookup("x") == IntValue(2)
    assert "x" not in child.bindings


def test_frame_assign_creates_local_binding_when_missing():
    root = Frame()
    child = root.extend()

    child.assign("x", IntValue(3))

    assert child.lookup("x") == IntValue(3)
    assert root.lookup("x") is None


def test_frame_extend_binds_parameters_and_arguments():
    root = Frame()

    child = root.extend(("x", "y"), (IntValue(1), StrValue("two")))

    assert child.lookup("x") == IntValue(1)
    assert child.lookup("y") == StrValue("two")


def test_frame_extend_rejects_arity_mismatch():
    with pytest.raises(TypeError, match="Expected 2 arguments"):
        Frame().extend(("x", "y"), (IntValue(1),))


def test_frame_export_unboxes_only_current_scope():
    root = Frame()
    child = root.extend()
    root.bind("outer", IntValue(1))
    child.bind("inner", StrValue("ok"))

    assert child.export_bindings() == {"inner": "ok"}
