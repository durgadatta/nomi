# Nomi

Nomi is an experimental programming language for starting with small, readable
scripts and gradually growing them into dependable programs. It aims to combine
Python's ease of use with clearer types, data validation, failures, and control
over operations such as reading files or making network requests.

Today you can try calculations, functions, collections, and a local JSON report
in the browser or from the command line. The broader language is still being
designed and built. Syntax and behavior may change as the project develops.

**[Try Nomi in your browser](https://durgadatta.github.io/nomi/web/)** ·
**[Getting started](docs/guide/getting_started.md)** ·
**[Documentation](docs/README.md)**

## Quick Start

### Try a calculation

Open the [playground](https://durgadatta.github.io/nomi/web/), choose
`calculate.nomi`, and run it. This program calculates an invoice in integer cents:

```nomi
func subtotal(price, quantity):
    return price * quantity

price = 1200
quantity = 3
delivery = 250
total = subtotal(price, quantity) + delivery
print(total)
```

It prints `3850`. Change `quantity` to `4` and run again to get `5050`.
Try `"three"` to see an error, then repair it by restoring a number.

### Run it locally

From a checkout of this repository, use Python 3.12 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
nomi samples/calculate.nomi --output program
```

You can also run directly from the checkout without installing the package:

```bash
python3 scripts/cli.py samples/calculate.nomi --output program
```

Continue with [Getting Started](docs/guide/getting_started.md) to validate JSON,
repair invalid input, inspect results, and try the experimental source checker.

## What You Can Use Today

These capabilities belong to the current prototype. The examples are a useful
starting point for the syntax supported by each execution path.

| Task | Start here | Current scope |
| --- | --- | --- |
| Write a calculation with a reusable function | [Calculation](samples/calculate.nomi) | Run, change values, and inspect output or errors. |
| Validate input and produce a JSON report | [Report walkthrough](docs/guide/getting_started.md#validate-a-json-report) | Two built-in report schemas; repair field errors and export JSON in the default browser route. |
| Transform collections and explore text | [Data pipeline](samples/data_pipeline.nomi), [text notebook](samples/text_pipeline.nomi.nb) | Prototype collection operations and delimited-text examples. |
| Check a calculation before running it | [Source checking](docs/guide/getting_started.md#check-a-program-without-running-it) | A limited experimental checker for scalar values and direct functions. |
| Work in notebooks or an editor | [Jupyter](tools/jupyter/README.md), [VS Code](docs/orientation/vscode_extension.md) | Local notebook kernel and an extension with highlighting and run commands. |

The browser and Python execution paths cover different subsets and have
different numeric limits. The [getting-started guide](docs/guide/getting_started.md#current-limits)
explains the limits relevant to these examples.

## How Nomi Will Grow

The first useful language is focused on **small scripts and trustworthy local
data reports**. The goal is to let you add stronger guarantees as a program
grows, while keeping ordinary code readable.

| Stage | What it should let you do | Status |
| --- | --- | --- |
| Explore a small script | Calculate, call functions, and see results immediately. | Runnable prototype examples. |
| Turn imperfect input into a useful report | Validate fields, repair errors, and export the result. | A bounded report workflow runs today; general typed data and decoding remain work in progress. |
| Grow a script into a reusable local library | Check inputs, outputs, expected failures, and operations that touch the outside world. | Limited source checking exists; checked local module reuse is still planned. |
| Build larger applications and domain tools | Add services, structured concurrent work, packages, and libraries for data and other domains. | Later delivery work; supporting research and target designs exist. |

These stages describe direction and dependencies, with no release dates promised.
The [target design](docs/design/README.md) explains the intended language;
the [delivery roadmap](docs/orientation/project_roadmap.md#delivery-order-and-dependencies)
tracks the steps toward it. Code in design documents may use features that do
not run yet. Runnable examples live in [samples](samples/).

## Find Your Next Step

| If you want to… | Read… |
| --- | --- |
| Learn by running and changing examples | [Getting Started](docs/guide/getting_started.md) |
| Find guides, design references, or research | [Documentation](docs/README.md) |
| Understand the intended language | [Target Design](docs/design/README.md) |
| See delivery priorities and recent changes | [Roadmap](docs/orientation/project_roadmap.md), [Changelog](CHANGELOG.md) |
| Set up tools or contribute to the implementation | [Developing Nomi](docs/orientation/development.md), [agent/contributor map](AGENTS.md) |
| Explore the evidence behind design choices | [Research](docs/research/README.md), [AI collaboration](docs/orientation/ai_collaboration.md) |

## Web Playground

The [online playground](https://durgadatta.github.io/nomi/web/) lets you edit and
run examples, inspect output and diagnostics, and download source. Notebook
examples use `# %%` cell markers: `Shift+Enter` runs the current cell and
`Run All` starts again from the top.

To run the playground locally from the repository root:

```bash
python3 scripts/launch_web.py
```

Local setup, Rust/WASM build requirements, and browser checks are described in
[Developing Nomi](docs/orientation/development.md#web-playground).

Nomi is an early experimental preview. There is no source compatibility promise
yet, and the prototype does not implement the complete target language.
