"""Check first-open example discovery and returning-file restoration."""


def check_learning_path_scenarios(page, expect, artifacts):
    expect(page.locator("#current-file")).to_have_text("calculate.nomi")
    expect(page.locator(".sample-group-label")).to_have_text(
        ["Start here", "Data and text", "Experiments"]
    )
    expect(page.locator('.sample[data-sample="calculate"]')).to_have_attribute(
        "aria-current", "page"
    )
    expect(page.locator('[data-sample="terse"] .sample-desc')).to_contain_text(
        "Experiment"
    )
    search = page.locator("#sample-search")
    search.fill("start here")
    expect(page.locator(".sample:not(.hidden)")).to_have_count(2)
    search.fill("experiment")
    expect(page.locator(".sample:not(.hidden)")).to_have_count(9)
    search.fill("")
    expect(page.get_by_role("link", name="User guide")).to_have_attribute(
        "href", "https://github.com/durgadatta/nomi/blob/main/docs/guide/README.md"
    )
    page.screenshot(path=str(artifacts / "learning-path.png"), full_page=True)

    page.locator('[data-sample="text-pipeline"]').click()
    expect(page.locator("#current-file")).to_have_text("text_pipeline.nomi.nb")
    page.reload(wait_until="domcontentloaded")
    expect(page.locator("#loading")).to_be_hidden(timeout=60_000)
    expect(page.locator("#current-file")).to_have_text("text_pipeline.nomi.nb")
    expect(page.locator("#status")).to_have_text("ready")
