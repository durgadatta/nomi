"""The first notebook is a clean, source-owned lesson with cross-cell behavior."""

from pathlib import Path

import nbformat
import pytest

from prototype.runtime import create_session
from tools.jupyter.create_demo_notebooks import calculation_notebook

ROOT = Path(__file__).resolve().parents[3]


def test_calculation_notebook_matches_generator_and_canonical_first_program():
    expected = calculation_notebook()
    actual = nbformat.read(ROOT / "notebooks/nomi_calculation.ipynb", as_version=4)
    assert actual == expected
    assert actual.cells[1].source == (ROOT / "samples/calculate.nomi").read_text().strip("\n")
    nbformat.validate(actual)
    for cell in actual.cells:
        if cell.cell_type == "code":
            assert cell.outputs == []
            assert cell.execution_count is None


@pytest.mark.parametrize("mode", ["nomi", "reduced"])
def test_calculation_lesson_runs_from_a_fresh_session_in_cell_order(mode):
    session = create_session(mode=mode)
    outputs = []
    for cell in calculation_notebook().cells:
        if cell.cell_type != "code":
            continue
        # The notebook kernel supplies the parser's terminating newline.
        result = session.run(source=cell.source + "\n", capture_output=True, raise_on_error=False)
        assert result.ok, result.diagnostics
        outputs.append(result.stdout)
    assert outputs == ["3850\n", "5050\n"]
