"""Extended UI scenarios called by the playground's Chromium release gate."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_workbench_scenarios(page, expect, artifacts):
    def set_source(source):
        page.evaluate("source => _cellEditors[0].setValue(source)", source)

    def run_source(source, expected):
        set_source(source)
        page.locator("#run-all-btn").click()
        expect(page.locator('[data-result-view="output"] pre').first).to_have_text(
            expected
        )
        expect(page.locator("#status")).to_have_text("ready")

    # The data sample exercises multiline parsing plus data-first fold insertion.
    page.locator('[data-sample="data-pipeline"]').click()
    page.locator("#run-all-btn").click()
    expect(page.locator('[data-result-view="output"] pre')).to_have_text(
        "Paid orders: 2\nAmounts in cents: [900, 360]\nTotal in cents: 1260\n"
        "Running cents, including seed: [0, 900, 1260]\nEmpty batch total: 0"
    )
    expect(page.locator("#status")).to_have_text("ready")
    page.get_by_role("tab", name="Bindings", exact=False).click()
    page.screenshot(path=str(artifacts / "data-bindings.png"), full_page=True)
    page.get_by_role("tab", name="Bindings", exact=False).press("ArrowRight")
    expect(page.get_by_role("tab", name="Diagnostics", exact=False)).to_be_focused()
    handle = page.get_by_role("separator", name="Resize result pane")
    handle.focus()
    old_width = float(handle.get_attribute("aria-valuenow"))
    handle.press("ArrowLeft")
    assert float(handle.get_attribute("aria-valuenow")) == old_width + 5

    # Loading/exporting a notebook must not create an immediate normalized draft.
    page.locator('[data-sample="text-pipeline"]').click()
    source = (ROOT / "samples/text_pipeline.nomi.nb").read_text(encoding="utf-8")
    assert page.evaluate("currentDocumentCode()") == source
    expect(page.locator("#document-state")).to_have_text("Sample")
    expect(page.locator(".nb-cell-title").first).to_have_text(
        "Normalize and select text"
    )
    with page.expect_download() as download_info:
        page.get_by_role("button", name="Download source", exact=True).click()
    downloaded = Path(download_info.value.path()).read_text(encoding="utf-8")
    assert downloaded == source
    page.locator("#run-all-btn").click()
    expect(page.locator("#status")).to_have_text("ready")
    outputs = page.locator('[data-result-view="output"] pre')
    expect(outputs.nth(0)).to_have_text("Records: 3")
    expect(outputs.nth(1)).to_have_text("Counts: [3, 5, 2]")
    expect(outputs.nth(2)).to_have_text("Total: 10\nHistory: [0, 3, 8, 10]")
    expect(outputs.nth(3)).to_have_text(
        "Last count: 2\nFirst record prefix: ada\nCount window: [5, 2]\nReverse counts: [2, 5, 3]"
    )
    page.screenshot(path=str(artifacts / "text-notebook.png"), full_page=True)

    # Edit/diagnose/repair; locations must survive UTF-8 -> UTF-16 conversion.
    page.get_by_role("button", name="Create local scratch file").click()
    run_source(
        "text = 'a\U0001f600e\u0301'\nprint(len(text))\nprint(text[1])\nprint(text[::-1])\n",
        "4\n\U0001f600\n\u0301e\U0001f600a",
    )
    set_source("print('before')\nprint([][0])\nprint('after')\n")
    page.locator("#run-all-btn").click()
    expect(page.locator("#status")).to_have_text("error")
    expect(page.locator(".diagnostic-message")).to_contain_text("index out of range")
    page.get_by_role("tab", name="Bindings", exact=False).click()
    expect(page.locator('[data-result-view="bindings"]')).to_have_text(
        "Bindings unavailable"
    )
    page.get_by_role("tab", name="Output", exact=True).click()
    expect(page.locator('[data-result-view="output"] pre')).to_have_text("before")
    set_source('text = "\U0001f600"\nx = !\n')
    page.locator("#run-all-btn").click()
    expect(page.locator("#status")).to_have_text("error")
    expect(page.locator(".diagnostic-message")).not_to_contain_text("undefined")
    page.get_by_role("button", name="Line 2:5", exact=True).click()
    assert page.evaluate("_cellEditors[0].getPosition()") == {
        "lineNumber": 2,
        "column": 5,
    }
    page.screenshot(path=str(artifacts / "source-diagnostic.png"), full_page=True)
    run_source("print(42)\n", "42")
    set_source("print(43)\n")
    expect(page.locator(".result-stale")).to_be_visible()
    page.locator("#run-all-btn").click()
    expect(page.locator('[data-result-view="output"] pre')).to_have_text("43")
    expect(page.locator(".result-stale")).to_be_hidden()
    expect(page.locator("#status")).to_have_text("ready")

    # Real worker cancellation, followed by execution in a fresh worker.
    set_source("while True:\n    pass\n")
    page.locator("#run-all-btn").click()
    expect(page.locator("#cancel-btn")).to_be_enabled()
    page.locator("#cancel-btn").click()
    expect(page.locator("#status")).to_have_text("ready")
    expect(page.locator("#run-all-btn")).to_be_enabled()
    run_source("print(44)\n", "44")

    # A delayed real result belongs to the old document, never the new model.
    page.evaluate("""() => {
        window.originalRun = _runFn;
        _runFn = async code => { const result = await originalRun(code); await new Promise(resolve => window.releaseReply = resolve); return result; };
    }""")
    page.locator("#run-all-btn").click()
    page.wait_for_function("typeof window.releaseReply === 'function'")
    page.locator('[data-sample="terse"]').click()
    page.evaluate("window.releaseReply()")
    expect(page.locator("#status")).to_have_text("ready")
    expect(page.locator('[data-result-view="output"] pre')).to_be_hidden()
    page.locator("#run-all-btn").click()
    expect(page.locator('[data-result-view="output"] pre')).to_contain_text(
        "Nomi triage"
    )
    expect(page.locator("#status")).to_have_text("ready")

    # Import is inert; source is stored locally and recovered after reload.
    uploaded = "# %% Kept title\nprint(45)\n"
    page.locator("#open-file-input").set_input_files(
        {"name": "local.nomi.nb", "mimeType": "text/plain", "buffer": uploaded.encode()}
    )
    expect(page.locator("#current-file")).to_have_text("local.nomi.nb")
    expect(page.locator('[data-result-view="output"] pre')).to_be_hidden()
    assert page.evaluate("currentDocumentCode()") == uploaded
    page.reload(wait_until="domcontentloaded")
    expect(page.locator("#loading")).to_be_hidden(timeout=60_000)
    expect(page.locator("#current-file")).to_have_text("local.nomi.nb")
    assert page.evaluate("currentDocumentCode()") == uploaded

    # Narrow layout, real sample selection, output and bounds checks.
    page.set_viewport_size({"width": 390, "height": 844})
    if page.locator("#sidebar-toggle").get_attribute("aria-expanded") == "true":
        page.get_by_role("button", name="Toggle sample browser").click()
    expect(page.locator("#sidebar-toggle")).to_have_attribute("aria-expanded", "false")
    expect(page.locator("#sidebar")).to_be_hidden()
    assert page.locator(".result-body").bounding_box()["width"] > 360
    page.screenshot(path=str(artifacts / "mobile-empty-notebook.png"), full_page=True)
    page.get_by_role("button", name="Toggle sample browser").click()
    expect(page.locator("#sidebar-toggle")).to_have_attribute("aria-expanded", "true")
    page.locator('[data-sample="data-pipeline"]').click()
    expect(page.locator("#sidebar-toggle")).to_have_attribute("aria-expanded", "false")
    page.locator("#run-all-btn").click()
    expect(page.locator("#status")).to_have_text("ready")
    expect(page.locator('[data-result-view="output"] pre')).to_contain_text(
        "Total in cents: 1260"
    )
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    boxes = page.locator(
        ".topbar, .nb-toolbar, .nb-cell-editor, .nb-cell-output"
    ).evaluate_all(
        "nodes => nodes.map(node => { const r=node.getBoundingClientRect(); return {left:r.left,right:r.right,width:r.width,height:r.height} })"
    )
    assert all(
        box["left"] >= 0
        and box["right"] <= 391
        and box["width"] > 0
        and box["height"] > 0
        for box in boxes
    )
    page.screenshot(path=str(artifacts / "mobile-data.png"), full_page=True)
    for width, height in [(320, 740), (768, 1024), (1920, 1080)]:
        page.set_viewport_size({"width": width, "height": height})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        expect(page.locator('[data-result-view="output"] pre')).to_contain_text(
            "Total in cents: 1260"
        )
        page.screenshot(path=str(artifacts / f"layout-{width}.png"), full_page=True)
        if width == 320:
            page.evaluate("failRuntime(new Error('simulated worker failure'))")
            expect(page.locator("#run-all-btn")).to_be_disabled()
            page.get_by_role(
                "button", name="Restart runtime worker", exact=True
            ).click()
            expect(page.locator("#status")).to_have_text("ready")
            page.locator("#run-all-btn").click()
            expect(page.locator('[data-result-view="output"] pre')).to_contain_text(
                "Total in cents: 1260"
            )
            expect(page.locator("#status")).to_have_text("ready")
    page.set_viewport_size({"width": 1440, "height": 1000})

    # Uniform CRLF survives the real Monaco/import/export path.
    crlf = "# preamble\r\n# %% Kept CRLF\r\nprint(46)\r\n"
    page.locator("#open-file-input").set_input_files(
        {"name": "crlf.nomi.nb", "mimeType": "text/plain", "buffer": crlf.encode()}
    )
    expect(page.locator("#current-file")).to_have_text("crlf.nomi.nb")
    assert page.evaluate("currentDocumentCode()") == crlf

    # Invalid UTF-8 never replaces the current document or starts execution.
    page.locator("#open-file-input").set_input_files(
        {"name": "bad.nomi", "mimeType": "text/plain", "buffer": b"\xff"}
    )
    expect(page.locator("#toast")).to_have_text("Could not open UTF-8 source")
    expect(page.locator("#current-file")).to_have_text("crlf.nomi.nb")

    # A quota failure is not a successful save; exporting remains independent.
    page.evaluate("""() => { window.originalSetItem = Storage.prototype.setItem;
        Storage.prototype.setItem = () => { throw new DOMException('quota', 'QuotaExceededError'); }; }""")
    page.evaluate("_cellEditors[0].setValue('print(47)\\r\\n')")
    assert page.evaluate("saveCurrentDraft(true)") is False
    expect(page.locator("#toast")).to_contain_text("Local storage unavailable")
    with page.expect_download() as download_info:
        page.get_by_role("button", name="Download source", exact=True).click()
    assert b"print(47)" in Path(download_info.value.path()).read_bytes()
    page.evaluate(
        "Storage.prototype.setItem = window.originalSetItem; persistWorkbenchState()"
    )

    # Denied clipboard plus a failed fallback must never announce success.
    copied = page.evaluate("""async () => {
        const writeText = navigator.clipboard.writeText;
        const execCommand = document.execCommand;
        try {
            navigator.clipboard.writeText = async () => { throw new Error('denied'); };
            document.execCommand = () => false;
            return await copyText('source', 'Should not report success');
        } finally {
            navigator.clipboard.writeText = writeText;
            document.execCommand = execCommand;
        }
    }""")
    assert copied is False
    expect(page.locator("#toast")).to_contain_text("Clipboard unavailable")

    # Missing deployment assets must fail visibly, without a fallback sample or
    # an infinite automatic restart cycle. These are intentional failure pages.
    for pattern, status, expected in [
        ("**/manifest.json", 404, "Sample manifest returned HTTP 404"),
        ("**/nomi_parser_worker_bg.wasm", 503, "WASM parser returned HTTP 503"),
    ]:
        failure_page = page.context.new_page()
        failure_page.route(
            pattern,
            lambda route: route.fulfill(status=status, body="unavailable"),
        )
        failure_page.goto(page.url, wait_until="domcontentloaded")
        expect(failure_page.locator("#loading-msg")).to_contain_text(
            expected, timeout=60_000
        )
        expect(failure_page.locator("#loading-retry-btn")).to_be_visible()
        expect(failure_page.locator("#loading-title")).to_have_text("Nomi unavailable")
        expect(failure_page.locator(".spinner")).to_be_hidden()
        expect(failure_page.locator("#run-all-btn")).to_be_disabled()
        failure_page.screenshot(
            path=str(artifacts / f"startup-{status}.png"), full_page=True
        )
        failure_page.close()
