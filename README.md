# Nomi

**A Minimal, Systematic, and Intuitive Programming Language**

Nomi is an experimental programming language built on a **small, coherent core**: variables, function definitions, and function applications. Inspired by functional programming and guided by cognitive principles, it emphasizes **clarity, coherence, and human-centered reasoning**.

Rather than piling on features, Nomi focuses on a unified core where expressiveness emerges naturally. This minimalism encourages intuitive composition and sharp mental models, aligning programming with how humans reason about processes and abstractions.

---

# Usage

Nomi programs are executed through a Python-based runner that parses Nomi source files using **Lark**, lowers them into a **Python AST**, and evaluates them via a layered interpreter. Python serves as the semantic baseline, with Nomi features introduced through explicit AST reduction and carefully scoped semantic extensions.

## Option 1: Install as a package (recommended for regular use)

```bash
# Install in editable mode from source
pip install -e .

# Run Nomi programs
nomi demo.nomi
nomi script.py
nomi --help
```

(This anticipates `nomi` becoming a general pip-installable PyPI package.)

## Option 2: Direct execution (no installation required)

```bash
# Run directly from the source directory
python scripts/cli.py [filename]  # defaults to demo.nomi
```

## Test Reports

```bash
python3 scripts/test_report.py
```

Open `reports/index.html` from VS Code after the command finishes. It links to the pytest HTML report and the line-by-line coverage report.

> **Note on contributions:** Nomi is in an early, fast-moving stage. Broad public contributions may be premature. Contribution guidelines will be added as the core stabilizes. Interested readers are encouraged to follow the notes and documentation, or reach out for discussion and feedback.

See [Artifacts and Usage](documentation/artifacts_and_usage.md) for more details.

---

# Vision

Programming today is fragmented across **frontend, backend, data science, AI, systems, embedded devices, cloud, deployment, testing, and configuration**, each with its own languages, libraries, and mental models. Developers constantly switch paradigms, while mainstream languages often emphasize **implementation details**—memory, optimization, and platform quirks—leaving abstraction, readability, and usability underdeveloped.

**Nomi takes a different path:**

* Built on a **minimal, coherent core** rooted in **Lambda Calculus**, favoring **expression and composition over machinery and incidental complexity**.
* Domain-specific features and libraries **layer naturally** without breaking the underlying model.
* Small core, large reach: usable across domains without conceptual fragmentation.

Performance is secondary; **readability, composability, and human-centered expression guide design**.

---

## AI Complementarity

AI dominates technical conversation, shaping how we think about software and computation. Nomi is not an AI system, but it exists in an AI-saturated world—and takes that reality seriously.

AI expands semantic possibility by exploring alternatives and accelerating synthesis. Programming languages, by contrast, reduce entropy: they crystallize intention into durable, composable structures that stabilize and accumulate thought.

* **AI** broadens the search frontier.
* **Languages** condense it into lasting form.

Nomi sits deliberately at the compressive pole. AI accelerates design exploration, critique, and synthesis, while Nomi provides semantics and constraints that preserve legibility, stability, and editability.

---

# Context

To understand Nomi's approach, it helps to see the programming journey that shaped it. My experience spans:

**C** – revealed low-level control and cognitive burden.
**Python** – highlighted readability and expressive power.
**Tcl** – introduced language as craft rather than mere tool.

Exploration continued through **Java, JavaScript, Scala, Julia, Lisp/Scheme, ALGOL, Haskell, PowerShell, Bash, Mathematica (Wolfram Language), R, and APL**, each contributing insights into abstraction, notation, and usability.

In 2015, I published an early [blog post](https://dindefi.wordpress.com/2015/09/08/programming-languages-pl/) capturing fragments of this vision. Nomi is a consolidation of these insights—minimal at its core, expansive in reach.

---

# Current Status

Nomi refines Python’s **function, binding, and control flow** foundations into a more **systematic, expression-oriented model**.

## Functions

`def` becomes **`func`** for semantic clarity, while **arrow syntax** enables concise, expression-level functions:

```python
@decorator
func greet(name):
    print("Hello", name)
```

```python
(x, y) => x + y
(x:int) => x^2
() => print("no args")
```

## Binding and Validation

All bindings—assignments, parameters, loops—can carry **type and predicate constraints** that are validated automatically:

```python
is_pos = (a) => a > 0
a:int, is_pos, a > 20 = 19  # Raises TypeError
```

```python
func f(a:int, b:(int, b > 20)): pass
f(1, 30)   # OK
f(1, 10)   # Fails
```

## Generator Blocks and Unified Control

Python’s **generators** are a specialized form of **coroutines**. Nomi generalizes generators, extending them to block-structured control patterns via the **yield-to-block** construct:

```python
func retry(max_times):
    for i in range(max_times):
        try:
            yield
            print(f"success on attempt {i+1}")
            return
        except Exception:
            print(f"failed attempt {i+1}")
```

```python
retry(3):
    1 / 0
```

This bridges **statements and expressions**, **functions and blocks**, and **decorators and context managers**, exposing the latent generality of Python’s `yield`.

> See [Delta on Python](documentation/delta_on_python.md) for detailed rationale and examples.

---

# Future Direction

> *Dedicated to **Peter Landin**, who revealed the prose within computation and championed abstraction as a bridge for human thought.*

Nomi has a functional, self-hosted Python interpreter—an extensible substrate incorporating emerging Nomi syntax and semantics. The primary work ahead is foundational: constructing a **principled, coherent design** for the language itself.

Its lineage traces from Leibniz’s *characteristica universalis*, through Boole’s algebra of logic, to Church’s Lambda Calculus. The goal is **synthetic**: uniting the compositional clarity of foundational models (Lisp, ALGOL) with the cognitive usability and simplicity of Python.

The vision is a language that is **industrial in capability** and **natural in expression**—prioritizing clear mental models over accidental complexity. Key design principles:

* Avoid over-formalization that sacrifices usability.
* Avoid abstraction that obscures clarity.
* Avoid ad-hoc growth that erodes conceptual unity.

The construct cycle remains: **primitive → combination → abstraction → new primitive**, scaling to unbounded complexity while preserving transparency.

This effort draws on:

* **Foundational rigor**: ALGOL, Landin, Strachey, Scott, Hoare
* **Modern synthesis**: Scala, Rust, Julia

The challenge is to distill decades of theoretical and practical insight into a **formally sound, semantically compositional, and human-intuitive language**.

---

# Ambition and Attrition

Nomi is experimental, guided by curiosity and long-term thinking. History shows many well-designed languages struggle to gain adoption due to **tooling, education, platforms, and social momentum**. Nomi may evolve slowly, change form, or even fade regardless of its internal merits. This is not failure—it is the **normal evolutionary pressure** of ambitious ideas.

Evaluation of a programming language is inherently long-term, shaped by debates between **theory and practice, academia and industry**. Progress emerges through **independence, perseverance, and continuous feedback**.

Rather than aiming for sweeping claims, the focus here is on **concrete tools, real-world grounding, and careful iteration**, anchored in Python as a baseline. Historical perspective and persistent questioning guide refinement toward **coherence, orthogonality, and long-term clarity**.

For a deeper look at the **intellectual lineage, design risks, and context of Nomi**, see [Positioning Within Ambition and Risk](documentation/positioning_ambition_risk.md).
