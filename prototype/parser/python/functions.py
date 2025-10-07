import ast
from typing import List, Optional, Tuple
from lark import Tree, Token
from prototype.parser.python.utils import ensure_expr, ensure_arg, ensure_name


class FunctionDefMixin:
    """
    Unified mixin for both function definitions and lambdas.
    Converts Lark Trees into Python ast.FunctionDef or ast.Lambda.

    Reuses the same _build_arguments() logic for both.
    """

    # ---------- shared helpers ----------
    def _name_to_arg(self, name: str) -> ast.arg:
        return ast.arg(arg=str(name), annotation=None)

    def _paramvalue_to_pair(self, item):
        """
        Normalize a parameter value node to (ast.arg, default_expr_or_None).
        Supports:
        - (name, default)
        - name
        - Token('NAME', ...)
        - ast.arg
        - Skip constants or unexpected expressions (e.g., stray default)
        """
        from lark import Token

        if item is None:
            return None, None

        # Handle (name, default) tuple from paramvalue
        if isinstance(item, tuple) and len(item) == 2:
            name, default_tree = item
            if name is None:
                return None, None
            arg = ensure_arg(name)
            default_expr = ensure_expr(default_tree) if default_tree is not None else None
            return arg, default_expr

        # Just a name or Token
        if isinstance(item, (str, Token)):
            return ensure_arg(item), None

        # Already an ast.arg
        if isinstance(item, ast.arg):
            return item, None

        # Skip unexpected expressions
        if isinstance(item, ast.expr):
            return None, None

        raise ValueError(f"Unsupported parameter value shape: {item!r}")

    def _build_arguments(self, items):
        """
        Convert flattened parameter-like items into ast.arguments.
        Works for both normal functions and lambdas.
        """
        if not items:
            return ast.arguments(
                posonlyargs=[], args=[], vararg=None,
                kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
            )

        posonlyargs = []
        args = []
        vararg = None
        kwonlyargs = []
        kw_defaults = []
        kwarg = None
        defaults_for_args = []
        seen_slash = False
        seen_star = False
        current_list = posonlyargs

        def _flatten(xs):
            out = []
            for x in xs:
                if x is None:
                    continue
                if isinstance(x, (list, tuple)) and not (len(x) == 2 and isinstance(x[0], (str, ast.arg))):
                    out.extend(_flatten(x))
                else:
                    out.append(x)
            return out

        flat = _flatten(items)

        for it in flat:
            # Handle bare tokens
            if isinstance(it, Token):
                if it.type == "SLASH":
                    seen_slash = True
                    current_list = args
                    continue
                if it.type == "STAR":
                    seen_star = True
                    current_list = kwonlyargs
                    continue

            # *args
            if isinstance(it, tuple) and it and it[0] == "vararg":
                vararg = ensure_arg(it[1])
                seen_star = True
                current_list = kwonlyargs
                continue

            # **kwargs
            if isinstance(it, tuple) and it and it[0] == "kwarg":
                kwarg = ensure_arg(it[1])
                continue

            # lambda_starparams dict form
            if isinstance(it, dict) and "star_name" in it:
                seen_star = True
                if it["star_name"]:
                    vararg = self._name_to_arg(it["star_name"])
                for pv in it.get("after_params", []):
                    arg_obj, default_expr = self._paramvalue_to_pair(pv)
                    if arg_obj:
                        kwonlyargs.append(arg_obj)
                        if default_expr is not None:
                            kw_defaults.append(default_expr)
                if it.get("kwparams"):
                    kwarg = self._name_to_arg(it["kwparams"])
                continue

            # Normal parameter
            arg_obj, default_expr = self._paramvalue_to_pair(it)
            if not arg_obj:
                continue

            current_list.append(arg_obj)
            if seen_star:
                if default_expr is not None:
                    kw_defaults.append(default_expr)
            else:
                if default_expr is not None:
                    defaults_for_args.append(default_expr)

        # Combine posonlyargs and args if no slash
        if not seen_slash:
            args = posonlyargs + args
            posonlyargs = []

        return ast.arguments(
            posonlyargs=posonlyargs,
            args=args,
            vararg=vararg,
            kwonlyargs=kwonlyargs,
            kw_defaults=kw_defaults,
            kwarg=kwarg,
            defaults=defaults_for_args
        )
   
    def typedparam(self, items):
        """
        Process a typed parameter, e.g., 'y: int' or 'y: int = 5'.
        Returns: ast.arg with optional annotation and default passed to _build_arguments.
        """
        name = items[0]
        annotation = items[1] if len(items) > 1 else None
        default = items[2] if len(items) > 2 else None
        arg = ast.arg(arg=ensure_name(name), annotation=ensure_expr(annotation) if annotation else None)
        if default is not None:
            return (arg, default)
        return arg

    def paramvalue(self, items):
        """
        Process a parameter, e.g., 'x' or 'y=5'.
        Returns: name (for no default) or (name, default) tuple.
        """
        if len(items) == 2:
            return (items[0], items[1])  # e.g., (y, 5)
        return items[0]  # e.g., x


    def starparam(self, items):
        return ("vararg", ensure_arg(items[0]))

    def starguard(self, _):
        return ("star", None)

    def kwparams(self, items):
        return ("kwarg", ensure_arg(items[0]))

    def parameters(self, items):
        return self._build_arguments(items)
    
    def decorator(self, items):
        """
        items[0] = decorator name (str, Token, or Tree)
        items[1] = optional arguments (tuple of (args, keywords)) or None
        """
        # Handle decorator name, which could be a string, Token, or Tree
        decorator_name = items[0]
        if isinstance(decorator_name, str):
            # Clean malformed strings like "['cache']", "['property']", or "'cache'"
            cleaned_name = decorator_name
            # Remove list-like syntax, e.g., "['cache']" -> "cache"
            if cleaned_name.startswith("[") and cleaned_name.endswith("]"):
                cleaned_name = cleaned_name[1:-1]
            # Strip quotes and whitespace, e.g., "'cache'" -> "cache"
            cleaned_name = cleaned_name.strip("'\" ").strip()
            name_expr = ensure_name(cleaned_name)
        elif isinstance(decorator_name, Tree) and decorator_name.data in ("decorator", "dotted_name"):
            # Handle Tree, e.g., Tree(decorator, [Token(NAME, 'cache')])
            name = decorator_name.children[0].value if decorator_name.children else ""
            name_expr = ensure_name(name)
        elif isinstance(decorator_name, Token):
            name_expr = ensure_name(decorator_name.value)
        else:
            raise ValueError(f"Unsupported decorator name type: {type(decorator_name)}")

        if len(items) > 1 and items[1]:
            # decorator with arguments
            args, keywords = items[1]
            return ast.Call(func=ast.Name(id=name_expr, ctx=ast.Load()), args=args, keywords=keywords)

        # decorator without arguments → just a Name
        return ast.Name(id=name_expr, ctx=ast.Load())

    def decorators(self, items):
        """
        Flatten and validate decorator items.
        """
        out = []
        for it in items:
            if isinstance(it, list):
                out.extend(self.decorators(it))  # Recursively flatten nested lists
            elif isinstance(it, (ast.expr, ast.Name, ast.Call)):
                out.append(it)
            else:
                raise ValueError(f"Invalid decorator type: {type(it)}")
        return out

    def decorated(self, items):
        # items[0] = decorators, items[1] = funcdef/classdef/async_funcdef
        decorator_nodes = items[0]
        target_node = items[1]

        if not hasattr(target_node, 'decorator_list'):
            raise TypeError(f"Target does not accept decorators: {type(target_node)}")

        target_node.decorator_list = decorator_nodes
        return target_node

    def funcdef(self, items):
        """
        items may include:
            - decorators (optional)
            - function name (Token or str)
            - arguments (ast.arguments)
            - return annotation (ast.expr, optional)
            - body (list of ast.stmt)
        """
        name = None
        args_node = None
        returns = None
        body = None
        decorator_list = []

        for it in items:
            if isinstance(it, Token) and it.type == "NAME":
                name = it.value
            elif isinstance(it, ast.arguments):
                args_node = it
            elif isinstance(it, list):
                # Might be body or decorators — detect via contents
                if it and all(isinstance(d, ast.expr) for d in it):
                    decorator_list = it
                else:
                    body = it
            elif isinstance(it, ast.expr):
                returns = it
            elif isinstance(it, str) and name is None:
                name = it

        args_node = args_node or self._build_arguments([])
        body = body or []

        return ast.FunctionDef(
            name=name,
            args=args_node,
            body=body,
            decorator_list=decorator_list,
            returns=returns,
            type_comment=None
        )

    def return_stmt(self, items):
        """
        items: list of expressions after 'return', or empty if just 'return'
        returns: ast.Return node
        """
        if not isinstance(items, list):
            raise TypeError(f"Expected list of expressions, got {type(items)}")
        
        if not items:
            # plain 'return' with no value
            return ast.Return(value=None)
        elif len(items) == 1:
            # single expression
            return ast.Return(value=ensure_expr(items[0]))
        else:
            # multiple expressions -> tuple
            exprs = [ensure_expr(item) for item in items]
            return ast.Return(value=ast.Tuple(elts=exprs, ctx=ast.Load()))


class LambdaMixin(FunctionDefMixin):
    '''
    NOTE: TODO:
    Why do lambdas and regular function parameter have different processing?
        - why is there difference in grammar ? (only the parameter part)
    '''
    def lambda_paramvalue(self, items):
        """
        Handle lambda parameters with optional defaults.
        E.g., 'b=1' → (name, default_expr)
        """
        if len(items) == 1:
            return (items[0], None)
        name, default_tree = items
        return (name, default_tree)
    
    def lambda_starparams(self, items):
        """
        Handle *args and **kwargs in lambda.
        Returns a dict for _build_arguments to process, ensuring **kwargs is only in kwparams.
        """
        star_name = None
        after_params = []
        kwparams = None
        star_name, *after_params, kwparams = items
        return {"star_name": star_name, "after_params": after_params, "kwparams": kwparams}


    def lambdef(self, items):
        """
        Handle lambda definition: lambda params: expr
        """
        if len(items) == 1:
            params_node = None
            test_node = items[0]
        else:
            params_node, test_node = items
        body = ensure_expr(test_node)
        args = self._build_arguments(params_node)
        return ast.Lambda(args=args, body=body)


class CallMixin:
    def argvalue(self, items):
        """
        Transform an argvalue node:
        - single item → positional argument (ast.expr)
        - two items → keyword argument (return (name, value))
        """
        if len(items) == 2:
            key = ensure_name(items[0])
            value = ensure_expr(items[1])
            return (key, value)
        return ensure_expr(items[0])

    def stararg(self, items):
        return ast.Starred(value=ensure_expr(items[0]), ctx=ast.Load())
    
    def starargs(self, items):
        out = []
        for it in items:
            if isinstance(it, list):
                out.extend(it)
            else:
                out.append(it)
        return out

    def kwargs(self, items):
        """
        Handle **kwargs possibly followed by key=value pairs (PEP 448)
        Example: **opts, scale=2
        """
        # first item is **expr
        base = ensure_expr(items[0])
        kw_nodes = [ast.keyword(arg=None, value=base)]

        # remaining items, if any, are argvalue nodes (key=value)
        for el in items[1:]:
            if isinstance(el, tuple) and len(el) == 2:
                key, val = el
                kw_nodes.append(ast.keyword(arg=str(key), value=ensure_expr(val)))
            else:
                raise SyntaxError(f"Unexpected item in kwargs: {el!r}")

        return kw_nodes

    def arguments(self, items):
        args, keywords = [], []

        def _flatten(xs):
            out = []
            for x in xs:
                if x is None:
                    continue
                if isinstance(x, list):
                    out.extend(_flatten(x))
                else:
                    out.append(x)
            return out

        flat = _flatten(items)

        for el in flat:
            if isinstance(el, tuple) and len(el) == 2:
                key, val = el
                keywords.append(ast.keyword(arg=str(key), value=ensure_expr(val)))
            elif isinstance(el, ast.Starred):
                args.append(el)
            elif isinstance(el, ast.keyword) and el.arg is None:
                keywords.append(el)
            elif isinstance(el, ast.keyword):
                keywords.append(el)
            else:
                args.append(ensure_expr(el))

        return args, keywords

    def funccall(self, items):
        """
        Build ast.Call from func and optional arguments.
        """
        func = items[0]
        args, keywords = ([], [])
        if len(items) > 1 and items[1]:
            args, keywords = items[1]
        return ast.Call(func=func, args=args, keywords=keywords)

class FunctionMixin(CallMixin, LambdaMixin):
    pass