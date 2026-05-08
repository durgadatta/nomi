"""Jupyter kernel for executing Nomi cells.

The kernel intentionally reuses the current Nomi parser and interpreter rather
than creating a separate execution model. Each notebook keeps one interpreter
instance alive so bindings, functions, classes, and imports persist across
cells in the expected notebook style.
"""

from __future__ import annotations

import ast
import io
import os
import shlex
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

from ipykernel.kernelapp import IPKernelApp
from ipykernel.kernelbase import Kernel


def _ensure_project_root_on_path() -> None:
    root = os.environ.get("NOMI_PROJECT_ROOT")
    if root and root not in sys.path:
        sys.path.insert(0, root)


_ensure_project_root_on_path()

from prototype.interpreter.nomi.interpreter import Interpreter
from prototype.parser.nomi.usage import generate_ast


class KernelStream(io.TextIOBase):
    """File-like stream that forwards writes to the notebook frontend."""

    def __init__(self, kernel: "NomiKernel", name: str):
        self.kernel = kernel
        self.name = name

    def writable(self) -> bool:
        return True

    def write(self, text: str) -> int:
        if text:
            self.kernel.send_response(
                self.kernel.iopub_socket,
                "stream",
                {"name": self.name, "text": text},
            )
        return len(text)

    def flush(self) -> None:
        return None


class NomiKernel(Kernel):
    implementation = "nomi"
    implementation_version = "0.1.0"
    language = "nomi"
    language_version = "0.1.0"
    language_info = {
        "name": "nomi",
        "mimetype": "text/x-nomi",
        "file_extension": ".nomi",
        "codemirror_mode": {"name": "python", "version": 3},
        "pygments_lexer": "python3",
    }
    banner = "Nomi kernel - Python-readable Nomi syntax via the prototype interpreter"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.interpreter = Interpreter()
        self.project_root = Path(os.environ.get("NOMI_PROJECT_ROOT", Path.cwd())).resolve()

    def do_execute(
        self,
        code: str,
        silent: bool,
        store_history: bool = True,
        user_expressions: dict | None = None,
        allow_stdin: bool = False,
    ) -> dict:
        if not code.strip():
            return self._ok(user_expressions)

        try:
            result = self._execute_with_output(code, silent=silent)
            return self._ok(user_expressions, result)
        except Exception as error:
            return self._error(error)

    def do_complete(self, code: str, cursor_pos: int) -> dict:
        prefix = self._completion_prefix(code[:cursor_pos])
        matches = sorted(
            name
            for name in self.interpreter.global_env.bindings
            if name.startswith(prefix) and not name.startswith("__")
        )
        return {
            "status": "ok",
            "matches": matches,
            "cursor_start": cursor_pos - len(prefix),
            "cursor_end": cursor_pos,
            "metadata": {},
        }

    def do_is_complete(self, code: str) -> dict:
        stripped = code.strip()
        if not stripped:
            return {"status": "complete"}
        if stripped.startswith("%"):
            return {"status": "complete"}
        try:
            generate_ast(code=self._normalize_source(code))
        except Exception:
            if code.rstrip().endswith(":"):
                return {"status": "incomplete", "indent": "    "}
            return {"status": "invalid"}
        return {"status": "complete"}

    def do_shutdown(self, restart: bool) -> dict:
        self.interpreter = Interpreter()
        return {"status": "ok", "restart": restart}

    def _execute_with_output(self, code: str, *, silent: bool) -> Any:
        stdout = KernelStream(self, "stdout")
        stderr = KernelStream(self, "stderr")
        with redirect_stdout(stdout), redirect_stderr(stderr):
            return self._execute_code_or_command(code, silent=silent)

    def _execute_code_or_command(self, code: str, *, silent: bool) -> Any:
        stripped = code.strip()
        if stripped.startswith("%"):
            return self._execute_command(stripped, silent=silent)
        return self._execute_nomi(code, silent=silent)

    def _execute_command(self, command: str, *, silent: bool) -> Any:
        first_line, _, rest = command.partition("\n")
        parts = shlex.split(first_line)
        name = parts[0]

        if name == "%help":
            self._write_stdout(self._help_text())
            return None

        if name == "%reset":
            self.interpreter = Interpreter()
            if not silent:
                self._write_stdout("Nomi interpreter reset.\n")
            return None

        if name == "%who":
            names = sorted(
                key
                for key in self.interpreter.global_env.bindings
                if key not in ("__builtins__", "builtins") and not key.startswith("__")
            )
            self._write_stdout("\n".join(names) + ("\n" if names else ""))
            return None

        if name == "%run":
            if len(parts) != 2:
                raise ValueError("Usage: %run path/to/file.nomi")
            file_path = self._resolve_path(parts[1])
            source = file_path.read_text(encoding="utf-8")
            return self._execute_nomi(source, silent=silent)

        if name == "%ast":
            source = rest if rest.strip() else command[len(first_line):].strip()
            if not source:
                raise ValueError("Usage: %ast followed by Nomi source")
            tree = generate_ast(code=self._normalize_source(source), dump=True)
            self._write_stdout(f"{tree}\n")
            return None

        raise ValueError(f"Unknown Nomi kernel command: {name}. Try %help.")

    def _execute_nomi(self, code: str, *, silent: bool) -> Any:
        tree = generate_ast(code=self._normalize_source(code))
        tree = ast.fix_missing_locations(tree)
        body = list(tree.body)

        if not body:
            return None

        last = body[-1]
        should_display = (
            isinstance(last, ast.Expr)
            and not self._is_block_call_expr(last)
            and not silent
        )

        if should_display and len(body) > 1:
            leading = ast.Module(body=body[:-1], type_ignores=[])
            leading = ast.fix_missing_locations(leading)
            self.interpreter.eval(leading)
            result = self.interpreter.eval(last)
        else:
            result = self.interpreter.eval(tree)

        if should_display and result is not None:
            self._send_execute_result(result)

        return result

    def _is_block_call_expr(self, node: ast.Expr) -> bool:
        value = node.value
        return (
            isinstance(value, ast.Call)
            and any(keyword.arg == "__block__" for keyword in value.keywords)
        )

    def _send_execute_result(self, value: Any) -> None:
        self.send_response(
            self.iopub_socket,
            "execute_result",
            {
                "execution_count": self.execution_count,
                "data": {"text/plain": repr(value)},
                "metadata": {},
            },
        )

    def _write_stdout(self, text: str) -> None:
        KernelStream(self, "stdout").write(text)

    def _resolve_path(self, raw_path: str) -> Path:
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            path = self.project_root / path
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError(f"Nomi file not found: {path}")
        if path.suffix != ".nomi":
            raise ValueError(f"%run expects a .nomi file, got: {path}")
        return path

    def _completion_prefix(self, code: str) -> str:
        i = len(code)
        while i > 0 and (code[i - 1].isalnum() or code[i - 1] == "_"):
            i -= 1
        return code[i:]

    def _normalize_source(self, code: str) -> str:
        return code if code.endswith("\n") else code + "\n"

    def _ok(self, user_expressions: dict | None = None, result: Any = None) -> dict:
        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": user_expressions or {},
        }

    def _error(self, error: Exception) -> dict:
        lines = traceback.format_exception(type(error), error, error.__traceback__)
        return {
            "status": "error",
            "ename": type(error).__name__,
            "evalue": str(error),
            "traceback": [line.rstrip("\n") for line in lines],
        }

    def _help_text(self) -> str:
        return (
            "Nomi kernel commands:\n"
            "  %run path/to/file.nomi   Run a Nomi source file in this notebook state.\n"
            "  %who                     List user-level global bindings.\n"
            "  %reset                   Reset the Nomi interpreter state.\n"
            "  %ast\\n<source>           Show the lowered Python AST for Nomi source.\n"
            "  %help                    Show this help text.\n"
        )


def main() -> None:
    IPKernelApp.launch_instance(kernel_class=NomiKernel)


if __name__ == "__main__":
    main()
