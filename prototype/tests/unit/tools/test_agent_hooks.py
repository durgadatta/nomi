import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def run_hook(script: str, event: dict) -> dict:
    completed = subprocess.run(
        [sys.executable, str(ROOT / script)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    assert completed.stdout
    return json.loads(completed.stdout)


def hook_context(payload: dict) -> str:
    return payload["hookSpecificOutput"]["additionalContext"]


def test_session_start_hook_mentions_meta_skill():
    payload = run_hook(
        ".codex/hooks/session_start.py",
        {
            "hook_event_name": "SessionStart",
            "source": "startup",
            "cwd": str(ROOT),
        },
    )

    assert "AGENTS.md" in hook_context(payload)
    assert "nomi-ai-native" in hook_context(payload)


def test_user_prompt_hook_routes_ai_native_work():
    payload = run_hook(
        ".codex/hooks/user_prompt_submit.py",
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "make the repo more AI-native with better hooks and subagents",
            "cwd": str(ROOT),
        },
    )

    assert "nomi-ai-native" in hook_context(payload)
    assert "subagents" in hook_context(payload)


def test_pre_tool_hook_blocks_destructive_git_reset():
    payload = run_hook(
        ".codex/hooks/pre_tool_use_policy.py",
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git reset --hard"},
            "cwd": str(ROOT),
        },
    )

    output = payload["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "git reset --hard" in output["permissionDecisionReason"]


def test_agent_doctor_has_no_failing_checks():
    completed = subprocess.run(
        [sys.executable, str(ROOT / ".codex/scripts/agent_doctor.py"), "--json"],
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )

    results = json.loads(completed.stdout)
    assert results
    assert {result["status"] for result in results} <= {"pass", "warn"}
