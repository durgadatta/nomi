"""Run explicit argv and retain local check evidence; this is not attestation."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import time


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=cwd, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", timeout=10,
    )


def _git_state(root: Path) -> dict:
    try:
        status = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
        try:
            head = _git(root, "rev-parse", "--verify", "HEAD").strip()
        except subprocess.CalledProcessError:
            head = None  # An initialized repository may have no commit yet.
        state = {
            "head": head,
            "dirty": bool(status),
            "status_porcelain_v1_z": status.split("\0")[:-1],
        }
        try:
            state["worktree_sha256"] = _worktree_digest(root)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            state.update(worktree_sha256=None, fingerprint_error=str(exc))
        return state
    except (OSError, subprocess.SubprocessError) as exc:
        return {"head": None, "dirty": None, "error": str(exc)}


def _worktree_digest(root: Path) -> str:
    """Fingerprint index plus nonignored files; never follow filesystem links."""
    digest = hashlib.sha256()

    def add(data):
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)

    index = subprocess.check_output(
        ["git", "ls-files", "--stage", "-z"], cwd=root, timeout=10,
    )
    add(index)
    names = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root, timeout=10,
    )
    for name in sorted(set(names.split(b"\0")) - {b""}):
        add(name)
        path = root / os.fsdecode(name)
        if path.parent.resolve() != path.parent:
            raise ValueError(f"cannot fingerprint through a linked parent: {os.fsdecode(name)}")
        try:
            info = path.lstat()
        except FileNotFoundError:
            add(b"missing")
            continue
        add(str(stat.S_IMODE(info.st_mode)).encode())
        if stat.S_ISLNK(info.st_mode):
            add(b"symlink")
            add(os.fsencode(os.readlink(path)))
        elif stat.S_ISREG(info.st_mode):
            add(b"file")
            content = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    content.update(chunk)
            add(content.digest())
        else:
            raise ValueError(f"cannot fingerprint non-file: {os.fsdecode(name)}")
    return digest.hexdigest()


def _write_receipt(directory: Path, receipt: dict) -> None:
    pending = directory / "receipt.tmp"
    pending.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    pending.replace(directory / "receipt.json")


def _stream_output(source, remaining: int = 1024 * 1024) -> None:
    # A bounded read per poll lets timeout and signal handling stay responsive.
    while remaining > 0:
        data = source.read(min(65536, remaining))
        if not data:
            break
        remaining -= len(data)
        try:
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        except BrokenPipeError:
            # The durable log is still useful when the console consumer closes.
            sys.stdout = open(os.devnull, "w")


def _stop(process: subprocess.Popen) -> None:
    def send(sig):
        try:
            if os.name == "posix":
                os.killpg(process.pid, sig)
            elif process.poll() is None:
                process.terminate() if sig == signal.SIGTERM else process.kill()
        except ProcessLookupError:
            pass

    send(signal.SIGTERM)
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass
    # A direct child may exit while descendants still hold the process group.
    if os.name == "posix":
        send(signal.SIGKILL)
    elif process.poll() is None:
        process.kill()
    process.wait()


def run_check(command: list[str], *, root: Path, cwd: Path, timeout: float | None) -> int:
    reports = root / "reports" / "checks"
    if reports.resolve() != reports:
        raise ValueError("reports/checks must not use symbolic links")
    if subprocess.run(
        ["git", "check-ignore", "-q", "reports/checks/receipt.json"], cwd=root,
    ).returncode != 0:
        raise ValueError("reports/checks must be ignored by Git")
    reports.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="check-", dir=reports))
    git_before = _git_state(root)
    started = time.monotonic()
    receipt = {
        "schema_version": 1,
        "command": command,
        "cwd": str(cwd),
        "started_at": _now(),
        "completed_at": None,
        "duration_seconds": None,
        "timeout_seconds": timeout,
        "status": "running",
        "returncode": None,
        "runner_exit_code": None,
        "git_before": git_before,
        "git_after": None,
        "output_log": "output.log",
    }
    _write_receipt(directory, receipt)
    print(f"Check receipt: {directory / 'receipt.json'}", file=sys.stderr, flush=True)
    process = None
    interrupted = None
    previous_handlers = {}

    def handle_signal(signum, frame):
        nonlocal interrupted
        interrupted = signum

    for sig in (signal.SIGINT, signal.SIGTERM):
        previous_handlers[sig] = signal.signal(sig, handle_signal)
    try:
        with (directory / "output.log").open("wb") as log:
            with (directory / "output.log").open("rb") as output:
                try:
                    process = subprocess.Popen(
                        command, cwd=cwd, stdin=subprocess.DEVNULL,
                        stdout=log, stderr=subprocess.STDOUT,
                        start_new_session=os.name == "posix",
                    )
                except OSError as exc:
                    receipt.update(status="launch_error", error=str(exc), runner_exit_code=127)
                if process is not None:
                    while True:
                        _stream_output(output)
                        if interrupted is not None:
                            receipt.update(status="interrupted", signal=interrupted,
                                           runner_exit_code=128 + interrupted)
                            _stop(process)
                            break
                        if timeout is not None and time.monotonic() - started >= timeout:
                            receipt.update(status="timed_out", runner_exit_code=124)
                            _stop(process)
                            break
                        if process.poll() is not None:
                            code = process.returncode
                            receipt.update(status="passed" if code == 0 else "failed",
                                           runner_exit_code=code if code >= 0 else 128 - code)
                            break
                        time.sleep(0.05)
                    receipt["returncode"] = process.returncode
                _stream_output(output, (directory / "output.log").stat().st_size - output.tell())
    except Exception as exc:
        receipt.update(status="runner_error", error=str(exc), runner_exit_code=1)
        if process is not None:
            _stop(process)
            receipt["returncode"] = process.returncode
    finally:
        receipt.update(completed_at=_now(), duration_seconds=time.monotonic() - started,
                       git_after=_git_state(root))
        before = receipt["git_before"].get("worktree_sha256")
        after = receipt["git_after"].get("worktree_sha256")
        receipt["worktree_changed"] = before != after if before and after else None
        if interrupted is not None:
            receipt.update(status="interrupted", signal=interrupted,
                           runner_exit_code=128 + interrupted)
        _write_receipt(directory, receipt)
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
    print(f"Check {receipt['status']}: {directory / 'receipt.json'}", file=sys.stderr)
    return receipt["runner_exit_code"]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, help="positive wall-clock seconds")
    parser.usage = "%(prog)s [--timeout SECONDS] -- COMMAND [ARG ...]"
    if "--" not in argv:
        parser.parse_args(argv)  # Preserve --help and unknown-option diagnostics.
        parser.error("supply an explicit command after --")
    boundary = argv.index("--")
    options = parser.parse_args(argv[:boundary])
    command = argv[boundary + 1:]
    if not command or not command[0] or any("\0" in arg for arg in command):
        parser.error("supply a nonempty executable and arguments without NUL bytes")
    if options.timeout is not None and (
        not math.isfinite(options.timeout) or options.timeout <= 0
    ):
        parser.error("--timeout must be a positive finite number")
    cwd = Path.cwd().resolve()
    try:
        root = Path(_git(cwd, "rev-parse", "--show-toplevel").strip()).resolve()
        return run_check(command, root=root, cwd=cwd, timeout=options.timeout)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
