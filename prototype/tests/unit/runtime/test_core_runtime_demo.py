"""Direct Core Runtime smoke tests for demo.nomi."""

from pathlib import Path

from prototype.runtime import create_session


def test_demo_nomi_runs_on_direct_core_runtime():
    session = create_session(mode="nomi", eval_backend="core-runtime")

    result = session.run(
        filename=Path("samples/demo.nomi"),
        capture_output=True,
    )

    assert result.ok
    assert result.bindings["count"] == 2
    assert result.bindings["collected"] == [2, 4, 6]
    assert result.bindings["total"] == 6
    assert result.bindings["parsed"] == 0
    assert "add(3, 4)         = 7" in result.stdout
    assert "block: collected  = [2, 4, 6]" in result.stdout
