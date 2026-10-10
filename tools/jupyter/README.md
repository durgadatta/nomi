# Nomi Jupyter Kernel

This folder contains a local Jupyter kernel for running Nomi syntax in notebooks.
The kernel reuses the existing Nomi parser and interpreter, so notebook cells
execute through the same prototype semantics as the CLI.

For the first learning route, use the [user guide](../../docs/guide/README.md)
and [Language Basics](../../docs/guide/language_basics.md). The separate syntax
tour covers older experimental forms as well; it is not the complete target
language or a promise that every form will remain.

Execution/session creation, `%ast`, completeness checks, and binding lookup
use the public runtime facade. The kernel does not choose a parser directly.
Silent execution still updates notebook state but suppresses streams, command
output, and displayed results, following the
[Jupyter messaging contract](https://jupyter-client.readthedocs.io/en/latest/messaging.html#execute).
Normal visible output and cross-cell bindings are unchanged.

Failed cells publish an error to the notebook and return the same diagnostic
in the execution reply. Parse errors keep known source positions and excerpts;
runtime messages retain their diagnostic code without Python implementation
frames. `nomi_diagnostics` carries the public runtime's structured records for
tool consumers. Silent failures return an error reply without publishing.
Kernel-command failures still use a concise exception message. This is a
prototype adapter, not a full source-level stack trace or target debugger.

Printed output and assignments completed before a failure remain. Repair and
rerun the cell, or use `%reset` and Run All to rebuild state. For implementation
debugging, the public runtime API still supports raising the original exception.

## Setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 tools/jupyter/launch_nomi_notebook.py
```

The launcher installs the editable package with Jupyter dependencies,
installs/refreshes the local kernelspec, smoke-tests the Nomi kernel, and opens
the first calculation notebook directly through Jupyter's interactive notebook route.
Then choose the `Nomi` kernel if Jupyter does not pick it automatically.

For a faster launch after the first run:

```bash
python3 tools/jupyter/launch_nomi_notebook.py --skip-install
```

For the smallest possible execution check:

```bash
python3 tools/jupyter/launch_nomi_notebook.py --skip-install --minimal
```

## Docker Setup

For a portable Linux-based notebook environment, run one host command:

```bash
python3 scripts/run_nomi_docker.py
```

The launcher is the whole front door. On first run it checks for Docker. On
macOS, if Docker is not ready, it can install the Docker CLI and Colima through
Homebrew, start Colima, build the `nomi:jupyter` image, start a container named
`nomi-jupyter`, wait for Jupyter Lab, and open
`notebooks/nomi_syntax_tour.ipynb` with a generated token. An explicit `--token`
or `NOMI_JUPYTER_TOKEN` overrides generation; blank tokens are rejected. Later
runs reuse a running container only after inspecting its image tag, exact
localhost port binding and credential. Mismatches require `--restart-container`;
old fixed-`nomi` containers also require a restart unless that token is explicitly
selected. Rebuild the image to pick up entrypoint changes.

The launcher does not print authenticated URLs or credentials, including its
timeout log excerpt. With `--no-browser`, obtain the token locally with
`docker exec nomi-jupyter jupyter server list` and enter it at login. Jupyter's
own logs and Docker inspection still expose credentials to Docker-authorized
users, as described in the [Jupyter security guide](https://jupyter-server.readthedocs.io/en/latest/operators/security.html).
This remains a development image, not a hardened or publicly exposed service.

Useful variants:

```bash
python3 scripts/run_nomi_docker.py --minimal
python3 scripts/run_nomi_docker.py --port 8890
python3 scripts/run_nomi_docker.py --no-browser
python3 scripts/run_nomi_docker.py --rebuild
python3 scripts/run_nomi_docker.py --restart-container
python3 scripts/run_nomi_docker.py --no-runtime-setup
```

Stop the running container with:

```bash
docker stop nomi-jupyter
```

The calculation notebook reuses `samples/calculate.nomi`, then demonstrates
cross-cell state and repair. The minimal smoke test and experimental syntax
tour remain available. Check the calculation through the installed kernel:

```bash
python3 -m tools.jupyter.check_nomi_kernel --notebook notebooks/nomi_calculation.ipynb
```

It should print `3850` and `5050` from the two code cells. This command executes
the supplied notebook; use it only with notebooks you intend to run. It checks
execution without saving outputs back into the file.

The notebooks are generated with clean metadata from:

```bash
python3 -m tools.jupyter.create_demo_notebooks
```

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

Open [nomi_minimal.ipynb](../../notebooks/nomi_minimal.ipynb) for a tiny smoke
test, or [nomi_syntax_tour.ipynb](../../notebooks/nomi_syntax_tour.ipynb) for a
tour of the syntax currently implemented in this repository: `func`, arrow
functions, constrained binding, constrained parameters, Python-compatible
expressions/control, matching, classes/imports, and yield-to-block calls.
