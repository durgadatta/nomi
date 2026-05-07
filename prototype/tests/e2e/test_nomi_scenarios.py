from prototype.interpreter.nomi.usage import run_eval_loop


def test_validation_functions_and_match_work_together():
    bindings = run_eval_loop(
        code=(
            "is_positive = (x) => x > 0\n"
            "score: int, is_positive = 72\n"
            "func grade(value):\n"
            "    match value:\n"
            "        case 100:\n"
            "            return 'perfect'\n"
            "        case _:\n"
            "            return 'regular'\n"
            "label = grade(score)\n"
        )
    )

    assert bindings["score"] == 72
    assert bindings["label"] == "regular"


def test_block_iteration_data_pipeline_scenario():
    bindings = run_eval_loop(
        code=(
            "func each(items):\n"
            "    for item in items:\n"
            "        yield item\n"
            "data = [1, -2, 3, 8]\n"
            "total = 0\n"
            "each(data) -> item:\n"
            "    if item > 0:\n"
            "        total += item\n"
        )
    )

    assert bindings["total"] == 12
    assert bindings["item"] == 8


def test_retry_style_yield_to_block_scenario():
    bindings = run_eval_loop(
        code=(
            "func retry(max_attempts):\n"
            "    for attempt in range(max_attempts):\n"
            "        try:\n"
            "            yield\n"
            "            return attempt + 1\n"
            "        except ValueError:\n"
            "            if attempt == max_attempts - 1:\n"
            "                raise\n"
            "attempts = 0\n"
            "retry(3):\n"
            "    attempts += 1\n"
            "    if attempts < 3:\n"
            "        raise ValueError('again')\n"
            "success = attempts\n"
        )
    )

    assert bindings["attempts"] == 3
    assert bindings["success"] == 3


def test_nested_functions_constraints_and_nonlocal_scenario():
    bindings = run_eval_loop(
        code=(
            "func make_counter(start: (int, start >= 0)):\n"
            "    value = start\n"
            "    func bump(step=1):\n"
            "        nonlocal value\n"
            "        value += step\n"
            "        return value\n"
            "    return bump\n"
            "counter = make_counter(2)\n"
            "first = counter()\n"
            "second = counter(3)\n"
        )
    )

    assert bindings["first"] == 3
    assert bindings["second"] == 6
