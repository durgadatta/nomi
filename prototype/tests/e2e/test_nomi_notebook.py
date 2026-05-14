import ast
import json
import sys
from pathlib import Path

from prototype.interpreter.nomi.interpreter import Interpreter
from prototype.parser.nomi.usage import generate_ast
from prototype.runtime import RuntimeSession
from tools.jupyter.check_nomi_kernel import run_smoke
from tools.jupyter.create_demo_notebooks import minimal_notebook, syntax_tour_notebook
from tools.jupyter.install_nomi_kernel import kernel_json
from tools.jupyter.nomi_kernel import NomiKernel
from tools.jupyter.launch_nomi_notebook import main as launch_main


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


def test_kernel_json_points_to_local_nomi_kernel():
    spec = kernel_json(ROOT, "Nomi")

    assert spec["display_name"] == "Nomi"
    assert spec["language"] == "nomi"
    assert spec["argv"][1:3] == ["-m", "tools.jupyter.nomi_kernel"]
    assert spec["env"]["NOMI_PROJECT_ROOT"] == str(ROOT)
    assert str(ROOT) in spec["env"]["PYTHONPATH"]


def test_kernel_owns_runtime_session_facade():
    kernel = NomiKernel()

    assert isinstance(kernel.runtime_session, RuntimeSession)
    assert kernel.interpreter is kernel.runtime_session.interpreter


def test_kernel_executes_nomi_through_runtime_session(monkeypatch):
    kernel = NomiKernel()
    sent = []

    monkeypatch.setattr(kernel, "_send_execute_result", sent.append)

    result = kernel._execute_nomi("x = 2\nx + 3\n", silent=False)

    assert result == 5
    assert sent == [5]
    assert kernel.runtime_session.bindings["x"] == 2


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


def test_one_command_launcher_runs_setup_check_and_notebook(monkeypatch):
    calls = []

    def fake_run_step(args, *, cwd):
        calls.append((args, cwd))

    monkeypatch.setattr("tools.jupyter.launch_nomi_notebook.run_step", fake_run_step)

    launch_main(["--skip-install", "--no-browser"])

    assert calls[0][0] == [
        sys.executable,
        "-m",
        "tools.jupyter.install_nomi_kernel",
        "--user",
    ]
    assert calls[1][0] == [sys.executable, "-m", "tools.jupyter.check_nomi_kernel"]
    assert calls[2][0][:3] == [sys.executable, "-m", "notebook"]
    assert calls[2][0][3] == f"--ServerApp.root_dir={ROOT}"
    assert calls[2][0][4] == "--ServerApp.default_url=/lab/tree/notebooks/nomi_syntax_tour.ipynb"
    assert calls[2][0][5] == "--LabServerApp.notebook_starts_kernel=True"
    assert calls[2][0][6] == "--no-browser"


def test_one_command_launcher_can_open_minimal_notebook(monkeypatch):
    calls = []

    def fake_run_step(args, *, cwd):
        calls.append((args, cwd))

    monkeypatch.setattr("tools.jupyter.launch_nomi_notebook.run_step", fake_run_step)

    launch_main(["--skip-install", "--skip-check", "--minimal", "--no-browser"])

    assert calls[0][0] == [
        sys.executable,
        "-m",
        "tools.jupyter.install_nomi_kernel",
        "--user",
    ]
    assert calls[1][0][:3] == [sys.executable, "-m", "notebook"]
    assert calls[1][0][4] == "--ServerApp.default_url=/lab/tree/notebooks/nomi_minimal.ipynb"
