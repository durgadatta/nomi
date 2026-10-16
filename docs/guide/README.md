# Learn And Use Nomi

> Status: user documentation entry point for the current prototype and its growth path.

[Project](../../README.md) / User guide

Nomi starts with ordinary programs: name values, call functions, choose what to
do, repeat work, and inspect the result. The current prototype lets you explore
those ideas in the browser and CLI. Stronger types, data boundaries, and reusable
checked libraries are being added gradually.

## Learn In Order

| Step | Guide | What you will learn |
| --- | --- | --- |
| 1 | [Getting Started](getting_started.md) | Run a calculation, repair input, and produce a JSON report. |
| 2 | [Language Basics](language_basics.md) | Values, functions, choices, loops, records, and collection operations. |
| 3 | [Example Catalog](examples.md) | Choose a focused example and recognize experimental syntax. |
| 4 | [Using Nomi's Tools](tools.md) | Work with source files, browser cells, the CLI, notebooks, and VS Code. |
| 5 | [Current Support And Growth](status.md) | Understand what is runnable, limited, planned, or still being researched. |

Start with a guide that matches your task. Each runnable code block in Language
Basics is a complete small program; you can paste it into a browser scratch
document or save it as `example.nomi` and run it from the CLI.

## Find An Answer

| Question | Go to |
| --- | --- |
| Why is this code failing? | [Troubleshooting](tools.md#troubleshooting) |
| How do I save my work or export results? | [Browser files and results](tools.md#browser-playground) |
| Which sample should I read next? | [Example catalog](examples.md) |
| Is syntax in a design document available yet? | [Support labels and differences](status.md#reading-status-labels) |
| What do types, effects, and capabilities mean? | [Growing a program](status.md#the-guarantees-being-built) |
| Can I install and distribute Nomi as a stable language? | [Distribution status](status.md#distribution-status) |
| Can I try the learning and reasoning experiments? | [Explore Learning And Reasoning](reasoning_lab.md) |
| How do I work on Nomi itself? | [Developing Nomi](../orientation/development.md) |

## About These Guides

These guides explain current behavior and link to the owners of future design
decisions. They do not turn a proposed feature into a supported one. Examples
under `samples/` are runnable prototype fixtures; experimental samples may deliberately
exercise syntax that will change. The catalog identifies that distinction.

For detailed reference, use the [documentation index](../README.md). The
[target design](../design/README.md) defines the intended language, and
[research](../research/README.md) records evidence and unresolved alternatives.
