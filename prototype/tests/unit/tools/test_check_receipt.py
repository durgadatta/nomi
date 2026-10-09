"""Check evidence must retain actual outcomes, including failures and interruption."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest


SCRIPT = Path(__file__).resolve().parents[4] / "tools/check_receipt.py"


@pytest.fixture
def repository(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("reports/\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Check Test", "-c", "user.email=check@example.invalid",
         "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"],
        cwd=tmp_path, check=True,
    )
    return tmp_path


def receipts(root):
    return {
        path: json.loads(path.read_text(encoding="utf-8"))
        for path in (root / "reports/checks").glob("*/receipt.json")
    }


def run(root, code, *args, options=()):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *options, "--", sys.executable, "-c", code, *args],
        cwd=root, capture_output=True, timeout=10,
    )


def test_success_retains_argv_output_and_git_states(repository):
    literal = "; touch never-executed; $(false)"
    result = run(repository,
                 "import pathlib, sys; print(sys.argv[1]); "
                 "print('error stream', file=sys.stderr); "
                 "pathlib.Path('new file.txt').write_text('evidence')", literal)
    assert result.returncode == 0
    assert literal.encode() in result.stdout
    assert b"error stream" in result.stdout
    path, receipt = next(iter(receipts(repository).items()))
    assert receipt["schema_version"] == 1
    assert receipt["command"][-1] == literal
    assert receipt["status"] == "passed"
    assert receipt["returncode"] == receipt["runner_exit_code"] == 0
    assert receipt["git_before"]["dirty"] is False
    assert receipt["git_before"]["head"] == receipt["git_after"]["head"]
    assert receipt["git_after"]["dirty"] is True
    assert "?? new file.txt" in receipt["git_after"]["status_porcelain_v1_z"]
    assert receipt["started_at"] <= receipt["completed_at"]
    assert receipt["duration_seconds"] >= 0
    assert (path.parent / "output.log").read_bytes() == result.stdout
    assert not (repository / "never-executed").exists()


def test_failed_run_survives_a_later_success(repository):
    failed = run(repository, "print('failing oracle'); raise SystemExit(7)")
    original = receipts(repository)
    assert failed.returncode == 7
    assert next(iter(original.values()))["status"] == "failed"
    assert next(iter(original.values()))["returncode"] == 7
    assert run(repository, "print('fixed')").returncode == 0
    updated = receipts(repository)
    assert len(updated) == 2
    assert all(updated[path] == receipt for path, receipt in original.items())


def test_same_dirty_path_with_different_contents_is_detected(repository):
    tracked = repository / ".gitignore"
    tracked.write_text("reports/\n# before\n", encoding="utf-8")
    result = run(repository,
                 "from pathlib import Path; Path('.gitignore').write_text('reports/\\n# after\\n')")
    receipt = next(iter(receipts(repository).values()))
    assert result.returncode == 0
    assert receipt["git_before"]["status_porcelain_v1_z"] == receipt["git_after"]["status_porcelain_v1_z"]
    assert receipt["git_before"]["worktree_sha256"] != receipt["git_after"]["worktree_sha256"]
    assert receipt["worktree_changed"] is True


def test_untracked_content_changes_are_detected_without_following_symlinks(repository):
    (repository / "untracked.txt").write_text("before", encoding="utf-8")
    (repository / "link").symlink_to(repository.parent / "missing-external-file")
    result = run(repository,
                 "from pathlib import Path; Path('untracked.txt').write_text('after')")
    receipt = next(iter(receipts(repository).values()))
    assert result.returncode == 0
    assert receipt["git_before"]["worktree_sha256"]
    assert receipt["worktree_changed"] is True


def test_output_larger_than_a_poll_chunk_is_fully_retained(repository):
    size = 1024 * 1024 + 713
    result = run(repository, f"import sys; sys.stdout.buffer.write(b'x' * {size})")
    path, receipt = next(iter(receipts(repository).items()))
    assert result.returncode == 0
    assert receipt["status"] == "passed"
    assert result.stdout == b"x" * size
    assert (path.parent / "output.log").read_bytes() == result.stdout


@pytest.mark.parametrize("arguments", [[], ["--"], ["python3"],
                         ["--timeout", "nan", "--", "echo"],
                         ["--timeout", "inf", "--", "echo"],
                         ["--timeout", "0", "--", "echo"]])
def test_invalid_invocation_does_not_create_success_evidence(repository, arguments):
    result = subprocess.run([sys.executable, str(SCRIPT), *arguments], cwd=repository,
                            capture_output=True, timeout=10)
    assert result.returncode == 2
    assert not receipts(repository)


def test_missing_executable_is_recorded(repository):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--", str(repository / "does-not-exist")],
        cwd=repository, capture_output=True, timeout=10,
    )
    receipt = next(iter(receipts(repository).values()))
    assert result.returncode == 127
    assert receipt["status"] == "launch_error"
    assert receipt["returncode"] is None
    assert receipt["completed_at"] is not None


def test_timeout_is_not_success_even_if_child_exits_zero_on_termination(repository):
    result = run(repository,
                 "import signal, sys, time; "
                 "signal.signal(signal.SIGTERM, lambda *args: sys.exit(0)); "
                 "print('ready', flush=True); time.sleep(60)",
                 options=("--timeout", "0.3"))
    receipt = next(iter(receipts(repository).values()))
    assert result.returncode == 124
    assert receipt["status"] == "timed_out"
    assert receipt["runner_exit_code"] == 124
    assert b"ready" in result.stdout


@pytest.mark.skipif(os.name != "posix", reason="POSIX signal delivery")
@pytest.mark.parametrize("interrupt", [signal.SIGINT, signal.SIGTERM])
def test_interrupt_retains_receipt_and_stops_child(repository, interrupt):
    process = subprocess.Popen(
        [sys.executable, str(SCRIPT), "--", sys.executable, "-c",
         "import os, time; print(os.getpid(), flush=True); time.sleep(60)"],
        cwd=repository, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            logs = list((repository / "reports/checks").glob("*/output.log"))
            if logs and logs[0].read_text().strip():
                break
            time.sleep(0.01)
        else:
            pytest.fail("child did not start")
        child_pid = int(logs[0].read_text().strip())
        process.send_signal(interrupt)
        process.communicate(timeout=5)
        receipt = next(iter(receipts(repository).values()))
        assert process.returncode == 128 + interrupt
        assert receipt["status"] == "interrupted"
        assert receipt["signal"] == interrupt
        assert receipt["returncode"] != 0
        assert receipt["completed_at"] is not None
        with pytest.raises(ProcessLookupError):
            os.kill(child_pid, 0)
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
