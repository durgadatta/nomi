"""Adapters from Rust parser JSON payloads to Python AST.

This module keeps parser-specific payload lowering out of ``frontend.py``.
Future serialized parser payloads, including PEG/CST candidates, should get
their own adapter modules and join the same frontend equivalence tests.
"""

from __future__ import annotations

import ast
import keyword
from typing import Any

from lark import Token

from .lowering.data_decl import DataDeclMixin


_DATA_DECL_BUILDER = DataDeclMixin()
_SECTION_OPERATOR_FACTORIES = {
    "+": ast.Add,
    "-": ast.Sub,
    "*": ast.Mult,
    "/": ast.Div,
    "//": ast.FloorDiv,
    "%": ast.Mod,
    "@": ast.MatMult,
    "**": ast.Pow,
}


def python_ast_from_rust_payload(payload: dict[str, Any]) -> ast.Module:
    schema = payload.get("schema", "nomi.rust-ast")
    version = payload.get("version", 1)
    if schema != "nomi.rust-ast" or version != 1:
        raise ValueError(
            f"unsupported Rust AST payload contract: {schema!r} v{version!r}"
        )
    if payload.get("type") != "Module":
        raise ValueError(f"unsupported Rust AST payload: {payload.get('type')!r}")
    body = []
    decorators = []
    for stmt_payload in payload["body"]:
        decorator = _decorator_from_rust_payload(stmt_payload)
        if decorator is not None:
            decorators.append(decorator)
            continue
        stmt = _stmt_from_rust_payload(stmt_payload)
        if decorators and isinstance(stmt, (ast.FunctionDef, ast.ClassDef)):
            stmt.decorator_list = [*decorators, *stmt.decorator_list]
            decorators = []
        body.append(stmt)
    if decorators:
        raise ValueError("dangling Rust decorator payload")
    return ast.Module(body=body, type_ignores=[])


def _stmt_from_rust_payload(payload: dict[str, Any]) -> ast.stmt:
    if payload["type"].startswith("defer "):
        return _defer_stmt_from_rust_text(payload["type"])

    match payload["type"]:
        case "Assign":
            if payload["target"].startswith("type "):
                return _type_alias_from_rust_payload(payload)
            if equation := _func_equation_from_assignment_payload(payload):
                return equation
            if ":" in payload["target"]:
                return _ann_assign_from_rust_payload(payload)
            return ast.Assign(
                targets=[_name_expr(payload["target"], ast.Store())],
                value=_expr_from_rust_payload(payload["value"]),
            )
        case "AugAssign":
            return ast.AugAssign(
                target=_name_expr(payload["target"], ast.Store()),
                op=_aug_operator_from_rust_payload(payload["op"]),
                value=_expr_from_rust_payload(payload["value"]),
            )
        case "Expr":
            if raw_stmt := _raw_stmt_from_rust_expr(payload["value"]):
                return raw_stmt
            return ast.Expr(value=_expr_from_rust_payload(payload["value"]))
        case "FunctionDef":
            return _function_equation_from_rust_payload(payload)
        case "Return":
            value = payload["value"]
            return ast.Return(
                value=None if value is None else _expr_from_rust_payload(value)
            )
        case "Yield":
            value = payload["value"]
            return ast.Expr(
                value=ast.Yield(
                    value=None if value is None else _expr_from_rust_payload(value)
                )
            )
        case "Raise":
            value = payload["value"]
            return ast.Raise(
                exc=None if value is None else _expr_from_rust_payload(value)
            )
        case "Pass" | "pass":
            return ast.Pass()
        case "Break" | "break":
            return ast.Break()
        case "Continue" | "continue":
            return ast.Continue()
        case "Suite" if payload.get("kind") == "Func":
            return _func_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "Class":
            return _class_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "For":
            return _for_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "If":
            return _if_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "Unless":
            return _unless_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "While":
            return _while_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "With":
            return _with_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "Guard":
            return _guard_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "Try":
            return _try_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "ReturnMatch":
            return _return_match_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "BlockCall":
            return _block_call_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "Data":
            return _data_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "Match":
            return _match_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "MatchAssign":
            return _match_assign_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "WhereAssign":
            return _where_assign_suite_from_rust_payload(payload)
        case "Suite" if payload.get("kind") == "WhereFunction":
            return _where_function_suite_from_rust_payload(payload)
        case other:
            raise ValueError(f"unsupported Rust AST statement: {other!r}")


def _decorator_from_rust_payload(payload: dict[str, Any]) -> ast.expr | None:
    if payload.get("type") != "Expr":
        return None
    value = payload.get("value", {})
    if value.get("type") != "Raw":
        return None
    raw = value["value"].strip()
    if not raw.startswith("@"):
        return None
    return _raw_or_python_expr(raw.removeprefix("@").strip())


def _raw_stmt_from_rust_expr(payload: dict[str, Any]) -> ast.stmt | None:
    if payload.get("type") != "Raw":
        return None
    raw = payload["value"].strip()
    if not (raw.startswith("import ") or raw.startswith("from ")):
        return None
    body = ast.parse(raw).body
    if len(body) == 1 and isinstance(body[0], (ast.Import, ast.ImportFrom)):
        return body[0]
    return None


def _defer_stmt_from_rust_text(raw: str) -> ast.stmt:
    stmt_text = raw.removeprefix("defer ").strip()
    try:
        body = ast.parse(stmt_text).body
    except SyntaxError:
        body = [ast.Expr(value=_raw_or_python_expr(stmt_text))]
    if len(body) != 1 or not isinstance(body[0], (ast.Assign, ast.Expr)):
        raise ValueError(f"unsupported Rust defer statement: {raw!r}")
    stmt = body[0]
    stmt._nomi_defer = True
    return stmt


def _func_equation_from_assignment_payload(
    payload: dict[str, Any],
) -> ast.FunctionDef | None:
    parsed = _func_equation_target_from_text(payload["target"])
    if parsed is None:
        return None
    name, eq_args, guard = parsed
    fn = _function_equation_from_parts(
        name=name,
        eq_args=eq_args,
        body=_expr_from_rust_payload(payload["value"]),
    )
    if guard is not None:
        fn._nomi_eq_guard = guard
    return fn


def _function_equation_from_parts(
    *, name: str, eq_args: list[Any], body: ast.expr
) -> ast.FunctionDef:
    args_list = []
    defaults = []
    for index, arg in enumerate(eq_args):
        if isinstance(arg, tuple):
            arg_name, arg_default = arg
            args_list.append(ast.arg(arg=arg_name))
            if arg_default is not None:
                defaults.append(arg_default)
        elif isinstance(arg, str):
            args_list.append(ast.arg(arg=arg))
        else:
            args_list.append(ast.arg(arg=f"__{index}"))
    fn = ast.FunctionDef(
        name=name,
        args=ast.arguments(
            posonlyargs=[],
            args=args_list,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=defaults,
            vararg=None,
            kwarg=None,
        ),
        body=[ast.Return(value=body)],
        decorator_list=[],
        returns=None,
    )
    fn._nomi_eq_args = eq_args
    return fn


def _function_equation_from_rust_payload(payload: dict[str, Any]) -> ast.FunctionDef:
    return _function_equation_from_parts(
        name=payload["name"],
        eq_args=[(param, None) for param in payload["params"]],
        body=_expr_from_rust_payload(payload["body"]),
    )


def _func_equation_target_from_text(
    target: str,
) -> tuple[str, list[Any], ast.expr | None] | None:
    head, _, guard_text = target.partition(" when ")
    guard = _raw_or_python_expr(guard_text.strip()) if guard_text else None
    head = head.strip()
    if " (" in head and head.endswith(")"):
        name, _, rest = head.partition(" (")
        if not name.strip().isidentifier():
            return None
        return (
            name.strip(),
            _func_equation_args_from_text(rest[:-1].strip()),
            guard,
        )
    parts = head.split()
    if len(parts) == 2 and all(part.isidentifier() for part in parts):
        return (parts[0], [parts[1]], guard)
    return None


def _func_equation_args_from_text(args_text: str) -> list[Any]:
    if not args_text:
        return []
    eq_args = []
    for part in _split_top_level(args_text):
        if not part:
            continue
        before_default, has_default, default_text = _partition_default(part)
        if has_default:
            eq_args.append((before_default.strip(), _raw_or_python_expr(default_text)))
            continue
        expr = _raw_or_python_expr(before_default.strip())
        if isinstance(expr, ast.Name):
            eq_args.append((expr.id, None))
        else:
            eq_args.append(expr)
    return eq_args


def _expr_from_rust_payload(payload: dict[str, Any]) -> ast.expr:
    match payload["type"]:
        case "Name":
            return _name_expr(payload["id"], ast.Load())
        case "Number":
            return ast.Constant(value=_number_value_from_text(payload["value"]))
        case "String":
            return _string_expr_from_rust_payload(payload)
        case "Constant":
            return ast.Constant(value=_constant_value_from_text(payload["value"]))
        case "List":
            return ast.List(
                elts=[_expr_from_rust_payload(item) for item in payload["items"]],
                ctx=ast.Load(),
            )
        case "Tuple":
            return ast.Tuple(
                elts=[_expr_from_rust_payload(item) for item in payload["items"]],
                ctx=ast.Load(),
            )
        case "Dict":
            return ast.Dict(
                keys=[_expr_from_rust_payload(item) for item in payload["keys"]],
                values=[_expr_from_rust_payload(item) for item in payload["values"]],
            )
        case "Attribute":
            return ast.Attribute(
                value=_expr_from_rust_payload(payload["value"]),
                attr=payload["attr"],
                ctx=ast.Load(),
            )
        case "Subscript":
            return ast.Subscript(
                value=_expr_from_rust_payload(payload["value"]),
                slice=_expr_from_rust_payload(payload["slice"]),
                ctx=ast.Load(),
            )
        case "Slice":
            return ast.Slice(
                lower=_optional_expr_from_rust_payload(payload["start"]),
                upper=_optional_expr_from_rust_payload(payload["end"]),
                step=_optional_expr_from_rust_payload(payload["step"]),
            )
        case "Call":
            return ast.Call(
                func=_expr_from_rust_payload(payload["func"]),
                args=[_expr_from_rust_payload(arg) for arg in payload["args"]],
            )
        case "BinOp":
            return ast.BinOp(
                left=_expr_from_rust_payload(payload["left"]),
                op=_operator_from_rust_payload(payload["op"]),
                right=_expr_from_rust_payload(payload["right"]),
            )
        case "Compare":
            return _compare_from_rust_payload(payload)
        case "BoolOp":
            return _bool_op_from_rust_payload(payload)
        case "UnaryOp":
            return ast.UnaryOp(
                op=_unary_operator_from_rust_payload(payload["op"]),
                operand=_expr_from_rust_payload(payload["value"]),
            )
        case "IfExp":
            return ast.IfExp(
                test=_expr_from_rust_payload(payload["test"]),
                body=_expr_from_rust_payload(payload["body"]),
                orelse=_expr_from_rust_payload(payload["orelse"]),
            )
        case "FunctionDef":
            return _function_from_rust_payload(payload)
        case "Raw":
            return _raw_expr_from_rust_payload(payload["value"])
        case other:
            raise ValueError(f"unsupported Rust AST expression: {other!r}")


def _optional_expr_from_rust_payload(payload: dict[str, Any] | None) -> ast.expr | None:
    if payload is None:
        return None
    return _expr_from_rust_payload(payload)


def _func_suite_from_rust_payload(payload: dict[str, Any]) -> ast.FunctionDef:
    parsed = _function_signature_from_text(payload["head"])
    return ast.FunctionDef(
        name=parsed.name,
        args=parsed.args,
        body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
    )


def _class_suite_from_rust_payload(payload: dict[str, Any]) -> ast.ClassDef:
    return ast.ClassDef(
        name=payload["head"],
        bases=[],
        keywords=[],
        body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]] or [ast.Pass()],
        decorator_list=[],
    )


def _for_suite_from_rust_payload(payload: dict[str, Any]) -> ast.For:
    target_text, separator, iter_text = payload["head"].partition(" in ")
    if not separator:
        raise ValueError(f"unsupported Rust for head: {payload['head']!r}")
    orelse = []
    for clause in payload.get("clauses", []):
        if clause.get("kind") == "Else":
            orelse = [_stmt_from_rust_payload(stmt) for stmt in clause["body"]]
    return ast.For(
        target=_store_ctx(_expr_from_python_source(target_text)),
        iter=_expr_from_python_source(iter_text),
        body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
        orelse=orelse,
    )


def _if_suite_from_rust_payload(payload: dict[str, Any]) -> ast.If:
    pattern_text, subject_text = _split_pattern_subject(payload["head"])
    if subject_text is not None:
        return ast.Match(
            subject=_raw_or_nomi_expr(subject_text),
            cases=[
                ast.match_case(
                    pattern=_pattern_from_rust_text(pattern_text),
                    guard=None,
                    body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
                ),
                ast.match_case(pattern=ast.MatchAs(), guard=None, body=[]),
            ],
        )
    return ast.If(
        test=_raw_or_nomi_expr(payload["head"]),
        body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
        orelse=[],
    )


def _unless_suite_from_rust_payload(payload: dict[str, Any]) -> ast.If:
    return ast.If(
        test=ast.UnaryOp(
            op=ast.Not(),
            operand=_raw_or_nomi_expr(payload["head"]),
        ),
        body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
        orelse=[],
    )


def _while_suite_from_rust_payload(payload: dict[str, Any]) -> ast.While:
    pattern_text, subject_text = _split_pattern_subject(payload["head"])
    if subject_text is not None:
        return ast.While(
            test=ast.Constant(value=True),
            body=[
                ast.Match(
                    subject=_raw_or_nomi_expr(subject_text),
                    cases=[
                        ast.match_case(
                            pattern=_pattern_from_rust_text(pattern_text),
                            guard=None,
                            body=[
                                _stmt_from_rust_payload(stmt)
                                for stmt in payload["body"]
                            ],
                        ),
                        ast.match_case(
                            pattern=ast.MatchAs(),
                            guard=None,
                            body=[ast.Break()],
                        ),
                    ],
                )
            ],
        )
    return ast.While(
        test=_raw_or_nomi_expr(payload["head"]),
        body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
    )


def _with_suite_from_rust_payload(payload: dict[str, Any]) -> ast.With:
    return ast.With(
        items=[ast.withitem(context_expr=_raw_or_python_expr(payload["head"]))],
        body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
    )


def _guard_suite_from_rust_payload(payload: dict[str, Any]) -> ast.Match:
    pattern_text, subject_text = _split_pattern_subject(payload["head"])
    if subject_text is None:
        raise ValueError(f"unsupported Rust guard head: {payload['head']!r}")
    return ast.Match(
        subject=_raw_or_nomi_expr(subject_text),
        cases=[
            ast.match_case(
                pattern=_pattern_from_rust_text(pattern_text),
                guard=None,
                body=[ast.Pass()],
            ),
            ast.match_case(
                pattern=ast.MatchAs(),
                guard=None,
                body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
            ),
        ],
    )


def _try_suite_from_rust_payload(payload: dict[str, Any]) -> ast.Try:
    return ast.Try(
        body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
        handlers=[
            _except_handler_from_rust_payload(clause)
            for clause in payload.get("clauses", ())
            if clause.get("kind") == "Except"
        ],
        orelse=[],
        finalbody=[
            stmt
            for clause in payload.get("clauses", ())
            if clause.get("kind") == "Finally"
            for stmt in [_stmt_from_rust_payload(item) for item in clause.get("body", ())]
        ],
    )


def _return_match_suite_from_rust_payload(payload: dict[str, Any]) -> ast.Return:
    match_node = ast.Match(
        subject=_raw_or_nomi_expr(payload["head"]),
        cases=[
            _match_case_from_rust_payload(case_payload, expression_case=True)
            for case_payload in payload["body"]
        ],
    )
    func = ast.FunctionDef(
        name=None,
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=None,
        ),
        body=[match_node],
        decorator_list=[],
        returns=None,
    )
    return ast.Return(value=ast.Call(func=func, args=[], keywords=[]))


def _except_handler_from_rust_payload(payload: dict[str, Any]) -> ast.ExceptHandler:
    head = payload["head"].strip()
    if not head:
        exc_type = None
        name = None
    else:
        exc_text, _, name = head.partition(" as ")
        exc_type = _expr_from_python_source(exc_text)
        name = name.strip() or None
    return ast.ExceptHandler(
        type=exc_type,
        name=name,
        body=[_stmt_from_rust_payload(stmt) for stmt in payload["body"]],
    )


def _block_call_suite_from_rust_payload(payload: dict[str, Any]) -> ast.Expr:
    from prototype.interpreter.constants import BLOCK_KWARG, Block

    call = _expr_from_rust_payload(payload["call"])
    if not isinstance(call, ast.Call):
        raise ValueError(f"unsupported Rust block-call target: {payload['call']!r}")
    block_params = _block_params_from_text(payload.get("params"))
    block_body = [_stmt_from_rust_payload(stmt) for stmt in payload["body"]]
    call.keywords.append(
        ast.keyword(arg=BLOCK_KWARG, value=Block(body=block_body, params=block_params))
    )
    return ast.Expr(value=call)


def _block_params_from_text(params: str | None) -> ast.expr | None:
    if params is None or not params.strip():
        return None
    return _expr_from_python_source(params)


def _ann_assign_from_rust_payload(payload: dict[str, Any]) -> ast.AnnAssign:
    target_text, _, annotation_text = payload["target"].partition(":")
    return ast.AnnAssign(
        target=_name_expr(target_text.strip(), ast.Store()),
        annotation=_annotation_from_rust_text(annotation_text.strip()),
        value=_expr_from_rust_payload(payload["value"]),
        simple=1,
    )


def _data_suite_from_rust_payload(payload: dict[str, Any]) -> ast.ClassDef:
    class_name = payload["head"]
    field_specs = [_data_field_spec_from_rust_payload(item) for item in payload["body"]]
    body = [_DATA_DECL_BUILDER._make_init(class_name, field_specs)]
    if field_specs:
        body.append(_DATA_DECL_BUILDER._make_repr(class_name, field_specs))
        body.append(_DATA_DECL_BUILDER._make_eq(class_name, field_specs))
    return ast.ClassDef(
        name=class_name,
        bases=[],
        keywords=[],
        body=body,
        decorator_list=[],
    )


def _data_field_spec_from_rust_payload(payload: dict[str, Any]):
    name = payload["head"]
    if payload.get("kind") != "BlockCall" or not payload.get("body"):
        return (name, None, None)
    field_body = payload["body"]
    if len(field_body) != 1 or field_body[0].get("type") != "Expr":
        return (name, None, None)
    field_expr = field_body[0]["value"]
    if field_expr.get("type") == "Raw":
        return _data_field_spec_from_raw(name, field_expr["value"])
    return (name, _expr_from_rust_payload(field_expr), None)


def _data_field_spec_from_raw(name: str, raw: str):
    type_text, separator, constraint_text = raw.partition(" where ")
    if not separator:
        return (name, _expr_from_python_source(raw), None)
    return (
        name,
        _expr_from_python_source(type_text.strip()),
        _expr_from_python_source(constraint_text.strip()),
    )


def _match_suite_from_rust_payload(payload: dict[str, Any]) -> ast.Match:
    return ast.Match(
        subject=_raw_or_nomi_expr(payload["head"]),
        cases=[
            _match_case_from_rust_payload(case_payload, expression_case=False)
            for case_payload in payload["body"]
        ],
    )


def _match_assign_suite_from_rust_payload(payload: dict[str, Any]) -> ast.Assign:
    target_text, _, subject_text = payload["head"].partition(" = match ")
    if not subject_text:
        raise ValueError(f"unsupported Rust match assignment head: {payload['head']!r}")
    match_node = ast.Match(
        subject=_raw_or_nomi_expr(subject_text),
        cases=[
            _match_case_from_rust_payload(case_payload, expression_case=True)
            for case_payload in payload["body"]
        ],
    )
    func = ast.FunctionDef(
        name=None,
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=None,
        ),
        body=[match_node],
        decorator_list=[],
        returns=None,
    )
    return ast.Assign(
        targets=[_name_expr(target_text.strip(), ast.Store())],
        value=ast.Call(func=func, args=[], keywords=[]),
    )


def _raw_expr_from_rust_payload(raw: str) -> ast.expr:
    if raw.startswith("$"):
        return ast.Name(id=raw, ctx=ast.Load())
    if _top_level_call_like_raw(raw):
        return _call_from_rust_text(raw)
    if raw.startswith("try "):
        return _try_expr_from_rust_text(raw)
    if raw.startswith("match "):
        return _inline_match_from_rust_text(raw)
    if _section_like_raw(raw):
        return _section_from_rust_text(raw)
    if "??" in raw:
        return _nullish_from_rust_text(raw)
    if "?." in raw:
        return _safe_navigation_from_rust_text(raw)
    if "|>" in raw:
        return _pipeline_from_rust_text(raw)
    if " > > > " in raw or " >>> " in raw:
        return _compose_from_rust_text(raw)
    if "=>" in raw:
        return _arrow_function_from_rust_text(raw)
    if raw.startswith("[") and raw.endswith("]"):
        return _list_from_rust_text(raw)
    if _top_level_call_like_raw(raw):
        return _call_from_rust_text(raw)
    if " .. " in raw or " ..< " in raw:
        return _range_from_rust_text(raw)
    if python_expr := _try_python_expr_from_source(raw):
        return python_expr
    raise ValueError(f"unsupported Rust AST expression: 'Raw'")


def _nullish_from_rust_text(raw: str) -> ast.IfExp:
    parts = _split_top_level_token(raw, "??")
    result = _raw_or_python_expr(parts[-1])
    for part in reversed(parts[:-1]):
        left = _raw_or_python_expr(part)
        result = ast.IfExp(
            test=ast.Compare(
                left=left,
                ops=[ast.IsNot()],
                comparators=[ast.Constant(value=None)],
            ),
            body=left,
            orelse=result,
        )
    return result


def _try_expr_from_rust_text(raw: str) -> ast.Call:
    text = raw.removeprefix("try ")
    body_text, separator, rest = text.partition(" except ")
    if not separator:
        raise ValueError(f"unsupported Rust try expression: {raw!r}")
    handlers = []
    current = rest
    while current.strip():
        error_text, sep, after = current.partition(" : ")
        if not sep:
            raise ValueError(f"unsupported Rust try expression handler: {raw!r}")
        fallback_text = ""
        depth = 0
        quote = None
        escaped = False
        next_start = len(after)
        for i, ch in enumerate(after):
            if quote is not None:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == quote:
                    quote = None
                fallback_text += ch
                continue
            if ch in "'\"":
                quote = ch
                fallback_text += ch
                continue
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == " " and after[i:i + len(" except ")] == " except " and depth == 0:
                fallback_text = fallback_text.rstrip()
                next_start = i + len(" except ")
                break
            fallback_text += ch
        handlers.append((error_text.strip(), fallback_text.strip()))
        current = after[next_start:]
        if not current.strip():
            break
    ast_handlers = [
        ast.ExceptHandler(
            type=_expr_from_python_source(err),
            name=None,
            body=[ast.Return(value=_raw_or_python_expr(fb))],
        )
        for err, fb in handlers
    ]
    return ast.Call(
        func=ast.FunctionDef(
            name=None,
            args=ast.arguments(args=[]),
            body=[
                ast.Try(
                    body=[ast.Return(value=_raw_or_python_expr(body_text))],
                    handlers=ast_handlers,
                    orelse=[],
                    finalbody=[],
                )
            ],
        ),
        args=[],
        keywords=[],
    )


def _safe_navigation_from_rust_text(raw: str) -> ast.expr:
    base_text, *operations = _split_top_level_token(raw, "?.")
    value = _raw_or_nomi_expr(base_text)
    for operation in operations:
        operation = operation.strip()
        value = _safe_access(value, operation)
    return value


def _safe_access(base: ast.expr, operation: str) -> ast.Call:
    if operation.startswith("[") and operation.endswith("]"):
        slice_expr = _raw_or_python_expr(operation[1:-1])
        access = ast.Subscript(
            value=ast.Name(id="__safe", ctx=ast.Load()),
            slice=slice_expr,
            ctx=ast.Load(),
        )
    else:
        name, _, args_text = operation.partition(" (")
        args_text = args_text.removesuffix(")").strip()
        access = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="__safe", ctx=ast.Load()),
                attr=name.strip(),
                ctx=ast.Load(),
            ),
            args=(
                []
                if not args_text
                else [_raw_or_python_expr(part) for part in _split_top_level(args_text)]
            ),
            keywords=[],
        )
    return ast.Call(
        func=ast.FunctionDef(
            name=None,
            args=ast.arguments(args=[ast.arg(arg="__safe")]),
            body=[
                ast.Return(
                    value=ast.IfExp(
                        test=ast.Compare(
                            left=ast.Name(id="__safe", ctx=ast.Load()),
                            ops=[ast.IsNot()],
                            comparators=[ast.Constant(value=None)],
                        ),
                        body=access,
                        orelse=ast.Constant(value=None),
                    )
                )
            ],
        ),
        args=[base],
        keywords=[],
    )


def _pipeline_from_rust_text(raw: str) -> ast.expr:
    parts = _split_top_level_token(raw, "|>")
    value = _raw_or_python_expr(parts[0])
    for func_text in parts[1:]:
        value = ast.Call(func=_raw_or_python_expr(func_text), args=[value], keywords=[])
    return value


def _compose_from_rust_text(raw: str) -> ast.FunctionDef:
    left_text, right_text = _split_top_level_token(raw, " >>> ") if " >>> " in raw else _split_top_level_token(raw, "> > >")
    return ast.FunctionDef(
        name=None,
        args=ast.arguments(args=[ast.arg(arg="__x")]),
        body=[
            ast.Return(
                value=ast.Call(
                    func=_raw_or_python_expr(right_text),
                    args=[
                        ast.Call(
                            func=_raw_or_python_expr(left_text),
                            args=[ast.Name(id="__x", ctx=ast.Load())],
                            keywords=[],
                        )
                    ],
                    keywords=[],
                )
            )
        ],
    )


def _arrow_function_from_rust_text(raw: str) -> ast.FunctionDef:
    raw = _strip_wrapping_parens(raw.strip())
    params_text, separator, body_text = raw.partition("=>")
    if not separator:
        raise ValueError(f"unsupported Rust arrow function: {raw!r}")
    params_text = _strip_wrapping_parens(params_text.strip())
    params = [part.strip() for part in _split_top_level(params_text) if part.strip()]
    return ast.FunctionDef(
        name=None,
        args=ast.arguments(args=[ast.arg(arg=param) for param in params]),
        body=[ast.Return(value=_raw_or_python_expr(body_text.strip()))],
    )


def _list_from_rust_text(raw: str) -> ast.List:
    inner = raw.removeprefix("[").removesuffix("]").strip()
    items = []
    for part in _split_top_level(inner):
        if part.startswith("* "):
            items.append(
                ast.Starred(
                    value=_raw_or_python_expr(part.removeprefix("* ").strip()),
                    ctx=ast.Load(),
                )
            )
        elif part:
            items.append(_raw_or_python_expr(part))
    return ast.List(elts=items, ctx=ast.Load())


def _call_like_raw(raw: str) -> bool:
    return raw.endswith(")") and " (" in raw


def _top_level_call_like_raw(raw: str) -> bool:
    if not _call_like_raw(raw):
        return False
    func_text, _, _rest = raw.partition(" (")
    if any(token in func_text for token in ("??", "?.", "|>", " > > > ", "=>")):
        return False
    return all(
        part.strip().isidentifier() and not keyword.iskeyword(part.strip())
        for part in func_text.split(".")
    )


def _call_from_rust_text(raw: str) -> ast.Call:
    func_text, _, rest = raw.partition(" (")
    args_text = rest[:-1].strip()
    args = []
    keywords = []
    for part in _split_top_level(args_text):
        before_default, has_default, default_text = _partition_default(part)
        if has_default and before_default.strip().isidentifier():
            keywords.append(
                ast.keyword(
                    arg=before_default.strip(),
                    value=_raw_or_python_expr(default_text),
                )
            )
        elif part:
            args.append(_raw_or_python_expr(part))
    return ast.Call(func=_raw_or_python_expr(func_text), args=args, keywords=keywords)


def _section_like_raw(raw: str) -> bool:
    if not (raw.startswith("(") and raw.endswith(")")):
        return False
    parts = raw[1:-1].strip().split()
    return (
        len(parts) in {1, 2}
        and any(part in _SECTION_OPERATOR_FACTORIES for part in parts)
    )


def _section_from_rust_text(raw: str) -> ast.FunctionDef:
    parts = raw[1:-1].strip().split()
    if len(parts) == 1:
        op_factory = _SECTION_OPERATOR_FACTORIES[parts[0]]
        return ast.FunctionDef(
            name=None,
            args=ast.arguments(args=[ast.arg(arg="__a"), ast.arg(arg="__b")]),
            body=[
                ast.Return(
                    value=ast.BinOp(
                        left=ast.Name(id="__a", ctx=ast.Load()),
                        op=op_factory(),
                        right=ast.Name(id="__b", ctx=ast.Load()),
                    )
                )
            ],
        )
    first, second = parts
    if first in _SECTION_OPERATOR_FACTORIES:
        op_factory = _SECTION_OPERATOR_FACTORIES[first]
        value = ast.BinOp(
            left=ast.Name(id="__s", ctx=ast.Load()),
            op=op_factory(),
            right=_raw_or_python_expr(second),
        )
    elif second in _SECTION_OPERATOR_FACTORIES:
        op_factory = _SECTION_OPERATOR_FACTORIES[second]
        value = ast.BinOp(
            left=_raw_or_python_expr(first),
            op=op_factory(),
            right=ast.Name(id="__s", ctx=ast.Load()),
        )
    else:
        raise ValueError(f"unsupported Rust operator section: {raw!r}")
    return ast.FunctionDef(
        name=None,
        args=ast.arguments(args=[ast.arg(arg="__s")]),
        body=[ast.Return(value=value)],
    )


def _range_from_rust_text(raw: str) -> ast.Call:
    if " ..< " in raw:
        start_text, end_text = raw.split(" ..< ", 1)
        inclusive = False
    else:
        start_text, end_text = raw.split(" .. ", 1)
        inclusive = True
    end_text, step_text = _split_range_step(end_text)
    end_expr = _raw_or_python_expr(end_text)
    if inclusive:
        end_expr = ast.BinOp(
            left=end_expr,
            op=ast.Add(),
            right=ast.Constant(value=1),
        )
    args = [_raw_or_python_expr(start_text), end_expr]
    if step_text is not None:
        args.append(_raw_or_python_expr(step_text))
    return ast.Call(func=ast.Name(id="range", ctx=ast.Load()), args=args, keywords=[])


def _split_range_step(text: str) -> tuple[str, str | None]:
    end_text, separator, step_text = text.partition(" by ")
    if not separator:
        return text.strip(), None
    return end_text.strip(), step_text.strip()


def _raw_or_python_expr(text: str) -> ast.expr:
    text = text.strip()
    if (
        _section_like_raw(text)
        or "??" in text
        or "?." in text
        or "=>" in text
        or "|>" in text
        or " > > > " in text
        or (text.startswith("[") and text.endswith("]"))
        or " .. " in text
        or " ..< " in text
        or _top_level_call_like_raw(text)
    ):
        return _raw_expr_from_rust_payload(text)
    return _expr_from_python_source(text)


def _try_python_expr_from_source(source: str) -> ast.expr | None:
    try:
        return _expr_from_python_source(source)
    except SyntaxError:
        return None


def _raw_or_nomi_expr(text: str) -> ast.expr:
    expr = _raw_or_python_expr(text)
    return _restore_nomi_name_tokens(expr)


def _inline_match_from_rust_text(raw: str) -> ast.Call:
    subject_and_cases = raw.removeprefix("match ").strip()
    subject_text, separator, cases_text = subject_and_cases.partition(":")
    if not separator:
        raise ValueError(f"unsupported Rust inline match expression: {raw!r}")
    cases = [
        _inline_match_case_from_text(part.strip())
        for part in _split_top_level(cases_text, delimiter=";")
        if part.strip()
    ]
    match_node = ast.Match(subject=_raw_or_nomi_expr(subject_text.strip()), cases=cases)
    func = ast.FunctionDef(
        name=None,
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=None,
        ),
        body=[match_node],
        decorator_list=[],
        returns=None,
    )
    return ast.Call(func=func, args=[], keywords=[])


def _inline_match_case_from_text(text: str) -> ast.match_case:
    case_text = text.removeprefix("case ").strip()
    head, separator, value_text = case_text.partition("=>")
    if not separator:
        raise ValueError(f"unsupported Rust inline match case: {text!r}")
    pattern, guard = _pattern_and_guard_from_case_head(head.strip())
    return ast.match_case(
        pattern=pattern,
        guard=guard,
        body=[ast.Return(value=_expr_from_python_source(value_text.strip()))],
    )


def _match_case_from_rust_payload(
    payload: dict[str, Any], *, expression_case: bool
) -> ast.match_case:
    pattern, guard = _pattern_and_guard_from_case_head(payload["head"])
    body = [_stmt_from_rust_payload(stmt) for stmt in payload["body"]]
    if expression_case:
        if len(body) != 1 or not isinstance(body[0], ast.Expr):
            raise ValueError(f"unsupported Rust match expression case body: {payload!r}")
        body = [ast.Return(value=body[0].value)]
    return ast.match_case(pattern=pattern, guard=guard, body=body)


def _pattern_and_guard_from_case_head(head: str) -> tuple[ast.pattern, ast.expr | None]:
    pattern_text, separator, guard_text = head.partition(" if ")
    pattern = _pattern_from_rust_text(pattern_text.strip())
    guard = _expr_from_python_source(guard_text.strip()) if separator else None
    return pattern, guard


def _pattern_from_rust_text(text: str) -> ast.pattern:
    if text == "_":
        return ast.MatchAs()
    if text.startswith("[") and text.endswith("]"):
        return ast.MatchSequence(
            patterns=[
                _pattern_from_rust_text(part)
                for part in _split_top_level(text[1:-1])
            ]
        )
    if text.startswith("{") and text.endswith("}"):
        keys = []
        patterns = []
        for part in _split_top_level(text[1:-1]):
            key_text, separator, pattern_text = part.partition(":")
            if not separator:
                raise ValueError(f"unsupported Rust mapping pattern: {text!r}")
            keys.append(_expr_from_python_source(key_text.strip()))
            patterns.append(_pattern_from_rust_text(pattern_text.strip()))
        return ast.MatchMapping(keys=keys, patterns=patterns)
    if text.startswith("*"):
        return ast.MatchStar(name=text.removeprefix("*").strip())
    if text.isidentifier():
        return ast.MatchAs(name=text)
    return ast.MatchValue(value=_expr_from_python_source(text))


def _split_pattern_subject(head: str) -> tuple[str, str | None]:
    pattern_text, separator, subject_text = head.partition(" = ")
    if not separator:
        return head, None
    return pattern_text.strip(), subject_text.strip()


def _type_alias_from_rust_payload(payload: dict[str, Any]) -> ast.Assign:
    target = payload["target"].removeprefix("type ").strip()
    return ast.Assign(
        targets=[_name_expr(target, ast.Store())],
        value=_expr_from_rust_payload(payload["value"]),
    )


def _where_assign_suite_from_rust_payload(payload: dict[str, Any]) -> ast.Assign:
    stmt = ast.Assign(
        targets=[_name_expr(payload["target"], ast.Store())],
        value=_expr_from_rust_payload(payload["value"]),
    )
    stmt._nomi_where_body = [
        _stmt_from_rust_payload(item) for item in payload.get("body", ())
    ]
    return stmt


def _where_function_suite_from_rust_payload(payload: dict[str, Any]) -> ast.FunctionDef:
    fn = _function_equation_from_parts(
        name=payload["name"],
        eq_args=[(param, None) for param in payload["params"]],
        body=_expr_from_rust_payload(payload["value"]),
    )
    fn._nomi_where_body = [
        _stmt_from_rust_payload(item) for item in payload.get("body", ())
    ]
    return fn


def _function_signature_from_text(head: str) -> ast.FunctionDef:
    try:
        parsed = ast.parse(f"def {head}: pass").body[0]
        if isinstance(parsed, ast.FunctionDef):
            return parsed
    except SyntaxError:
        pass
    name, _, rest = head.partition("(")
    if not rest.endswith(")"):
        raise ValueError(f"unsupported Rust function head: {head!r}")
    args, defaults = _arguments_from_rust_params(rest[:-1])
    return ast.FunctionDef(
        name=name.strip(),
        args=ast.arguments(args=args, defaults=defaults),
        body=[ast.Pass()],
    )


def _arguments_from_rust_params(params_text: str) -> tuple[list[ast.arg], list[ast.expr]]:
    args: list[ast.arg] = []
    defaults_by_index: dict[int, ast.expr] = {}
    for index, param_text in enumerate(_split_top_level(params_text)):
        param_text = param_text.strip()
        if not param_text:
            continue
        before_default, has_default, default_text = _partition_default(param_text)
        before_annotation, has_annotation, annotation_text = before_default.partition(":")
        annotation = (
            _annotation_from_rust_text(annotation_text.strip()) if has_annotation else None
        )
        args.append(ast.arg(arg=before_annotation.strip(), annotation=annotation))
        if has_default:
            defaults_by_index[index] = _expr_from_python_source(default_text.strip())
    defaults = [
        defaults_by_index[index]
        for index in range(len(args) - len(defaults_by_index), len(args))
        if index in defaults_by_index
    ]
    return args, defaults


def _partition_default(text: str) -> tuple[str, str, str]:
    depth = 0
    quote: str | None = None
    escaped = False
    for index, ch in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in {"'", '"'}:
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif (
            ch == "="
            and depth == 0
            and text[index - 1 : index] not in {"<", ">", "!", "="}
            and text[index + 1 : index + 2] != "="
        ):
            return text[:index], ch, text[index + 1 :]
    return text, "", ""


def _annotation_from_rust_text(text: str) -> ast.expr:
    text = _strip_wrapping_parens(text.strip())
    parts = _split_top_level(text)
    if len(parts) == 1 and " else " not in parts[0]:
        return _expr_from_python_source(parts[0].strip())
    return ast.Tuple(
        elts=[_constraint_part_from_rust_text(part.strip()) for part in parts],
        ctx=ast.Load(),
    )


def _constraint_part_from_rust_text(text: str) -> ast.expr:
    expr_text, separator, message_text = text.partition(" else ")
    if not separator:
        return _expr_from_python_source(text)
    return ast.Call(
        func=ast.Name(id="__constraint_message__", ctx=ast.Load()),
        args=[
            _expr_from_python_source(expr_text.strip()),
            _expr_from_python_source(message_text.strip()),
        ],
    )


def _strip_wrapping_parens(text: str) -> str:
    if not (text.startswith("(") and text.endswith(")")):
        return text
    inner = text[1:-1].strip()
    if _split_top_level(inner):
        return inner
    return text


def _split_top_level(text: str, delimiter: str = ",") -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, ch in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in {"'", '"'}:
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == delimiter and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def _split_top_level_token(text: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    start = 0
    index = 0
    depth = 0
    quote: str | None = None
    escaped = False
    while index < len(text):
        ch = text[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            index += 1
            continue
        if ch in {"'", '"'}:
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0 and text.startswith(delimiter, index):
            parts.append(text[start:index].strip())
            index += len(delimiter)
            start = index
            continue
        index += 1
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def _function_from_rust_payload(payload: dict[str, Any]) -> ast.FunctionDef:
    return ast.FunctionDef(
        name=payload["name"],
        args=ast.arguments(
            args=[ast.arg(arg=param) for param in payload["params"]],
        ),
        body=[ast.Return(value=_expr_from_rust_payload(payload["body"]))],
    )


def _compare_from_rust_payload(payload: dict[str, Any]) -> ast.Compare:
    left = _expr_from_rust_payload(payload["left"])
    ops = [_cmp_operator_from_rust_payload(payload["op"])]
    comparators = [_expr_from_rust_payload(payload["right"])]
    if isinstance(left, ast.Compare):
        return ast.Compare(
            left=left.left,
            ops=[*left.ops, *ops],
            comparators=[*left.comparators, *comparators],
        )
    return ast.Compare(left=left, ops=ops, comparators=comparators)


def _bool_op_from_rust_payload(payload: dict[str, Any]) -> ast.BoolOp:
    op = _bool_operator_from_rust_payload(payload["op"])
    values = [
        _expr_from_rust_payload(payload["left"]),
        _expr_from_rust_payload(payload["right"]),
    ]
    if isinstance(values[0], ast.BoolOp) and type(values[0].op) is type(op):
        values = [*values[0].values, values[1]]
    return ast.BoolOp(op=op, values=values)


def _string_expr_from_rust_payload(payload: dict[str, Any]) -> ast.expr:
    source = payload.get("source")
    if source:
        return _expr_from_python_source(source)
    return ast.Constant(value=payload["value"])


def _name_expr(name: str, ctx: ast.expr_context) -> ast.Name:
    return ast.Name(id=_name_id_from_rust_text(name), ctx=ctx)


def _name_id_from_rust_text(name: str) -> str | Token:
    if name == "data":
        return Token("DATA", "data")
    return name


def _expr_from_python_source(source: str) -> ast.expr:
    return ast.parse(source, mode="eval").body


def _restore_nomi_name_tokens(node: ast.expr) -> ast.expr:
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id == "data":
            child.id = Token("DATA", "data")
    return node


def _store_ctx(node: ast.expr) -> ast.expr:
    if isinstance(node, ast.Name):
        node.ctx = ast.Store()
    elif isinstance(node, (ast.Tuple, ast.List)):
        node.ctx = ast.Store()
        for item in node.elts:
            _store_ctx(item)
    return node


def _operator_from_rust_payload(name: str) -> ast.operator:
    match name:
        case "Add":
            return ast.Add()
        case "Sub":
            return ast.Sub()
        case "Mult":
            return ast.Mult()
        case "Div":
            return ast.Div()
        case "FloorDiv":
            return ast.FloorDiv()
        case "Mod":
            return ast.Mod()
        case "MatMult":
            return ast.MatMult()
        case "Pow":
            return ast.Pow()
        case "BitAnd":
            return ast.BitAnd()
        case "BitOr":
            return ast.BitOr()
        case "BitXor":
            return ast.BitXor()
        case "LShift":
            return ast.LShift()
        case "RShift":
            return ast.RShift()
        case other:
            raise ValueError(f"unsupported Rust AST operator: {other!r}")


def _aug_operator_from_rust_payload(name: str) -> ast.operator:
    match name:
        case "+=":
            return ast.Add()
        case "-=":
            return ast.Sub()
        case "*=":
            return ast.Mult()
        case "/=":
            return ast.Div()
        case other:
            raise ValueError(f"unsupported Rust AST augmented operator: {other!r}")


def _cmp_operator_from_rust_payload(name: str) -> ast.cmpop:
    match name:
        case "Lt":
            return ast.Lt()
        case "LtE":
            return ast.LtE()
        case "Gt":
            return ast.Gt()
        case "GtE":
            return ast.GtE()
        case "Eq":
            return ast.Eq()
        case "NotEq":
            return ast.NotEq()
        case other:
            raise ValueError(f"unsupported Rust AST comparison operator: {other!r}")


def _bool_operator_from_rust_payload(name: str) -> ast.boolop:
    match name:
        case "And":
            return ast.And()
        case "Or":
            return ast.Or()
        case other:
            raise ValueError(f"unsupported Rust AST boolean operator: {other!r}")


def _unary_operator_from_rust_payload(name: str) -> ast.unaryop:
    match name:
        case "UAdd":
            return ast.UAdd()
        case "USub":
            return ast.USub()
        case "Not":
            return ast.Not()
        case "Invert":
            return ast.Invert()
        case other:
            raise ValueError(f"unsupported Rust AST unary operator: {other!r}")


def _number_value_from_text(value: str) -> int | float:
    normalized = value.replace("_", "")
    if "." in normalized:
        return float(normalized)
    return int(normalized)


def _constant_value_from_text(value: str) -> object:
    match value:
        case "None":
            return None
        case "True":
            return True
        case "False":
            return False
        case other:
            raise ValueError(f"unsupported Rust AST constant: {other!r}")
