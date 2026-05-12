"""
Pytest configuration for multi-interpreter testing.

Adds a --interpreter-modes CLI flag that controls which interpreter(s) to test.
Tests request the ``interpreter_mode`` fixture to opt into auto-parametrization.

Examples::

    pytest                                               # runs all three
    pytest --interpreter-modes reduced                   # only reduced
    pytest --interpreter-modes python nomi               # python + nomi
    NOMI_INTERPRETER_MODE=reduced pytest                 # env-var override
"""

import pytest
import os

from prototype.interpreter.helpers import INTERPRETER_MODES

AVAILABLE_MODES = INTERPRETER_MODES


def pytest_addoption(parser):
    parser.addoption(
        "--interpreter-modes",
        nargs="+",
        default=None,
        choices=AVAILABLE_MODES + ("all",),
        help=(
            "Which interpreter(s) to test. "
            "Accepts one or more of: python, nomi, reduced, all. "
            "Default: all interpreters. "
            "Can also be set via NOMI_INTERPRETER_MODE env var "
            "(space-separated; 'all' means every mode)."
        ),
    )


def _resolve_modes(config) -> list[str]:
    cli_val = config.getoption("--interpreter-modes", default=None) or []
    env_val = os.environ.get("NOMI_INTERPRETER_MODE")

    if not cli_val and not env_val:
        return list(AVAILABLE_MODES)

    if cli_val:
        if "all" in cli_val:
            return list(AVAILABLE_MODES)
        return [m for m in cli_val if m in AVAILABLE_MODES]

    if env_val:
        if env_val.strip().lower() == "all":
            return list(AVAILABLE_MODES)
        modes = env_val.strip().split()
        return [m for m in modes if m in AVAILABLE_MODES]

    return list(AVAILABLE_MODES)


def pytest_generate_tests(metafunc):
    if "interpreter_mode" in metafunc.fixturenames:
        modes = _resolve_modes(metafunc.config)
        metafunc.parametrize("interpreter_mode", modes, scope="function")


def pytest_configure(config):
    modes = _resolve_modes(config)
    config._nomi_interpreter_modes = modes
