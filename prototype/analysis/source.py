"""Conservative scalar facts over a replaceable Python-AST input adapter.

This is not a general typechecker. Facts describe normal completion at their
source position. Purity concerns observable effects, not termination or panic.
Unknown operations invalidate environmental knowledge because host calls and
overloads can mutate globals, function objects, and the prelude. No source
operation or imported dependency is executed to discover facts.
"""

import ast
import hashlib
from dataclasses import dataclass, field

from .model import AnalysisPolicy, AnalysisResult, RESTRICTIONS


SCALAR_TYPES = {int: "Int", float: "Float", bool: "Bool", str: "Text",
                type(None): "None"}
ANNOTATIONS = {"int": "Int", "Int": "Int", "float": "Float", "Float": "Float",
               "bool": "Bool", "Bool": "Bool", "str": "Text", "Text": "Text"}
NUMERIC = {"Int", "Float"}
MAX_STEPS = 4096
MAX_CALL_DEPTH = 16
MAX_EXPRESSION_DEPTH = 96
MAX_INPUT_NODES = 20000


@dataclass(frozen=True)
class _Value:
    type: str | None = None
    function: ast.FunctionDef | None = None
    builtin: str | None = None


UNKNOWN = _Value()
NONE = _Value("None")


@dataclass
class _Frame:
    values: dict[str, _Value] = field(default_factory=dict)
    local_names: set[str] = field(default_factory=set)
    context: str = "module"


class _LimitReached(Exception):
    pass


class _Analyzer:
    def __init__(self, source, filename, frontend, policy):
        self.source = source
        self.filename = filename
        self.frontend = frontend
        self.policy = policy
        self.facts = []
        self.obligations = []
        self.effects = set()
        self.latent = []
        self.module = _Frame()
        self.frames = [self.module]
        self.calls = []
        self.steps = 0
        self.epoch = 0
        self.pristine_prelude = True
        self.current = None

    def span(self, node):
        if self.frontend not in ("python-ast", "cpython-ast"):
            return None
        lines = self.source.splitlines()

        def position(line, offset):
            if type(line) is not int or not 1 <= line <= len(lines) or type(offset) is not int:
                return None
            prefix = lines[line - 1].encode("utf-8")[:offset]
            try:
                return len(prefix.decode("utf-8")) + 1
            except UnicodeDecodeError:
                return None

        line = getattr(node, "lineno", None)
        column = position(line, getattr(node, "col_offset", None))
        if column is None:
            return None
        end_line = getattr(node, "end_lineno", None)
        return {"filename": self.filename, "line": line, "column": column,
                "end_line": end_line,
                "end_column": position(end_line, getattr(node, "end_col_offset", None)),
                "coordinate_unit": "unicode-code-point"}

    def obligation(self, code, message, node, blocks=RESTRICTIONS, repair=None):
        self.obligations.append({
            "code": code, "message": message, "span": self.span(node),
            "blocks": list(blocks), "context": self.frames[-1].context,
            "repair": repair or "Keep this operation outside the checked scalar slice, "
                                   "or add independently verified analysis support.",
        })

    def invalidate(self):
        self.epoch += 1
        self.pristine_prelude = False
        for frame in self.frames:
            frame.values = {name: UNKNOWN for name in frame.values}

    def unknown(self, code, message, node, *, invalidates=True):
        self.obligation(code, message, node)
        if invalidates:
            self.invalidate()
        return UNKNOWN

    def tick(self, node, depth=0):
        self.current = node
        self.steps += 1
        if self.steps > MAX_STEPS or depth > MAX_EXPRESSION_DEPTH:
            raise _LimitReached

    @staticmethod
    def metadata(node):
        return any(name.startswith("_nomi_") for name in vars(node))

    def fact(self, node, value, *, name, kind="binding", provenance="scalar-flow", **extra):
        self.facts.append({"kind": kind, "name": name, "type": value.type,
                           "span": self.span(node), "scope": self.frames[-1].context,
                           "provenance": provenance, **extra})

    def lookup(self, node, frame):
        name = node.id
        if name in frame.values:
            value = frame.values[name]
            if value.type is None:
                self.obligation("binding-unproved", f"The current value of {name!r} is unknown.",
                                node, ("known-types",))
            return value
        if frame is not self.module:
            if name in frame.local_names:
                self.obligation("unbound-local", f"Local {name!r} is read before its binding.",
                                node, ("known-types",))
                return UNKNOWN
            global_value = self.module.values.get(name)
            if global_value is not None:
                if global_value.function is not None:
                    return global_value
                return self.unknown("capture-unproved",
                                    f"Captured binding {name!r} is outside this analysis slice.", node)
        if name == "print" and self.pristine_prelude:
            return _Value("Function", builtin="print")
        self.obligation("name-unproved", f"No checked binding is available for {name!r}.",
                        node, ("known-types",))
        return UNKNOWN

    def annotation(self, node, value):
        if node is None:
            return
        self.obligation("annotation-unverified",
                        "A declaration is not inferred evidence; annotation/constraint "
                        "evaluation is outside this slice.", node)
        if isinstance(node, ast.Name):
            expected = ANNOTATIONS.get(node.id)
            if expected and value.type and expected != value.type:
                self.obligation("annotation-mismatch",
                                f"Declared {expected}, but this expression has type {value.type}.",
                                node, ("known-types",),
                                "Correct the declaration or the expression; do not treat "
                                "an annotation as a coercion.")
        self.invalidate()

    def statements(self, statements, frame):
        for node in statements:
            self.tick(node)
            if self.metadata(node):
                self.unknown("unsupported-metadata", "Source extension metadata needs its own "
                             "analysis contract.", node)
                continue
            if type(node) is ast.Assign:
                value = self.expression(node.value, frame)
                if all(type(target) is ast.Name for target in node.targets):
                    for target in node.targets:
                        frame.values[target.id] = value
                        self.fact(target, value, name=target.id)
                else:
                    self.unknown("assignment-unproved", "Only simple name bindings are checked.", node)
            elif type(node) is ast.AnnAssign:
                value = self.expression(node.value, frame) if node.value else UNKNOWN
                self.annotation(node.annotation, value)
                if type(node.target) is ast.Name:
                    # Constraint evaluation can change a binding; retain expression evidence only.
                    frame.values[node.target.id] = UNKNOWN
                    self.fact(node.target, value, name=node.target.id,
                              provenance="annotated-initializer",
                              current_binding_proved=False)
                else:
                    self.unknown("assignment-unproved", "Only simple name bindings are checked.", node)
            elif type(node) is ast.Expr:
                self.expression(node.value, frame)
            elif type(node) is ast.FunctionDef:
                self.function_definition(node, frame)
            elif type(node) is ast.Return and frame is not self.module:
                return self.expression(node.value, frame) if node.value else NONE
            elif type(node) is ast.Pass:
                continue
            elif type(node) in (ast.Import, ast.ImportFrom):
                self.unknown("import-unproved", "Imports can execute dependency code; no "
                             "dependency contract is available.", node)
                for alias in node.names:
                    if alias.name != "*":
                        frame.values[alias.asname or alias.name.split(".")[0]] = UNKNOWN
            else:
                self.unknown("statement-unproved", f"{type(node).__name__} is outside the "
                             "straight-line statement slice.", node)
        return NONE

    def function_definition(self, node, frame):
        if frame is not self.module:
            self.unknown("closure-unproved", "Nested function capture is not checked.", node)
            frame.values[node.name] = UNKNOWN
            return
        potential = sorted({"ConsoleWrite" for item in ast.walk(node)
                            if isinstance(item, ast.Call) and isinstance(item.func, ast.Name)
                            and item.func.id == "print"})
        self.latent.append({"name": node.name, "span": self.span(node),
                            "status": "latent-unchecked", "potential_effects": potential,
                            "public_contract": "unproved"})
        args = node.args
        annotated = [arg.annotation for arg in self.parameters(args)
                     if getattr(arg, "annotation", None) is not None]
        for name in ("vararg", "kwarg"):
            parameter = getattr(args, name, None)
            if parameter is not None and getattr(parameter, "annotation", None):
                annotated.append(parameter.annotation)
        if getattr(node, "returns", None):
            annotated.append(node.returns)
        unsupported = (getattr(node, "decorator_list", []) or getattr(args, "defaults", [])
                       or any(getattr(args, "kw_defaults", []))
                       or getattr(node, "type_params", []))
        if unsupported:
            self.unknown("function-definition-unproved", "Defaults, decorators and generic "
                         "parameters need a definition-time analysis contract.", node)
            value = UNKNOWN
        else:
            value = _Value("Function", function=node)
        for annotation in annotated:
            self.annotation(annotation, UNKNOWN)
            value = UNKNOWN
        frame.values[node.name] = value
        self.fact(node, value, name=node.name, provenance="function-definition",
                  public_contract="unproved")

    def expression(self, node, frame, depth=0):
        self.tick(node, depth)
        if self.metadata(node):
            return self.unknown("unsupported-metadata", "Source extension metadata needs its "
                                "own analysis contract.", node)
        if type(node) is ast.Constant:
            scalar = SCALAR_TYPES.get(type(node.value))
            if scalar is not None:
                return _Value(scalar)
            return self.unknown("literal-unproved", "This literal is outside the scalar slice.",
                                node, invalidates=False)
        if type(node) is ast.Name:
            return self.lookup(node, frame)
        if type(node) is ast.BinOp:
            left = self.expression(node.left, frame, depth + 1)
            right = self.expression(node.right, frame, depth + 1)
            result = self.binary_type(type(node.op), left.type, right.type)
            if result:
                return _Value(result)
            return self.unknown("operator-unproved", "This operator/operand combination "
                                "has no checked primitive contract; overloads may have effects.", node)
        if type(node) is ast.UnaryOp:
            value = self.expression(node.operand, frame, depth + 1)
            if type(node.op) in (ast.UAdd, ast.USub) and value.type in NUMERIC:
                return value
            if type(node.op) is ast.Invert and value.type == "Int":
                return value
            if type(node.op) is ast.Not and value.type in SCALAR_TYPES.values():
                return _Value("Bool")
            return self.unknown("operator-unproved", "Unary dispatch/truth testing is unproved.", node)
        if type(node) is ast.Compare and len(node.ops) == 1:
            left = self.expression(node.left, frame, depth + 1)
            right = self.expression(node.comparators[0], frame, depth + 1)
            both_scalar = left.type in SCALAR_TYPES.values() and right.type in SCALAR_TYPES.values()
            equality = type(node.ops[0]) in (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)
            ordered = (type(node.ops[0]) in (ast.Lt, ast.LtE, ast.Gt, ast.GtE)
                       and ((left.type in NUMERIC and right.type in NUMERIC)
                            or left.type == right.type == "Text"))
            if both_scalar and (equality or ordered):
                return _Value("Bool")
            return self.unknown("operator-unproved", "Comparison dispatch is unproved.", node)
        if type(node) is ast.Call:
            return self.call(node, frame, depth)
        return self.unknown("expression-unproved", f"{type(node).__name__} is outside the "
                            "scalar expression slice.", node)

    @staticmethod
    def parameters(args):
        return (getattr(args, "posonlyargs", []) + getattr(args, "args", [])
                + getattr(args, "kwonlyargs", []))

    @staticmethod
    def binary_type(operator, left, right):
        if left in NUMERIC and right in NUMERIC:
            if operator is ast.Div:
                return "Float"
            if operator in (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod):
                return "Float" if "Float" in (left, right) else "Int"
            if left == right == "Int" and operator in (ast.BitAnd, ast.BitOr, ast.BitXor,
                                                        ast.LShift, ast.RShift):
                return "Int"
        if operator is ast.Add and left == right == "Text":
            return "Text"
        if operator is ast.Mult and {left, right} == {"Text", "Int"}:
            return "Text"
        return None

    def call(self, node, frame, depth):
        callee = self.expression(node.func, frame, depth + 1)
        epoch = self.epoch
        positional = [self.expression(arg, frame, depth + 1) for arg in node.args]
        keywords = [(kw.arg, self.expression(kw.value, frame, depth + 1)) for kw in node.keywords]
        if epoch != self.epoch:
            return self.unknown("callee-invalidated", "Argument evaluation can change the "
                                "callee; its earlier binding is no longer evidence.", node)
        if type(node.func) is not ast.Name or any(isinstance(arg, ast.Starred) for arg in node.args):
            return self.unknown("call-unproved", "Only ordinary direct calls are checked.", node)
        if callee.builtin == "print":
            if keywords or any(value.type not in SCALAR_TYPES.values() for value in positional):
                return self.unknown("print-unproved", "Only print of checked scalars without "
                                    "keyword arguments has a known host contract.", node)
            self.effects.add("ConsoleWrite")
            self.obligation("observable-effect", "Printing contributes ConsoleWrite.", node,
                            ("pure",), "Keep output outside the pure computation, or omit "
                            "the pure restriction when output is intentional.")
            self.fact(node, NONE, kind="call", name=node.func.id, provenance="prelude-contract")
            return NONE
        if callee.function is None:
            return self.unknown("call-unproved", "The call has no checked function body or "
                                "host contract; its result and effects remain unknown.", node)
        function = callee.function
        if any(function is active for active in self.calls):
            return self.unknown("recursion-unproved", "Recursive call contracts are not inferred.", node)
        if len(self.calls) >= MAX_CALL_DEPTH:
            self.current = node
            raise _LimitReached
        if any(isinstance(item, (ast.Yield, ast.YieldFrom, ast.Await))
               for statement in function.body for item in ast.walk(statement)):
            return self.unknown("function-convention-unproved", "Generator/suspending function "
                                "construction and latent execution need separate contracts.", node)
        if any(type(statement) not in (ast.Assign, ast.AnnAssign, ast.Expr, ast.Return, ast.Pass)
               or self.metadata(statement) for statement in function.body):
            return self.unknown("function-body-unproved", "This function contains unsupported "
                                "control, declarations or scope changes; no return contract "
                                "can be inferred from its final statement.", node)
        args = function.args
        if (getattr(args, "vararg", None) or getattr(args, "kwarg", None)
                or getattr(args, "defaults", []) or any(getattr(args, "kw_defaults", []))):
            return self.unknown("arguments-unproved", "Variadic/default argument binding is "
                                "outside this slice.", node)
        parameters = getattr(args, "posonlyargs", []) + getattr(args, "args", [])
        kwonlyargs = getattr(args, "kwonlyargs", [])
        if len(positional) > len(parameters):
            return self.unknown("argument-mismatch", "Too many positional arguments.", node,
                                invalidates=False)
        bound = {arg.arg: value for arg, value in zip(parameters, positional)}
        keyword_names = {arg.arg for arg in getattr(args, "args", []) + kwonlyargs}
        for name, value in keywords:
            if name is None or name not in keyword_names or name in bound:
                return self.unknown("argument-mismatch", "Unknown, duplicated, unpacked or "
                                    "positional-only keyword argument.", node, invalidates=False)
            bound[name] = value
        required = {arg.arg for arg in parameters + kwonlyargs}
        if bound.keys() != required:
            return self.unknown("argument-mismatch", "Required arguments are missing.", node,
                                invalidates=False)
        if any(value.type not in SCALAR_TYPES.values() for value in bound.values()):
            return self.unknown("arguments-unproved", "Direct calls need checked scalar arguments.", node)
        locals_ = {item.id for statement in function.body for item in ast.walk(statement)
                   if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Store)}
        locals_.update(item.name for statement in function.body for item in ast.walk(statement)
                       if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
        child = _Frame(dict(bound), locals_ | required,
                       f"call:{function.name}@{getattr(node, 'lineno', 1)}")
        self.frames.append(child)
        self.calls.append(function)
        try:
            value = self.statements(function.body, child)
        finally:
            self.calls.pop()
            self.frames.pop()
        self.fact(node, value, kind="call", name=node.func.id,
                  provenance="direct-call-context", argument_types={k: v.type for k, v in bound.items()},
                  public_contract="unproved")
        return value

    def run(self, tree):
        try:
            count = 0
            pending = [tree]
            while pending:
                node = pending.pop()
                count += 1
                if count > MAX_INPUT_NODES:
                    self.current = tree
                    raise _LimitReached
                pending.extend(ast.iter_child_nodes(node))
            self.statements(getattr(tree, "body", []), self.module)
        except _LimitReached:
            self.obligation("analysis-limit", "The bounded analysis work/depth limit was reached; "
                            "remaining source is unproved.", self.current,
                            repair="Split this calculation into smaller checked units, or add "
                            "a verified summary mechanism before increasing analysis scope.")
        restrictions = tuple({
            "name": name, "satisfied": not any(name in item["blocks"] for item in self.obligations),
            "blocking_obligations": [index for index, item in enumerate(self.obligations)
                                     if name in item["blocks"]],
        } for name in self.policy.requirements)
        return AnalysisResult(
            version=1,
            source={"filename": self.filename, "sha256": hashlib.sha256(self.source.encode()).hexdigest(),
                    "frontend": self.frontend},
            analyzer={"name": "nomi-scalar-source", "version": 1},
            scope="module-execution", facts=tuple(self.facts), obligations=tuple(self.obligations),
            effects=tuple(sorted(self.effects)), latent_functions=tuple(self.latent),
            restrictions=restrictions,
            assumptions=(
                "Fresh module with the standard scalar/print prelude; no injected host bindings.",
                "Facts concern normal completion at the stated source position, not termination or panic.",
                "Function call contexts do not establish exported or polymorphic contracts.",
                "The caller supplies the frontend AST corresponding to the source digest.",
            ),
        )


def analyze_ast(tree, *, source, filename="<input>", frontend="python-ast", policy=AnalysisPolicy()):
    """Inspect a parsed module without executing source or loading dependencies.

    Frontend identity is provenance, not a semantics switch. Unsupported syntax
    or extension metadata produces obligations. The adapter must pass its raw
    source AST rather than an optimization that erased source operations.
    """
    if type(tree) is not ast.Module:
        raise TypeError("source analysis requires an ast.Module")
    if not isinstance(source, str) or not isinstance(filename, str) or not isinstance(frontend, str):
        raise TypeError("source, filename and frontend must be strings")
    if type(policy) is not AnalysisPolicy:
        raise TypeError("policy must be an AnalysisPolicy")
    return _Analyzer(source, filename, frontend, policy).run(tree)
