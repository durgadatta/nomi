"""Independent judgments for the bounded S1 source-analysis experiment."""

import ast
import hashlib
import json

import pytest

from prototype.analysis import AnalysisPolicy, analyze_ast


def check(source, requirements=("known-types", "pure")):
    return analyze_ast(
        ast.parse(source), source=source, filename="invoice.py",
        policy=AnalysisPolicy(requirements=requirements),
    )


def binding(result, name):
    return [fact for fact in result.facts if fact["kind"] == "binding"
            and fact["name"] == name][-1]


def codes(result):
    return {item["code"] for item in result.obligations}


def test_scalar_invoice_needs_no_declarations():
    source = "price = 1200\nquantity = 3\ntotal = price * quantity\n"
    result = check(source)
    assert result.admitted and result.ok
    assert binding(result, "total")["type"] == "Int"
    assert result.effects == ()
    assert result.obligations == ()
    report = json.loads(json.dumps(result.to_dict()))
    assert report["source"]["sha256"] == hashlib.sha256(source.encode()).hexdigest()
    assert report["scope"] == "module-execution"
    assert report["analyzer"]["version"] == 1


def test_scalar_call_is_specialized_evidence_not_a_public_interface():
    result = check("def invoice(price, quantity):\n    return price * quantity\n"
                   "total = invoice(1200, 3)\n")
    assert result.admitted
    assert binding(result, "total")["type"] == "Int"
    call = next(fact for fact in result.facts if fact["kind"] == "call")
    assert call["provenance"] == "direct-call-context"
    assert call["argument_types"] == {"price": "Int", "quantity": "Int"}
    assert result.latent_functions[0]["public_contract"] == "unproved"


def test_policies_select_obligations_without_changing_facts():
    source = "total = 3 * 1200\nprint(total)\n"
    reports = [check(source, requirements) for requirements in (
        (), ("known-types",), ("pure",), ("known-types", "pure"))]
    assert [item.admitted for item in reports] == [True, True, False, False]
    assert all(item.facts == reports[0].facts for item in reports)
    assert all(item.obligations == reports[0].obligations for item in reports)
    assert all(item.effects == ("ConsoleWrite",) for item in reports)


def test_an_uncalled_function_does_not_execute_its_body():
    result = check("def later(value):\n    print(value)\nanswer = 42\n")
    assert result.admitted
    assert result.effects == ()
    assert result.latent_functions[0]["potential_effects"] == ["ConsoleWrite"]
    assert result.latent_functions[0]["status"] == "latent-unchecked"


@pytest.mark.parametrize("source", [
    "import remote\nvalue = remote.read()\n",
    "value = missing()\nanswer = value + 1\n",
    "def f(value):\n    return f(value)\nanswer = f(1)\n",
    "captured = 1\ndef f():\n    return captured\nanswer = f()\n",
    "answer = 1\nif flag:\n    answer = 'text'\nresult = answer + 1\n",
    "def f(value=external()):\n    return value\nanswer = f()\n",
    "def outer():\n    def inner():\n        return 1\n    return inner()\nanswer = outer()\n",
])
def test_unproved_programs_fail_both_restrictions(source):
    result = check(source)
    assert not result.admitted
    assert all(not restriction["satisfied"] for restriction in result.restrictions)
    assert all(obligation["span"]["line"] >= 1 for obligation in result.obligations)
    assert all(obligation["repair"] for obligation in result.obligations)


def test_annotations_cannot_launder_unknown_values():
    result = check("answer: Int = missing()\n")
    assert not result.admitted
    assert binding(result, "answer")["type"] is None
    assert "annotation-unverified" in codes(result)


def test_a_contradictory_annotation_is_reported():
    result = check("answer: Int = 'wrong'\n")
    assert "annotation-mismatch" in codes(result)
    assert not result.admitted


def test_rebinding_and_builtin_shadowing_use_current_bindings():
    result = check("value = 1\nvalue = 'text'\nanswer = value + '! '\n"
                   "def print(value):\n    return value + 1\nresult = print(3)\n")
    assert result.admitted
    assert binding(result, "answer")["type"] == "Text"
    assert binding(result, "result")["type"] == "Int"
    assert result.effects == ()


def test_unknown_calls_invalidate_previously_known_bindings_and_prelude():
    result = check("def f():\n    return 1\nx = 2\nunknown()\n"
                   "result = f()\nnext_value = x + 1\nprinted = print(1)\n")
    assert not result.admitted
    assert binding(result, "result")["type"] is None
    assert binding(result, "next_value")["type"] is None
    assert binding(result, "printed")["type"] is None


def test_unknown_argument_can_mutate_a_previously_resolved_callee():
    result = check("def f(x):\n    return 1\nresult = f(unknown())\n")
    assert binding(result, "result")["type"] is None


def test_unknown_operator_can_invalidate_facts_through_overloads():
    result = check("def f():\n    return 1\nvalue = external + 1\nresult = f()\n")
    assert binding(result, "result")["type"] is None
    assert "operator-unproved" in codes(result)


def test_function_local_name_does_not_fall_back_to_a_global():
    result = check("def f():\n    before = print(1)\n    print = 3\n    return before\n"
                   "result = f()\n")
    assert not result.admitted
    assert "unbound-local" in codes(result)


def test_keyword_arguments_and_multiple_known_calls():
    result = check("def multiply(left, right):\n    return left * right\n"
                   "one = multiply(right=3, left=2)\ntwo = multiply(2.0, 4)\n")
    assert result.admitted
    assert binding(result, "one")["type"] == "Int"
    assert binding(result, "two")["type"] == "Float"


def test_unsupported_embedded_metadata_is_not_silently_ignored():
    source = "x = 1\n"
    tree = ast.parse(source)
    tree.body[0]._nomi_where_body = ast.parse("print('effect')").body
    result = analyze_ast(tree, source=source,
                         policy=AnalysisPolicy(requirements=("pure",)))
    assert not result.admitted
    assert "unsupported-metadata" in codes(result)


def test_source_analysis_never_calls_or_imports_user_code(tmp_path):
    marker = tmp_path / "must-not-exist"
    source = f"import pathlib\npathlib.Path({str(marker)!r}).write_text('ran')\n"
    result = check(source)
    assert not marker.exists()
    assert not result.admitted


@pytest.mark.parametrize("kwargs", [
    {"requirements": ("unsafe",)}, {"requirements": "pure"},
    {"requirements": ("pure", "pure")}, {"version": 2}, {"version": True},
])
def test_invalid_policy_fails_closed(kwargs):
    with pytest.raises((ValueError, TypeError)):
        AnalysisPolicy(**kwargs)


def test_analysis_work_is_bounded_across_repeated_nested_calls():
    parts = ["def f0():\n    return 1\n"]
    parts.extend(f"def f{i}():\n    a = f{i - 1}()\n    return f{i - 1}()\n"
                 for i in range(1, 18))
    result = check("".join(parts) + "value = f17()\n")
    assert not result.admitted
    assert "analysis-limit" in codes(result)


def test_lark_frontend_does_not_claim_fabricated_source_positions():
    from prototype.parser.nomi.usage import generate_ast

    source = "func invoice(price, quantity):\n    return price * quantity\n" \
             "total = invoice(1200, 3)\n"
    tree = generate_ast(code=source, preserve_positions=True)
    result = analyze_ast(tree, source=source, frontend="lark-lalr",
                         policy=AnalysisPolicy(requirements=("known-types", "pure")))
    assert result.admitted
    assert binding(result, "total")["type"] == "Int"
    assert all(fact["span"] is None for fact in result.facts)


def test_lark_unknown_has_an_explicitly_unavailable_span():
    from prototype.parser.nomi.usage import generate_ast

    source = "answer = missing()\n"
    result = analyze_ast(generate_ast(code=source), source=source, frontend="lark-lalr",
                         policy=AnalysisPolicy(requirements=("pure",)))
    assert not result.admitted
    assert all(item["span"] is None for item in result.obligations)


def test_empty_lark_module_is_analyzed():
    from prototype.parser.nomi.usage import generate_ast

    source = "\n"
    result = analyze_ast(generate_ast(code=source), source=source, frontend="lark-lalr",
                         policy=AnalysisPolicy(requirements=("known-types", "pure")))
    assert result.admitted
    assert result.facts == ()


@pytest.mark.parametrize("source", [
    "def f(a):\n    return a\nanswer = f()\n",
    "def f(a):\n    return a\nanswer = f(1, 2)\n",
    "def f(a):\n    return a\nanswer = f(1, a=2)\n",
    "def f(a, /):\n    return a\nanswer = f(a=1)\n",
    "def f(*args):\n    return 1\nanswer = f(1)\n",
    "def f(**args):\n    return 1\nanswer = f(a=1)\n",
    "def f(a):\n    return a\nanswer = f(**unknown)\n",
])
def test_unchecked_argument_binding_is_not_admitted(source):
    assert not check(source).admitted


def test_required_keyword_only_arguments_are_checked():
    result = check("def f(a, *, b):\n    return a + b\nanswer = f(1, b=2)\n")
    assert result.admitted
    assert binding(result, "answer")["type"] == "Int"


def test_annotations_can_replace_current_environment_facts():
    result = check("def f():\n    return 1\nx: constraint = 1\nanswer = f()\n")
    assert not result.admitted
    assert binding(result, "answer")["type"] is None


def test_huge_numeric_expression_is_never_evaluated_to_infer_type():
    result = check("answer = 10 ** 1000000000000000000000000\n")
    assert not result.admitted
    assert "operator-unproved" in codes(result)


def test_separate_calls_do_not_generalize_a_first_call_result():
    result = check("def identity(value):\n    return value\n"
                   "one = identity(1)\ntext = identity('text')\n")
    assert result.admitted
    assert binding(result, "one")["type"] == "Int"
    assert binding(result, "text")["type"] == "Text"


def test_function_rebinding_changes_the_next_call_contract():
    result = check("def f():\n    return 1\nfirst = f()\n"
                   "def f():\n    return 'text'\nsecond = f()\n")
    assert result.admitted
    assert binding(result, "first")["type"] == "Int"
    assert binding(result, "second")["type"] == "Text"


def test_function_resolves_current_global_function_binding():
    result = check("def helper():\n    return 1\ndef f():\n    return helper()\n"
                   "def helper():\n    return 'text'\nanswer = f()\n")
    assert result.admitted
    assert binding(result, "answer")["type"] == "Text"


def test_print_of_unknown_value_has_unknown_conversion_effects():
    result = check("print(unknown)\n")
    assert not result.admitted
    assert "print-unproved" in codes(result)


def test_a_later_return_does_not_invent_unconditional_reachability():
    result = check("def f(flag):\n    if flag:\n        return 'text'\n    return 1\n"
                   "answer = f(True)\n")
    assert not result.admitted
    assert "function-body-unproved" in codes(result)
    assert binding(result, "answer")["type"] is None


def test_previously_bound_names_after_unknown_code_are_only_historical_facts():
    result = check("x = 1\nunknown()\ny = x\n")
    assert binding(result, "x")["type"] == "Int"
    assert binding(result, "x")["span"]["line"] == 1
    assert binding(result, "y")["type"] is None


def test_generator_construction_does_not_claim_its_return_or_execute_latent_print():
    result = check("def f():\n    print(1)\n    yield 2\n    return 3\nanswer = f()\n")
    assert not result.admitted
    assert binding(result, "answer")["type"] is None
    assert result.effects == ()
    assert "function-convention-unproved" in codes(result)


def test_import_local_shadowing_cannot_produce_a_prelude_call_fact():
    result = check("def f():\n    print(1)\n    import print\nanswer = f()\n")
    assert not result.admitted
    assert result.effects == ()
    assert binding(result, "answer")["type"] is None
