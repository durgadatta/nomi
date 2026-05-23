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
    YieldSignal,
)
from prototype.runtime.backends.environment import Frame
from prototype.runtime.backends.values import (
    DataConstructorValue,
    DataValue,
    ErrorValue,
    FunctionValue,
    MappingValue,
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
    Break,
    Branch,
    Call,
    CompareOp,
    Continue,
    ConditionalExpr,
    ConstructData,
    CoreNode,
    Diagnostic,
    Function,
    ForEach,
    GetField,
    GetItem,
    Handle,
    Literal,
    Load,
    Loop,
    MappingLiteral,
    Match,
    Module,
    NoOp,
    PatternTest,
    Raise,
    Return,
    Sequence,
    Spread,
    UnaryOp,
    Yield,
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
        default_host_calls = self._default_host_calls()
        self._default_host_names = frozenset(default_host_calls)
        self._raw_host_calls = {
            **default_host_calls,
            **dict(host_calls or {}),
        }
        self._global_frame = Frame()
        self._current_frame = self._global_frame
        self._current_block: FunctionValue | None = None
        self._host_calls = {
            name: (
                func
                if isinstance(func, NativeValue)
                else box_value(func)
            )
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
            bindings=self._export_global_bindings(),
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
        block = self.eval(node.block) if node.block is not None else None
        if isinstance(block, ControlFlow):
            return block
        if block is not None and not isinstance(block, FunctionValue):
            raise TypeError(f"{type(block).__name__} is not a block")
        if isinstance(func, NativeValue):
            return self._call_native(func, tuple(args))
        if isinstance(func, DataConstructorValue):
            return self._construct_data(func, tuple(args))
        if isinstance(func, FunctionValue):
            return self._call_function(func, tuple(args), block=block)
        raise TypeError(f"{type(func).__name__} is not callable")

    def _call_function(
        self,
        func: FunctionValue,
        args: tuple[Value, ...],
        *,
        block: FunctionValue | None = None,
    ) -> Value | ControlFlow:
        saved_frame = self._current_frame
        saved_block = self._current_block
        self._current_frame = func.closure.extend(func.params, args)
        self._current_block = block
        try:
            result = self._eval_module(func.body)
            if isinstance(result, ReturnSignal):
                return result.value
            return result
        finally:
            self._current_frame = saved_frame
            self._current_block = saved_block

    def _eval_Return(self, node: Return) -> ControlFlow:
        value = self.eval(node.value)
        if isinstance(value, ControlFlow):
            return value
        if isinstance(value, ErrorValue):
            return value
        return ReturnSignal(value)

    def _eval_Yield(self, node: Yield) -> ControlFlow:
        value = self.eval(node.value)
        if isinstance(value, ControlFlow):
            return value
        if self._current_block is not None:
            args = (value,) if self._current_block.params else ()
            result = self._call_function(self._current_block, args)
            if isinstance(result, ControlFlow):
                return result
            return NIL
        return YieldSignal(value)

    def _eval_Branch(self, node: Branch) -> Value | ControlFlow:
        test = self.eval(node.test)
        if isinstance(test, ControlFlow):
            return test
        branch = node.then_body if is_truthy(test) else node.else_body
        return self._eval_module(branch)

    def _eval_NoOp(self, node: NoOp) -> Value:
        return NIL

    def _eval_Break(self, node: Break) -> ControlFlow:
        return BreakSignal()

    def _eval_Continue(self, node: Continue) -> ControlFlow:
        return ContinueSignal()

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

    def _eval_ConditionalExpr(self, node: ConditionalExpr) -> Value | ControlFlow:
        test = self.eval(node.test)
        if isinstance(test, ControlFlow):
            return test
        branch = node.then_value if is_truthy(test) else node.else_value
        return self.eval(branch)

    def _eval_Sequence(self, node: Sequence) -> Value | ControlFlow:
        elements: list[Value] = []
        for elem in node.elements:
            if isinstance(elem, Spread):
                spread_value = self.eval(elem.value)
                if isinstance(spread_value, ControlFlow):
                    return spread_value
                elements.extend(self._spread_elements(spread_value))
                continue
            value = self.eval(elem)
            if isinstance(value, ControlFlow):
                return value
            elements.append(value)
        return SequenceValue(tuple(elements))

    def _eval_MappingLiteral(self, node: MappingLiteral) -> Value | ControlFlow:
        entries: dict[Any, Value] = {}
        for key_node, value_node in node.entries:
            key = self.eval(key_node)
            if isinstance(key, ControlFlow):
                return key
            value = self.eval(value_node)
            if isinstance(value, ControlFlow):
                return value
            entries[unbox_value(key)] = value
        return MappingValue(entries)

    def _eval_GetItem(self, node: GetItem) -> Value | ControlFlow:
        obj = self.eval(node.object_)
        if isinstance(obj, ControlFlow):
            return obj
        key = self.eval(node.key)
        if isinstance(key, ControlFlow):
            return key
        key_value = unbox_value(key)
        if isinstance(obj, SequenceValue):
            return obj.elements[key_value]
        if isinstance(obj, MappingValue):
            return obj.entries[key_value]
        return box_value(unbox_value(obj)[key_value])

    def _eval_Spread(self, node: Spread) -> Value | ControlFlow:
        raise RuntimeError("Spread can only be evaluated inside Sequence")

    def _eval_ConstructData(self, node: ConstructData) -> Value | ControlFlow:
        if any(
            not isinstance(field_node, Literal) or field_node.value is not None
            for _, field_node in node.fields
        ):
            fields: dict[str, Value] = {}
            for name, field_node in node.fields:
                value = self.eval(field_node)
                if isinstance(value, ControlFlow):
                    return value
                fields[name] = value
            return DataValue(name=node.name, fields=fields)
        constructor = DataConstructorValue(
            name=node.name,
            fields=tuple(name for name, _ in node.fields),
        )
        self._current_frame.assign(node.name, constructor)
        return constructor

    def _eval_GetField(self, node: GetField) -> Value | ControlFlow:
        obj = self.eval(node.object_)
        if isinstance(obj, ControlFlow):
            return obj
        if isinstance(obj, MappingValue) and node.field == "get":
            return NativeValue(
                name="mapping.get",
                callable=lambda key, default=NIL: obj.entries.get(
                    unbox_value(key),
                    default,
                ),
                expects_values=True,
            )
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

    def _eval_ForEach(self, node: ForEach) -> Value | ControlFlow:
        iterable = self.eval(node.iterable)
        if isinstance(iterable, ControlFlow):
            return iterable
        ran = False
        last: Value | ControlFlow = NIL
        for item in self._iter_values(iterable):
            ran = True
            self._current_frame.assign(node.target, item)
            body_result = self._eval_module(node.body)
            if isinstance(body_result, BreakSignal):
                return NIL
            if isinstance(body_result, ContinueSignal):
                continue
            if isinstance(body_result, ControlFlow):
                return body_result
            last = body_result
        if not ran and node.else_body is not None:
            return self._eval_module(node.else_body)
        return last

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
        snapshot = dict(self._current_frame.bindings)
        if not self._pattern_matches(node.pattern, subject):
            self._current_frame.bindings.clear()
            self._current_frame.bindings.update(snapshot)
            return False, NIL
        if node.guard is not None:
            guard = self.eval(node.guard)
            if isinstance(guard, ControlFlow):
                return True, guard
            if not is_truthy(guard):
                self._current_frame.bindings.clear()
                self._current_frame.bindings.update(snapshot)
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
        if isinstance(pattern, Sequence):
            if not isinstance(subject, SequenceValue):
                return False
            return self._sequence_pattern_matches(pattern, subject)
        if isinstance(pattern, Spread):
            if isinstance(pattern.value, Load) and pattern.value.name != "_":
                self._current_frame.bind(pattern.value.name, subject)
            return True
        if isinstance(pattern, MappingLiteral):
            if not isinstance(subject, MappingValue):
                return False
            for key_pattern, value_pattern in pattern.entries:
                key = self.eval(key_pattern)
                if isinstance(key, ControlFlow):
                    return False
                key_value = unbox_value(key)
                if key_value not in subject.entries:
                    return False
                if not self._pattern_matches(
                    value_pattern,
                    subject.entries[key_value],
                ):
                    return False
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
                matched, result = self._eval_error_handler(handler, error)
                if matched:
                    return result
        return error

    def _eval_Diagnostic(self, node: Diagnostic) -> Value:
        raise RuntimeError(f"Unexecutable Core diagnostic: {node.message}")

    def _export_global_bindings(self) -> dict[str, object]:
        exported = {}
        for name, value in self._global_frame.bindings.items():
            if (
                name in self._default_host_names
                and self._host_calls.get(name) is value
            ):
                continue
            exported[name] = unbox_value(value)
        return exported

    def _call_native(
        self, func: NativeValue, args: tuple[Value, ...]
    ) -> Value | ControlFlow:
        try:
            if func.expects_values:
                result = func.callable(*args)
            else:
                result = func.callable(*[unbox_value(arg) for arg in args])
        except Exception as exc:
            return ErrorValue(str(exc), kind=type(exc).__name__)
        return result if isinstance(result, Value) else box_value(result)

    def _construct_data(
        self, constructor: DataConstructorValue, args: tuple[Value, ...]
    ) -> DataValue:
        if len(args) != len(constructor.fields):
            raise TypeError(
                f"{constructor.name} expected {len(constructor.fields)} "
                f"arguments, received {len(args)}"
            )
        return DataValue(
            name=constructor.name,
            fields=dict(zip(constructor.fields, args)),
        )

    def _default_host_calls(self) -> dict[str, NativeValue]:
        return {
            "abs": NativeValue("abs", lambda value: abs(unbox_value(value)), True),
            "bool": NativeValue("bool", lambda value: is_truthy(value), True),
            "filter": NativeValue("filter", self._host_filter, True),
            "float": NativeValue(
                "float",
                lambda value: float(unbox_value(value)),
                True,
            ),
            "int": NativeValue("int", lambda value: int(unbox_value(value)), True),
            "len": NativeValue("len", lambda value: len(unbox_value(value)), True),
            "list": NativeValue("list", self._host_list, True),
            "map": NativeValue("map", self._host_map, True),
            "print": NativeValue("print", self._host_print, True),
            "range": NativeValue("range", self._host_range, True),
            "str": NativeValue("str", self._host_str, True),
            "sum": NativeValue("sum", lambda value: sum(unbox_value(value)), True),
        }

    def _host_filter(self, func: Value, sequence: Value) -> SequenceValue:
        kept: list[Value] = []
        for item in self._iter_values(sequence):
            result = self._apply_value_callable(func, (item,))
            if isinstance(result, ControlFlow):
                raise RuntimeError(
                    f"Unexpected {type(result).__name__} inside filter"
                )
            if is_truthy(result):
                kept.append(item)
        return SequenceValue(tuple(kept))

    def _host_list(self, value: Value | None = None) -> SequenceValue:
        if value is None:
            return SequenceValue(())
        return SequenceValue(tuple(self._iter_values(value)))

    def _host_map(self, func: Value, sequence: Value) -> SequenceValue:
        mapped: list[Value] = []
        for item in self._iter_values(sequence):
            result = self._apply_value_callable(func, (item,))
            if isinstance(result, ControlFlow):
                raise RuntimeError(
                    f"Unexpected {type(result).__name__} inside map"
                )
            mapped.append(result)
        return SequenceValue(tuple(mapped))

    def _host_print(self, *values: Value) -> None:
        print(*(self._display_value(value) for value in values))
        return None

    def _host_range(self, *values: Value) -> SequenceValue:
        args = [unbox_value(value) for value in values]
        return SequenceValue(tuple(box_value(item) for item in range(*args)))

    def _host_str(self, value: Value) -> str:
        return self._display_value(value)

    def _apply_value_callable(
        self, func: Value, args: tuple[Value, ...]
    ) -> Value | ControlFlow:
        if isinstance(func, FunctionValue):
            return self._call_function(func, args)
        if isinstance(func, NativeValue):
            return self._call_native(func, args)
        if isinstance(func, DataConstructorValue):
            return self._construct_data(func, args)
        raise TypeError(f"{type(func).__name__} is not callable")

    def _iter_values(self, value: Value) -> tuple[Value, ...]:
        if isinstance(value, SequenceValue):
            return value.elements
        if isinstance(value, MappingValue):
            return tuple(box_value(key) for key in value.entries)
        return tuple(box_value(item) for item in unbox_value(value))

    def _display_value(self, value: Value) -> str:
        if isinstance(value, DataValue):
            fields = ", ".join(
                f"{name}={self._display_value(field_value)}"
                for name, field_value in value.fields.items()
            )
            return f"{value.name}({fields})"
        if isinstance(value, SequenceValue):
            return str([unbox_value(item) for item in value.elements])
        if isinstance(value, MappingValue):
            return str(unbox_value(value))
        if isinstance(value, FunctionValue):
            return unbox_value(value)
        if isinstance(value, DataConstructorValue):
            return unbox_value(value)
        return str(unbox_value(value))

    def _eval_error_handler(
        self, handler: PatternTest, error: ErrorValue
    ) -> tuple[bool, Value | ControlFlow]:
        if handler.pattern is not None and not self._error_pattern_matches(
            handler.pattern,
            error,
        ):
            return False, NIL
        if handler.guard is not None:
            guard = self.eval(handler.guard)
            if isinstance(guard, ControlFlow):
                return True, guard
            if not is_truthy(guard):
                return False, NIL
        return True, self._eval_module(handler.body)

    def _error_pattern_matches(self, pattern: CoreNode, error: ErrorValue) -> bool:
        if isinstance(pattern, Load):
            return pattern.name in {"_", "Exception", error.kind}
        if isinstance(pattern, Literal):
            return pattern.value in {error.kind, error.message}
        return self._pattern_matches(pattern, error)

    @staticmethod
    def _spread_elements(value: Value) -> tuple[Value, ...]:
        if isinstance(value, SequenceValue):
            return value.elements
        if isinstance(value, MappingValue):
            return tuple(box_value(key) for key in value.entries)
        return tuple(box_value(item) for item in unbox_value(value))

    def _sequence_pattern_matches(
        self, pattern: Sequence, subject: SequenceValue
    ) -> bool:
        spread_index = next(
            (
                index
                for index, item in enumerate(pattern.elements)
                if isinstance(item, Spread)
            ),
            None,
        )
        if spread_index is None:
            if len(pattern.elements) != len(subject.elements):
                return False
            return all(
                self._pattern_matches(item_pattern, item_value)
                for item_pattern, item_value in zip(
                    pattern.elements,
                    subject.elements,
                )
            )
        prefix = pattern.elements[:spread_index]
        suffix = pattern.elements[spread_index + 1 :]
        if len(subject.elements) < len(prefix) + len(suffix):
            return False
        for item_pattern, item_value in zip(prefix, subject.elements):
            if not self._pattern_matches(item_pattern, item_value):
                return False
        if suffix:
            suffix_values = subject.elements[-len(suffix) :]
        else:
            suffix_values = ()
        for item_pattern, item_value in zip(suffix, suffix_values):
            if not self._pattern_matches(item_pattern, item_value):
                return False
        rest_end = len(subject.elements) - len(suffix)
        rest = SequenceValue(subject.elements[len(prefix) : rest_end])
        return self._pattern_matches(pattern.elements[spread_index], rest)

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
