Artifacts and Usage
===

Nomi programs are executed by running a Nomi source file through a
Python-based runner. Parsing is performed with **Lark**, grammars live
under `prototype/grammar/`, and Nomi code is first lowered into a
**Python AST** before being interpreted by the layered runtime in
`prototype/interpreter/`. Python serves as the semantic baseline, with
Nomi features introduced through explicit AST reduction and embedded
semantic changes. Additional parsing and execution examples live under
`prototype/test/data/sample_source/`, and tests are in
`prototype/tests/`.

The primary entry point of the project is the execution of a **Nomi
source file**, currently exposed through a Python-based runner:

``` bash
python run_nomi.py [filename]  # defaults to demo.nomi
```

This command parses and executes the given Nomi file. The default
behavior runs `demo.nomi`, which serves as the reference execution
example. The implementation can be inspected directly in `run_nomi.py`.

A variety of additional Python and Nomi source examples---covering both
parsing and execution---are available under:

    prototype/test/data/sample_source/

These examples are designed to expose the full pipeline, from surface
syntax to runtime behavior.

-   **Grammar and Parsing:** Lark is used to define the grammar and
    perform parsing. Grammars live under `prototype/grammar/`, and
    parsing logic resides under `prototype/parse/`.
-   **AST Lowering:** Parsed programs are first transformed into a
    Python AST, establishing Python as the baseline semantic substrate.
-   **Execution:** Execution is handled by a layered interpreter located
    in `prototype/interpreter/`.

At each stage, Python structure is established first, and Nomi-specific
behavior is then embedded on top of it---primarily via **AST reduction
and semantic overlays** (via inheritance and controlled use of context
managers). In effect, every Nomi feature is realized as a **systematic
deformation of Python's AST and evaluation model**, rather than as a
parallel runtime.

This approach serves several purposes simultaneously:

-   It grounds the project in Python's historical evolution and
    practical experience\
-   It exposes internal inconsistencies and redundancies as concrete
    design inputs\
-   It enables orthogonal redesign through direct semantic substitution

Semantic extensions---such as **constraint handling** and
**yield-to-block generalization**---are implemented through explicit AST
rewrites combined with embedded semantic shifts.

The test suite is located under:

    prototype/tests/

This has been central to driving small, incremental changes in parsing,
AST transformation, and execution across both Python and Nomi layers.
Most tests currently operate at the regression/functional level;
finer-grained coverage will be introduced gradually.
