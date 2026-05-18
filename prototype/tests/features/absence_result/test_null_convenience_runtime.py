from prototype.interpreter.helpers import get_run_eval_loop


def test_null_coalesce_uses_fallback_for_none(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = None ?? 'anonymous'\n")
    assert bindings["result"] == "anonymous"


def test_safe_getattr_returns_none_for_none_receiver(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="user = None\nresult = user?.name\n")
    assert bindings["result"] is None


def test_safe_call_returns_none_for_none_receiver(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="data = None\nresult = data?.get('key')\n")
    assert bindings["result"] is None


def test_safe_subscript_reads_existing_value(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="items = [10, 20]\nresult = items?.[1]\n")
    assert bindings["result"] == 20


def test_safe_subscript_returns_none_for_none_receiver(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="items = None\nresult = items?.[0]\n")
    assert bindings["result"] is None


def test_safe_subscript_chains_with_null_coalesce(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="items = None\nresult = items?.[0] ?? 'missing'\n")
    assert bindings["result"] == "missing"


def test_safe_navigation_evaluates_receiver_once(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "calls = []\n"
            "func data():\n"
            "    calls.append('called')\n"
            "    return ['value']\n"
            "result = data()?.[0]\n"
        )
    )
    assert bindings["result"] == "value"
    assert bindings["calls"] == ["called"]

