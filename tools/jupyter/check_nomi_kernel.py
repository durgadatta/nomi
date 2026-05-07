"""Smoke-test the installed Nomi Jupyter kernel."""

from __future__ import annotations

import argparse
from pathlib import Path

from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager


def run_smoke(kernel_name: str, timeout: int) -> list[str]:
    manager = KernelManager(kernel_name=kernel_name)
    manager.start_kernel()
    client = manager.client()
    client.start_channels()

    try:
        client.wait_for_ready(timeout=timeout)
        client.execute("add = (x, y) => x + y\nprint(add(2, 5))\nadd(10, 20)")

        outputs = []
        while True:
            message = client.get_iopub_msg(timeout=timeout)
            message_type = message["header"]["msg_type"]
            content = message["content"]

            if message_type == "stream":
                outputs.append(content["text"])
            elif message_type == "execute_result":
                outputs.append(content["data"]["text/plain"])
            elif message_type == "error":
                raise RuntimeError("\n".join(content["traceback"]))
            elif message_type == "status" and content["execution_state"] == "idle":
                break

        reply = client.get_shell_msg(timeout=timeout)
        if reply["content"]["status"] != "ok":
            raise RuntimeError(str(reply["content"]))
        return outputs
    finally:
        client.stop_channels()
        manager.shutdown_kernel(now=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the installed Nomi Jupyter kernel.")
    parser.add_argument("--kernel", default="nomi", help="Kernel name to test.")
    parser.add_argument("--timeout", type=int, default=10, help="Jupyter message timeout in seconds.")
    args = parser.parse_args()

    specs = KernelSpecManager().find_kernel_specs()
    if args.kernel not in specs:
        available = ", ".join(sorted(specs)) or "<none>"
        raise SystemExit(f"Kernel '{args.kernel}' is not installed. Available kernels: {available}")

    print(f"Found kernel '{args.kernel}' at {Path(specs[args.kernel]).resolve()}")
    outputs = run_smoke(args.kernel, args.timeout)
    print("Smoke-test output:")
    print("".join(outputs))


if __name__ == "__main__":
    main()

