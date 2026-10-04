"""Keep the opt-in Pyodide gate's programs runnable on the hosted bridge."""

import pytest

from prototype.runtime import create_session
from scripts.check_legacy_call_scenarios import CALL_SCENARIOS


@pytest.mark.parametrize("name, source", CALL_SCENARIOS, ids=[item[0] for item in CALL_SCENARIOS])
def test_legacy_browser_call_scenario_source(nomi_mode, name, source):
    session = create_session(mode=nomi_mode, eval_backend="python-ast")
    result = session.run(source=source, capture_output=True)
    assert result.stdout == f"{name} passed\n"
    assert result.exception is None
    assert not result.diagnostics
