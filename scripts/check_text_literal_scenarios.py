"""Unsupported browser literal diagnostics and an explicit source repair."""


def check_text_literal_scenarios(page, expect, artifacts):
    page.locator('[data-sample="calculate"]').click()
    expect(page.locator("#current-file")).to_have_text("calculate.nomi")
    for literal in ['f"Hello {name}"', 'b"Hello"']:
        source = "name = 'Ada'\nprint('before')\nprint(" + literal + ")\n"
        page.evaluate("source => _cellEditors[0].setValue(source)", source)
        page.locator("#run-all-btn").click()
        expect(page.locator('[data-result-count="diagnostics"]')).to_have_text("1")
        page.get_by_role("tab", name="Diagnostics", exact=False).click()
        expect(page.locator('[data-result-view="diagnostics"]')).to_contain_text("not supported by the browser prototype")
        expect(page.locator('[data-result-view="diagnostics"]')).to_contain_text(literal)
        record = page.evaluate("_cellResults[0]")
        assert not record["ok"]
        assert record["diagnostics"][0]["code"] == "NOMI-UNSUPPORTED-LITERAL"
        assert record["diagnostics"][0]["source_excerpt"] == literal
        assert "before" not in record.get("stdout", "")
    page.screenshot(path=str(artifacts / "text-literal-refusal.png"), full_page=True)

    page.evaluate("source => _cellEditors[0].setValue(source)", "name = 'Ada'\nprint('Hello ' + name)\n")
    page.locator("#run-all-btn").click()
    expect(page.locator('[data-result-count="diagnostics"]')).to_have_text("0")
    page.get_by_role("tab", name="Output", exact=True).click()
    expect(page.locator('[data-result-view="output"] pre')).to_have_text("Hello Ada")
    expect(page.locator("#status")).to_have_text("ready")
