import asyncio
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_nomi_web():
    spec = importlib.util.spec_from_file_location(
        "nomi_web_test_bridge",
        ROOT / "web" / "nomi_web.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_web_runtime_bridge_uses_persistent_session_with_cache():
    async def run():
        nomi_web = load_nomi_web()
        await nomi_web.init_nomi()
        first = await nomi_web.run_nomi("web_value = 4\nprint(web_value)\n")
        second = await nomi_web.run_nomi("web_value = 4\nprint(web_value)\n")
        return first, second

    first, second = asyncio.run(run())

    assert first["output"] == "4\n"
    assert second["output"] == "4\n"
    assert first["timing"]["cache_hit"] is False
    assert second["timing"]["cache_hit"] is True
    assert "parse_ms" in first["timing"]
    assert "cache_ms" in second["timing"]
