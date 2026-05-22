import ast
import pytest
from pathlib import Path
import json
import io
import contextlib
import re

from prototype.interpreter.helpers import get_run_eval_loop
from prototype.parser.nomi.frontend import DEFAULT_FRONTEND
from prototype.runtime import execute
from prototype.tests.shared_utils import stabilize_value, stabilize_locals

SAMPLE_DIR = Path(__file__).resolve().parents[1]/'data/sample_sources/interpreter'
SAMPLES_DIR = Path(__file__).resolve().parents[3]/'samples'
ALL_SOURCES = (
    list(SAMPLE_DIR.glob('*.py')) + list(SAMPLE_DIR.glob('*.nomi')) +
    list(SAMPLES_DIR.glob('*.nomi')) + list(SAMPLES_DIR.glob('*.nomi.nb'))
)


def _is_nomi_source(path: Path) -> bool:
    return path.suffix == '.nomi' or path.name.endswith('.nomi.nb')


def _param_id(path: Path) -> str:
    """Name snapshots so ``samples/`` files are grouped under a ``sample-`` prefix."""
    if str(path).startswith(str(SAMPLES_DIR)):
        return f"sample-{path.name}"
    return path.name


@pytest.mark.parametrize("source_file", ALL_SOURCES, ids=_param_id)
def test_eval_loop(
    source_file,
    file_regression,
    capsys,
    interpreter_mode,
    nomi_parser_frontend,
):
    ext = source_file.suffix
    is_nomi_source = _is_nomi_source(source_file)
    if not is_nomi_source and nomi_parser_frontend != DEFAULT_FRONTEND:
        pytest.skip(".py source uses the Python parser, not Nomi parser frontends")
    if ext == '.py' and interpreter_mode != 'python':
        pytest.skip(f".py source requires 'python' interpreter mode, got {interpreter_mode!r}")
    if is_nomi_source and interpreter_mode == 'python':
        pytest.skip(f".nomi source requires 'nomi' or 'reduced' interpreter mode, got {interpreter_mode!r}")

    stable_bindings = _stable_eval_result(
        source_file=source_file,
        interpreter_mode=interpreter_mode,
        parser_frontend=nomi_parser_frontend,
        capsys=capsys,
    )

    if is_nomi_source and nomi_parser_frontend != DEFAULT_FRONTEND:
        expected = _stable_eval_result(
            source_file=source_file,
            interpreter_mode=interpreter_mode,
            parser_frontend=DEFAULT_FRONTEND,
            capsys=capsys,
        )
        assert stable_bindings == expected
        return

    file_regression.check(
        stable_bindings,
        fullpath=_snapshot_path(source_file, interpreter_mode),
    )


def _stable_eval_result(
    *,
    source_file: Path,
    interpreter_mode: str,
    parser_frontend: str,
    capsys,
) -> str:
    if _is_nomi_source(source_file):
        result = execute(
            filename=source_file,
            mode=interpreter_mode,
            parser_frontend=parser_frontend,
            capture_output=True,
        )
        bindings = result.bindings
        stdout_value = result.stdout.split('\n')
        return _stable_result_text(bindings, stdout_value)

    code = source_file.read_text()
    run_eval_loop = get_run_eval_loop(interpreter_mode)

    eval_loop_stdout = io.StringIO()
    with capsys.disabled():
        with contextlib.redirect_stdout(eval_loop_stdout):
            bindings = run_eval_loop(code=code)
        stdout_value = eval_loop_stdout.getvalue().split('\n')

    return _stable_result_text(bindings, stdout_value)


def _stable_result_text(bindings, stdout_value) -> str:
    stable_bindings = stabilize_locals(bindings)
    stable_bindings['stdout'] = stdout_value
    return json.dumps(stable_bindings, indent=2)


def _snapshot_path(source_file: Path, interpreter_mode: str) -> Path:
    stem = f"test_eval_loop_{interpreter_mode}_{_param_id(source_file)}"
    normalized = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    if not normalized.endswith("_"):
        normalized += "_"
    return Path(__file__).with_name("test_interpreter") / f"{normalized}.txt"
