#!/usr/bin/env python3
"""Exercise the public playground in Chromium using its actual UI and worker."""

from __future__ import annotations

import argparse
import json
import sys
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
if __package__ in {None, ""}:
    sys.path.insert(0, str(ROOT))

SAMPLE = "samples/demo_terse.nomi"
EXPECTED_OUTPUT = (
    "Nomi triage\n"
    "scores = [90, 48, 80]\n"
    "hot tickets = 2\n"
    "checkout -> 90 / page now\n"
    "range total = 15"
)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


@contextmanager
def playground_url(remote_url: str | None):
    if remote_url:
        yield remote_url
        return
    handler = partial(QuietHandler, directory=str(ROOT))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}/web/"
        finally:
            server.shutdown()
            thread.join()


def check_browser(
    url: str, artifacts: Path, headed: bool, legacy_pyodide: bool = False
) -> None:
    from scripts.check_workbench_scenarios import check_workbench_scenarios

    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Install browser checks with: python3 -m pip install -e '.[web-test]'\n"
            "Then: python3 -m playwright install chromium"
        ) from exc

    artifacts.mkdir(parents=True, exist_ok=True)
    messages: list[str] = []
    page_errors: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not headed)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        context.set_default_timeout(30_000)
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("console", lambda msg: messages.append(f"{msg.type}: {msg.text}"))
        page.on(
            "requestfailed",
            lambda req: messages.append(f"request failed: {req.url}: {req.failure}"),
        )
        page.on(
            "response",
            lambda resp: (
                messages.append(f"HTTP {resp.status}: {resp.url}")
                if resp.status >= 400
                else None
            ),
        )
        try:
            # Observe real startup fetches: embedded fallback demos must not hide
            # a missing manifest or sample in a Pages deployment.
            with (
                page.expect_response(urljoin(url, "manifest.json")) as manifest_info,
                page.expect_response(urljoin(url, f"../{SAMPLE}")) as sample_info,
            ):
                response = page.goto(url, wait_until="domcontentloaded")
            assert response and response.ok, f"Playground did not load: {url}"
            manifest = manifest_info.value
            sample = sample_info.value
            assert manifest.ok, f"Manifest returned HTTP {manifest.status}"
            assert SAMPLE in manifest.json()["samples"], f"Manifest is missing {SAMPLE}"
            assert sample.ok, f"Sample returned HTTP {sample.status}"
            source = sample.text()

            expect(page.locator("#loading")).to_be_hidden(timeout=60_000)
            expect(page.locator("#status")).to_have_text("ready")
            expect(page.locator(".monaco-editor")).to_be_visible()
            page.locator('[data-sample="terse"]').click()
            expect(page.locator("#current-file")).to_have_text("demo_terse.nomi")
            page.wait_for_function(
                "source => monaco.editor.getModels().some(model => model.getValue() === source)",
                arg=source,
            )

            page.locator("#run-all-btn").click()
            output = page.locator('[data-result-view="output"] pre')
            expect(output).to_be_visible()
            expect(output).to_have_text(EXPECTED_OUTPUT)
            expect(
                page.locator('[data-result-view="output"] .empty-result')
            ).to_be_hidden()
            expect(page.locator("#status")).to_have_text("ready")
            expect(page.locator('[data-result-count="diagnostics"]')).to_have_text("0")

            page.get_by_role("tab", name="Pipeline", exact=True).click()
            pipeline = page.locator('[data-result-view="pipeline"]')
            expect(pipeline).to_be_visible()
            for value in ("rust-fast-ast-wasm", "js-core-runtime", "browser-worker"):
                expect(pipeline).to_contain_text(value)
            page.screenshot(path=str(artifacts / "sample-pipeline.png"), full_page=True)
            page.get_by_role("tab", name="Output", exact=True).click()
            page.screenshot(path=str(artifacts / "sample-output.png"), full_page=True)

            page.get_by_role("button", name="Create local scratch file").click()
            editor_input = page.locator(".monaco-editor textarea.inputarea")
            editor_input.focus()
            page.keyboard.insert_text("print(6 * 7)\n")
            page.locator("#run-all-btn").click()
            expect(output).to_be_visible()
            expect(output).to_have_text("42")
            expect(page.locator("#status")).to_have_text("ready")
            check_workbench_scenarios(page, expect, artifacts)
            if legacy_pyodide:
                legacy_page = context.new_page()
                try:
                    legacy_page.on(
                        "pageerror", lambda error: page_errors.append(str(error))
                    )
                    legacy_page.goto(
                        urljoin(url, "?backend=pyodide"), wait_until="domcontentloaded"
                    )
                    expect(legacy_page.locator("#loading")).to_be_hidden(timeout=90_000)
                    legacy_page.locator('[data-sample="terse"]').click()
                    legacy_page.locator("#run-all-btn").click()
                    expect(
                        legacy_page.locator('[data-result-view="output"] pre')
                    ).to_have_text(EXPECTED_OUTPUT)
                    expect(legacy_page.locator("#status")).to_have_text("ready")
                    legacy_page.get_by_role("tab", name="Pipeline", exact=True).click()
                    expect(
                        legacy_page.locator('[data-result-view="pipeline"]')
                    ).to_contain_text("python-ast")
                    legacy_page.screenshot(
                        path=str(artifacts / "legacy-pyodide.png"), full_page=True
                    )
                    legacy_page.get_by_role("tab", name="Bindings", exact=False).click()
                    expect(
                        legacy_page.locator('[data-result-view="bindings"]')
                    ).to_have_text("Bindings unavailable")
                    expect(
                        legacy_page.locator('[data-result-count="bindings"]')
                    ).to_have_text("-")
                except Exception:
                    legacy_page.screenshot(
                        path=str(artifacts / "legacy-failure.png"), full_page=True
                    )
                    raise
                finally:
                    legacy_page.close()
            assert not page_errors, "Uncaught browser errors: " + "; ".join(page_errors)
        except Exception:
            page.screenshot(path=str(artifacts / "failure.png"), full_page=True)
            raise
        finally:
            (artifacts / "browser-log.json").write_text(
                json.dumps(
                    {"url": url, "page_errors": page_errors, "messages": messages},
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            context.tracing.stop(path=str(artifacts / "trace.zip"))
            context.close()
            browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        help="existing playground URL ending in /web/ (default: temporary local server)",
    )
    parser.add_argument(
        "--headed", action="store_true", help="show Chromium while checking"
    )
    parser.add_argument(
        "--legacy-pyodide",
        action="store_true",
        help="also check the opt-in Pyodide quick tour (network bootstrap)",
    )
    parser.add_argument(
        "--artifacts", type=Path, default=ROOT / "reports" / "web-browser"
    )
    args = parser.parse_args()
    with playground_url(args.url) as url:
        print(f"Checking playground: {url}", flush=True)
        check_browser(url, args.artifacts, args.headed, args.legacy_pyodide)
    print(
        f"Browser checks passed: samples, notebook, diagnostics, cancellation, drafts, desktop/mobile. Artifacts: {args.artifacts}"
    )
    if args.legacy_pyodide:
        print("Opt-in legacy Pyodide quick tour and pipeline passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
