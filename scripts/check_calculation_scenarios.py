"""The calculation/edit/error/repair journey through the actual browser UI."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def check_calculation_scenarios(page, expect, artifacts):
    source = (ROOT / "samples/calculate.nomi").read_text(encoding="utf-8")
    page.locator('[data-sample="calculate"]').click()
    expect(page.locator("#current-file")).to_have_text("calculate.nomi")
    assert page.evaluate("currentDocumentCode()") == source
    expect(page.locator('[data-result-view="output"] pre')).to_be_hidden()
    page.locator("#run-all-btn").click()
    output = page.locator('[data-result-view="output"] pre')
    expect(output).to_have_text("3850")
    expect(page.locator("#status")).to_have_text("ready")

    edited = source.replace("quantity = 3", "quantity = 4")
    page.evaluate("source => _cellEditors[0].setValue(source)", edited)
    expect(page.locator(".result-stale")).to_be_visible()
    page.locator("#run-all-btn").click()
    expect(output).to_have_text("5050")
    expect(page.locator(".result-stale")).to_be_hidden()

    wrong = source.replace("quantity = 3", 'quantity = "three"')
    page.evaluate("source => _cellEditors[0].setValue(source)", wrong)
    page.locator("#run-all-btn").click()
    expect(page.locator("#status")).to_have_text("error")
    expect(page.locator(".diagnostic-message")).to_contain_text("Text and Int")
    expect(page.locator(".diagnostic-message")).to_contain_text("convert external text explicitly")
    failure = page.evaluate("_cellResults[0]")
    assert failure["ok"] is False
    assert failure["stdout"] == ""
    assert failure["diagnostics"][0]["code"] == "NOMI-OPERAND-TYPE"
    page.get_by_role("tab", name="Output", exact=True).click()
    expect(output).to_contain_text("eval error:")
    expect(output).not_to_contain_text("5050")

    page.evaluate("source => _cellEditors[0].setValue(source)", source)
    page.locator("#run-all-btn").click()
    expect(output).to_have_text("3850")
    expect(page.locator("#status")).to_have_text("ready")
    expect(page.locator('[data-result-count="diagnostics"]')).to_have_text("0")
    with page.expect_download() as download_info:
        page.get_by_role("button", name="Download source", exact=True).click()
    assert Path(download_info.value.path()).read_text(encoding="utf-8") == source
    page.screenshot(path=str(artifacts / "calculation-repaired.png"), full_page=True)
