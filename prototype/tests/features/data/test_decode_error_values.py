from prototype.runtime import (
    DecodeError,
    DecodeErrorList,
    RuntimeEventCollector,
    record_decode_event,
)


def test_decode_error_records_field_path_source_and_redaction():
    error = DecodeError(
        source_identity="POST /signup",
        field_path=("users", 2, "age"),
        expected="int",
        raw_value_summary="'unknown'",
        rule="age >= 13",
        message="Signup requires age 13+",
        redaction={"paths": ["users[2].token"]},
        next_step="Provide an integer age of at least 13.",
    )

    assert error.path_text() == "users[2].age"
    assert error.to_record() == {
        "kind": "decode-error",
        "source_identity": "POST /signup",
        "field_path": ["users", 2, "age"],
        "field_path_text": "users[2].age",
        "expected": "int",
        "raw_value_summary": "'unknown'",
        "rule": "age >= 13",
        "message": "Signup requires age 13+",
        "redaction": {"paths": ["users[2].token"]},
        "next_step": "Provide an integer age of at least 13.",
        "span": None,
    }


def test_decode_error_list_accumulates_without_becoming_success():
    first = DecodeError(source_identity="config.toml", field_path=("host",))
    second = DecodeError(source_identity="config.toml", field_path=("port",))

    errors = DecodeErrorList().add(first).add(second)

    assert not errors
    assert errors.to_record() == {
        "kind": "decode-error-list",
        "source_identity": "config.toml",
        "error_count": 2,
        "errors": [first.to_record(), second.to_record()],
    }


def test_decode_error_payload_feeds_decode_event_shape():
    collector = RuntimeEventCollector()
    error = DecodeError(
        source_identity="env",
        field_path=("PORT",),
        expected="int",
        raw_value_summary="'abc'",
        rule="int",
        message="Expected int, got str",
        redaction={"paths": []},
        next_step="Use a numeric port.",
    )

    event = record_decode_event(
        collector,
        "failed",
        subject=error.path_text(),
        value_summary=error.raw_value_summary,
        failure_kind="decode",
        redaction=error.redaction,
        next_step=error.next_step,
        payload=error.to_event_payload(),
    )

    assert event.name == "semantic.decode.failed"
    assert event.subject == "PORT"
    assert event.capability == "data.decode"
    assert event.failure_kind == "decode"
    assert event.to_record()["payload"] == {
        "kind": "decode",
        "action": "failed",
        "feature": "data-decode",
        "source_identity": "env",
        "field_path": ["PORT"],
        "field_path_text": "PORT",
        "expected": "int",
        "rule": "int",
        "message": "Expected int, got str",
    }
