# Nomi Jupyter Kernel

This folder contains a local Jupyter kernel for running Nomi syntax in notebooks.
The kernel reuses the existing Nomi parser and interpreter, so notebook cells
execute through the same prototype semantics as the CLI.

## Setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[jupyter]"
python3 -m tools.jupyter.install_nomi_kernel --user
python3 -m notebook
```

Then open a notebook and choose the `Nomi` kernel.

The installer writes a kernelspec that points back to this checkout through
`NOMI_PROJECT_ROOT` and `PYTHONPATH`. Re-run the installer if the repository is
moved.

## Kernel Commands

Inside a Nomi notebook:

```python
%run scripts/demo.nomi
%who
%reset
```

Use `%ast` followed by Nomi source to inspect the lowered Python AST:

```python
%ast
add = (x, y) => x + y
```

## Syntax Tour

Open [nomi_syntax_tour.ipynb](../../notebooks/nomi_syntax_tour.ipynb) after the
kernel is installed. It covers the Nomi syntax currently implemented in this
repository: `func`, arrow functions, constrained binding, constrained
parameters, Python-compatible expressions/control, matching, classes/imports,
and yield-to-block calls.
