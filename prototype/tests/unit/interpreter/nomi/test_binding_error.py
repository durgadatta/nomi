import pytest
from prototype.interpreter.nomi.binding_error import BindingError


class TestBindingErrorType:
    def test_is_type_error(self):
        assert issubclass(BindingError, TypeError)

    def test_caught_by_type_error_handler(self):
        try:
            raise BindingError("x", 42, message="bad value")
        except TypeError:
            pass
        else:
            pytest.fail("BindingError should be caught by TypeError handler")


class TestBindingErrorFields:
    def test_positional_fields(self):
        err = BindingError("name", 42)
        assert err.name == "name"
        assert err.value == 42
        assert err.message is None
        assert err.binding_kind == "assignment"
        assert err.constraint_expr is None

    def test_message_kwarg(self):
        err = BindingError("x", 1, message="too small")
        assert err.message == "too small"

    def test_binding_kind_kwarg(self):
        err = BindingError("x", 1, binding_kind="parameter")
        assert err.binding_kind == "parameter"

    def test_constraint_expr_kwarg(self):
        err = BindingError("x", 1, constraint_expr="x > 0")
        assert err.constraint_expr == "x > 0"


class TestBindingErrorFormat:
    def test_format_with_message(self):
        err = BindingError("x", 42, message="bad value")
        text = str(err)
        assert "x" in text
        assert "assignment" in text
        assert "bad value" in text

    def test_format_with_constraint_expr(self):
        err = BindingError("x", 42, constraint_expr="x > 0")
        text = str(err)
        assert "x > 0" in text
        assert "42" in text

    def test_format_without_message_or_constraint(self):
        err = BindingError("x", 42)
        text = str(err)
        assert "does not satisfy constraint" in text

    def test_format_parameter_kind(self):
        err = BindingError("x", 1, binding_kind="parameter")
        assert "parameter" in str(err)

    def test_format_block_parameter_kind(self):
        err = BindingError("x", 1, binding_kind="block_parameter")
        assert "block parameter" in str(err)

    def test_format_pattern_capture_kind(self):
        err = BindingError("x", 1, binding_kind="pattern_capture")
        assert "pattern capture" in str(err)

    def test_format_destructure_target_kind(self):
        err = BindingError("x", 1, binding_kind="destructure_target")
        assert "destructure target" in str(err)

    def test_format_falls_back_to_raw_kind(self):
        err = BindingError("x", 1, binding_kind="unknown_kind")
        assert "unknown_kind" in str(err)


class TestBindingErrorChaining:
    def test_chained_from_inner_error(self):
        try:
            try:
                raise BindingError("inner", 1, message="first")
            except BindingError as inner:
                raise BindingError(
                    inner.name, inner.value,
                    message=f"outer ({inner.message})",
                    binding_kind=inner.binding_kind,
                ) from inner
        except BindingError as outer:
            assert outer.message == "outer (first)"
            assert outer.__cause__ is not None
            assert outer.__cause__.message == "first"

    def test_chained_from_type_error(self):
        try:
            raise TypeError("raw error")
        except TypeError as raw:
            err = BindingError("x", 1, message=f"wrap ({raw})")
            assert "raw error" in err.message
