"""Create the Nomi demo notebooks with clean, stable metadata."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


KERNELSPEC = {
    "display_name": "Nomi",
    "language": "nomi",
    "name": "nomi",
}

LANGUAGE_INFO = {
    "codemirror_mode": {"name": "python", "version": 3},
    "file_extension": ".nomi",
    "mimetype": "text/x-nomi",
    "name": "nomi",
    "pygments_lexer": "python3",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def clean_source(source: str) -> str:
    return dedent(source).strip("\n")


def markdown(cell_id: str, source: str):
    cell = new_markdown_cell(clean_source(source))
    cell["id"] = cell_id
    return cell


def code(cell_id: str, source: str):
    cell = new_code_cell(clean_source(source))
    cell["id"] = cell_id
    cell["execution_count"] = None
    cell["outputs"] = []
    return cell


def nomi_notebook(cells):
    notebook = new_notebook(cells=cells)
    notebook["metadata"]["kernelspec"] = KERNELSPEC
    notebook["metadata"]["language_info"] = LANGUAGE_INFO
    notebook["nbformat"] = 4
    notebook["nbformat_minor"] = 5
    return notebook


def minimal_notebook():
    return nomi_notebook(
        [
            markdown(
                "nomi-minimal-title",
                """
                # Nomi Minimal Smoke Notebook

                This tiny notebook is the first thing to try when checking that
                the Nomi Jupyter kernel is executing cells and showing outputs.
                """,
            ),
            code(
                "nomi-minimal-hello",
                """
                print("hello from Nomi")
                1 + 2
                """,
            ),
            code(
                "nomi-minimal-function",
                """
                add = (x, y) => x + y
                print(add(2, 5))
                add(10, 20)
                """,
            ),
            code(
                "nomi-minimal-who",
                """
                %who
                """,
            ),
        ]
    )


def syntax_tour_notebook():
    return nomi_notebook(
        [
            markdown(
                "nomi-tour-title",
                """
                # Nomi Syntax Tour

                This notebook uses the `Nomi` Jupyter kernel and covers the
                language surface currently implemented in the prototype.
                """,
            ),
            code(
                "nomi-tour-hello",
                """
                print("Hello from Nomi in Jupyter")
                project = "Nomi"
                version = 1
                f"{project} notebook tour v{version}"
                """,
            ),
            markdown(
                "nomi-tour-functions-md",
                """
                ## Functions With `func`

                `func` is the named function form. It maps to the prototype
                function implementation and supports ordinary calls, returns,
                defaults, and closures.
                """,
            ),
            code(
                "nomi-tour-functions",
                """
                func greet(name, punctuation="!"):
                    return f"Hello, {name}{punctuation}"

                print(greet("Nomi"))
                print(greet("notebook", punctuation="."))
                """,
            ),
            markdown(
                "nomi-tour-arrows-md",
                """
                ## Arrow Functions

                Arrow functions are expression-level function values. They are
                useful for small transformations and higher-order calls.
                """,
            ),
            code(
                "nomi-tour-arrows",
                """
                add = (x, y) => x + y
                square = (x) => x * x
                doubled = list(map((x) => x * 2, [1, 2, 3, 4]))

                print(add(3, 4))
                print(square(5))
                doubled
                """,
            ),
            markdown(
                "nomi-tour-binding-md",
                """
                ## Constrained Binding

                Annotated bindings are enforced at runtime. A constraint can be
                a type, a predicate function, or an expression over the bound
                name.
                """,
            ),
            code(
                "nomi-tour-binding",
                """
                is_positive = (x) => x > 0
                age:int, is_positive, age < 130 = 34
                age
                """,
            ),
            markdown(
                "nomi-tour-params-md",
                """
                ## Constrained Parameters

                Function parameters are bindings too, so constraints apply when
                arguments are bound to parameters.
                """,
            ),
            code(
                "nomi-tour-params",
                """
                func grade(score:(int, 0 <= score <= 100)):
                    return "pass" if score >= 60 else "fail"

                print(grade(85))
                print(grade(40))
                """,
            ),
            markdown(
                "nomi-tour-destructuring-md",
                """
                ## Destructuring Assignment

                The interpreter supports tuple/list unpacking, starred targets,
                and ordinary Python-style assignment forms.
                """,
            ),
            code(
                "nomi-tour-destructuring",
                """
                first, second = (10, 20)
                head, *tail = [1, 2, 3, 4]

                print(first, second)
                print(head, tail)
                """,
            ),
            markdown(
                "nomi-tour-control-md",
                """
                ## Python-Compatible Data And Control

                Nomi currently keeps much of Python's readable expression and
                control surface.
                """,
            ),
            code(
                "nomi-tour-control",
                """
                values = [1, 2, 3, 4, 5]
                total = 0

                for value in values:
                    if value % 2 == 1:
                        total += value

                total
                """,
            ),
            markdown(
                "nomi-tour-match-md",
                """
                ## Match Statements

                Pattern matching supports literal cases, wildcard cases, and
                guards through the lowered Python AST.
                """,
            ),
            code(
                "nomi-tour-match",
                """
                func describe(value):
                    match value:
                        case 0:
                            return "zero"
                        case 1 if value > 0:
                            return "guarded one"
                        case _:
                            return "something else"

                print(describe(0))
                print(describe(1))
                print(describe(9))
                """,
            ),
            markdown(
                "nomi-tour-classes-md",
                """
                ## Imports And Classes

                The prototype supports imports, classes, methods, and
                context-manager style `with` blocks through the
                Python-compatible interpreter layer.
                """,
            ),
            code(
                "nomi-tour-classes",
                """
                import math

                class ErrorPrinter:
                    func __enter__(self):
                        return self

                    func __exit__(self, exc_type, exc_val, exc_tb):
                        if exc_val:
                            print(f"suppressed: {exc_val}")
                            return True

                print(math.sqrt(81))
                with ErrorPrinter():
                    1 / 0
                """,
            ),
            markdown(
                "nomi-tour-yield-md",
                """
                ## Yield-To-Block

                A caller-side block is attached to a call. The callee controls
                when the block runs by using `yield`.
                """,
            ),
            code(
                "nomi-tour-yield",
                """
                func times(n):
                    for i in range(n):
                        yield

                counter = 0
                times(3):
                    counter += 1

                counter
                """,
            ),
            markdown(
                "nomi-tour-block-params-md",
                """
                ## Block Parameters

                A callee can yield values into a caller block. The names after
                `->` bind those yielded values.
                """,
            ),
            code(
                "nomi-tour-block-params",
                """
                func each(items):
                    for item in items:
                        yield item

                collected = []
                each([10, 20, 30]) -> item:
                    collected.append(item * 2)

                collected
                """,
            ),
            markdown(
                "nomi-tour-retry-md",
                """
                ## Retry As Library-Defined Control

                The same block mechanism can express retry-style control
                without adding a dedicated retry keyword.
                """,
            ),
            code(
                "nomi-tour-retry",
                """
                func retry(max_attempts):
                    for attempt in range(max_attempts):
                        try:
                            yield
                            return attempt + 1
                        except ValueError:
                            if attempt == max_attempts - 1:
                                raise

                attempts = 0
                retry(3):
                    attempts += 1
                    if attempts < 3:
                        raise ValueError("again")

                attempts
                """,
            ),
            markdown(
                "nomi-tour-closures-md",
                """
                ## Closures And `nonlocal`

                Nested functions and `nonlocal` bindings work through the
                Python-compatible environment model.
                """,
            ),
            code(
                "nomi-tour-closures",
                """
                func make_counter(start:(int, start >= 0)):
                    value = start
                    func bump(step=1):
                        nonlocal value
                        value += step
                        return value
                    return bump

                counter_fn = make_counter(2)
                print(counter_fn())
                print(counter_fn(3))
                """,
            ),
            markdown(
                "nomi-tour-kernel-commands-md",
                """
                ## Kernel Commands

                The custom kernel also supports `%who`, `%reset`, `%ast`, and
                `%run path/to/file.nomi`.
                """,
            ),
            code(
                "nomi-tour-who",
                """
                %who
                """,
            ),
        ]
    )


def write_notebook(path: Path, notebook) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    print(f"Wrote {path}")


def main() -> None:
    notebooks_dir = project_root() / "notebooks"
    write_notebook(notebooks_dir / "nomi_minimal.ipynb", minimal_notebook())
    write_notebook(notebooks_dir / "nomi_syntax_tour.ipynb", syntax_tour_notebook())


if __name__ == "__main__":
    main()

