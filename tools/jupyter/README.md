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
python3 -m tools.jupyter.check_nomi_kernel
python3 -m notebook notebooks/nomi_syntax_tour.ipynb
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

## Troubleshooting

If the server log shows lines like this:

```text
404 GET /api/contents/Projects/practice/Untitled.ipynb
```

that usually means the browser or Jupyter frontend is polling a stale recent
notebook path. It does not by itself mean the Nomi kernel failed. Open the tour
directly from the repository root:

```bash
python3 -m notebook notebooks/nomi_syntax_tour.ipynb
```

If the notebook opens but cells do not execute, run the kernel smoke check:

```bash
python3 -m tools.jupyter.check_nomi_kernel
```

Expected output includes:

```text
Found kernel 'nomi' ...
Smoke-test output:
7
30
```

If the check fails, reinstall the kernelspec from the environment that has the
project installed:

```bash
python3 -m pip install -e ".[jupyter]"
python3 -m tools.jupyter.install_nomi_kernel --user
```

An SSL warning such as `CERTIFICATE_VERIFY_FAILED` is normally produced by a
Jupyter extension or remote service check. It is separate from local Nomi kernel
execution unless it appears immediately beside a kernel startup traceback.

## Syntax Tour

Open [nomi_syntax_tour.ipynb](../../notebooks/nomi_syntax_tour.ipynb) after the
kernel is installed. It covers the Nomi syntax currently implemented in this
repository: `func`, arrow functions, constrained binding, constrained
parameters, Python-compatible expressions/control, matching, classes/imports,
and yield-to-block calls.
