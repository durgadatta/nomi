"""The legacy browser must not announce readiness after partial asset loading."""

import asyncio
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
pytestmark = pytest.mark.contract


@pytest.fixture
def bridge():
    spec = importlib.util.spec_from_file_location(
        "bootstrap_contract", ROOT / "web/nomi_web.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_required_asset_prevents_readiness(bridge, monkeypatch):
    async def fetch(base, path):
        return path, "prototype/runtime/host_capabilities.json (404)"

    monkeypatch.setattr(bridge, "_fetch_manifest_file", fetch)
    with pytest.raises(RuntimeError, match="Required runtime assets unavailable"):
        asyncio.run(
            bridge._load_from_manifest(
                "https://example.invalid/",
                {"files": ["prototype/runtime/host_capabilities.json"]},
            )
        )


@pytest.mark.parametrize(
    "manifest",
    [
        None,
        [],
        {},
        {"files": "prototype/module.py"},
        {"files": []},
        {"files": [None]},
        {"files": ["../module.py"]},
        {"files": ["prototype/../module.py"]},
        {"files": ["/prototype/module.py"]},
        {"files": ["prototype/module.py?redirect=1"]},
        {"files": ["prototype/%2e%2e/module.py"]},
        {"files": ["prototype\\module.py"]},
        {"files": ["prototype/module.py", "prototype/module.py"]},
    ],
)
def test_invalid_manifest_is_rejected_before_fetching(bridge, monkeypatch, manifest):
    async def never_fetch(*args):
        pytest.fail("malformed manifest reached asset loading")

    monkeypatch.setattr(bridge, "_fetch_manifest_file", never_fetch)
    with pytest.raises(ValueError, match="runtime manifest"):
        asyncio.run(bridge._load_from_manifest("https://example.invalid/", manifest))


def test_complete_manifest_loads_all_batches(bridge, monkeypatch):
    paths = [f"prototype/module_{index}.py" for index in range(25)]
    loaded = []

    async def fetch(base, path):
        loaded.append(path)
        return path, None

    monkeypatch.setattr(bridge, "_fetch_manifest_file", fetch)
    asyncio.run(
        bridge._load_from_manifest("https://example.invalid/", {"files": paths})
    )
    assert loaded == paths


def test_manifest_http_failure_is_not_treated_as_source(bridge, monkeypatch):
    class Response:
        status = 503

        async def string(self):
            pytest.fail("error body must not be interpreted as a manifest")

    async def fetch(url):
        return Response()

    monkeypatch.setattr(bridge, "PYODIDE", True)
    monkeypatch.setattr(bridge, "_base_url", lambda: "https://example.invalid/")
    monkeypatch.setattr(bridge, "pyfetch", fetch, raising=False)
    with pytest.raises(RuntimeError, match="manifest returned HTTP 503"):
        asyncio.run(bridge._ensure_prototype_loaded())
