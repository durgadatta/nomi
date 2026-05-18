import pytest

from prototype.syntax.core import (
    Bind,
    Branch,
    CoreVerificationError,
    Diagnostic,
    Literal,
    Load,
    Module,
    dump_core,
    verify_core,
)
from prototype.syntax.surface import SurfaceNode


def test_verify_core_accepts_passive_core_tree():
    tree = Module(body=(Bind(name="x", value=Literal(value=1)),))

    verify_core(tree)


def test_verify_core_rejects_surface_nodes():
    class DummySurface(SurfaceNode):
        def lower(self):
            raise NotImplementedError

    tree = Module(body=(Bind(name="x", value=DummySurface()),))

    with pytest.raises(CoreVerificationError, match="surface node"):
        verify_core(tree)


def test_verify_core_rejects_non_core_values():
    tree = Module(body=(Bind(name="x", value=object()),))

    with pytest.raises(CoreVerificationError, match="non-core value"):
        verify_core(tree)


def test_dump_core_is_stable_and_readable():
    tree = Module(
        body=(
            Bind(name="x", value=Literal(value=1)),
            Branch(
                test=Load(name="x"),
                then_body=Module(body=(Diagnostic(message="ok"),)),
            ),
        )
    )

    assert dump_core(tree) == "\n".join(
        [
            "Module",
            "  Bind('x')",
            "    Literal(1)",
            "  Branch",
            "    Load('x')",
            "    Module",
            "      Diagnostic('ok')",
        ]
    )
