"""Independent metadata expectations for a fenced AI description profile."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.ai_probe import DTYPES, OPERATIONS, Program
from tools.object_interface.documents import ContractError

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "docs/research/data_workflows/ai_linear_program.json"


def source():
    return json.loads(FIXTURE.read_text())


def row(document, identity):
    return next(row for row in document["objects"] if row["id"] == identity)


def test_loss_program_is_checkable_without_weights_data_or_framework():
    report = Program(source()).check()
    prediction = row(report, "prediction")
    loss = row(report, "loss")
    assert prediction["axes"] == ["batch", "outputs"]
    assert prediction["extents"] == ["N", 1]
    assert prediction["leaf_dependencies"] == ["bias", "features", "weights"]
    assert loss["axes"] == []
    assert loss["leaf_dependencies"] == ["bias", "features", "target", "weights"]
    assert report["backend"]["status"] == "unknown"
    assert report["scope"]["derivatives"] == "not-produced"
    assert report["scope"]["execution"] == "not-run"
    assert report["scope"]["numerical-correctness"] == "not-established"


def test_equal_size_different_axes_cannot_contract():
    document = source()
    document["axes"].append({"id": "tokens", "extent": 32})
    row(document, "weights")["axes"][0] = "tokens"
    with pytest.raises(ContractError, match="contracting axis identities differ"):
        Program(document)


def test_bias_broadcast_is_explicit_not_inferred_from_extents():
    document = source()
    row(document, "prediction")["args"][1] = "bias"
    with pytest.raises(ContractError, match="broadcast explicitly"):
        Program(document)


def test_broadcast_cannot_drop_or_reorder_axes():
    document = source()
    row(document, "bias_batch")["axes"] = ["batch", "features"]
    with pytest.raises(ContractError, match="retain ordered source axes"):
        Program(document)


def test_same_operand_twice_preserves_ordered_application():
    document = source()
    row(document, "prediction")["args"] = ["projection", "projection"]
    assert row(Program(document).check(), "prediction")["leaf_dependencies"] == [
        "features",
        "weights",
    ]


def test_forward_references_are_resolved_and_disconnected_objects_checked():
    document = source()
    document["objects"].reverse()
    assert row(Program(document).check(), "loss")["axes"] == []
    document["objects"].append(
        {"id": "unused", "op": "input", "axes": ["missing"], "dtype": "Float32"}
    )
    with pytest.raises(ContractError, match="unknown axis"):
        Program(document)


def test_snapshots_reports_and_named_explanations_are_detached():
    document = source()
    program = Program(document)
    original = program.check()
    document["revision"] += 1
    program.document["revision"] += 1
    report = program.explain("prediction")
    report["object"]["axes"].clear()
    assert program.check() == original
    assert Program(document).check()["context"] != original["context"]
    with pytest.raises(AttributeError):
        program._source = "{}"
    with pytest.raises(ContractError, match="unknown tensor object"):
        program.explain("absent")


def test_backend_support_is_a_declaration_not_a_verified_kernel():
    descriptor = {
        "id": "mock",
        "revision": 0,
        "operations": list(OPERATIONS),
        "dtypes": list(DTYPES),
    }
    program = Program(source())
    supported = program.check(descriptor)
    assert supported["backend"]["status"] == "declared-coverage"
    assert supported["scope"]["execution"] == "not-run"
    original = deepcopy(descriptor)
    descriptor["operations"].remove("matmul")
    unsupported = program.check(descriptor)
    assert unsupported["backend"]["status"] == "unsupported"
    assert unsupported["backend"]["missing_objects"] == ["projection"]
    assert supported["context"] == unsupported["context"]
    assert supported["backend"]["context"] != unsupported["backend"]["context"]
    assert original["operations"] == list(OPERATIONS)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(version=True),
        lambda d: d.update(profile="unknown"),
        lambda d: d.update(revision=-1),
        lambda d: d.update(values=[1]),
        lambda d: d.update(outputs=[]),
        lambda d: d.update(outputs=["absent"]),
        lambda d: d.update(outputs=["loss", "loss"]),
        lambda d: d.update(extent_variables=["N", "N"]),
        lambda d: d["axes"][0].update(extent="N+1"),
        lambda d: d["axes"][0].update(extent=0),
        lambda d: d["axes"][0].update(extent=True),
        lambda d: d["axes"][0].update(extent=1.5),
        lambda d: d["axes"].append(d["axes"][0]),
        lambda d: row(d, "weights").update(dtype="Int"),
        lambda d: row(d, "weights").update(dtype="Float64"),
        lambda d: row(d, "weights").update(axes=["features", "features"]),
        lambda d: row(d, "weights").update(axes=["features"]),
        lambda d: row(d, "prediction").update(args=["absent", "projection"]),
        lambda d: row(d, "prediction").update(args=["prediction", "projection"]),
        lambda d: row(d, "prediction").update(args=["projection"]),
        lambda d: row(d, "prediction").update(op="host_callback"),
        lambda d: row(d, "prediction").update(effects=["Network"]),
        lambda d: d["objects"].append(d["objects"][0]),
    ],
)
def test_unsupported_or_malformed_programs_refuse_before_execution(mutate):
    document = source()
    mutate(document)
    with pytest.raises(ContractError):
        Program(document)


def test_generic_axis_vocabulary_does_not_import_an_ai_interpretation():
    document = source()
    mapping = {"batch": "scenarios", "features": "basis", "outputs": "responses"}
    for axis in document["axes"]:
        axis["id"] = mapping[axis["id"]]
    for object_row in document["objects"]:
        if "axes" in object_row:
            object_row["axes"] = [mapping[axis] for axis in object_row["axes"]]
    assert row(Program(document).check(), "prediction")["axes"] == [
        "scenarios",
        "responses",
    ]


def test_cli_reports_checked_metadata_and_backend_refusal(tmp_path):
    checked = subprocess.run(
        [sys.executable, "-m", "tools.ai_probe", str(FIXTURE), "--object", "loss"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert checked.returncode == 0
    assert json.loads(checked.stdout)["object"]["axes"] == []
    backend = tmp_path / "backend.json"
    backend.write_text(
        json.dumps({"id": "empty", "revision": 0, "operations": [], "dtypes": []})
    )
    missing = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.ai_probe",
            str(FIXTURE),
            "--backend",
            str(backend),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert missing.returncode == 1
    assert json.loads(missing.stdout)["backend"]["status"] == "unsupported"
    bad = subprocess.run(
        [sys.executable, "-m", "tools.ai_probe", str(FIXTURE), "--object", "absent"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert bad.returncode == 2
