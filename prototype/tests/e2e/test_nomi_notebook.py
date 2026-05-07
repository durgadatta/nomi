import ast
import json
from pathlib import Path

from prototype.interpreter.nomi.interpreter import Interpreter
from prototype.parser.nomi.usage import generate_ast
from tools.jupyter.install_nomi_kernel import kernel_json


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


def test_syntax_tour_notebook_cells_run_on_current_nomi_interpreter():
    notebook_path = ROOT / "notebooks" / "nomi_syntax_tour.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    interpreter = Interpreter()

    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        code = "".join(cell["source"])
        if code.strip().startswith("%"):
            continue
        execute_nomi_cell(interpreter, code)


def test_kernel_json_points_to_local_nomi_kernel():
    spec = kernel_json(ROOT, "Nomi")

    assert spec["display_name"] == "Nomi"
    assert spec["language"] == "nomi"
    assert spec["argv"][1:3] == ["-m", "tools.jupyter.nomi_kernel"]
    assert spec["env"]["NOMI_PROJECT_ROOT"] == str(ROOT)
    assert str(ROOT) in spec["env"]["PYTHONPATH"]

