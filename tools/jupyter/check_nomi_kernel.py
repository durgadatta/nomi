"""Smoke-test the installed Nomi Jupyter kernel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from queue import Empty
from time import monotonic

from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager


def execution_error(content: dict) -> str:
    return f"{content.get('ename', 'Error')}: {content.get('evalue', 'Kernel execution failed')}"


def run_smoke(kernel_name: str, timeout: int) -> list[str]:
    return run_sources(kernel_name, timeout, [
        "add = (x, y) => x + y\nprint(add(2, 5))\nadd(10, 20)"
    ])[0]


def run_sources(kernel_name: str, timeout: int, sources: list[str]) -> list[list[str]]:
    manager = KernelManager(kernel_name=kernel_name)
    manager.start_kernel()
    client = manager.client()
    client.start_channels()

    try:
        client.wait_for_ready(timeout=timeout)
        all_outputs = []
        for source in sources:
            request_id = client.execute(source)
            deadline = monotonic() + timeout
            outputs = []
            while True:
                message = client.get_iopub_msg(timeout=max(0, deadline - monotonic()))
                if message.get("parent_header", {}).get("msg_id") != request_id:
                    continue
                message_type = message["header"]["msg_type"]
                content = message["content"]
                if message_type == "stream":
                    outputs.append(content["text"])
                elif message_type == "execute_result":
                    outputs.append(content["data"]["text/plain"])
                elif message_type == "error":
                    raise RuntimeError(execution_error(content))
                elif message_type == "status" and content["execution_state"] == "idle":
                    break
            while True:
                reply = client.get_shell_msg(timeout=max(0, deadline - monotonic()))
                if reply.get("parent_header", {}).get("msg_id") == request_id:
                    break
            if reply["content"]["status"] != "ok":
                raise RuntimeError(execution_error(reply["content"]))
            all_outputs.append(outputs)
        return all_outputs
    finally:
        client.stop_channels()
        manager.shutdown_kernel(now=True)


def notebook_sources(path: Path) -> list[str]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(notebook, dict) or not isinstance(notebook.get("cells"), list):
        raise ValueError("Expected a notebook object with a cells list")
    sources = []
    for cell in notebook["cells"]:
        if not isinstance(cell, dict):
            raise ValueError("Notebook cells must be objects")
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source")
        if isinstance(source, list) and all(isinstance(line, str) for line in source):
            source = "".join(source)
        if not isinstance(source, str):
            raise ValueError("Code cells need a text source or a list of text lines")
        sources.append(source)
    if not sources:
        raise ValueError("The notebook contains no code cells to check")
    return sources


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the installed Nomi Jupyter kernel.")
    parser.add_argument("--kernel", default="nomi", help="Kernel name to test.")
    parser.add_argument("--timeout", type=int, default=10, help="Jupyter message timeout in seconds.")
    parser.add_argument("--notebook", type=Path, help="Execute a trusted notebook's code cells in order instead of the smoke program.")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    try:
        sources = notebook_sources(args.notebook) if args.notebook else None
    except (OSError, ValueError) as error:
        parser.error(f"Cannot read notebook {args.notebook}: {error}")

    specs = KernelSpecManager().find_kernel_specs()
    if args.kernel not in specs:
        available = ", ".join(sorted(specs)) or "<none>"
        raise SystemExit(f"Kernel '{args.kernel}' is not installed. Available kernels: {available}")

    print(f"Found kernel '{args.kernel}' at {Path(specs[args.kernel]).resolve()}")
    try:
        outputs_by_cell = run_sources(args.kernel, args.timeout, sources) if sources is not None else [run_smoke(args.kernel, args.timeout)]
    except Empty:
        parser.exit(1, f"Kernel check timed out after {args.timeout} seconds; inspect the cell or increase --timeout.\n")
    except RuntimeError as error:
        parser.exit(1, f"Kernel check failed: {error}\n")
    if args.notebook:
        for number, outputs in enumerate(outputs_by_cell, 1):
            print(f"Cell {number} output:")
            print("".join(outputs))
    else:
        print("Smoke-test output:")
        print("".join(outputs_by_cell[0]))


if __name__ == "__main__":
    main()

