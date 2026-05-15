from prototype.interpreter.helpers import get_run_eval_loop


# ── basic product types ──────────────────────────────────────────────

def test_data_simple_typed_fields(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "data Point:",
        "    x: int",
        "    y: int",
        "",
        "p = Point(x=1, y=2)",
        "r1 = p.x",
        "r2 = p.y",
        "",
    ]))
    assert bindings["r1"] == 1
    assert bindings["r2"] == 2


def test_data_equality(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "data Point:",
        "    x: int",
        "    y: int",
        "",
        "r1 = Point(x=1, y=2) == Point(x=1, y=2)",
        "r2 = Point(x=1, y=2) == Point(x=3, y=4)",
        "",
    ]))
    assert bindings["r1"] is True
    assert bindings["r2"] is False


def test_data_repr(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "data Point:",
        "    x: int",
        "    y: int",
        "",
        "r1 = repr(Point(x=10, y=20))",
        "",
    ]))
    assert bindings["r1"] == "Point(x=10, y=20)"


# ── constraints ──────────────────────────────────────────────────────

def test_data_constraint_passes(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "data User:",
        "    name: str",
        "    age: int where age >= 0",
        "",
        "user = User(name='alice', age=25)",
        "r1 = user.age",
        "",
    ]))
    assert bindings["r1"] == 25


def test_data_constraint_violation_raises(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    try:
        run(code="\n".join([
            "data User:",
            "    name: str",
            "    age: int where age >= 0",
            "",
            "user = User(name='bob', age=-5)",
            "",
        ]))
        assert False, "Should have raised"
    except RuntimeError:
        pass


def test_data_constraint_without_type(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "data Pos:",
        "    x where x > 0",
        "    y where y > 0",
        "",
        "p = Pos(x=10, y=20)",
        "r1 = p.x",
        "r2 = p.y",
        "",
    ]))
    assert bindings["r1"] == 10
    assert bindings["r2"] == 20


def test_data_constraint_without_type_violation_raises(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    try:
        run(code="\n".join([
            "data Pos:",
            "    x where x > 0",
            "",
            "p = Pos(x=-1)",
            "",
        ]))
        assert False, "Should have raised"
    except RuntimeError:
        pass


# ── bare and mixed fields ────────────────────────────────────────────

def test_data_bare_field_no_type(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "data Pair:",
        "    first",
        "    second",
        "",
        "p = Pair(first=1, second=2)",
        "r1 = p.first",
        "r2 = p.second",
        "",
    ]))
    assert bindings["r1"] == 1
    assert bindings["r2"] == 2


def test_data_mixed_typed_and_bare_fields(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "data Person:",
        "    name: str",
        "    age",
        "    active where active == True",
        "",
        "p = Person(name='alice', age=30, active=True)",
        "r1 = p.name",
        "r2 = p.age",
        "r3 = p.active",
        "",
    ]))
    assert bindings["r1"] == "alice"
    assert bindings["r2"] == 30
    assert bindings["r3"] is True


def test_data_repr_with_bare_fields(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "data Simple:",
        "    x",
        "",
        "r1 = repr(Simple(x=42))",
        "",
    ]))
    assert bindings["r1"] == "Simple(x=42)"


# ── single-field data ─────────────────────────────────────────────────

def test_data_single_field(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "data Wrapper:",
        "    value",
        "",
        "w = Wrapper(value=99)",
        "r1 = w.value",
        "r2 = repr(w)",
        "",
    ]))
    assert bindings["r1"] == 99
    assert bindings["r2"] == "Wrapper(value=99)"
