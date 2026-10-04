"""Editor CDN failure and explicit recovery in the real browser playground."""


def check_editor_startup_scenarios(page, expect, artifacts):
    failure_page = page.context.new_page()
    pattern = "**/vs/editor/editor.main.js"
    try:
        # Hold actual worker progress messages to exercise their arrival after
        # the editor failure; execution/result transport remains untouched.
        failure_page.add_init_script(
            """window.queuedStartupLogs = [];
            const NativeWorker = window.Worker;
            window.Worker = class extends NativeWorker {
                constructor(...args) {
                    super(...args);
                    this.addEventListener('message', event => {
                        if (event.data.type !== 'log') return;
                        event.stopImmediatePropagation();
                        window.queuedStartupLogs.push(() => this.onmessage?.(event));
                    });
                }
            };"""
        )

        def reject_editor(route):
            failure_page.wait_for_function("window.queuedStartupLogs.length > 0")
            route.fulfill(status=404, body="editor unavailable")

        failure_page.route(pattern, reject_editor)
        failure_page.goto(page.url, wait_until="domcontentloaded")
        expect(failure_page.locator("#loading-msg")).to_contain_text(
            "Editor startup failed", timeout=40_000
        )
        expect(failure_page.locator("#loading-msg")).not_to_contain_text("[object")
        expect(failure_page.locator("#loading-title")).to_have_text("Nomi unavailable")
        expect(failure_page.locator(".spinner")).to_be_hidden()
        expect(failure_page.locator("#loading-retry-btn")).to_be_visible()
        expect(failure_page.locator("#run-all-btn")).to_be_disabled()
        expect(failure_page.locator("#restart-btn")).to_be_disabled()
        message = failure_page.locator("#loading-msg").text_content()
        released = failure_page.evaluate(
            """() => {
                const queued = window.queuedStartupLogs.splice(0);
                queued.forEach(deliver => deliver());
                return queued.length;
            }"""
        )
        assert released > 0
        expect(failure_page.locator("#loading-msg")).to_have_text(message)
        failure_page.evaluate("restartWorker()")
        expect(failure_page.locator("#status")).to_have_text("error")
        assert failure_page.evaluate("_runtimeWorker === null && _runtimePending.size === 0")
        failure_page.screenshot(
            path=str(artifacts / "startup-editor-404.png"), full_page=True
        )

        failure_page.unroute(pattern)
        failure_page.locator("#loading-retry-btn").click()
        expect(failure_page.locator("#loading")).to_be_hidden(timeout=60_000)
        expect(failure_page.locator("#status")).to_have_text("ready")
        expect(failure_page.locator(".monaco-editor")).to_be_visible()
        expect(failure_page.locator("#run-all-btn")).to_be_enabled()
    finally:
        failure_page.close()


def check_sample_manifest_startup_scenarios(page, expect, artifacts):
    failure_page = page.context.new_page()
    pattern = "**/manifest.json"
    try:
        failure_page.route(
            pattern,
            lambda route: route.fulfill(
                status=200, content_type="application/json", body="{}"
            ),
        )
        failure_page.goto(page.url, wait_until="domcontentloaded")
        expect(failure_page.locator("#loading-msg")).to_contain_text(
            "Sample manifest needs a nonempty text-path samples list"
        )
        expect(failure_page.locator("#loading-title")).to_have_text("Nomi unavailable")
        expect(failure_page.locator(".spinner")).to_be_hidden()
        expect(failure_page.locator("#loading-retry-btn")).to_be_visible()
        expect(failure_page.locator("#run-all-btn")).to_be_disabled()
        failure_page.screenshot(
            path=str(artifacts / "startup-manifest-shape.png"), full_page=True
        )

        failure_page.unroute(pattern)
        failure_page.locator("#loading-retry-btn").click()
        expect(failure_page.locator("#loading")).to_be_hidden(timeout=60_000)
        expect(failure_page.locator("#status")).to_have_text("ready")
        expect(failure_page.locator(".monaco-editor")).to_be_visible()
    finally:
        failure_page.close()
