"""Exercise real Monaco focus/cursor/disposal during repeated document changes."""

import json


def check_editor_lifecycle_scenarios(page, expect, artifacts):
    previous_storage = page.evaluate("localStorage.getItem(WORKBENCH_STORAGE_KEY)")
    stress_page = page.context.new_page()
    errors = []
    stress_page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        stress_page.goto(page.url, wait_until="domcontentloaded")
        expect(stress_page.locator("#loading")).to_be_hidden(timeout=60_000)
        stress_page.wait_for_function("_cellEditors.length > 0")
        result = stress_page.evaluate(
            """async () => {
                for (let index = 0; index < 30; index++) {
                    document.querySelector(`[data-sample="${index % 2 ? 'terse' : 'text-pipeline'}"]`).click();
                    _cellEditors[0].focus();
                    _cellEditors[0].setPosition({ lineNumber: 1, column: 3 });
                    await new Promise(resolve => requestAnimationFrame(resolve));
                }
                await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
                const editor = _cellEditors[0];
                editor.setSelection(new monaco.Range(1, 1, 1, 4));
                await editor.getAction('actions.find').run();
                return {
                    switches: 30,
                    models: monaco.editor.getModels().length,
                    editors: _cellEditors.length,
                    occurrences: editor.getOption(monaco.editor.EditorOption.occurrencesHighlight),
                    selectionHighlight: editor.getOption(monaco.editor.EditorOption.selectionHighlight),
                    selectionColumns: editor.getSelection().endColumn - editor.getSelection().startColumn,
                };
            }"""
        )
        expect(stress_page.locator(".find-widget")).to_be_visible()
        assert result["occurrences"] == "off"
        assert result["selectionHighlight"] is True
        assert result["selectionColumns"] == 3
        assert result["models"] == result["editors"] == 1
        assert not errors, "Editor lifecycle errors: " + "; ".join(errors)
        (artifacts / "editor-lifecycle.json").write_text(
            json.dumps({**result, "page_errors": errors}, indent=2) + "\n",
            encoding="utf-8",
        )
    finally:
        stress_page.close()
        page.evaluate(
            """stored => {
                if (stored === null) localStorage.removeItem(WORKBENCH_STORAGE_KEY);
                else localStorage.setItem(WORKBENCH_STORAGE_KEY, stored);
            }""",
            previous_storage,
        )
