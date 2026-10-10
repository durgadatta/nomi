"""The offline documentation gate catches drift without executing examples."""

from pathlib import Path

from scripts.check_doc_links import check_documents, local_links, main


def test_code_samples_and_remote_urls_are_not_filesystem_links():
    source = """[remote](https://example.invalid/a) [heading](#start)
`[inline](missing.md)`
~~~markdown
[example](missing.md)
~~~
```python
text = '[example](missing.md)'
```
[real](README.md#start)
"""
    assert list(local_links(source)) == [(9, "README.md")]


def test_inline_reference_image_and_encoded_paths_share_file_checks(tmp_path):
    (tmp_path / "a file.md").write_text("# A", encoding="utf-8")
    (tmp_path / "image.svg").write_text("<svg/>", encoding="utf-8")
    path = tmp_path / "README.md"
    path.write_text('[file](<a file.md>) [encoded](a%20file.md)\n![image](image.svg)\n[reference]: a%20file.md "title"\n', encoding="utf-8")
    assert check_documents([path], root=tmp_path) == (4, [])


def test_failure_identifies_source_line_and_destination(tmp_path):
    path = tmp_path / "README.md"
    path.write_text("# Start\n\n[broken](gone.md#part)\n", encoding="utf-8")
    count, errors = check_documents([path], root=tmp_path)
    assert count == 1
    assert errors == [f"{path}:3: missing local destination: gone.md"]
    assert main([str(path)]) == 1


def test_missing_document_is_a_failed_check(tmp_path):
    assert main([str(tmp_path / "missing.md")]) == 1


def test_root_relative_links_resolve_in_the_repository(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (tmp_path / "README.md").write_text("# Start", encoding="utf-8")
    path = folder / "guide.md"
    path.write_text("[root](/README.md)", encoding="utf-8")
    assert check_documents([path], root=tmp_path) == (1, [])


def test_fragment_validation_is_explicitly_outside_the_file_gate(tmp_path):
    path = tmp_path / "README.md"
    path.write_text("[heading](#does-not-exist) [local](README.md#does-not-exist)", encoding="utf-8")
    assert check_documents([path], root=tmp_path) == (1, [])


def test_explicit_documents_work_outside_the_checkout(tmp_path, monkeypatch, capsys):
    path = tmp_path / "README.md"
    path.write_text("[self](README.md)", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert main([str(Path("README.md"))]) == 0
    assert "Checked 1 local file links across 1 documents" in capsys.readouterr().out
