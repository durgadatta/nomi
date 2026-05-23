"""Core Runtime backend — portable reference evaluator for Core IR."""

from __future__ import annotations

from typing import Any

from prototype.runtime.backends import (
    EvalBackendCapabilities,
    EvalBackendResult,
    EvalBackendSpec,
    register_backend,
)
from prototype.runtime.backends.control_flow import (
    BreakSignal,
    ContinueSignal,
    ControlFlow,
    ReturnSignal,
)
from prototype.runtime.backends.environment import Frame
from prototype.runtime.backends.values import (
    DataValue,
    ErrorValue,
    FunctionValue,
    NIL,
    NativeValue,
    SequenceValue,
    Value,
    box_value,
    is_truthy,
    unbox_value,
)
from prototype.syntax.core import (
    BinaryOp,
    Bind,
    BooleanOp,
    Branch,
    Call,
    CompareOp,
    ConstructData,
    CoreNode,
    Diagnostic,
    Function,
    GetField,
    Handle,
    Literal,
    Load,
    Loop,
    Match,
    Module,
    PatternTest,
    Raise,
    Return,
    Sequence,
    UnaryOp,
    verify_core,
)


CORE_RUNTIME_SPEC = EvalBackendSpec(
    name="core-runtime",
    status="prototype",
    ir_contract="Core IR (L1 nodes)",
    implementation="Nomi-owned Value/Frame/ControlFlow runtime",
    output_contract="dict of global bindings + optional last-expression value",
    capabilities=EvalBackendCapabilities(
        evaluates_native_ir=True,
        supports_full_language=False,
        supports_blocks=False,
        supports_exceptions=False,
        supports_resume=False,
        supports_python_interop=False,
        selectable_for_execution=False,
    ),
    notes=(
        "reference backend shape for future native backends",
        "initial parity subset: Module, Literal, Load, Bind, Function, Call, Return, Branch",
    ),
)


class CoreRuntimeEvaluator:
    """Evaluate Core IR through portable runtime abstractions."""

    spec = CORE_RUNTIME_SPEC

    def __init__(self, host_calls: dict[str, Any] | None = None) -> None:
        self._raw_host_calls = dict(host_calls or {})
        self._global_frame = Frame()
        self._current_frame = self._global_frame
        self._host_calls = {
            name: box_value(func)
            for name, func in self._raw_host_calls.items()
        }
        for name, value in self._host_calls.items():
            self._global_frame.bind(name, value)

    def fork(self) -> CoreRuntimeEvaluator:
        """Return a fresh evaluator with the same host-call configuration."""
        return CoreRuntimeEvaluator(host_calls=self._raw_host_calls)

    def evaluate(
        self, core_ir: Module, *, display_last_expr: bool = False
    ) -> EvalBackendResult:
        verify_core(core_ir, strict=True)
        result = self._eval_module(core_ir)
        if isinstance(result, ControlFlow):
            raise RuntimeError(
                f"Unexpected {type(result).__name__} at module level"
            )
        if isinstance(result, ErrorValue):
            raise RuntimeError(result.message)
        has_value = display_last_expr and result is not NIL
        return EvalBackendResult(
            bindings=self._global_frame.export_bindings(),
            value=unbox_value(result) if has_value else None,
            has_value=has_value,
        )

    def eval(self, node: CoreNode | None) -> Value | ControlFlow:
        if node is None:
            return NIL
        method = getattr(self, f"_eval_{type(node).__name__}", None)
        if method is None:
            raise NotImplementedError(
                f"Core Runtime does not dispatch {type(node).__name__}"
            )
        return method(node)

    def _eval_module(self, node: Module | None) -> Value | ControlFlow:
        if node is None:
            return NIL
        last: Value | ControlFlow = NIL
        for stmt in node.body:
            last = self.eval(stmt)
            if isinstance(last, ControlFlow):
                return last
            if isinstance(last, ErrorValue):
                return last
        return last

    def _eval_Module(self, node: Module) -> Value | ControlFlow:
        return self._eval_module(node)

    def _eval_Literal(self, node: Literal) -> Value:
        return box_value(node.value)

    def _eval_Load(self, node: Load) -> Value:
        value = self._current_frame.lookup(node.name)
        if value is None:
            raise NameError(f"name {node.name!r} is not defined")
        return value

    def _eval_Bind(self, node: Bind) -> Value | ControlFlow:
        value = self.eval(node.value)
        if isinstance(value, ControlFlow):
            return value
        self._current_frame.assign(node.name, value)
        return value

    def _eval_Function(self, node: Function) -> Value:
        return FunctionValue(
            params=node.params,
            body=node.body,
            closure=self._current_frame,
        )

    def _eval_Call(self, node: Call) -> Value | ControlFlow:
        func = self.eval(node.func)
        if isinstance(func, ControlFlow):
            return func
        args: list[Value] = []
        for arg in node.args:
            value = self.eval(arg)
            if isinstance(value, ControlFlow):
                return value
            args.append(value)
        if isinstance(func, NativeValue):
            return box_value(func.callable(*[unbox_value(arg) for arg in args]))
        if isinstance(func, FunctionValue):
            return self._call_function(func, tuple(args))
        raise TypeError(f"{type(func).__name__} is not callable")

    def _call_function(
        self, func: FunctionValue, args: tuple[Value, ...]
    ) -> Value | ControlFlow:
        saved_frame = self._current_frame
        self._current_frame = func.closure.extend(func.params, args)
        try:
            result = self._eval_module(func.body)
            if isinstance(result, ReturnSignal):
                return result.value
            return result
        finally:
            self._current_frame = saved_frame

    def _eval_Return(self, node: Return) -> ControlFlow:
        value = self.eval(node.value)
        if isinstance(value, ControlFlow):
            return value
        return ReturnSignal(value)

    def _eval_Branch(self, node: Branch) -> Value | ControlFlow:
        test = self.eval(node.test)
        if isinstance(test, ControlFlow):
            return test
        branch = node.then_body if is_truthy(test) else node.else_body
        return self._eval_module(branch)

    def _eval_UnaryOp(self, node: UnaryOp) -> Value | ControlFlow:
        operand = self.eval(node.operand)
        if isinstance(operand, ControlFlow):
            return operand
        value = unbox_value(operand)
        if node.op == "+":
            return box_value(+value)
        if node.op == "-":
            return box_value(-value)
        if node.op == "~":
            return box_value(~value)
        if node.op == "not":
            return box_value(not is_truthy(operand))
        raise RuntimeError(f"Unsupported unary op {node.op!r}")

    def _eval_BinaryOp(self, node: BinaryOp) -> Value | ControlFlow:
        left = self.eval(node.left)
        if isinstance(left, ControlFlow):
            return left
        right = self.eval(node.right)
        if isinstance(right, ControlFlow):
            return right
        return box_value(
            self._apply_binary_op(node.op, unbox_value(left), unbox_value(right))
        )

    def _eval_BooleanOp(self, node: BooleanOp) -> Value | ControlFlow:
        if not node.values:
            return NIL
        if node.op == "and":
            last: Value = NIL
            for value_node in node.values:
                value = self.eval(value_node)
                if isinstance(value, ControlFlow):
                    return value
                last = value
                if not is_truthy(value):
                    return value
            return last
        if node.op == "or":
            last = NIL
            for value_node in node.values:
                value = self.eval(value_node)
                if isinstance(value, ControlFlow):
                    return value
                last = value
                if is_truthy(value):
                    return value
            return last
        raise RuntimeError(f"Unsupported boolean op {node.op!r}")

    def _eval_CompareOp(self, node: CompareOp) -> Value | ControlFlow:
        left = self.eval(node.left)
        if isinstance(left, ControlFlow):
            return left
        current = unbox_value(left)
        for op, comparator in zip(node.ops, node.comparators):
            right = self.eval(comparator)
            if isinstance(right, ControlFlow):
                return right
            right_value = unbox_value(right)
            if not self._apply_compare_op(op, current, right_value):
                return box_value(False)
            current = right_value
        return box_value(True)

    def _eval_Sequence(self, node: Sequence) -> Value | ControlFlow:
        elements: list[Value] = []
        for elem in node.elements:
            value = self.eval(elem)
            if isinstance(value, ControlFlow):
                return value
            elements.append(value)
        return SequenceValue(tuple(elements))

    def _eval_ConstructData(self, node: ConstructData) -> Value | ControlFlow:
        fields: dict[str, Value] = {}
        for name, field_node in node.fields:
            value = self.eval(field_node)
            if isinstance(value, ControlFlow):
                return value
            fields[name] = value
        return DataValue(name=node.name, fields=fields)

    def _eval_GetField(self, node: GetField) -> Value | ControlFlow:
        obj = self.eval(node.object_)
        if isinstance(obj, ControlFlow):
            return obj
        if not isinstance(obj, DataValue):
            raise TypeError(f"{type(obj).__name__} has no field {node.field!r}")
        try:
            return obj.fields[node.field]
        except KeyError as exc:
            raise AttributeError(node.field) from exc

    def _eval_Loop(self, node: Loop) -> Value | ControlFlow:
        last: Value | ControlFlow = NIL
        while True:
            test = self.eval(node.test)
            if isinstance(test, ControlFlow):
                return test
            if not is_truthy(test):
                return self._eval_module(node.else_body) if node.else_body else last
            body_result = self._eval_module(node.body)
            if isinstance(body_result, BreakSignal):
                return NIL
            if isinstance(body_result, ContinueSignal):
                continue
            if isinstance(body_result, ControlFlow):
                return body_result
            last = body_result

    def _eval_Match(self, node: Match) -> Value | ControlFlow:
        subject = self.eval(node.subject)
        if isinstance(subject, ControlFlow):
            return subject
        for case in node.cases:
            if not isinstance(case, PatternTest):
                raise TypeError(
                    f"Match case must be PatternTest, got {type(case).__name__}"
                )
            matched, result = self._eval_pattern_test(case, subject)
            if matched:
                return result
        return NIL

    def _eval_PatternTest(self, node: PatternTest) -> Value | ControlFlow:
        raise RuntimeError("PatternTest can only be evaluated inside Match")

    def _eval_pattern_test(
        self, node: PatternTest, subject: Value
    ) -> tuple[bool, Value | ControlFlow]:
        if not self._pattern_matches(node.pattern, subject):
            return False, NIL
        if node.guard is not None:
            guard = self.eval(node.guard)
            if isinstance(guard, ControlFlow):
                return True, guard
            if not is_truthy(guard):
                return False, NIL
        return True, self._eval_module(node.body)

    def _pattern_matches(self, pattern: CoreNode | None, subject: Value) -> bool:
        if pattern is None:
            return True
        if isinstance(pattern, Literal):
            return unbox_value(subject) == pattern.value
        if isinstance(pattern, Load):
            if pattern.name == "_":
                return True
            self._current_frame.bind(pattern.name, subject)
            return True
        raise TypeError(f"Unsupported pattern node {type(pattern).__name__}")

    def _eval_Raise(self, node: Raise) -> Value | ControlFlow:
        value = self.eval(node.exception)
        if isinstance(value, ControlFlow):
            return value
        if isinstance(value, ErrorValue):
            return value
        return ErrorValue(str(unbox_value(value)), payload=value)

    def _eval_Handle(self, node: Handle) -> Value | ControlFlow:
        result = self._eval_module(node.body)
        if isinstance(result, ErrorValue):
            handled = self._handle_error(result, node.handlers)
            final = self._eval_module(node.finalbody)
            if isinstance(final, ControlFlow):
                return final
            return handled
        final = self._eval_module(node.finalbody)
        if isinstance(final, ControlFlow):
            return final
        return result

    def _handle_error(
        self, error: ErrorValue, handlers: tuple[CoreNode, ...]
    ) -> Value | ControlFlow:
        for handler in handlers:
            if isinstance(handler, PatternTest):
                matched, result = self._eval_pattern_test(handler, error)
                if matched:
                    return result
        return error

    def _eval_Diagnostic(self, node: Diagnostic) -> Value:
        raise RuntimeError(f"Unexecutable Core diagnostic: {node.message}")

    @staticmethod
    def _apply_binary_op(op: str, left: Any, right: Any) -> Any:
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == "//":
            return left // right
        if op == "%":
            return left % right
        if op == "**":
            return left ** right
        if op == "@":
            return left @ right
        if op == "<<":
            return left << right
        if op == ">>":
            return left >> right
        if op == "|":
            return left | right
        if op == "^":
            return left ^ right
        if op == "&":
            return left & right
        raise RuntimeError(f"Unsupported binary op {op!r}")

    @staticmethod
    def _apply_compare_op(op: str, left: Any, right: Any) -> bool:
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "is":
            return left is right
        if op == "is not":
            return left is not right
        if op == "in":
            return left in right
        if op == "not in":
            return left not in right
        raise RuntimeError(f"Unsupported compare op {op!r}")


register_backend("core-runtime", CoreRuntimeEvaluator())
