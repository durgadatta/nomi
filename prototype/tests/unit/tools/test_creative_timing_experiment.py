"""Independent literal cases for the isolated timing/revision model."""

import json

import pytest

from tools import creative_timing_experiment as experiment


MODELS, CASES = experiment.load_fixtures()


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_supplied_model_matches_literal_expectations(case):
    observation = experiment.run_case(MODELS, case)

    assert experiment.differences(observation, case["expect"]) == {}


def test_expectation_comparison_does_not_equate_bool_and_integer():
    mismatches = experiment.differences(
        {"revision": 1, "values": [1]}, {"revision": True, "values": [True]}
    )

    assert set(mismatches) == {"revision", "values"}


@pytest.mark.parametrize("invalid", [[1, 0], [1, -1], [True, 1], [1.0, 1], "1/"])
def test_time_ratio_refuses_undefined_or_host_coerced_values(invalid):
    with pytest.raises(ValueError):
        experiment.ratio(invalid)


def test_new_run_identity_cannot_overwrite_retained_history():
    case = {
        "model": "beat",
        "steps": [{"op": "run", "run_id": "one"}, {"op": "run", "run_id": "one"}],
    }

    with pytest.raises(ValueError, match="cannot be reused"):
        experiment.run_case(MODELS, case)


def test_fixture_without_cases_cannot_pass_vacuously(tmp_path):
    fixture = json.loads(experiment.FIXTURES.read_text())
    fixture["cases"] = []
    path = tmp_path / "empty.json"
    path.write_text(json.dumps(fixture))

    with pytest.raises(ValueError, match="needs models and cases"):
        experiment.load_fixtures(path)


def test_unknown_expectation_path_cannot_be_ignored():
    with pytest.raises(ValueError, match="unknown expectation path"):
        experiment.differences({"model": {"revision": 1}}, {"model.rev": 1})


def test_unknown_case_cannot_report_a_successful_empty_selection(capsys):
    with pytest.raises(SystemExit) as error:
        experiment.main(["--check", "--case", "missing"])

    assert error.value.code == 2
    assert "unknown case" in capsys.readouterr().err


def test_observation_output_discloses_scope_and_old_run(capsys):
    assert experiment.main(["--case", "late-run-keeps-old-basis"]) == 0
    result = json.loads(capsys.readouterr().out)

    assert result["scope"] == experiment.SCOPE
    assert result["host"]["python"]
    assert result["execution"] == {
        "nomi": False,
        "device": False,
        "concurrency": False,
        "human": False,
    }
    run = result["cases"][0]["observation"]["runs"]["old"]
    assert run["relation_to_current"] == "older_revision"
    assert run["external_outcome"] == "unobserved"


def test_wrong_literal_oracle_makes_check_fail_without_rewriting(tmp_path, capsys):
    fixture = json.loads(experiment.FIXTURES.read_text())
    fixture["cases"] = [fixture["cases"][0]]
    fixture["cases"][0]["expect"] = {"model.revision": 999}
    path = tmp_path / "wrong.json"
    original = json.dumps(fixture)
    path.write_text(original)

    assert experiment.main(["--fixtures", str(path), "--check"]) == 1
    assert "FAIL" in capsys.readouterr().out
    assert path.read_text() == original
