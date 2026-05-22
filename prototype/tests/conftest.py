"""
Pytest configuration for multi-interpreter testing.

Two fixtures are available:

``interpreter_mode``
    Parametrizes over **all** interpreters (python, nomi, reduced).
    Use when a test is meaningful for the full stack.

``nomi_mode``
    Parametrizes over Nomi-family interpreters only (nomi, reduced).
    This is the **default for new tests** — most language features
    are Nomi-specific.  No marker or skip boilerplate needed.

``nomi_parser_frontend``
    Parametrizes tests that opt in over Python-AST-capable Nomi parser
    frontends (currently Lark and rust-fast-ast). Use this for runtime or
    regression checks that should prove parser-family equivalence.

Examples::

    def test_something(nomi_mode):          # runs on nomi, reduced
        run = get_run_eval_loop(nomi_mode)

    def test_parity(interpreter_mode):      # runs on python, nomi, reduced
        run = get_run_eval_loop(interpreter_mode)

CLI::

    pytest                                          # all three
    pytest --interpreter-modes reduced              # only reduced
    pytest --interpreter-modes python nomi          # python + nomi
    NOMI_INTERPRETER_MODE=reduced pytest            # env-var override
    pytest --nomi-parser-frontends rust-fast-ast    # one Nomi parser frontend
    NOMI_PARSER_FRONTEND=all pytest                 # all AST-capable frontends
"""

import pytest
import os

from prototype.interpreter.helpers import INTERPRETER_MODES
from prototype.parser.nomi.frontend import get_python_ast_frontends

ALL_MODES = INTERPRETER_MODES          # ("python", "nomi", "reduced")
NOMI_MODES = ("nomi", "reduced")
NOMI_PARSER_FRONTENDS = tuple(
    frontend.spec.name for frontend in get_python_ast_frontends()
)


def pytest_addoption(parser):
    # TODO(NOMI-SUBSTRATE-026): Once syntax feature manifests exist, add
    # feature-profile selection here so tests can combine interpreter modes
    # with parse-only, lowering-only, runtime, web, and notebook feature checks.
    parser.addoption(
        "--interpreter-modes",
        nargs="+",
        default=None,
        choices=ALL_MODES + ("all",),
        help=(
            "Which interpreter(s) to test. "
            "Accepts one or more of: python, nomi, reduced, all. "
            "Default: all interpreters. "
            "Can also be set via NOMI_INTERPRETER_MODE env var "
            "(space-separated; 'all' means every mode)."
        ),
    )
    parser.addoption(
        "--nomi-parser-frontends",
        nargs="+",
        default=None,
        choices=NOMI_PARSER_FRONTENDS + ("all",),
        help=(
            "Which Python-AST-capable Nomi parser frontend(s) to test. "
            "Accepts one or more registered frontend names or 'all'. "
            "Default: all Python-AST-capable frontends. "
            "Can also be set via NOMI_PARSER_FRONTEND env var "
            "(space-separated; 'all' means every Python-AST-capable frontend)."
        ),
    )


def _resolve_modes(config, available) -> list[str]:
    cli_val = config.getoption("--interpreter-modes", default=None) or []
    env_val = os.environ.get("NOMI_INTERPRETER_MODE")

    if not cli_val and not env_val:
        return list(available)

    if cli_val:
        if "all" in cli_val:
            return list(available)
        return [m for m in cli_val if m in available]

    if env_val:
        if env_val.strip().lower() == "all":
            return list(available)
        modes = env_val.strip().split()
        return [m for m in modes if m in available]

    return list(available)


def _resolve_parser_frontends(config, available) -> list[str]:
    cli_val = config.getoption("--nomi-parser-frontends", default=None) or []
    env_val = os.environ.get("NOMI_PARSER_FRONTEND")

    if not cli_val and not env_val:
        return list(available)

    if cli_val:
        if "all" in cli_val:
            return list(available)
        return [frontend for frontend in cli_val if frontend in available]

    if env_val:
        if env_val.strip().lower() == "all":
            return list(available)
        frontends = env_val.strip().split()
        return [frontend for frontend in frontends if frontend in available]

    return list(available)


def pytest_generate_tests(metafunc):
    if "interpreter_mode" in metafunc.fixturenames:
        modes = _resolve_modes(metafunc.config, ALL_MODES)
        metafunc.parametrize("interpreter_mode", modes, scope="function")
    if "nomi_mode" in metafunc.fixturenames:
        modes = _resolve_modes(metafunc.config, NOMI_MODES)
        metafunc.parametrize("nomi_mode", modes, scope="function")
    if "nomi_parser_frontend" in metafunc.fixturenames:
        frontends = _resolve_parser_frontends(metafunc.config, NOMI_PARSER_FRONTENDS)
        metafunc.parametrize("nomi_parser_frontend", frontends, scope="function")


def pytest_configure(config):
    config._nomi_interpreter_modes = _resolve_modes(config, ALL_MODES)
    config._nomi_parser_frontends = _resolve_parser_frontends(
        config,
        NOMI_PARSER_FRONTENDS,
    )
