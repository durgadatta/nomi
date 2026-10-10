"""Starter tooling leads to the same calculation while keeping explicit choices."""

import importlib.util
import json
from pathlib import Path

import pytest

from tools.jupyter.launch_nomi_notebook import parse_args
from tools.jupyter.check_nomi_kernel import notebook_sources, execution_error

ROOT = Path(__file__).resolve().parents[4]


def test_notebook_default_is_calculation_and_explicit_paths_are_preserved():
    assert parse_args([]).notebook == ROOT / "notebooks/nomi_calculation.ipynb"
    assert parse_args(["my-work.ipynb"]).notebook == Path("my-work.ipynb")
    assert parse_args(["--minimal"]).notebook == ROOT / "notebooks/nomi_minimal.ipynb"


def test_editor_enable_opens_calculation_in_the_repository(monkeypatch):
    path = ROOT / "tools/vscode/nomi/scripts/nomi-vscode.py"
    spec = importlib.util.spec_from_file_location("nomi_vscode_first_task", path)
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    commands = []
    monkeypatch.setattr(wrapper, "require_code", lambda: "code")
    monkeypatch.setattr(wrapper, "install_local", lambda: None)
    monkeypatch.setattr(wrapper, "run", lambda command, **kwargs: commands.append((command, kwargs)))
    assert wrapper.enable_local() == 0
    assert commands == [
        (["code", "--reuse-window", str(ROOT / "samples/calculate.nomi")], {"cwd": ROOT})
    ]


@pytest.mark.parametrize("document", [[], {"cells": []}, {"cells": [3]}, {"cells": [{"cell_type": "code", "source": 3}]}])
def test_invalid_notebook_cannot_be_mistaken_for_an_execution_check(tmp_path, document):
    path = tmp_path / "input.ipynb"
    path.write_text(json.dumps(document))
    with pytest.raises(ValueError):
        notebook_sources(path)


def test_notebook_checker_reads_both_valid_source_encodings(tmp_path):
    path = tmp_path / "input.ipynb"
    path.write_text(json.dumps({"cells": [
        {"cell_type": "markdown", "source": "Intro"},
        {"cell_type": "code", "source": ["print(1)", "\n"]},
        {"cell_type": "code", "source": "print(2)"},
    ]}))
    assert notebook_sources(path) == ["print(1)\n", "print(2)"]


def test_kernel_checker_keeps_the_user_error_without_internal_frames():
    assert execution_error({
        "ename": "TypeError", "evalue": "wrong quantity", "traceback": ["internal evaluator frames"],
    }) == "TypeError: wrong quantity"
