"""Function-local prototype defer scheduling survives repeated and nested calls."""

from __future__ import annotations

import shutil

import pytest

from prototype.runtime import create_session


NODE = shutil.which("node")
BACKENDS = ("python-ast", "core-runtime", "js-core-runtime")
CASES = (
    (
        "nested-call-preserves-outer-cleanup",
        "func inner():\n    defer print('inner cleanup')\n    return 0\n"
        "func outer():\n    defer print('outer cleanup')\n    inner()\n    return 1\n"
        "outer()\n",
        "inner cleanup\nouter cleanup\n",
    ),
    (
        "repeated-call-preserves-scheduling",
        "func calculate():\n    defer print('cleanup')\n    print('body')\n"
        "calculate()\ncalculate()\n",
        "body\ncleanup\nbody\ncleanup\n",
    ),
    (
        "recursive-deferred-call-preserves-source-marker",
        "func calculate(number):\n"
        "    defer calculate(number - 1) if number > 0 else print('cleanup')\n"
        "    print(number)\ncalculate(2)\n",
        "2\n1\n0\ncleanup\n",
    ),
    (
        "failing-cleanup-preserves-repeat-call",
        "func calculate():\n    defer int('invalid')\n    print('body')\n"
        "try:\n    calculate()\nexcept ValueError:\n    print('caught')\n"
        "try:\n    calculate()\nexcept ValueError:\n    print('caught')\n",
        "body\ncaught\nbody\ncaught\n",
    ),
    (
        "nested-failing-cleanup-restores-outer-stack",
        "func inner():\n    defer int('invalid')\n    print('inner body')\n"
        "func outer():\n    defer print('outer cleanup')\n    inner()\n"
        "try:\n    outer()\nexcept ValueError:\n    print('caught')\n",
        "inner body\nouter cleanup\ncaught\n",
    ),
)


@pytest.mark.parametrize("mode", ("nomi", "reduced"))
@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize(
    "_name, source, expected", CASES, ids=[case[0] for case in CASES]
)
def test_function_defer_reentrancy_and_failure_boundaries(
    mode, backend, _name, source, expected
):
    if backend == "js-core-runtime" and NODE is None:
        pytest.skip("node is not installed")

    result = create_session(mode=mode, eval_backend=backend).run(
        source=source,
        capture_output=True,
    )

    assert result.ok
    assert result.stdout == expected
