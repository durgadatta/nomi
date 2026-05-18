import ast
import json
from pathlib import Path

from prototype.interpreter.nomi.interpreter import Interpreter
from prototype.parser.nomi.usage import generate_ast
from tools.jupyter.create_demo_notebooks import minimal_notebook, syntax_tour_notebook


ROOT = Path(__file__).resolve().parents[3]


def execute_nomi_cell(interpreter, code):
    if not code.endswith("\n"):
        code += "\n"
    tree = ast.fix_missing_locations(generate_ast(code=code))
    body = list(tree.body)

    if body and isinstance(body[-1], ast.Expr):
        leading = ast.Module(body=body[:-1], type_ignores=[])
        interpreter.eval(ast.fix_missing_locations(leading))
        return interpreter.eval(body[-1])

    return interpreter.eval(tree)


def run_notebook_code_cells(notebook_path):
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    interpreter = Interpreter()

    for cell in notebook["cells"]:
        assert cell.get("id")
        if cell["cell_type"] != "code":
            continue
        code = "".join(cell["source"])
        if code.strip().startswith("%"):
            continue
        execute_nomi_cell(interpreter, code)


def test_minimal_notebook_cells_run_on_current_nomi_interpreter():
    run_notebook_code_cells(ROOT / "notebooks" / "nomi_minimal.ipynb")


def test_syntax_tour_notebook_cells_run_on_current_nomi_interpreter():
    run_notebook_code_cells(ROOT / "notebooks" / "nomi_syntax_tour.ipynb")


def test_demo_notebooks_match_generator_outputs():
    expected = {
        "nomi_minimal.ipynb": minimal_notebook(),
        "nomi_syntax_tour.ipynb": syntax_tour_notebook(),
    }

    for name, notebook in expected.items():
        actual = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
        expected_json = json.loads(json.dumps(notebook))

        assert actual["metadata"] == expected_json["metadata"]
        assert actual["nbformat"] == expected_json["nbformat"]
        assert actual["nbformat_minor"] == expected_json["nbformat_minor"]
        assert len(actual["cells"]) == len(expected_json["cells"])

        for actual_cell, expected_cell in zip(actual["cells"], expected_json["cells"], strict=True):
            assert actual_cell["id"] == expected_cell["id"]
            assert actual_cell["cell_type"] == expected_cell["cell_type"]
            assert actual_cell["metadata"] == expected_cell["metadata"]
            assert "".join(actual_cell["source"]) == expected_cell["source"]
            if actual_cell["cell_type"] == "code":
                assert actual_cell["execution_count"] is None
                assert actual_cell["outputs"] == []
