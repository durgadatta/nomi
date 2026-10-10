"""An installed package points users to guidance and identifies its version."""

from email import message_from_string
import subprocess
import sys

from prototype.tests.e2e import test_distribution_boundary as wheel_helpers

distribution = wheel_helpers.distribution


def test_wheel_metadata_links_to_user_guidance_and_problem_intake(distribution):
    installed, _ = distribution
    metadata = next(installed.glob("nomi-*.dist-info/METADATA"))
    record = message_from_string(metadata.read_text())
    assert set(record.get_all("Project-URL")) == {
        "Repository, https://github.com/durgadatta/nomi",
        "Documentation, https://github.com/durgadatta/nomi/blob/main/docs/guide/README.md",
        "Issues, https://github.com/durgadatta/nomi/issues",
    }


def test_installed_cli_version_and_help_work_outside_checkout(distribution, tmp_path):
    installed, _ = distribution
    for argument in ("--version", "--help"):
        code = (
            f"import sys; sys.path.insert(0, {str(installed)!r}); "
            f"sys.argv=['nomi', {argument!r}]; from scripts.cli import main; main()"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-c", code], cwd=tmp_path,
            capture_output=True, text=True, timeout=20,
        )
        assert result.returncode == 0, result.stderr
        assert result.stderr == ""
        assert "experimental preview" in result.stdout
        if argument == "--version":
            assert "nomi 0.1.0" in result.stdout
        else:
            assert "docs/guide/README.md" in result.stdout
            assert "--output program" in " ".join(result.stdout.split())
