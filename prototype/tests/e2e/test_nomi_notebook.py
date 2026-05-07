import ast
import json
from pathlib import Path

from prototype.interpreter.nomi.interpreter import Interpreter
from prototype.parser.nomi.usage import generate_ast
from tools.jupyter.check_nomi_kernel import run_smoke
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


def test_kernel_smoke_runner_reports_expected_output(monkeypatch):
    calls = []

    class FakeClient:
        def __init__(self):
            self.messages = [
                {"header": {"msg_type": "stream"}, "content": {"text": "7\n"}},
                {"header": {"msg_type": "execute_result"}, "content": {"data": {"text/plain": "30"}}},
                {"header": {"msg_type": "status"}, "content": {"execution_state": "idle"}},
            ]

        def start_channels(self):
            calls.append("start_channels")

        def wait_for_ready(self, timeout):
            calls.append(("wait_for_ready", timeout))

        def execute(self, code):
            calls.append(("execute", code))

        def get_iopub_msg(self, timeout):
            calls.append(("iopub", timeout))
            return self.messages.pop(0)

        def get_shell_msg(self, timeout):
            calls.append(("shell", timeout))
            return {"content": {"status": "ok"}}

        def stop_channels(self):
            calls.append("stop_channels")

    class FakeKernelManager:
        def __init__(self, kernel_name):
            calls.append(("manager", kernel_name))

        def start_kernel(self):
            calls.append("start_kernel")

        def client(self):
            return FakeClient()

        def shutdown_kernel(self, now):
            calls.append(("shutdown", now))

    monkeypatch.setattr("tools.jupyter.check_nomi_kernel.KernelManager", FakeKernelManager)

    outputs = run_smoke("nomi", 10)

    assert outputs == ["7\n", "30"]
    assert ("execute", "add = (x, y) => x + y\nprint(add(2, 5))\nadd(10, 20)") in calls
