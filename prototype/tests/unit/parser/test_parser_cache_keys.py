from prototype.parser.nomi import usage
from prototype.parser.nomi.usage import ParserCacheKey, RawTreeCacheKey


def test_parser_cache_uses_typed_key():
    usage.get_parser(preserve_positions=False)

    assert usage._PARSER_CACHE
    key = next(iter(usage._PARSER_CACHE))
    assert isinstance(key, ParserCacheKey)
    assert key.preserve_positions is False
    assert key.feature_profile == "default"
    assert key.frontend == "lark-lalr"
    assert "statements.lark" not in key.grammar_layers


def test_raw_tree_cache_uses_source_identity(tmp_path):
    first = tmp_path / "first.nomi"
    second = tmp_path / "second.nomi"
    first.write_text("x = 1\n", encoding="utf-8")
    second.write_text("x = 1\n", encoding="utf-8")
    before = set(usage._RAW_TREE_CACHE)

    first_tree = usage.parse_raw_tree(filename=first, preserve_positions=False)
    second_tree = usage.parse_raw_tree(filename=second, preserve_positions=False)

    assert first_tree is not second_tree
    new_keys = set(usage._RAW_TREE_CACHE) - before
    identities = {key.source_identity for key in new_keys}
    assert str(first.resolve()) in identities
    assert str(second.resolve()) in identities
    assert all(isinstance(key, RawTreeCacheKey) for key in new_keys)
    assert {key.source_digest for key in new_keys} == {
        "1de70bc15d424d4453e6c531451e490b"
    }


def test_raw_tree_cache_digest_distinguishes_source_text(tmp_path):
    first = tmp_path / "first.nomi"
    second = tmp_path / "second.nomi"
    first.write_text("x = 1\n", encoding="utf-8")
    second.write_text("x = 2\n", encoding="utf-8")
    before = set(usage._RAW_TREE_CACHE)

    usage.parse_raw_tree(filename=first, preserve_positions=False)
    usage.parse_raw_tree(filename=second, preserve_positions=False)

    new_keys = set(usage._RAW_TREE_CACHE) - before
    digests = {key.source_digest for key in new_keys}
    assert len(digests) == 2
    assert all(len(digest) == 32 for digest in digests)
