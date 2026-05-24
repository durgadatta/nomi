import pytest

from prototype.parser.nomi.rust_payload import python_ast_from_rust_payload


def test_rust_payload_adapter_rejects_unknown_schema():
    with pytest.raises(ValueError, match="unsupported Rust AST payload contract"):
        python_ast_from_rust_payload(
            {
                "schema": "nomi.other-ast",
                "version": 1,
                "type": "Module",
                "body": [],
            }
        )


def test_rust_payload_adapter_rejects_unknown_version():
    with pytest.raises(ValueError, match="unsupported Rust AST payload contract"):
        python_ast_from_rust_payload(
            {
                "schema": "nomi.rust-ast",
                "version": 2,
                "type": "Module",
                "body": [],
            }
        )
