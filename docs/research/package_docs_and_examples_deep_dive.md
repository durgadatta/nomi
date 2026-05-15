# Package Docs & Examples: Cross-Language Deep Dive

> Status: source research for Nomi design.
> Purpose: Study how ten major documentation systems make documentation a
> first-class part of the language experience — API docs, examples, literate
> programming, doctests, and the integration of documentation with the
> development workflow. Extract structural invariants, genuine design forks,
> anti-patterns, and concrete recommendations for Nomi's documentation surface.

## Table of Contents

1. [Rustdoc](#1-rustdoc)
2. [ExDoc (Elixir)](#2-exdoc-elixir)
3. [Julia Documentation](#3-julia-documentation)
4. [Python Documentation (Sphinx + doctest)](#4-python-documentation-sphinx--doctest)
5. [Racket Scribble](#5-racket-scribble)
6. [Go Documentation](#6-go-documentation)
7. [Javadoc](#7-javadoc)
8. [TypeDoc (TypeScript)](#8-typedoc-typescript)
9. [Literate Programming Systems](#9-literate-programming-systems)
10. [Diataxis Framework](#10-diataxis-framework)
11. [Cross-Language Synthesis](#11-cross-language-synthesis)
12. [Nomi Adopt / Refuse / Adapt Table](#12-nomi-adopt--refuse--adapt-table)
13. [Sources](#sources)

---

## 1. Rustdoc

### Core Documentation Philosophy

Rustdoc is not a third-party tool — it is part of the Rust compiler toolchain.
This is the single most important fact about Rustdoc and the decision that
shapes everything downstream. Running `cargo doc` invokes `rustdoc` on every
crate in the dependency tree, including the standard library. Every Rust
developer has API documentation one command away, and every published crate has
its documentation automatically rendered on docs.rs.

The philosophy is: **documentation is a compiler concern, not a separate
ecosystem.** The compiler already parses the source code, resolves types,
understands visibility, and tracks cross-crate references. Rustdoc plugs into
that machinery to produce documentation that is always accurate with respect to
the compiled code — function signatures cannot drift from their docs because
they are extracted from the same AST.

### What Worked Exceptionally Well

**`///` and `//!` as the two documentation comment forms.**
The distinction is precise and clear:

```rust
/// This documents the **next** item — a function, struct, enum, or module member.
/// Markdown is supported. Code blocks with triple backticks are recognized.
///
/// # Examples
///
/// ```
/// let x = add(2, 3);
/// assert_eq!(x, 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 { a + b }

//! This documents the **enclosing** item — typically a module or crate root.
//! Module-level documentation describes the purpose of the whole module,
//! its public API surface, and when you should use it.
```

The `///` (outer doc) vs `//!` (inner doc) distinction eliminates ambiguity
about what is being documented. `///` attaches to the next declaration; `//!`
attaches to the enclosing scope. Every other doc comment system has to resolve
this ambiguity with conventions or position rules; Rustdoc solved it with two
syntactic forms.

**Doc tests as first-class tests.**
Code blocks in `///` comments are compiled and executed by `cargo test`:

```
cargo test
   Compiling my-crate v0.1.0
   Doc-tests my_crate

running 1 test
test src/lib.rs - add (line 10) ... ok

test result: ok. 1 passed; 0 failed
```

The doc test runner wraps the code block in a `fn main()`, adds `extern crate`
and `use` declarations automatically, and runs it as a separate binary. If the
code block starts with `#`, that line is hidden in the rendered docs but
executed in the test — allowing setup code that would clutter the docs:

```rust
/// ```
/// # use std::collections::HashMap;
/// # let mut map = HashMap::new();
/// # map.insert("key", "value");
/// let val = map.get("key");
/// assert_eq!(val, Some(&"value"));
/// ```
```

This single feature — making examples in documentation executable and tested —
is arguably the single most effective documentation quality mechanism in any
language ecosystem. It means:
- Documentation examples can never silently go stale.
- A failing doc test fails CI with a precise error message pointing to the
  exact doc comment and line number.
- The existence of doc tests sets a cultural norm: good crates have doc tests.

**Intra-doc links using path syntax.**
Rustdoc supports linking to items using Rust path syntax:

```rust
/// Returns a new [`Vec`] containing elements that satisfy the predicate.
/// See [`Iterator::filter`] for the lazy version.
///
/// [`Vec`]: std::vec::Vec
```

The `` [`Iterator::filter`] `` syntax resolves to the actual item in the
compiled crate graph. Broken links generate warnings. This is not a fragile
URL-based system — the compiler verifies that every linked item exists.

**The `#[doc]` attribute for programmatic documentation.**
Rust allows documentation to be generated or modified via attributes:

```rust
#[doc = include_str!("../README.md")]
// or
#[cfg_attr(feature = "serde", doc = "This type implements `Serialize` when the `serde` feature is enabled.")]
```

This is used for conditional documentation (showing/hiding content based on
feature flags) and for embedding external files. The `#[doc]` attribute is
Rust's escape hatch: when the `///` comment convention is insufficient, you can
programmatically construct documentation.

**docs.rs as a unified documentation surface.**
Every crate published to crates.io automatically gets documentation built and
hosted at `https://docs.rs/crate-name/latest`. The site provides:
- Version switching (every published version is available).
- Search across the crate's public API.
- Source links ("[src]") on every item that link to the exact line in the
  crate's repository.
- Feature flag documentation that shows what is available when each feature
  is enabled.
- A Rust version badge showing the minimum supported Rust version.

This is a genuine ecosystem-level feature. A Rust developer can read any
library's API documentation without installing anything, and every library's
documentation looks and works the same way. The uniformity lowers the cognitive
cost of exploring a new library.

### What Failed or Caused Persistent Friction

**Doc comment discoverability for beginners.**
`///` is not an obvious syntax for documentation. Beginners frequently write
`//` instead of `///` and don't understand why their comments don't appear in
the generated docs. The distinction between `///` and `//!` is also non-obvious
to newcomers. The error messages for "doc comment on something that can't take
a doc comment" are compiler errors that don't clearly explain the distinction.

**Doc test limitations.**
Doc tests run as separate binaries, which means:
- They cannot access private items (they are external crates relative to the
  crate being documented).
- Compilation overhead is higher than unit tests (each code block is a
  separate binary).
- There is no way to share setup code across multiple doc tests in the same
  module.

The separate-binary model is correct for ensuring examples are valid external
API usage, but it makes some kinds of examples awkward to write.

**`cargo doc` build time.**
Building documentation for a crate with many dependencies requires compiling
every dependency's documentation. For large projects, `cargo doc` can be
slower than `cargo build`. Rustdoc processes the entire crate dependency tree,
and while it has gotten faster, the "documentation takes as long as
compilation" experience is a friction point.

**Limited narrative/documentation structure.**
Rustdoc generates API reference documentation. It is not designed for
tutorials, guides, or narrative documentation. The Rust ecosystem separates
these: API reference lives in Rustdoc, while the book, the reference, and
tutorials live in mdBook. This separation works, but navigating between the two
is a persistent UX friction — when you're reading a tutorial and want to see
the exact signature of a function, you must leave the book and open the docs
page.

### The Key Structural Insight for Nomi

**Documentation infrastructure must ship with the compiler.** Rustdoc is not
the best documentation generator because of its design (it is good but not
revolutionary). It is the best because it is always available, always
consistent, and always verified against the actual code. A language that
outsources documentation to a third-party tool (Python with Sphinx, TypeScript
with TypeDoc, Java with Javadoc) will always have weaker documentation
integration than a language that treats documentation as a compiler concern.

The doc-test-as-executable-example feature is the single most important
documentation quality mechanism across all ecosystems studied. It creates a
hard gate: examples either compile and run correctly, or the documentation
fails CI. This single constraint eliminates the "stale documentation problem"
that every other ecosystem struggles with.

---

## 2. ExDoc (Elixir)

### Core Documentation Philosophy

ExDoc is Elixir's documentation generator, and its philosophy combines several
strands: **documentation is a first-class language construct** (`@doc` and
`@moduledoc` are language-level attributes, not comment conventions),
**doctests are built into the test framework** (ExUnit, not ExDoc), and
**documentation generation produces a structured HTML application with search,
version switching, and function signature linking.**

The Elixir philosophy on documentation is explicit: "Documentation is a
contract. A function without documentation does not exist." The language
encourages documentation as a form of specification — the `@doc` attribute is
where you define what a function promises, and the doctests verify that the
function keeps its promise.

### What Worked Exceptionally Well

**`@doc` and `@moduledoc` as language-level attributes.**
Unlike `///` comments, Elixir's documentation is written as module attributes:

```elixir
defmodule Calculator do
  @moduledoc """
  A module for arithmetic operations.

  Supports addition, subtraction, multiplication, and division
  with configurable precision.
  """

  @doc """
  Adds two numbers.

  ## Examples

      iex> Calculator.add(2, 3)
      5

      iex> Calculator.add(-1, 1)
      0
  """
  def add(a, b), do: a + b
end
```

This is a meaningful design choice. `@doc` is a string that is attached to the
function as metadata. It participates in the Elixir macro system — you can
generate documentation programmatically, conditionally include documentation,
or extract documentation at runtime. The `Code` module provides
`Code.fetch_docs/1` for accessing documentation at runtime. Documentation is
not a comment that is stripped by compilation — it is a language construct.

**Doctests with `iex>` prompts.**
Elixir's doctests use the actual `iex>` (interactive Elixir) prompt syntax:

```elixir
@doc """
Parses a comma-separated string into a list of integers.

## Examples

    iex> Parser.parse("1,2,3")
    {:ok, [1, 2, 3]}

    iex> Parser.parse("1,a,3")
    {:error, "invalid integer at position 2"}
"""
```

The `iex>` convention is a readability win. It is immediately recognizable to
any Elixir developer — this is exactly what you would see in a terminal. The
test framework runs these as actual tests: it evaluates the expression after
`iex>` and compares it to the expected result on the next line. Mismatches
produce diffs showing the expected vs actual output.

**ExDoc's HTML output with search and version switching.**
ExDoc generates a single-page application with several distinguishing features:
- Full-text search across all modules, functions, types, and doc content.
- A keyboard-navigable sidebar (type to filter modules/functions).
- Function signature linking that shows types, default values, and guards.
- Dark/light theme switching.
- Version dropdown for switching between releases.
- Mobile-responsive layout.

The search is particularly well-executed: typing `"parse"` finds functions
named `parse`, modules containing "parse" in their names, and documentation
text containing "parse." The search is client-side (no server needed) and
responds on every keystroke.

**Integration with Mix and hex.pm.**
`mix docs` generates ExDoc documentation locally. `mix hex.publish` publishes
the package to hex.pm, which automatically builds and hosts the documentation.
The integration is seamless: you cannot publish a package without generating
documentation (though you can configure it to skip), and the documentation
appears at `https://hexdocs.pm/package-name/` with the same ExDoc UI as every
other package.

**Documentation as a first-class artifact with metadata.**
ExDoc supports `@doc` metadata tags:

```elixir
@doc since: "1.3.0", deprecated: "Use String.split/2 instead"
```

The rendered HTML shows "Since version 1.3.0" and a deprecation notice with the
recommended replacement. This is lightweight but effective: version tracking
and deprecation notices are part of the documentation metadata, not separate
changelog entries or manual annotations.

### What Failed or Caused Persistent Friction

**Markdown vs. the `iex>` prompt convention.**
The `iex>` convention is visually clear but has a parsing problem: ExDoc needs
to distinguish between `iex>` code blocks and regular Markdown code blocks. The
indentation-based convention (4 spaces before `iex>`) conflicts with Markdown's
indentation rules. This is a design tension that no documentation system has
completely resolved — the desire to use a familiar interactive prompt syntax
conflicts with the need for unambiguous machine-parsable doc tests.

**Narrative documentation support.**
ExDoc generates API reference documentation. Like Rustdoc, it is not designed
for tutorials or guides. The Elixir ecosystem uses ExDoc for API reference and
the separate `ex_doc` tooling chain (or Markdown files rendered on hexdocs.pm)
for guides. The separation between API reference and narrative documentation is
the same problem Rust has.

**Build-time overhead.**
`mix docs` needs to compile the project before generating documentation. For
large umbrella projects, this can be slow. There is no incremental
documentation generation — changing one docstring rebuilds all documentation.

**Runtime documentation overhead.**
Because `@doc` attributes are retained in compiled BEAM files, they contribute
to the size of compiled applications. This is a deliberate tradeoff (documentation
is accessible at runtime), but it means release builds carry documentation bytes
that are never used in production.

### The Key Structural Insight for Nomi

**Documentation as a language construct, not a comment convention.** Elixir's
`@doc` and `@moduledoc` are the most principled approach to doc comments in any
language studied. They make documentation a first-class language feature:
accessible at runtime, transformable by macros, and retained in compiled
artifacts. This is the opposite of the "comment that gets stripped" model
(Javadoc, `///`) and enables use cases that the comment model cannot support:
runtime documentation introspection, programmatic doc generation, and
documentation-aware tooling.

The `iex>` doctest convention is a close second. The insight is that examples
should look like what the user sees in their development environment. The
familiarity of the prompt syntax lowers the barrier to writing doctests and
makes them immediately recognizable.

---

## 3. Julia Documentation

### Core Documentation Philosophy

Julia's documentation system is built around the `@doc` macro, which attaches
documentation to any Julia object. The philosophy is: **documentation is a
binding between a descriptive string and a program object, and that binding is
accessible through the same reflection mechanisms as everything else in the
language.** Julia's documentation is not a comment system, not an attribute
system, but a genuine metadata binding system.

The Markdown standard library provides the content format. Documenter.jl
provides the site generation. The combination gives Julia a documentation
pipeline that is more programmable than Rustdoc/ExDoc but less unified than
either.

### What Worked Exceptionally Well

**The `@doc` macro as a universal documentation mechanism.**
Julia's approach to documentation is to make it a macro that binds a
Markdown string to an object:

```julia
@doc """
    add(x::Number, y::Number) -> Number

Add two numbers together.

# Examples
```julia-repl
julia> add(2, 3)
5

julia> add(2.5, 3.5)
6.0
```

# Extended Help

`add` supports all numeric types that implement `+`.
"""
function add(x::Number, y::Number)
    return x + y
end
```

The `@doc` macro works on any object — functions, types, modules, global
variables, even individual method signatures (thanks to multiple dispatch).
You can query documentation at runtime via `?add` in the REPL, or
`@doc add` in code, or `Docs.doc(add)` programmatically.

**The convention of including the function signature in the docstring.**
Julia's convention is that the first line of a docstring shows the function
signature. This is not enforced — it is a community convention that is so
strongly followed that it functions as a de facto standard:

```julia
"""
    sort(v::AbstractVector; kws...) -> AbstractVector
    sort(A::AbstractArray; dims::Integer) -> AbstractArray
"""
```

The `->` arrow shows the return type. This convention means every docstring
serves as both documentation and a type signature reference, even in the REPL.

**Mathematical notation via LaTeX in Markdown.**
Julia is the only language studied where mathematical notation is a
first-class documentation concern. The Markdown standard library supports
LaTeX math via ````math` blocks and inline `` `$...$` ``. Documenter.jl
renders this to MathJax/KaTeX. This is a genuine domain requirement for a
scientific computing language, and Julia's documentation tooling handles it
without extra configuration:

```julia
@doc """
"""
    gradient(f, x)

Compute the gradient ``\\nabla f(x)`` of the function ``f`` at ``x``.

For a scalar function ``f: \\mathbb{R}^n \\to \\mathbb{R}``, the gradient is:

```math
\\nabla f = \\left[\\frac{\\partial f}{\\partial x_1}, \\ldots, \\frac{\\partial f}{\\partial x_n}\\right]
```
"""
"""
```

**Documenter.jl for building documentation sites.**
Documenter.jl is the de facto standard for building Julia documentation
sites. It reads `@doc` strings from source code and combines them with
Markdown files to produce a static HTML site. Features include:
- Automatic API reference generation from docstrings.
- Cross-references between documented items (`[`sort`](@ref)`).
- Doctest execution during site build (with `doctest = true`).
- Versioned documentation deployment to GitHub Pages.
- PDF generation via LaTeX.

Documenter.jl's architecture separates content (docstrings + Markdown files)
from presentation (HTML/PDF generation). This separation is correct: the
`@doc` macro is the content mechanism, and Documenter.jl is the presentation
layer.

**Doctesting with `jldoctest` blocks.**
Julia's doctesting uses `jldoctest` fence blocks:

````julia
"""
```jldoctest
julia> 1 + 1
2

julia> sqrt(4)
2.0
```
"""
````

Documenter.jl runs these as actual Julia code during documentation build.
The convention of `julia> ` prompt is the same as the REPL, providing the
same familiarity benefit as Elixir's `iex>` prompts.

### What Failed or Caused Persistent Friction

**The `@doc` before declaration convention.**
Julia requires `@doc "..." function ...` — the docstring comes before the
declaration. This is semantically clean (document the thing before you
define it) but visually awkward: the documentation can be quite long, and
the actual function declaration can be hundreds of lines away from its
name. Some developers work around this by writing stub docstrings and
detailed documentation in separate files.

**Documenter.jl configuration complexity.**
While Documenter.jl is powerful, the `make.jl` build script is nontrivial:

```julia
using Documenter
using MyPackage

makedocs(
    modules = [MyPackage],
    format = Documenter.HTML(),
    sitename = "MyPackage.jl",
    pages = [
        "Home" => "index.md",
        "Guide" => "guide.md",
        "API Reference" => "api.md",
    ],
    doctest = true,
)

deploydocs(repo = "github.com/user/MyPackage.jl.git")
```

This is a build script in Julia, not a declarative configuration. Changing
documentation structure requires editing this script. Compared to Rustdoc's
zero-configuration approach (documentation works with no config file), this
is a regression. The power of the script is real, but the cost is that
every package must duplicate a boilerplate `make.jl`.

**Search limitations.**
Documenter.jl's built-in search is functional but inferior to ExDoc's. It
searches only item names and docstrings, not narrative documentation pages.
The search index is generated at build time and loaded client-side, which
limits its size for large packages.

**Module-qualified vs. unqualified docstring lookup.**
Because Julia has multiple dispatch, a function can have many methods, each
with its own docstring. The `?sort` lookup in the REPL must decide which
docstring to show. Julia shows the "most specific" documentation, but this
heuristic can be surprising — adding a new method can change which
docstring the user sees.

### The Key Structural Insight for Nomi

**The tightest possible coupling between documentation and the object it
documents.** Julia's `@doc` macro doesn't just associate documentation with
a name — it associates documentation with a specific object identity. When
you ask for documentation on `sort`, you get the documentation for that
specific method, considering overloading and dispatch. This is the most
precise doc-binding model of any language studied.

The function-signature-in-docstring convention is a pragmatic solution to a
real problem: when a function has multiple methods, the docstring is the
natural place to enumerate them. A doc comment system that only attaches to
one declaration at a time cannot handle multiple dispatch well; Julia's
convention acknowledges this explicitly.

---

## 4. Python Documentation (Sphinx + doctest)

### Core Documentation Philosophy

Python's documentation ecosystem is centered on Sphinx, a documentation
generator that converts reStructuredText (rST) to HTML, PDF, and other
formats. Unlike Rustdoc or ExDoc, Sphinx is not a Python-specific tool — it
is a general-purpose documentation system that happens to have excellent
Python support via its `autodoc` extension.

The philosophy is: **documentation is separate from code, but tooling should
be able to extract documentation from code.** This is in tension with the
Rustdoc/ExDoc philosophy, and understanding this tension is key to
understanding Python's documentation landscape.

### What Worked Exceptionally Well

**`autodoc` — extracting documentation from docstrings.**
Sphinx's `autodoc` extension reads Python docstrings and generates API
documentation. It does this at Sphinx build time (not compile time), which
means it works with dynamically-typed Python where there is no compiler to
query:

```rst
.. automodule:: mymodule
   :members:
   :undoc-members:
   :show-inheritance:
```

This single directive generates documentation for an entire module, including
all classes, methods, and functions. It supports filtering by visibility,
inheritance, and docstring presence. The `autosummary` extension can generate
summary tables of module contents.

**doctest — executable examples in docstrings.**
Python's `doctest` module is part of the standard library and predates every
other doctest system studied:

```python
def add(a, b):
    """Add two numbers.

    >>> add(2, 3)
    5
    >>> add(-1, 1)
    0
    >>> add(2.5, 3.5)
    6.0
    """
    return a + b
```

`python -m doctest mymodule.py` runs all `>>>` examples in docstrings and
reports failures. The `>>>` / `... ` (continuation) syntax is instantly
recognizable to any Python developer — it is the interactive interpreter
prompt. `doctest` also supports `ELLIPSIS` mode for matching variable output,
`NORMALIZE_WHITESPACE` for matching when whitespace is not significant, and
directives like `# doctest: +SKIP` for examples that should not be tested.

**Intersphinx — cross-project documentation linking.**
Sphinx's `intersphinx` extension allows linking to documentation in other
projects:

```rst
:py:func:`numpy.array` creates a new array.
```

When configured with `intersphinx_mapping`, this resolves `numpy.array` to the
actual NumPy documentation URL. This is Sphinx's answer to Rustdoc's intra-doc
links — but it works across projects, not just within a crate.

**Read the Docs for hosting.**
Read the Docs (RTD) provides free documentation hosting for open-source
Python projects. Every push to the project's repository triggers a Sphinx
build and deploys the result. Versioned documentation (stable, latest, and
per-release) is automatic. RTD solved the documentation hosting problem for
Python before docs.rs existed for Rust, and its model of automatic
build-from-repository influenced every subsequent documentation hosting
service.

**Numpydoc and Google-style docstrings — ecosystem conventions.**
The Python community developed two detailed docstring conventions:

Numpydoc style:
```python
def add(a, b):
    """Add two numbers.

    Parameters
    ----------
    a : int or float
        The first number.
    b : int or float
        The second number.

    Returns
    -------
    int or float
        The sum of `a` and `b`.

    Examples
    --------
    >>> add(2, 3)
    5
    """
```

Google style:
```python
def add(a, b):
    """Add two numbers.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The sum of a and b.

    Examples:
        >>> add(2, 3)
        5
    """
```

Both styles are supported by Sphinx via the `napoleon` extension. The
existence of two major conventions is a reflection of Python's decentralized
ecosystem, but both conventions converge on the same information: parameter
descriptions, return descriptions, and examples. The fragmentation is a cost,
but the conventions themselves encode a genuinely useful standard for what API
documentation should include.

### What Failed or Caused Persistent Friction

**Sphinx's configuration complexity.**
A minimal Sphinx `conf.py` is not minimal:

```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
]
html_theme = 'furo'
```

But that's misleading — a real project's `conf.py` grows to 100+ lines with
intersphinx mappings, autodoc configuration, Napoleon settings, and
customization. The configuration is a Python script, which means it can do
arbitrary things, which means it can break in arbitrary ways.

**reStructuredText vs. Markdown.**
Sphinx's native format is rST, not Markdown. While MyST-Parser now enables
Markdown in Sphinx, the rST legacy creates friction:
- rST has a learning curve that Markdown does not.
- rST link syntax (`` :ref:`link` ``) is more verbose than Markdown.
- rST table syntax is genuinely painful.
- Most developers write Markdown in every other context (GitHub, README,
  commit messages), making rST the odd format out.

The MyST-Parser bridge helps, but it is a bridge — not a native experience.
Every Python project must decide whether to use rST or MyST, and the
ecosystem documentation diverges depending on the choice.

**Docstring extraction gap.**
Sphinx extracts documentation at build time, not at run time. This means:
- Docstrings can reference types that don't exist at Sphinx build time.
- Dynamic attributes and generated methods require manual `autodoc`
  configuration.
- Documentation can be silently wrong if the code changes but docs are
  not rebuilt.

**doctest limitations.**
Python's `doctest` has several sharp edges:
- Whitespace sensitivity: `>>> result ` (trailing space) is different from
  `>>> result`.
- Dictionary output ordering was nondeterministic before Python 3.7, making
  dictionary doctests fragile.
- Floating-point comparisons require `# doctest: +ELLIPSIS` or
  `+NORMALIZE_WHITESPACE` for approximate matching.
- Long doctests are hard to maintain because they're embedded in strings
  within the source code.

**No universal documentation host with versioning.**
While RTD is excellent, it is not universal. Python packages can host
documentation anywhere. The result is that a Python developer cannot assume
that `package-name/docs.python.org` or a similar predictable URL exists.
Compare this to docs.rs and hexdocs.pm, where every package's documentation
is at a predictable URL.

**The typing documentation gap.**
Python's optional type annotations are not consistently reflected in
documentation. Sphinx can extract type annotations via `autodoc_typehints`,
but the integration is optional, the rendering varies by theme, and many
projects still document types in docstring text that can diverge from the
actual annotations.

### The Key Structural Insight for Nomi

**A documentation generator must not require per-project build scripts.**
Sphinx's `conf.py` is an anti-pattern — a documentation system that requires
every project to maintain a build script in the target language is one that
has failed at the "just works" bar. Rustdoc requires zero configuration.
ExDoc requires minimal configuration (`:docs` in `mix.exs`). Sphinx requires
a nontrivial configuration file that grows with the project.

The second insight is that **documentation format must match the developer's
working format.** Python developers write Markdown everywhere except in
documentation, where they write rST. This format mismatch is friction that no
tool can eliminate. A documentation system should use the same markup format
that the ecosystem already uses for READMEs, issues, and commit messages.

---

## 5. Racket Scribble

### Core Documentation Philosophy

Scribble is Racket's documentation language, and it is the most radical
documentation system in this survey. Its philosophy is: **documentation is a
program.** Scribble is not a markup language with a documentation generator
behind it. It is a Racket language — it has the full power of Racket's macro
system, module system, and runtime behind every documentation page.

A Scribble document is a Racket module that produces a rendered document as
output. You can define functions, use libraries, and generate content
programmatically from within documentation. The boundary between "writing
documentation" and "writing a program that produces documentation" does not
exist in Scribble.

### What Worked Exceptionally Well

**Documentation is programmable.**
In Scribble, you write:

```racket
#lang scribble/manual

@title{My Library}

@defmodule[my-library]

@defproc[(add [a number?] [b number?]) number?]{
  Returns the sum of @racket[a] and @racket[b].

  @examples[
    (add 2 3)
    (add -1 1)
  ]
}

@defthing[pi number?]{
  The mathematical constant @math{\pi}.
}
```

The `@` forms are Racket functions. `@title`, `@defproc`, `@examples` are
not markup tags — they are Racket functions that produce documentation
elements. You can write:

```racket
@(for/list ([n (in-range 1 6)])
   @item{Factorial of @n is @(factorial n)})
```

This generates an itemized list of factorial values by calling an actual
function. The documentation is a program that computes some of its own
content.

**`@examples` and `@interactions` — evaluable code blocks.**
Scribble's `@examples` and `@interactions` forms are the most
sophisticated evaluable documentation blocks in any system:

```racket
@examples[
  (add 2 3)
  (add -1 1)
  (add "hello" "world")
]
```

Scribble evaluates each expression at documentation-build time, captures the
result, and renders both the expression and its result as a formatted
interaction. The result is always accurate — if the code changes, the
evaluated output changes. There is no separate doctest pass; evaluation and
rendering are the same step.

**`@racketblock` and `@codeblock` for typed code presentation.**
Scribble understands Racket syntax. When you write:

```racket
@racketblock[
  (define (fib n)
    (cond [(= n 0) 0]
          [(= n 1) 1]
          [else (+ (fib (- n 1)) (fib (- n 2)))]))
]
```

The output is syntax-highlighted Racket code with proper indentation.
Scribble knows that `define` is a keyword, `fib` is a function name, and
`cond` is a special form. This is not regex-based highlighting — it is
parser-based and always correct.

**The Racket Guide + Racket Reference separation.**
Racket's documentation is split into two canonical documents:
- The **Racket Guide** — a narrative introduction with examples, intended to
  be read sequentially.
- The **Racket Reference** — a comprehensive specification of every form
  and function, intended for lookup.

This separation is deliberate and successful. A learner reads the Guide; an
experienced developer looks up details in the Reference. The Guide links to
the Reference for comprehensive details; the Reference links to the Guide
for contextual explanation. This is the cleanest implementation of the
tutorial/reference separation in any language ecosystem.

**Contract examples in documentation.**
Racket's contract system integrates with Scribble:

```racket
@defproc[(safe-divide [x number?] [y (and/c number? (not/c zero?))])
         number?]{
  Divides @racket[x] by @racket[y], which must be non-zero.
}
```

The contracts in `@defproc` are not just documentation — they are executable
specifications. Documentation says what the function expects and returns, and
the contract system enforces it at runtime. When a contract is violated, the
error message includes the documentation-level description of what was
expected.

### What Failed or Caused Persistent Friction

**The `@` syntax learning curve.**
Scribble's `@` syntax is Racket's reader syntax. To write `@title{...}` you
need to understand Racket's `@`-reader, which transforms `@`-expressions
into Racket S-expressions. This means that writing Scribble requires
understanding a non-trivial reader transformation. The cognitive load is
real: you are effectively writing Racket code, not markup, and the
transformation from `@`-notation to S-expressions must be understood to
debug rendering issues.

**Scribble documents cannot be read as plain text.**
A Scribble document with `@examples`, `@racketblock`, and `@defproc` forms
is not meaningfully readable without rendering. The raw source is a Racket
program peppered with `@`-forms. This is in direct tension with Javadoc and
Rustdoc, where the raw doc comment is readable as text. Scribble trades
source readability for rendering power.

**Tooling outside DrRacket.**
Scribble is tightly integrated with DrRacket (the Racket IDE) but has limited
support in other editors. VS Code's Racket support can syntax-highlight
Scribble, but the `@examples` evaluation and live preview that DrRacket
provides are absent. This limits Scribble's utility for developers who prefer
other editors.

**Build dependency on Racket.**
Because Scribble documents are Racket programs, building documentation
requires a full Racket installation. There is no "Scribble-lite" that can
render documentation without the complete Racket runtime. This is a design
choice (documentation is programmable, and programmability requires the
runtime), but it means documentation cannot be built on machines without
Racket.

**Limited adoption outside Racket.**
Scribble's model is deeply compelling, but Racket's small ecosystem means
that Scribble's ideas have not propagated to other languages. The
"documentation is a program" model has not been adopted by any major
language. This may be because the model is too powerful (most documentation
does not need programmability) or because the Racket-specific `@`-reader
syntax is not transferable.

### The Key Structural Insight for Nomi

**Documentation as a program is a legitimate extreme, not a mistake.**
Scribble is the only documentation system in this survey that treats
documentation as a genuinely executable artifact. The `@examples` form
evaluates code at documentation-build time and renders the result — there
is no separate "doctest" pass because evaluation and rendering are unified.
This model eliminates the stale-example problem more thoroughly than any
other system: an example in Scribble is always evaluated against the current
code, always.

The Guide/Reference split is the second major insight. Racket demonstrates
that a language's documentation should be two distinct artifacts: one for
learning (sequential, narrative, example-driven) and one for reference
(comprehensive, lookup-oriented, contract-specified). The structural
separation between these two modes of documentation is more important than
any specific rendering technology.

---

## 6. Go Documentation

### Core Documentation Philosophy

Go's documentation philosophy is radical minimalism: **documentation is
comments, formatted to a convention that the tools understand.** There is
no special doc comment syntax. There are no documentation tags. There is
no documentation configuration. `go doc` reads comments, and `go doc`
outputs formatted text.

This is Go's simplicity thesis applied to documentation: the tool does one
thing (extract and format comments), and the conventions do the rest. The
result is the lowest-friction documentation experience of any language
studied — but also the least powerful.

### What Worked Exceptionally Well

**`go doc` — instant, zero-config documentation.**
```bash
go doc fmt.Println
# func Println(a ...any) (n int, err error)
# Println formats using the default formats for its operands and writes to
# standard output. Spaces are always added between operands and a newline
# is appended. It returns the number of bytes written and any write error
# encountered.
```

`go doc` works with zero configuration. It reads comments from source files,
identifies the comment block that precedes the declaration, and formats it
to the terminal. It works for standard library packages, third-party
packages, and local packages with identical syntax. `go doc` is the
documentation equivalent of `gofmt`: one tool, one canonical behavior, no
options.

**The convention: comment starts with the symbol name.**
Go's documentation convention is that the first sentence of a doc comment
starts with the name of the thing being documented:

```go
// Println formats using the default formats for its operands and writes to
// standard output.
func Println(a ...any) (n int, err error) { ... }

// Regexp is the representation of a compiled regular expression.
// A Regexp is safe for concurrent use by multiple goroutines,
// except for configuration methods, such as Longest.
type Regexp struct { ... }
```

This convention means that `go doc` output is always self-describing. The
tool doesn't need to prepend the symbol name — the comment already contains
it. The convention also produces documentation that reads naturally as
prose: "Println formats using..." reads like a sentence, not a tag.

**Package documentation via `doc.go`.**
Go convention is to place package-level documentation in a `doc.go` file
(or at the top of any file in the package). The comment before `package`
becomes the package documentation:

```go
// Package fmt implements formatted I/O with functions analogous
// to C's printf and scanf. The format 'verbs' are derived from
// C's but are simpler.
//
// # Printing
//
// The verbs:
//
//	%v	the value in a default format
//	%+v	when printing structs, the plus flag adds field names
//
// # Scanning
// ...
package fmt
```

Package documentation is plain text formatted by `go doc`. There is no
Markdown rendering in the terminal. The convention of indented lists (using
tabs) is understood by `go doc` and formatted as run-in headings.

**pkg.go.dev — the universal Go documentation host.**
Go's module proxy (proxy.golang.org) powers pkg.go.dev, which provides a
unified documentation surface for every Go package:
- Every published Go module has documentation at
  `pkg.go.dev/module/path`.
- Documentation shows types, functions, constants, and variables.
- Source links on every declaration.
- Import graph visualization.
- License detection and display.
- Search across the entire Go ecosystem.

The key feature is that pkg.go.dev is automatic. A Go developer publishes a
module to a repository, and within minutes, pkg.go.dev has its documentation.
There is no opt-in, no configuration, no build script.

**Example functions as both tests and documentation.**
Go's testing package recognizes functions named `ExampleXxx`:

```go
func ExamplePrintln() {
    fmt.Println("hello", "world")
    // Output:
    // hello world
}
```

Example functions serve three purposes simultaneously:
- They are runnable tests (`go test` executes them and checks the `// Output:`).
- They appear in `go doc` output as usage examples.
- They appear on pkg.go.dev as formatted, runnable examples (with a "Run" button).

The `// Output:` comment is the expected output. The test runner captures
stdout and compares it. If the output changes, the test fails. This is Go's
answer to doctests — but as separate functions rather than embedded doc
comments.

### What Failed or Caused Persistent Friction

**No Markdown in terminal output.**
`go doc` outputs plain text. Package documentation can use simple formatting
conventions (indented lists, headings by convention), but there is no
bold/italic/code formatting in the terminal. Developers reading complex
documentation in the terminal get a wall of undifferentiated text.

The rationale is Go's simplicity thesis: `go doc` should work the same
everywhere, and terminal rendering of Markdown is inconsistent. But the
result is that `go doc` is less useful for complex documentation than
a browser-based version.

**Limited inter-package linking.**
Go doc comments can reference other packages by their import path, but there
is no formal linking syntax. `go doc` does not resolve these references.
pkg.go.dev does some automatic linking of import paths, but it is
heuristic-based. Compare to Rustdoc's `` [`Vec`] `` syntax, which the
compiler resolves and verifies.

**No type-driven doc generation.**
Go's documentation is entirely comment-driven. The tool does not leverage
the type system to generate any part of the documentation. Function
signatures are shown, but there is no extraction of type relationships,
interface implementations, or method sets beyond what the comments describe.
TypeDoc (TypeScript) demonstrates what is possible when documentation
generation leverages the type system; Go demonstrates the minimal-comment
alternative.

**Example function naming rigidity.**
`ExampleFunc`, `ExampleType_Method`, `Example()` — the naming convention
for example functions is strict but not type-checked. Misspelling a function
name in an example just means the example won't appear in documentation,
with no warning.

**The `doc.go` convention is inconsistent.**
The convention of putting package documentation in `doc.go` is not enforced.
Package documentation can be in any file. Multiple files can have package
documentation (the first one wins, but it's not deterministic which file
comes first). The result is that package documentation location is a
convention, not a rule, and tooling cannot reliably identify it.

### The Key Structural Insight for Nomi

**"No special syntax" is a legitimate documentation posture.** Go
demonstrates that a documentation system can work with zero special doc
comment syntax. `//` comments before declarations ARE the documentation,
and `go doc` extracts them. This is the most radical simplification of
the doc comment design space, and it works — Go has excellent standard
library documentation produced with this system.

The example-function-as-test-and-documentation pattern is the cleanest
doctest model of any language studied. By making examples first-class
functions rather than embedded code blocks, Go solves three problems at
once:
- Example organization (one function = one example, clearly named).
- Example execution (examples ARE tests, run by the test framework).
- Example presentation (examples are rendered as formatted code with
  an expected output comment).

The cost is that examples are not inline — you cannot put a small example
next to a parameter description. But for larger examples, the function
separation is a win.

---

## 7. Javadoc

### Core Documentation Philosophy

Javadoc is the original API documentation standard (released with JDK 1.0 in
1996). Its philosophy is: **documentation is structured comments with tagged
sections for parameters, return values, exceptions, and other API contract
elements.** Javadoc established the paradigm that every other documentation
system in this survey either extends or reacts against.

The core mechanism is simple: `/** ... */` comments preceding declarations,
containing a description followed by `@tag` annotations. `javadoc` (the tool)
processes these comments and generates HTML.

### What Worked Exceptionally Well

**The `@param @return @throws` tag convention.**
Javadoc's tag vocabulary is small, precise, and universally understood:

```java
/**
 * Divides one integer by another.
 *
 * @param dividend the number to be divided
 * @param divisor  the number to divide by
 * @return the quotient of {@code dividend / divisor}
 * @throws ArithmeticException if {@code divisor} is zero
 * @since 1.2
 * @see Math#floorDiv(int, int)
 */
public int divide(int dividend, int divisor) {
    if (divisor == 0) throw new ArithmeticException("division by zero");
    return dividend / divisor;
}
```

Each tag has a clear, non-overlapping responsibility:
- `@param` — describe a parameter
- `@return` — describe the return value
- `@throws` — describe when and why an exception is thrown
- `@see` — cross-reference to related items
- `@since` — version when the API was introduced
- `@deprecated` — mark as deprecated with replacement guidance

This small vocabulary is arguably the most successful API of any
documentation system. Every Java developer knows these tags. Every Java IDE
understands them. Every documentation tool in the Java ecosystem parses them.
The tags are so successful that they have been copied (with slight
variations) by JSDoc, TSDoc, Doxygen, and Python docstring conventions.

**Ecosystem-wide standardization.**
Javadoc created a uniform documentation standard for the entire Java
ecosystem. Every Java library's documentation looks and works the same way.
The HTML output may vary in styling, but the structure (class hierarchy,
method summaries, field details, tag sections) is identical. A Java
developer can navigate any Java library's API documentation without
learning a new documentation layout.

**IDE integration.**
Modern Java IDEs (IntelliJ, Eclipse, VS Code) parse Javadoc comments and
provide:
- Hover documentation showing formatted Javadoc.
- Parameter name and type hints derived from `@param` tags.
- Autocompletion of `@` tags within doc comments.
- Warning when `@param` references a parameter that doesn't exist.
- Warning when a parameter lacks a `@param` tag.
- Refactoring support: renaming a parameter updates its `@param` references.

This level of IDE integration for documentation is unmatched by any other
language ecosystem. It exists because Javadoc has been stable and
standardized for 25+ years, giving IDE developers a fixed target.

**Package-level documentation.**
Javadoc supports `package-info.java` for package-level documentation:

```java
/**
 * Provides the classes and interfaces for the Nomi language runtime.
 *
 * <h2>Package Specification</h2>
 * <ul>
 *   <li><a href="...">Nomi Language Specification</a>
 * </ul>
 *
 * @since 1.0
 */
package com.nomi.runtime;
```

This is a design choice that persists: every documentation system needs a
way to document packages/modules separately from individual declarations.

**Inheritance of documentation.**
Javadoc can inherit documentation from superclasses and interfaces when a
method overrides another without adding new documentation. The
`{@inheritDoc}` inline tag allows selective inheritance with augmentation:

```java
/**
 * {@inheritDoc}
 * <p>This implementation also validates the input range.</p>
 */
@Override
public int divide(int dividend, int divisor) { ... }
```

This is a genuine documentation DRY mechanism — the documentation for a
method contract lives in the interface, and implementations inherit it
automatically.

### What Failed or Caused Persistent Friction

**HTML embedded in comments.**
Javadoc's biggest design mistake is the requirement to embed HTML directly
in doc comments for any formatting beyond plain text:

```java
/**
 * Returns a <em>view</em> of the portion of this list between the specified
 * {@code fromIndex}, <b>inclusive</b>, and {@code toIndex}, <b>exclusive</b>.
 * <p>
 * This method eliminates the need for explicit range operations (of the sort
 * that commonly exist for arrays). Any operation that expects a list can be
 * used as a range operation by passing a {@link List#subList(int, int)} view.
 * <table>
 *   <caption>Supported operations</caption>
 *   <tr><th>Operation</th><th>Behavior</th></tr>
 *   <tr><td>{@code size()}</td><td>returns {@code toIndex - fromIndex}</td></tr>
 * </table>
 */
```

`<p>`, `<em>`, `<b>`, `<table>` — the need to write HTML tags within Java
comments is a persistent pain point. Javadoc introduced `{@code ...}` for
inline code and `{@link ...}` for links, but these escape hatches only
highlight how much of the documentation is raw HTML.

The failure is not just aesthetic. HTML-in-comments means:
- Documentation is harder to read in source code (HTML tags break the text
  flow).
- Documentation is harder to write (developers must know HTML).
- Documentation is fragile (mismatched tags produce broken rendering with
  no warning).
- Documentation portability is limited (the comments are not plain text).

**No Markdown support before Java 23.**
Javadoc added Markdown support in Java 23 (2024) — 28 years after it was
released. For nearly three decades, Java developers had exactly one option
for formatting documentation: raw HTML. This is the most visible failure of
the Javadoc model and a cautionary tale for any documentation system that
commits to a specific markup format without an escape path.

**The tool/comment coupling.**
Javadoc comments are semantically meaningless without the Javadoc tool.
`/**` is just a multi-line comment to the Java compiler — the compiler does
not parse `@param` tags, does not verify `@see` references, and does not
warn about missing documentation. This is the opposite of Rustdoc, where
the compiler resolves `[`Item`]` links and warns about doc comments on
the wrong targets.

**Generated HTML defaults.**
The default HTML output of Javadoc is unattractive and information-sparse
compared to modern documentation sites. The "frames" layout (class list in
one frame, method details in another) feels dated. Modern alternatives
(like Dokka for Kotlin) produce much better-looking output from the same
Javadoc comments, proving that the problem is the Javadoc HTML generator,
not the comment format.

**Verbosity without proportional value.**
Javadoc's `@param` and `@return` tags encourage documentation of every
parameter, but the value of `@param x the x coordinate` is zero. The
tags create an expectation of completeness that leads to documentation
that is complete but worthless. This is a systemic failure: the tool
encourages documentation volume over documentation quality.

### The Key Structural Insight for Nomi

**Standard tags for API contract elements are valuable, but they must be
paired with good defaults.** Javadoc's `@param @return @throws` vocabulary
is genuinely useful — it standardizes the structure of API documentation
across an entire ecosystem. The failure is not the tags but the
encouragement of boilerplate: a system that pushes developers toward
`@param x the x coordinate` is a system that has failed to distinguish
between documentation that adds information and documentation that
re-states the obvious.

The second insight is that **the raw source must be readable without
rendering.** Javadoc's HTML-in-comments requirement makes source code
documentation harder to read as source code. A good documentation system
uses a lightweight markup format that reads naturally as plain text
(Markdown, AsciiDoc) and renders to rich HTML.

---

## 8. TypeDoc (TypeScript)

### Core Documentation Philosophy

TypeDoc is TypeScript's documentation generator, and its philosophy is
distinctive: **the type system IS documentation.** TypeDoc leverages
TypeScript's type system to generate documentation that would be redundant
to write manually. Parameter types, return types, generic constraints,
union types, and conditional types are all extracted from the compiled
type information and rendered automatically.

The developer writes description text and examples; TypeDoc handles
everything the type system already knows. This is the documentation
equivalent of "don't repeat yourself."

### What Worked Exceptionally Well

**Type information extracted from the compiler.**
TypeDoc uses the TypeScript compiler API to extract types:

```typescript
/**
 * Creates a new reactive value.
 *
 * @typeParam T - The type of the contained value
 * @param initialValue - The initial value of the signal
 * @returns A readonly signal and a setter function
 *
 * @example
 * ```ts
 * const [count, setCount] = createSignal(0);
 * setCount(5); // count() now returns 5
 * ```
 */
export function createSignal<T>(
  initialValue: T
): readonly [() => T, (value: T | ((prev: T) => T)) => void] {
  // implementation
}
```

The rendered documentation shows the function signature with complete type
information — the generic `T`, the parameter type, the complex return type
with union and function types. The developer only wrote the description and
the `@typeParam` annotation. TypeDoc extracted everything else.

**Generics, union types, and conditional types rendered natively.**
TypeDoc renders complex TypeScript types in a structured way:

- `T extends { length: number }` — generic constraints are shown as
  type-level documentation.
- `string | number | boolean` — union types are shown with each member
  as a clickable link to its own documentation.
- `Pick<T, K> & Partial<Omit<T, K>>` — intersection types, mapped types,
  and utility types are all rendered with links.
- Conditional types (`T extends Promise<infer U> ? U : T`) are shown with
  syntax highlighting and links.

This is documentation that leverages the type system as a source of truth.
There is no manual `@param name The name (string)` when TypeScript already
knows `name: string`. The type annotation is the parameter documentation.

**`@example` blocks rendered as formatted, typed code.**
TypeDoc's `@example` blocks render TypeScript code with full syntax
highlighting, and the examples can include type annotations:

```typescript
/**
 * @example
 * ```ts
 * interface User {
 *   id: number;
 *   name: string;
 *   email: string;
 * }
 *
 * const user: User = { id: 1, name: "Alice", email: "alice@example.com" };
 * ```
 */
```

The rendered examples show types as part of the code, making the examples
both usage documentation and type documentation.

**Reflection-based documentation of everything.**
TypeDoc can generate documentation for:
- Classes, interfaces, type aliases, enums.
- Functions, methods, constructors.
- Properties, accessors, index signatures.
- Type parameters, type arguments.
- Modules and namespaces.
- The module graph (imports/exports).

The reflection-based approach means TypeDoc discovers the entire API surface
automatically. You can configure it to show only exported items, only public
items, or everything including internal details.

**Configuration via `typedoc.json`.**
TypeDoc uses a JSON configuration file (or CLI flags) rather than a build
script:

```json
{
  "entryPoints": ["src/index.ts"],
  "out": "docs",
  "excludePrivate": true,
  "excludeProtected": false,
  "includeVersion": true,
  "searchInComments": true,
  "navigation": {
    "includeCategories": true,
    "includeGroups": true
  }
}
```

This is a declarative configuration — no build script, no programmable
configuration. It is simpler than Sphinx's `conf.py` but less flexible.
For API documentation, the simplicity is appropriate.

### What Failed or Caused Persistent Friction

**Limited narrative documentation support.**
TypeDoc generates API reference, not narrative documentation. Writing a
tutorial or guide requires a separate tool (VitePress, Docusaurus, Nextra).
The TypeScript ecosystem has no unified answer to "how do I write a guide
with inline API reference links?" This is the same problem that Rust,
Elixir, and Julia face — but TypeScript's ecosystem is larger and more
fragmented, so the tools don't converge.

**Comment syntax — JSDoc legacy.**
TypeDoc uses JSDoc-style `/** */` comments with `@tag` annotations. This is
a legacy of TypeScript's JavaScript heritage, but it means TypeDoc inherits
JSDoc's weaknesses: the `@tag` syntax is verbose compared to Rustdoc's
`` [`Item`] `` or ExDoc's `@doc`, and the `/** */` delimiters are heavy
compared to `///`.

**Configuration drift between TypeDoc versions.**
TypeDoc's configuration format has changed across major versions, and the
migration path is not always smooth. Plugins written for one TypeDoc version
may not work with the next. This is a stability problem that Rustdoc and
Javadoc avoid by being more tightly coupled to the compiler.

**No inline doctest execution.**
TypeDoc does not run example code. `@example` blocks are rendered as
formatted code but not executed. The TypeScript ecosystem relies on
separate test files for verifying examples. This is a meaningful hole:
there is no mechanical guarantee that TypeDoc examples are correct.

**The `@typeParam` redundancy.**
TypeDoc extracts generic type parameters from the type system, but
`@typeParam T - The element type` is still written manually. The description
is useful, but the tag syntax is boilerplate that must be kept in sync with
the actual type parameter name. Renaming a type parameter requires updating
every `@typeParam` reference.

### The Key Structural Insight for Nomi

**The type system should generate all the documentation that the type system
already knows.** TypeDoc's core insight — that parameter types, return
types, and generic constraints are documentation that should be extracted,
not manually written — applies to any statically-typed language. Nomi
should never require a developer to write `@param x The x coordinate
(int)` when the type system already knows `x: Int`.

The configuration approach (declarative JSON vs build script) is secondary
but important. TypeDoc's `typedoc.json` is simpler than Sphinx's `conf.py`,
and the simplicity is appropriate. Documentation configuration should be
declarative data, not executable code.

---

## 9. Literate Programming Systems

### Core Documentation Philosophy

Literate programming is a paradigm where the program and its documentation
are a single artifact, authored for human understanding first and machine
execution second. The canonical formulation is Knuth's WEB system (1984):
"Instead of imagining that our main task is to instruct a computer what to
do, let us concentrate rather on explaining to human beings what we want a
computer to do."

The key structural idea: the source code is a document written in natural
language, and the executable code is extracted (tangled) from it. The
reverse process (weaving) produces the formatted documentation.

### WEB / CWEB (Knuth, 1984/1990)

WEB is the original literate programming system. A WEB document interleaves
TeX documentation with Pascal code:

```
@* Introduction.
This section explains the algorithm for finding prime numbers using the
Sieve of Eratosthenes.

@p
The program has two parts: setting up the sieve and printing the results.
We begin by defining the maximum sieve size:

@c
@<Constants@>=
#define MAX_N 1000

@ The main program allocates the sieve and calls the two subroutines.

@c
int main() {
    int sieve[MAX_N + 1];
    @<Initialize the sieve@>@;
    @<Cross out multiples@>@;
    @<Print the primes@>@;
}
```

The `@` forms (`@*`, `@c`, `@p`) are control codes that tell the WEB
system how to process the text. `@<...@>` is a named code section — the WEB
system can output code sections in any order, reordering them for human
readability while tangling produces the correct compilation order.

**What WEB got right:**
- The "explain, then implement" narrative structure forces authors to
  justify code decisions.
- Named code sections allow presenting code in an order optimized for
  human understanding, not compiler requirements.
- The interleaving of documentation and code at the paragraph level means
  every piece of code has context immediately adjacent.

**Why WEB did not become the dominant paradigm:**
- The write-tangle-weave cycle is slow (seconds, not milliseconds).
- The weaving/tangling toolchain is fragile and language-specific.
- TeX as the documentation language is both powerful and intimidating.
- Named code sections make debugging harder (the compiled code does not
  match the woven source line-for-line).
- The requirement to justify every code decision in prose is exhausting
  for routine code.
- Most programmers want to think about code, then document — the reverse
  order is a cognitive mismatch for many.

### noweb (Ramsey, 1989)

noweb simplified WEB's model by removing TeX dependency and using a simpler
section syntax:

```
\section{Prime number sieve}
This section implements the Sieve of Eratosthenes.

<<Constants>>=
#define MAX_N 1000

\section{Main program}
<<main program>>=
int main() {
    int sieve[MAX_N + 1];
    <<Initialize the sieve>>
    <<Cross out multiples>>
    <<Print the primes>>
}
```

noweb is language-agnostic (it works with any programming language) and
uses a simpler markup syntax. It was more practical than WEB but still
suffered from the same fundamental problem: programmers don't want to write
documentation-first, and the tangle step adds friction to the edit-compile
cycle.

### Org-mode with Babel (Emacs, 2010s)

Org-mode's Babel extension is the most practical literate programming system
in active use. An Org document contains code blocks that can be executed
inline:

```
* Data analysis pipeline

#+begin_src python :results output
import pandas as pd

df = pd.read_csv("data.csv")
print(df.describe())
#+end_src

The output shows that our dataset has significant skew in the
#+end_src
```

Org Babel supports 50+ languages, can pass data between code blocks in
different languages, and can tangle code blocks to separate source files.
It is widely used for computational notebooks, research papers, and
reproducible data analysis.

**What Org Babel got right:**
- Code blocks are first-class document elements with a standard syntax.
- Results are captured and displayed inline — the document is a live
  computational artifact.
- Tangling to separate source files means Org documents can produce
  standard project structures.
- Language-agnostic: one document can contain R, Python, SQL, and shell
  blocks.

**Why Org Babel did not become the dominant paradigm:**
- Emacs dependency limits adoption.
- The Org syntax is rich but unfamiliar to non-Emacs users.
- Mixing prose and code at the paragraph level works for analysis but
  scales poorly to large software projects.
- The execution model (evaluate blocks in order) does not match modern
  build systems.

### What Survived of Literate Programming

Several ideas from literate programming survived in mainstream tools:

1. **Doc comments with embedded examples** (Rustdoc, ExDoc, Python doctest).
   The idea that examples are part of the documentation and can be executed
   is a direct descendant of WEB's "this is the program and this is what it
   does" interleaving.

2. **Computational notebooks** (Jupyter, Observable, Quarto). The notebook
   model — interleaved prose, code, and output — is the most successful
   adaptation of literate programming. Jupyter notebooks are the dominant
   format for data science and scientific computing, and they preserve the
   core literate programming idea: the document is both narrative and
   executable.

3. **Documentation tests** (doctests in every language). The idea that
   documentation examples should be executed and verified is WEB's most
   enduring contribution to software engineering.

4. **README-driven development.** The practice of writing the README before
   the code — describing the API as you want developers to experience it —
   is a literate-programming-in-miniature.

5. **mdBook, Quarto, and computational publishing.** Tools that produce
   books and articles from Markdown files with embedded, executable code
   blocks are the direct descendants of the weave step.

### The Key Structural Insight for Nomi

**Literate programming failed as a universal paradigm but succeeded as a
specialized mode for explanation, teaching, and research.** The "document
first, code second" ordering is genuinely better for some artifacts:
tutorials, language guides, algorithm explanations, and analysis notebooks.
It is worse for routine application code where the structure is
well-understood and the documentation need is reference, not explanation.

Nomi should not mandate literate programming but should enable it as a
mode. A Nomi documentation system should:
- Support interleaved prose and executable code blocks (like Org Babel or
  Jupyter).
- Allow documentation-first authoring for tutorials and guides.
- Generate API reference from source doc comments (the standard model).
- Let the two modes coexist: guides are literate programs; reference is
  generated from comments.

---

## 10. Diataxis Framework

### Core Documentation Philosophy

Diataxis (from the Greek "dia" + "taxis" = across + arrangement) is a
documentation organization framework developed by Daniele Procida. It is
not a tool — it is a theory that documentation should be organized into
four distinct modes, each with a different purpose, form, and reader
relationship:

```
              ┌─────────────────────────┐
              │    Practical steps      │
              ├────────────┬────────────┤
              │  Tutorial  │ How-to     │  ← Learning / doing
              ├────────────┼────────────┤
              │ Explanation│ Reference  │  ← Understanding / looking up
              └────────────┴────────────┘
              │                        │
         Learning-oriented     Information-oriented
```

The four modes:
1. **Tutorial** — a lesson that teaches through doing. The user is a
   learner. The tone is "let me show you." The form is a sequential
   narrative that the user follows step by step.
2. **How-to guide** — a recipe for solving a specific problem. The user
   has a task. The tone is "here's how to do X." The form is a series
   of steps with a clear goal.
3. **Explanation** — background, context, and design rationale. The user
   wants to understand. The tone is "here's why." The form is discursive
   and can be read in any order.
4. **Reference** — technical description of the machinery. The user knows
   what they're looking for. The tone is "just the facts." The form is
   structured, exhaustive, and designed for lookup.

### The Four Modes in Detail

**Tutorials** must work — the learner follows along and gets a working
result. A tutorial that fails at step 3 is worse than no tutorial. Good
tutorials include:
- A clear, narrow goal stated at the top.
- Every step specified exactly (no "now just configure your database").
- Working code that produces visible output at each step.
- A satisfying conclusion that shows the learner they succeeded.

**How-to guides** solve problems. A good how-to:
- Has a title that is a concrete user goal: "How to connect to PostgreSQL."
- Assumes the user knows the domain but not the specific API.
- Provides the minimum steps to achieve the goal.
- Does not explain why (that's explanation) or explore alternatives
  (that's tutorial).

**Explanation** provides understanding. It answers "why was this designed
this way?" and "what are the tradeoffs?" Good explanation:
- Connects concepts across the system.
- Provides historical context and design rationale.
- Is not sequenced (can be read in any order).
- Does not contain step-by-step instructions.

**Reference** is the API documentation. Good reference:
- Is complete and accurate.
- Is structured for lookup, not reading.
- Describes the machinery, not the task.
- Uses a consistent format that the user can scan.

### Applying Diataxis to Language Documentation

Under Diataxis, a programming language's documentation surface should be:

| Mode | What it is | Where it lives | Example |
|------|------------|----------------|---------|
| Tutorial | Getting started guide | `docs/tutorial/` | "Your first Nomi program" |
| How-to | Task-oriented recipes | `docs/howto/` | "How to handle null values" |
| Explanation | Design rationale | `docs/explanation/` | "Why Nomi uses constraints instead of types" |
| Reference | API docs, spec | Generated from source | Module index, function reference |

### What Rust/Elixir/Julia Get Right or Wrong Under This Lens

**Rust:** Excellent reference (Rustdoc + std::docs), excellent explanation
(The Book's early chapters on ownership/borrowing), good tutorials
(Rustlings, "The Book" Ch 1-2), weak how-to guides (discoverable recipes
for common tasks are scattered across blog posts and Stack Overflow). The
Rust Reference is a pure reference; The Book mixes tutorial and explanation.

**Elixir:** Excellent reference (ExDoc), good tutorials (Getting Started
guide), weak how-to guides, limited formal explanation (design rationale
lives in José Valim's talks and blog posts, not in the documentation). The
Getting Started guide is a true tutorial: step-by-step, works end-to-end.

**Julia:** Excellent reference (Documenter.jl), good tutorials (JuliaAcademy,
the manual's getting-started chapter), mixed explanation (some good
rationale in the manual, but scattered), limited how-to guides.

**Python:** Excellent reference (Sphinx docs for stdlib), good tutorials
(official tutorial is genuinely good), mixed how-to guides (official howto
section is thin; real how-to content is on Stack Overflow and blog posts),
variable explanation (PEPs provide design rationale, but they are not
integrated into the documentation).

**Racket:** The cleanest Diataxis alignment of any language studied. The
Racket Guide is a tutorial/explanation artifact for learners. The Racket
Reference is a pure reference. The separation is explicit and navigable.

### The Key Structural Insight for Nomi

**Documentation organization must be a first-class design decision, not an
emergent property of the tooling.** Every language in this survey has some
form of tutorial, reference, and explanation, but none (except Racket) has
a deliberate structural separation of the four Diataxis modes. The result
is documentation that works well for one mode (usually reference) and poorly
for the others.

Nomi's documentation should be organized explicitly by Diataxis mode. The
documentation structure should make it impossible to confuse a tutorial
(which is sequential, narrative, and should be read start-to-finish) with
a reference page (which is structured, exhaustive, and should be scanned
for specific information).

---

## 11. Cross-Language Synthesis

### 11.1 Structural Invariants (Patterns Across All Successful Systems)

These are features that appear in every mature documentation system,
regardless of language or era. They represent convergence, not fashion —
a documentation system that omits them will eventually add them.

**1. Doc comments attach to declarations at the syntax level.**
Every system has a mechanism for associating documentation text with a
specific declaration (function, type, module, class). The syntax varies
(`///`, `/**`, `@doc`, `#`), but the invariant is universal:
documentation lives adjacent to the thing it documents in the source file.
No successful system relies on a separate documentation file for API
reference.

**2. A standard markup format for documentation content.**
Every system converges on a lightweight markup language for documentation
content. Markdown is the dominant choice (Rustdoc, ExDoc, Documenter.jl,
TypeDoc, Go's pkg.go.dev rendering). Even Javadoc, which used raw HTML for
28 years, added Markdown support in Java 23. The markup must be readable as
plain text and render to rich HTML.

**3. Executable examples as documentation verification.**
Every system studied has some form of executable examples. Rustdoc runs doc
tests as part of `cargo test`. ExDoc/ExUnit runs doctests as part of `mix
test`. Julia's Documenter.jl runs `jldoctest` blocks. Python's `doctest`
module runs `>>>` examples. Go's example functions run as tests. Scribble
evaluates `@examples` at build time. The invariant: examples in
documentation should be verified against the current code.

**4. Cross-references between documented items.**
Every system provides a mechanism for linking from one documented item to
another. Rustdoc uses `` [`Item`] `` with compiler resolution. Sphinx uses
`:ref:` and `:py:func:` roles. Javadoc uses `{@link}`. ExDoc links module
and function names automatically. The invariant: documentation is a graph,
not a flat list, and cross-references make the graph navigable.

**5. An ecosystem-level documentation host.**
Every successful ecosystem has a central documentation host. docs.rs for
Rust, hexdocs.pm for Elixir, pkg.go.dev for Go, Read the Docs for Python,
and Julia's package documentation hosted via Documenter.jl's deployment. The
invariant: users should be able to read any package's documentation without
installing the package.

**6. Search across the documentation surface.**
Every documentation system provides search. Rustdoc, ExDoc, Documenter.jl,
TypeDoc, pkg.go.dev, and Read the Docs all include client-side search across
documentation content. The invariant: users should be able to find things
by typing what they're looking for, not by navigating a hierarchy.

**7. Documentation generation as a build step.**
Every system integrates documentation generation into the build pipeline.
`cargo doc` is a Cargo subcommand. `mix docs` is a Mix task. `sphinx-build`
runs as part of the CI pipeline. The invariant: documentation is built from
source, not maintained separately.

### 11.2 Genuine Design Forks (Where Systems Made Different Tradeoffs)

**1. Documentation as comment vs. documentation as language construct.**
| Model | Systems | Tradeoff |
|-------|---------|----------|
| Comment (not part of the language) | Javadoc, Rustdoc, Go | Simpler syntax, no runtime overhead, documentation stripped at compile time |
| Language construct (accessible at runtime) | Elixir (`@doc`), Julia (`@doc` macro) | Documentation is introspectable, transformable, retained in artifacts; adds runtime size |
| Programmable document (documentation is code) | Scribble | Maximum power, documentation can compute content; requires the runtime to build |

Rustdoc's model (comment syntax, compiler-integrated processing) has won in
terms of ecosystem adoption. Elixir's model (language construct) enables use
cases (runtime documentation introspection, `h` helper in IEx) that the
comment model cannot. Scribble's model (documentation is a program) enables
use cases (computed documentation, documentation that generates itself from
the codebase) that neither can.

**2. Inline examples vs. separate example functions.**
| Model | Systems | Tradeoff |
|-------|---------|----------|
| Inline examples (code blocks in doc comments) | Rustdoc, ExDoc, Julia, Python, Scribble | Examples are co-located with documentation; harder to maintain for complex examples |
| Separate example functions (named test functions) | Go | Examples are first-class tests; examples are separated from the documentation they illustrate |
| Both | — | No system successfully supports both models equally well |

Go's example functions are the cleaner design for complex examples, but
they lose the spatial locality of inline examples. Inline examples are
better for showing a single function's usage; separate functions are better
for showing multi-function workflows.

**3. Markup format: Markdown vs. custom vs. nothing.**
| Format | Systems | Tradeoff |
|--------|---------|----------|
| Markdown | Rustdoc, ExDoc, Julia, TypeDoc, pkg.go.dev | Familiar to developers, rich ecosystem, good plain-text readability |
| rST | Sphinx/Python | More powerful than Markdown, better cross-referencing, steeper learning curve |
| Custom | Scribble (Racket `@`-reader) | Optimized for the language, programmable, unfamiliar to newcomers |
| Plain text | `go doc` terminal output | Zero overhead, works everywhere, no rich formatting |

Markdown has won the markup format war. Even systems that started with
other formats (Python's rST, Java's HTML) have added Markdown support. The
only holdouts are Go (which deliberately offers no rich formatting in
terminal output) and Scribble (which needs a custom format for its
programmability model).

**4. Configuration: zero vs. minimal vs. build script.**
| Configuration model | Systems | Tradeoff |
|---------------------|---------|----------|
| Zero configuration | Rustdoc, Go | Works out of the box; no per-project customization |
| Minimal declarative config | TypeDoc (`typedoc.json`), ExDoc (`:docs` in `mix.exs`) | Some customization; configuration is data, not code |
| Build script | Sphinx (`conf.py`), Documenter.jl (`make.jl`) | Full power; requires maintenance, can break |

Rustdoc's zero-configuration approach is the ideal. Every documentation
system should aim for "works out of the box with no configuration," with
minimal declarative configuration for customization and a fixed escape
hatch for genuinely unusual requirements.

**5. Search implementation: client-side vs. server-side.**
| Search model | Systems | Tradeoff |
|--------------|---------|----------|
| Client-side (JavaScript search index) | Rustdoc, ExDoc, Documenter.jl | Works offline; search index must be downloaded; index size limited |
| Server-side (search API) | Read the Docs (with addon), docs.rs (limited) | Handles large datasets; requires a server; doesn't work offline |
| Hybrid | pkg.go.dev | Server-side for ecosystem-wide search; no offline mode |

Client-side search is the right default for API documentation (fast,
works offline, no infrastructure). Server-side search is necessary for
ecosystem-wide search across all packages.

**6. Versioning: per-version builds vs. latest-only.**
| Versioning model | Systems | Tradeoff |
|------------------|---------|----------|
| Every version documented | docs.rs, hexdocs.pm, Read the Docs | Users can read docs for their installed version; higher storage cost |
| Latest version only | pkg.go.dev (with redirect to older versions) | Lower storage cost; users on older versions must search for their docs |
| Release branches | Sphinx/RTD (version selector) | Users switch between versions; build cost per version |

Every system converges on versioned documentation. The only question is
whether every version is permanently available (docs.rs) or whether old
versions eventually disappear (some RTD configurations).

**7. The tutorial/reference boundary.**
| Boundary model | Systems | Tradeoff |
|----------------|---------|----------|
| Single tool for everything | Sphinx (with extensions for tutorials) | One tool, one format; tutorial content is shoehorned into API doc format |
| Two separate tools | Rust (mdBook for books, Rustdoc for API) | Each tool is optimized for its mode; navigating between them requires context switches |
| Explicit mode separation in tool | Documenter.jl (manual pages, API pages) | Pages can be marked as guide or reference; same tool, different rendering |

No system has solved the tutorial/reference unification problem well.
Rust's two-tool split is pragmatic but creates navigation friction. The
Diataxis framework describes what the solution should look like — four
distinct modes within a single documentation surface — but no language
ecosystem has built it.

### 11.3 The "Doc Comment" Design Space

How doc comments attach to declarations is a design decision with deep
consequences. The dimensions are:

**Syntax: prefix, delimiter, or attribute?**
- **Prefix** (`///`, `//!`, `##`): Every doc line starts with a marker.
  Pros: lightweight, reads like a comment, easy to scan. Cons: repetition
  of the prefix character on every line; less natural for multi-paragraph
  text.
- **Delimiter** (`/** ... */`, `"""..."""`): Doc text is enclosed in
  delimiters. Pros: natural for multi-paragraph text; the enclosing
  delimiters signal "this is documentation." Cons: delimiters are heavy
  for single-line docs; nesting issues with code blocks.
- **Attribute** (`@doc "...", @moduledoc "..."`): Documentation is a
  language attribute. Pros: documentation is a language construct;
  programmatic generation possible; runtime accessible. Cons: more
  verbose syntax; looks less like a comment and more like code.

**Attachment: position-based or name-based?**
- **Position-based** (Rustdoc `///`, Javadoc `/**`, Python docstrings):
  Documentation attaches to the next (or previous) declaration. The
  compiler determines what is being documented by syntactic position.
- **Name-based** (Elixir's `@doc` before `def`, Go's comment convention):
  Documentation includes the name of the thing being documented. The
  convention, not the compiler, determines the attachment.
- **Explicit binding** (Julia's `@doc "..." function ...`): The `@doc`
  macro explicitly binds documentation to the following declaration.

**Content: inline or external?**
- **Inline** (every system surveyed): Documentation lives in the source
  file adjacent to the code. This is universal for API documentation.
- **External** (Sphinx's `autodoc` can pull from separate `.rst` files,
  but this is secondary): Documentation lives in separate files. Rare
  for API documentation; common for narrative documentation.

**The best design for Nomi:**
A prefix-based syntax (like Rustdoc's `///`) for single-line and
short documentation, with a delimiter-based alternative (like
`"""..."""` docstrings) for multi-paragraph documentation, both attaching
to the next declaration by position. The prefix syntax handles the common
case (a one-line description) with minimal visual noise. The delimiter
syntax handles the complex case (multi-paragraph documentation with
examples) with natural text flow.

### 11.4 Doctest Design

Executable examples are the single most effective documentation quality
mechanism. The design dimensions:

**When should doctests run?**
Every system converges on the same answer: doctests run as part of the
test suite. `cargo test` includes doctests. `mix test` includes doctests.
Documenter.jl's `doctest = true` runs them during the documentation build.
Go's `go test` runs example functions. The invariant: **doctests are tests
that happen to live in documentation, not documentation that happens to be
testable.**

**What makes a good doctest?**
- It is minimal — the smallest example that demonstrates the behavior.
- It produces deterministic output that can be mechanically compared.
- It tests the documented behavior, not edge cases (those belong in unit
  tests).
- It is readable as documentation first and as a test second.
- It is self-contained (or uses `# ` hidden lines for setup).

**How should doctests be structured?**
- **Inline code blocks** (Rustdoc, ExDoc, Python): The doctest is a code
  block within the doc comment. Pros: spatial locality. Cons: difficult to
  share setup; long examples clutter the doc comment.
- **Separate functions** (Go): The doctest is a named function. Pros:
  first-class test status; clear naming. Cons: separated from the
  documentation it illustrates.
- **Evaluated blocks** (Scribble `@examples`): The code is evaluated at
  documentation build time. Pros: always current. Cons: build time
  dependency; evaluation order constraints.

The inline code block model is the right default for Nomi, with a mechanism
for named example blocks (like Go's example functions) for complex,
multi-function workflows.

### 11.5 API Reference vs. Guide vs. Tutorial

The structural tension: how to organize documentation across the four
Diataxis modes without creating four separate documentation silos.

**The current state (across all ecosystems):**
- API reference is well-served by doc comment generators (Rustdoc, ExDoc,
  TypeDoc, Javadoc).
- Tutorials exist in most ecosystems but vary in quality and discoverability.
- How-to guides are the most neglected mode — scattered across blog posts,
  Stack Overflow, and wiki pages.
- Explanation is usually deferred to blog posts, conference talks, and
  design documents rather than being part of the official documentation.

**The ideal structure (Diataxis-aligned):**
```
docs/
  tutorial/      # Sequential, narrative, "follow along"
  howto/         # Task-oriented, "I want to do X"
  explanation/   # Design rationale, "why is it this way"
  reference/     # Generated API docs, "what does this function do"
```

Each section has different rendering, navigation, and authoring conventions.
The tutorial is long-form sequential pages. The how-to is a searchable
list of recipes. The explanation is interlinked essays. The reference is
the structured API docs.

**The key insight:** These four modes should be visible as four distinct
sections in the documentation navigation, with different visual treatment
and different reading expectations. A user should never wonder "am I reading
a tutorial or a reference page?" — the mode should be immediately apparent
from the page layout.

### 11.6 Search and Navigation

**What search must support:**
- Full-text search across all documentation (reference, tutorials, how-to,
  explanation).
- Search by function/type/module name (fuzzy matching).
- Search by concept ("how to parse JSON").
- Search filtering by documentation mode ("show me only reference results").
- Keyboard navigation (type to search, arrow keys to navigate, enter to
  select).

**What navigation must support:**
- Sidebar with collapsible module/class hierarchy.
- Breadcrumb trail showing the current page's location in the hierarchy.
- "See also" links at the bottom of reference pages.
- Previous/next links in sequential content (tutorials).
- Cross-references that work across documentation modes (tutorial linking
  to reference, reference linking to explanation).

**The ExDoc/Observable standard:**
ExDoc's search is the best implementation in the survey: client-side,
responsive on every keystroke, searches names and content, keyboard
navigable. Combined with the sidebar module hierarchy, it makes finding
things fast. The Observable pattern (instant preview of search results,
not just a list of links) is a further improvement that no documentation
system has adopted.

### 11.7 Versioning

Documentation versioning is a solved problem with a clear best practice:
every version should have permanently available documentation, and the
version selector should be prominent.

**docs.rs model (best):**
- Every published version has documentation at a predictable URL.
- The URL structure is `docs.rs/crate/version/`.
- `docs.rs/crate/latest/` redirects to the latest stable version.
- The version dropdown in the page header lists all versions.
- Old versions are never removed (storage is the only cost).

This model requires:
- A documentation host that builds and stores documentation for every
  version.
- Immutable published versions (if a version can be changed, its
  documentation is stale).
- A URL scheme that encodes version information.

For Nomi, the docs.rs model is the clear target. Every version published
to the package registry should have documentation built and hosted at a
predictable URL, with a version selector on every page.

### 11.8 Anti-Patterns (Documentation Mistakes That Consistently Hurt Ecosystems)

**1. HTML embedded in documentation comments.**
Javadoc's raw-HTML requirement was the single worst documentation design
decision in this survey. It made documentation harder to write, harder to
read in source, and harder to port to new rendering targets. The lesson: use
a lightweight markup format (Markdown) for documentation content, and let
the tool render it.

**2. Documentation generator as a separate project from the compiler.**
Python's Sphinx, Java's Javadoc (which runs as a separate tool, not as part
of `javac`), and TypeScript's TypeDoc are all separate from the language
compiler/runtime. This means the documentation generator cannot leverage
compiler internals (type resolution, cross-crate references) and must
reimplement them. Rustdoc's integration with `rustc` is the correct model.

**3. A documentation system that requires per-project build scripts.**
Sphinx's `conf.py` and Documenter.jl's `make.jl` are anti-patterns.
Documentation generation should require at most a declarative configuration
file, and ideally zero configuration.

**4. Doc comment syntax that is hard to discover.**
`///` and `//!` are not intuitive to newcomers. The documentation system
should make its syntax discoverable: if a developer writes `// This is a
doc comment` when they should have written `/// This is a doc comment`,
the tool should warn or suggest the correct syntax.

**5. Documentation examples that are not tested.**
The most common documentation quality failure is examples that don't work.
Every system that added doctest execution (Rust, Elixir, Julia, Python, Go)
saw a dramatic improvement in documentation quality. A documentation system
without automated example verification is incomplete.

**6. Mixing documentation modes without clear visual distinction.**
When a reference page looks like a tutorial page, users apply the wrong
reading strategy. Reference pages should be scannable and structured;
tutorial pages should be linear and narrative. The page layout should make
the mode immediately apparent.

**7. No ecosystem-level documentation host.**
Languages where documentation hosting is left to individual projects
(Python before RTD, C/C++, early JavaScript) have fragmented documentation
that varies in quality, availability, and format. A central documentation
host (docs.rs, hexdocs.pm, pkg.go.dev) is an ecosystem-level good that
benefits every user.

**8. Doc comments that duplicate type information.**
When `@param x int the x coordinate` appears in a language where the
compiler already knows `x: int`, the documentation system has failed.
Documentation should add information that the type system does not provide:
semantics, constraints, examples, and context.

**9. Breaking documentation toolchain on language version upgrades.**
Sphinx version upgrades, TypeDoc version upgrades, and Javadoc tool
changes have all broken documentation builds for existing projects. The
documentation toolchain should be as stable as the compiler — a project's
documentation should build correctly on the same language version for the
lifetime of that version.

**10. @deprecated without migration guidance.**
Marking an API as deprecated without telling the user what to use instead
is worse than not deprecating it. Every deprecation notice should include
the replacement API and the version when the deprecated API will be
removed.

---

## 12. Nomi Adopt / Refuse / Adapt Table

| # | Insight | Action | Rationale |
|---|---------|--------|-----------|
| 1 | **Documentation infrastructure ships with the compiler** (Rustdoc, Go doc) | **Adopt** | `nomi doc` generates documentation for any Nomi package with zero configuration. The documentation generator is part of the Nomi toolchain, not a separate project. This is the single most important documentation decision — it ensures documentation is always available, always consistent, and always verified against the actual code. Rustdoc is the reference implementation. |
| 2 | **Prefix-based doc comment syntax** (Rustdoc `///`, Go `//`) | **Adapt** | Use `///` for outer doc comments (document the next declaration) and `//!` for inner doc comments (document the enclosing module). This is Rustdoc's syntax and it works well. Add IDE quick-fixes for common mistakes: if a developer writes `//` instead of `///` before a declaration, suggest the correction. The two-form distinction (`///` vs `//!`) is precise and unambiguous. |
| 3 | **Doctests as first-class tests** (Rustdoc, Elixir/ExUnit, Go) | **Adopt** | Code blocks marked as examples in doc comments are compiled and executed by `nomi test`. Doctest failures fail CI with a precise error pointing to the doc comment location. The `nomi>` prompt convention (analogous to Elixir's `iex>` and Python's `>>>`) makes doctests immediately recognizable as interactive sessions. Support `# ` hidden lines for setup code (Rustdoc convention). |
| 4 | **Documentation as a language construct, accessible at runtime** (Elixir `@doc`, Julia `@doc` macro) | **Adapt** | Documentation is compiled into the module as metadata and accessible at runtime via reflection. This enables `help()` in the REPL, runtime documentation queries, and documentation-aware tooling. Unlike Elixir, use a lightweight syntax (`///`) rather than `@doc` attributes for the common case, but retain the metadata in compiled artifacts. The tradeoff (binary size for doc strings) is acceptable for development and debugging builds; provide a `--strip-docs` flag for release optimization. |
| 5 | **Ecosystem-level documentation host** (docs.rs, hexdocs.pm, pkg.go.dev) | **Adopt** | Every package published to the Nomi registry has documentation built and hosted at `docs.nomi.dev/package-name/latest`. Version switching is built into every page. The URL scheme follows docs.rs: `docs.nomi.dev/pkg/version/`, with `/latest/` redirecting to the most recent stable release. This is an ecosystem-level feature that should be designed before the first public package exists. |
| 6 | **Diataxis-aligned documentation structure** (Racket Guide/Reference split, Diataxis framework) | **Adopt** | Nomi's documentation surface is organized into four explicit sections: Tutorial, How-to, Explanation, Reference. Each section has distinct rendering and navigation. The Reference section is generated from doc comments (`nomi doc` output). The other three sections are written in a format that supports interleaved prose and executable code blocks. The Racket Guide/Reference separation proves this model works at language scale. |
| 7 | **Type information extracted from the compiler, not duplicated in docs** (TypeDoc) | **Adopt** | Never require `@param x: Int the x coordinate` when the compiler already knows `x: Int`. Generated documentation shows parameter types, return types, and generic constraints from the type system. The developer writes the semantic description and examples — everything the type system already knows is rendered automatically. TypeDoc is the reference for this model. |
| 8 | **Intra-doc links verified by the compiler** (Rustdoc `` [`Item`] ``) | **Adopt** | Documentation links use namespace-qualified paths that the compiler resolves and verifies. `` [`Vec::map`] `` either resolves to the correct item or produces a compiler warning/error. This eliminates broken documentation links — the most common documentation drift problem in systems that use URL-based links (Javadoc, Sphinx). |
| 9 | **Markdown as the documentation content format** (universal convergence) | **Adopt** | Documentation content is written in Markdown (CommonMark with extensions: tables, footnotes, task lists, LaTeX math). Markdown is readable as plain text, widely understood, and has a rich rendering ecosystem. Reject rST (learning curve), raw HTML (unreadable in source), and custom formats (require learning). The Markdown dialect should be specified and stable. |
| 10 | **Example functions as named documentation tests** (Go `func ExampleXxx()`) | **Adapt** | Adopt Go's example-function pattern for complex, multi-step examples that don't fit in inline doc comments. An `example` block in a Nomi source file is both a runnable example and a documentation artifact. The naming convention `example_<function_name>` or `example_<concept>` makes examples discoverable by both the test runner and the documentation generator. Inline doctests handle the simple case; example functions handle the complex case. |
| 11 | **Sphinx-style per-project build scripts** (`conf.py`, `make.jl`) | **Refuse** | Documentation generation should not require writing a build script. `nomi doc` works with zero configuration. For customization, use a declarative `[doc]` section in `Nomi.toml` (like Cargo's approach). An escape hatch for programmatic documentation generation (analogous to Rust's `#[doc]` attribute) is acceptable, but the escape hatch should produce documentation content, not configure the build pipeline. |
| 12 | **Javadoc-style `@param @return @throws` tag vocabulary** | **Adapt** | Provide a small, fixed vocabulary of semantic tags for API documentation: `@param` for parameter semantics (not type — the type system provides that), `@returns` for return value semantics, `@throws` for error conditions, `@since` for version introduction, `@deprecated` with replacement guidance. The tags are structured so tools can validate them (e.g., `@param` references a parameter that exists). Javadoc's tag vocabulary is genuinely useful; the failure was the requirement to use them for information the type system already provides. |
| 13 | **Deprecation with structured migration guidance** (ExDoc `@doc deprecated:`) | **Adopt** | `@deprecated "Use split/2 instead" since: "1.3.0" removal: "2.0.0"` — every deprecation includes the replacement API, the version when deprecation started, and the version when removal is planned. Tools can surface this information at the call site (IDE warnings, compile-time hints) and in generated documentation. ExDoc's `@doc deprecated:` attribute is the cleanest implementation. |
| 14 | **Executable tutorials with inline results** (Scribble `@examples`, Org Babel, Jupyter) | **Adapt** | Tutorials and how-to guides support interleaved prose and executable code blocks. A code block in a tutorial is executable — the documentation build runs it and captures the output. The rendered tutorial shows both the code and the captured output. This is the Jupyter/Quarto model applied to language documentation: the tutorials are live computational documents, not static text. Scribble's `@examples` and Org Babel's model are the references. |
| 15 | **Scribble-level documentation programmability** (documentation as a Racket program) | **Refuse** | Documentation should not be a Turing-complete program. The Scribble model (documentation IS code in the host language) is powerful but creates three problems: documentation cannot be read without rendering, documentation builds require the full language runtime, and the barrier to writing documentation is the barrier to writing code. Keep documentation content as Markdown with executable code blocks — the content is data, the code blocks are executed, but the document structure is not a program. |
| 16 | **Client-side search with instant response** (ExDoc) | **Adopt** | Documentation search is client-side (JavaScript search index), responds on every keystroke, searches across names, docstrings, and narrative content, and supports keyboard navigation. ExDoc's search is the best reference implementation. For ecosystem-wide search (across all packages), a server-side search index is acceptable as a supplementary feature. |
| 17 | **Versioned documentation with permanent URLs** (docs.rs) | **Adopt** | Every published version has permanently available documentation at `docs.nomi.dev/pkg/version/`. `/latest/` redirects to the latest stable release. The version selector on every page lists all versions. Old versions are never removed. This is the docs.rs model and it is the correct one. |
| 18 | **Hover documentation in IDEs** (Javadoc IDE integration) | **Adopt** | The language server protocol (LSP) integration surfaces documentation in hover tooltips. `///` doc comments on functions, types, and modules are the primary content source. The hover shows the formatted doc comment, the function signature (from the type system), and links to related documentation. Javadoc's IDE integration is 25 years old and still the standard; Nomi's LSP server should match or exceed it. |
| 19 | **Go's "comment starts with symbol name" convention** | **Adapt** | Encourage but do not enforce. `go doc` output is readable because every doc comment starts with the name of the thing it documents. Nomi should recommend this convention in the style guide and provide a lint that suggests it, but not make it a compiler requirement. The convention improves `nomi doc` terminal output and makes generated documentation more scannable. |
| 20 | **Narrative documentation with API reference inline** | **Adapt** | The four documentation modes (tutorial, how-to, explanation, reference) live in separate sections with distinct rendering, but cross-references work across all sections. A tutorial can link to a reference page for a specific function, and the reference page can link back to the tutorial that introduces it. The reference uses a `:[link]` syntax that the compiler verifies; the narrative sections use standard Markdown links with a convention for cross-mode references. |

---

## 13. Sources

- Rustdoc: [The rustdoc Book](https://doc.rust-lang.org/rustdoc/), [Documentation tests](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html), [Intra-doc links](https://doc.rust-lang.org/rustdoc/write-documentation/linking-to-items-by-name.html), [The `#[doc]` attribute](https://doc.rust-lang.org/rustdoc/write-documentation/the-doc-attribute.html)
- docs.rs: [About docs.rs](https://docs.rs/about), [docs.rs build environment](https://docs.rs/releases/queue)
- ExDoc: [ExDoc documentation](https://hexdocs.pm/ex_doc/), [Doctests in Elixir](https://hexdocs.pm/ex_unit/ExUnit.DocTest.html), [Writing Documentation](https://hexdocs.pm/elixir/writing-documentation.html)
- Julia: [Julia Documentation](https://docs.julialang.org/en/v1/manual/documentation/), [Documenter.jl](https://documenter.juliadocs.org/), [Doctests in Documenter.jl](https://documenter.juliadocs.org/stable/man/doctests/)
- Sphinx: [Sphinx Documentation](https://www.sphinx-doc.org/), [autodoc extension](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html), [Napoleon (NumPy/Google docstrings)](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- Python doctest: [doctest module](https://docs.python.org/3/library/doctest.html)
- Read the Docs: [Read the Docs Documentation](https://docs.readthedocs.io/)
- NumPy docstring standard: [numpydoc docstring guide](https://numpydoc.readthedocs.io/en/latest/format.html)
- Scribble: [Scribble: The Racket Documentation Tool](https://docs.racket-lang.org/scribble/), [Scribble Manual](https://docs.racket-lang.org/scribble/index.html), [Racket Guide](https://docs.racket-lang.org/guide/)
- Go: [Go Doc Comments](https://go.dev/doc/comment), [Example functions](https://go.dev/pkg/testing/#hdr-Examples), [pkg.go.dev](https://pkg.go.dev/)
- Javadoc: [Javadoc Guide](https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html), [JEP 467: Markdown Documentation Comments](https://openjdk.org/jeps/467)
- TypeDoc: [TypeDoc Documentation](https://typedoc.org/), [TypeDoc with TypeScript](https://typedoc.org/guides/doccomments/)
- TSDoc: [TSDoc Standard](https://tsdoc.org/)
- WEB/CWEB: Knuth, D. E. (1984). "Literate Programming." The Computer Journal, 27(2), 97-111. [CWEB Manual](https://www-cs-faculty.stanford.edu/~knuth/cweb.html)
- noweb: Ramsey, N. (1994). "Literate Programming Simplified." IEEE Software, 11(5), 97-105. [noweb homepage](https://www.cs.tufts.edu/~nr/noweb/)
- Org-mode Babel: [Org Babel](https://orgmode.org/worg/org-contrib/babel/), [Org Mode Manual](https://orgmode.org/manual/)
- Diataxis: Procida, D. (2021). "Diataxis: A systematic approach to technical documentation authoring." [diataxis.fr](https://diataxis.fr/)
- Observable: [Observable Documentation](https://observablehq.com/documentation/)
- Quarto: [Quarto Documentation](https://quarto.org/)
- Dokka: [Dokka (Kotlin documentation engine)](https://github.com/Kotlin/dokka)

---

*This document synthesizes research across ten documentation systems and frameworks.
It is not a specification — it is source material for Nomi's documentation design.
File under `docs/research/`. Companion docs: `packaging_and_project_structure_deep_dive.md`
(packaging), `standard_library_design_comparative.md` (stdlib design),
`interactive_explanation_deep_dive.md` (explanatory tooling), `cross_language_synthesis_master.md`
(capstone synthesis). Connecting Nomi concept: the `explain` design primitive should
bridge documentation and interactive explanation — see `docs/convenience/design_lessons_and_integration.md`
for the explain/error/docs integration surface.*
