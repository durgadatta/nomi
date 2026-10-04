"""Redact launcher-owned diagnostics without altering subprocess arguments."""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def redacted_command(arguments: list[str]) -> list[str]:
    result = []
    secret_next = False
    secret_flags = {
        "--token",
        "--password",
        "--ServerApp.token",
        "--ServerApp.password",
    }
    secret_assignments = {"NOMI_JUPYTER_TOKEN", *secret_flags}
    for argument in arguments:
        if secret_next:
            result.append("<redacted>")
            secret_next = False
            continue
        key, separator, _ = argument.partition("=")
        if separator and key in secret_assignments:
            result.append(f"{key}=<redacted>")
        else:
            result.append(argument)
            secret_next = argument in secret_flags
    return result


def unauthenticated_url(url: str) -> str:
    parts = urlsplit(url)
    query = urlencode(
        [
            (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
            if key not in {"token", "password"}
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))
