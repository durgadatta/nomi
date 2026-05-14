from prototype.interpreter.python.usage import run_eval_loop


def test_keyword_only_default_stays_out_of_kwargs():
    bindings = run_eval_loop(
        code=(
            "def configure(*, scale=2, **kwargs):\n"
            "    return scale, kwargs\n"
            "result = configure(extra=5)\n"
        )
    )

    assert bindings["result"] == (2, {"extra": 5})


def test_keyword_only_argument_overrides_default():
    bindings = run_eval_loop(
        code=(
            "def configure(*, scale=2, **kwargs):\n"
            "    return scale, kwargs\n"
            "result = configure(scale=3, extra=5)\n"
        )
    )

    assert bindings["result"] == (3, {"extra": 5})


def test_positional_only_argument_uses_position():
    bindings = run_eval_loop(
        code=(
            "def label(value, /):\n"
            "    return value\n"
            "result = label(3)\n"
        )
    )

    assert bindings["result"] == 3


def test_positional_only_argument_ignores_keyword_binding():
    bindings = run_eval_loop(
        code=(
            "def label(value, /, **kwargs):\n"
            "    return kwargs['value']\n"
            "result = label(value=3)\n"
        )
    )

    assert bindings["result"] == 3
