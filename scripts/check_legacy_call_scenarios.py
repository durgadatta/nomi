"""Real Pyodide call-boundary scenarios for the playground release gate."""

CALL_SCENARIOS = (
    (
        "context-unwind",
        """events = []
class Manager:
    func __init__(self, label):
        self.label = label
    func __enter__(self, /):
        events.append(('enter', self.label))
        return self.label
    func __exit__(self, error_type, error, traceback, /):
        events.append(('exit', self.label))
        return False
func scoped():
    with Manager('outer'), Manager('inner'):
        return 7
assert scoped() == 7
assert events == [('enter', 'outer'), ('enter', 'inner'), ('exit', 'inner'), ('exit', 'outer')]
events = []
acquired: int
try:
    with Manager('outer'), Manager('inner') as acquired:
        events.append('body')
except TypeError:
    pass
assert events == [('enter', 'outer'), ('enter', 'inner'), ('exit', 'inner'), ('exit', 'outer')]
print('context-unwind passed')
""",
    ),
    (
        "nested-resume",
        """events = []
func inner(value):
    events.append(value)
    return value + 1
func gather(**values):
    return values
func resume_nested():
    result = gather(first=inner((yield 'one')), second=inner((yield 'two')))
    yield result
generator = resume_nested()
assert next(generator) == 'one'
assert generator.send(10) == 'two'
assert generator.send(20) == {'first': 11, 'second': 21}
assert events == [10, 20]
print('nested-resume passed')
""",
    ),
    (
        "positional-only",
        """events = []
func required(value, /, **extra):
    events.append('body')
failed = False
try:
    required(value=3)
except TypeError:
    failed = True
assert failed
assert events == []
func ordered(first=1, second=2, /, named=3, **extra):
    return first, second, list(extra.items())
result = ordered(before=4, second=9, named=5, first=7, after=10)
assert result == (1, 2, [('before', 4), ('second', 9), ('first', 7), ('after', 10)])
print('positional-only passed')
""",
    ),
    (
        "call-shape",
        """events = []
func default_value():
    events.append('default')
    return 2
func shape(first, optional=default_value(), *, required):
    events.append('body')
    return first
failed = 0
try:
    shape(required=3)
except TypeError:
    failed += 1
try:
    shape(1, 2, 3, required=4)
except TypeError:
    failed += 1
try:
    shape(1, first=2, required=3)
except TypeError:
    failed += 1
try:
    shape(1, required=3, unexpected=4)
except TypeError:
    failed += 1
try:
    shape(1, required=3, **{'required': 4})
except TypeError:
    failed += 1
assert failed == 5
assert events == []
print('call-shape passed')
""",
    ),
    (
        "keyword-mapping",
        """from collections import UserDict
func gather(**values):
    return values
assert gather(**UserDict({'first': 1}), second=2) == {'first': 1, 'second': 2}
failed = False
try:
    gather(**{1: 2})
except TypeError:
    failed = True
assert failed
print('keyword-mapping passed')
""",
    ),
    (
        "keyword-resume",
        """events = []
func mark(label, value):
    events.append(label)
    return value
func gather(**values):
    events.append('body')
    return values
func resume():
    result = gather(first=mark('first', 1), second=(yield 'ready'), third=mark('third', 3))
    yield result
generator = resume()
assert next(generator) == 'ready'
assert generator.send(None) == {'first': 1, 'second': None, 'third': 3}
assert events == ['first', 'third', 'body']
print('keyword-resume passed')
""",
    ),
)


def check_legacy_call_scenarios(page, expect, artifacts):
    page.get_by_role("button", name="Create local scratch file").click()
    for name, source in CALL_SCENARIOS:
        # Match the workbench harness: typing multiline text invokes autoindent.
        page.evaluate("source => _cellEditors[0].setValue(source)", source)
        assert page.evaluate("() => _cellEditors[0].getValue()") == source
        page.locator("#run-all-btn").click()
        expect(page.locator("#status")).to_have_text("ready")
        page.get_by_role("tab", name="Output", exact=True).click()
        expect(page.locator('[data-result-view="output"] pre')).to_have_text(
            f"{name} passed"
        )
        expect(page.locator('[data-result-count="diagnostics"]')).to_have_text("0")
    page.screenshot(path=str(artifacts / "legacy-call-boundaries.png"), full_page=True)
