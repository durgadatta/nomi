from prototype.runtime import RuntimeCacheKey, create_session


def test_session_cache_uses_typed_runtime_cache_key():
    session = create_session(mode="nomi", cache_size=2)

    first = session.run(source="cached_value = 4\n")
    second = session.run(source="cached_value = 4\n")

    assert first.ok
    assert second.ok
    assert "cache" in second.timings

    [cache_key] = session._ast_cache.keys()
    assert isinstance(cache_key, RuntimeCacheKey)
    assert cache_key.source_text == "cached_value = 4\n"
    assert cache_key.source_identity is None
    assert cache_key.mode == "nomi"
    assert cache_key.profile == "default"
    assert cache_key.eval_backend == session.pipeline.eval_backend
    assert cache_key.parser == session.pipeline.parser
    assert cache_key.lowering == session.pipeline.lowering


def test_session_cache_distinguishes_source_identity(tmp_path):
    first_file = tmp_path / "first.nomi"
    second_file = tmp_path / "second.nomi"
    first_file.write_text("cached_value = 4\n", encoding="utf-8")
    second_file.write_text("cached_value = 4\n", encoding="utf-8")
    session = create_session(mode="nomi", cache_size=4)

    first = session.run(filename=first_file)
    second = session.run(filename=second_file)

    assert first.ok
    assert second.ok
    assert "cache" not in second.timings
    assert len(session._ast_cache) == 2
    identities = {key.source_identity for key in session._ast_cache}
    assert identities == {str(first_file.resolve()), str(second_file.resolve())}
