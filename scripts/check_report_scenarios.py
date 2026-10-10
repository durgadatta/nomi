"""Report validation, repair and explicit JSON publication in the real browser."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def check_report_scenarios(page, expect, artifacts, *, legacy=False):
    source = (ROOT / "samples/report.nomi").read_text(encoding="utf-8")
    fixtures = json.loads(
        (ROOT / "prototype/tests/data/report_boundary/v1.json").read_text()
    )["cases"]
    expected_wire = next(
        case["expected"]["text"] for case in fixtures if case["id"] == "report-wire"
    )
    page.locator('[data-sample="report"]').click()
    expect(page.locator("#current-file")).to_have_text("report.nomi")
    assert page.evaluate("currentDocumentCode()") == source
    page.locator("#run-all-btn").click()
    output = page.locator('[data-result-view="output"] pre')
    expect(output).to_have_text(expected_wire)
    expect(page.locator("#status")).to_have_text("ready")
    if not legacy:
        report = page.evaluate("_cellResults[0].bindings.result.report")
        assert report == json.loads(expected_wire)
        page.get_by_role("tab", name="Bindings", exact=False).click()
        download = page.get_by_role("button", name="Download wire as JSON", exact=True)
        expect(download).to_be_enabled()
        with page.expect_download() as downloaded:
            download.click()
        assert downloaded.value.suggested_filename == "wire.json"
        assert Path(downloaded.value.path()).read_bytes() == expected_wire.encode(
            "utf-8"
        )

        # Failure to initiate a download must preserve the inspectable report.
        page.evaluate("""() => {
          window._savedCreateObjectURL = URL.createObjectURL;
          URL.createObjectURL = () => { throw new Error('injected save failure'); };
        }""")
        try:
            download.click()
            expect(page.locator("#toast")).to_contain_text("Could not download JSON")
            assert page.evaluate("_cellResults[0].bindings.result.report") == report
            expect(download).to_be_enabled()
        finally:
            page.evaluate(
                "() => { URL.createObjectURL = window._savedCreateObjectURL; }"
            )

    broken = source.replace('"name":" Ada "', '"name":""').replace(
        '"age":20', '"age":-1'
    )
    page.evaluate("source => _cellEditors[0].setValue(source)", broken)
    expect(page.locator(".result-stale")).to_be_visible()
    if not legacy:
        expect(download).to_be_disabled()
    page.get_by_role("tab", name="Output", exact=True).click()
    page.locator("#run-all-btn").click()
    expect(output).to_contain_text("$.customers[0].name")
    expect(output).to_contain_text("$.customers[0].age")
    expect(output).not_to_contain_text(expected_wire)
    expect(page.locator("#status")).to_have_text("ready")
    if not legacy:
        bindings = page.evaluate("_cellResults[0].bindings")
        result = bindings["result"]
        assert result["ok"] is False and "report" not in result
        assert [error["path"] for error in result["failure"]["errors"]] == [
            ["customers", 0, "name"],
            ["customers", 0, "age"],
        ]
        assert bindings["wire"] is None
        expect(page.locator(".result-download")).to_have_count(0)

        # Encoding is a separate action; failure cannot erase a valid report.
        unencodable = source.replace(
            "return encode_json(report)", "return encode_json(1.5)"
        )
        page.evaluate("source => _cellEditors[0].setValue(source)", unencodable)
        page.locator("#run-all-btn").click()
        expect(output).to_contain_text("NOMI-ENCODE-TYPE")
        assert page.evaluate("_cellResults[0].bindings.result.report") == report
        expect(page.locator(".result-download")).to_have_count(0)

    page.evaluate("source => _cellEditors[0].setValue(source)", source)
    page.locator("#run-all-btn").click()
    expect(output).to_have_text(expected_wire)
    expect(page.locator("#status")).to_have_text("ready")
    expect(page.locator(".result-stale")).to_be_hidden()
    if not legacy:
        page.get_by_role("tab", name="Bindings", exact=False).click()
        expect(
            page.get_by_role("button", name="Download wire as JSON", exact=True)
        ).to_be_enabled()
    page.screenshot(
        path=str(
            artifacts
            / ("report-legacy-repaired.png" if legacy else "report-repaired.png")
        ),
        full_page=True,
    )
    page.get_by_role("tab", name="Output", exact=True).click()
