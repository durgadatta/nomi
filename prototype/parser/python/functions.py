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

        # Already a (name, default_expr)
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

        # Literal constant or expression — skip, likely stray default
        if isinstance(item, ast.expr):
            # Log or safely ignore
            return None, None

        raise ValueError(f"Unsupported parameter value shape: {item!r}")

    # ---------- argument normalization ----------
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
                if isinstance(x, (list, tuple)) and not (len(x) == 2 and isinstance(x[0], str)):
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
                        kw_defaults.append(default_expr)
                if it.get("kwparams"):
                    kwarg = self._name_to_arg(it["kwparams"])
                continue

            # normal parameter
            pair = self._paramvalue_to_pair(it)
            if not pair or pair[0] is None:
                continue

            arg_obj, default_expr = pair
            current_list.append(arg_obj)
            if seen_star:
                kw_defaults.append(default_expr)
            elif default_expr is not None:
                defaults_for_args.append(default_expr)

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

    # ---------- normal function rules ----------
    def typedparam(self, items):
        name = items[0]
        annotation = items[1] if len(items) > 1 else None
        return ast.arg(arg=ensure_name(name), annotation=annotation)

    def paramvalue(self, items):
        if len(items) == 2:
            return (items[0], ensure_expr(items[1]))
        return items[0]

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
        items[0] = dotted_name (str)
        items[1] = optional arguments (tuple of (args, keywords)) or None
        """
        name_expr = ensure_expr(items[0])

        if len(items) > 1 and items[1]:
            # decorator with arguments
            args, keywords = items[1]
            return ast.Call(func=name_expr, args=args, keywords=keywords)

        # decorator without arguments → just a Name
        return name_expr

    def decorators(self, items):
        # Flatten if nested
        out = []
        for it in items:
            if isinstance(it, list):
                out.extend(it)
            else:
                out.append(it)
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



class LambdaMixin(FunctionDefMixin):
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
        Returns a dict for _build_arguments to process.
        """
        star_name = None
        rest = []
        kwparams = None
        for it in items:
            if isinstance(it, str) and star_name is None:
                if it != "*":
                    star_name = it
            elif isinstance(it, Tree) and it.data == "lambda_kwparams":
                kwparams = it.children[0] if it.children else None
            else:
                rest.append(it)
        return {"star_name": star_name, "after_params": rest, "kwparams": kwparams}

    def lambda_kwparams(self, items):
        """
        Handle **kwargs in lambda.
        """
        if not items:
            raise ValueError("lambda_kwparams: expected name after **")
        return items[0]

    def lambda_params(self, items):
        """
        Pass parameters to _build_arguments.
        """
        return items

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
        return ast.fix_missing_locations(ast.Lambda(args=args, body=body))

    def lambdef_nocond(self, items):
        """
        Handle lambda definition without condition (same as lambdef for now).
        """
        if len(items) == 1:
            params_node = None
            test_node = items[0]
        else:
            params_node, test_node = items
        body = ensure_expr(test_node)
        args = self._build_arguments(params_node)
        return ast.fix_missing_locations(ast.Lambda(args=args, body=body))
# ---------- Calls ----------
class CallMixin():
    def argvalue(self, items):
        """
        Transform an argvalue node:
        - single item → positional argument (ast.expr)
        - two items → keyword argument (return (name, value))
        """
        if len(items) == 2:
            # items[0] is the name, items[1] is the value
            key = ensure_name(items[0])   # 'a'
            value = ensure_expr(items[1]) # 2
            return (key, value)
        # otherwise positional
        return ensure_expr(items[0])

    def stararg(self, items):
        return ('star_arg', ensure_expr(items[0]))

    def starargs(self, items):
        out = []
        for it in items:
            if isinstance(it, list): out.extend(it)
            else: out.append(it)
        return out

    def kwargs(self, items):
        return ('kwstar', ensure_expr(items[0]))
    
    def arguments(self, items):
        """
        Normalize Lark argument items into (args, keywords) for ast.Call
        Supports:
            f(1, 2, a=3, *lst, **d)
        """
        # flatten nested lists
        flat = []
        for it in items:
            if isinstance(it, list):
                flat.extend(it)
            else:
                flat.append(it)

        args = []
        keywords = []

        for el in flat:
            if el is None:
                continue

            # keyword argument: tuple (key, value)
            if isinstance(el, tuple) and len(el) == 2:
                key, val = el
                # convert key to str
                if isinstance(key, ast.Name):
                    key_str = key.id
                elif isinstance(key, Token):
                    key_str = key.value
                elif isinstance(key, str):
                    key_str = key
                else:
                    raise TypeError(f"Unexpected keyword key: {key!r}")
                keywords.append(ast.keyword(arg=key_str, value=ensure_expr(val)))
                continue

            # *args
            if isinstance(el, tuple) and el and el[0] == 'star_arg':
                args.append(ast.Starred(value=ensure_expr(el[1]), ctx=ast.Load()))
                continue

            # **kwargs
            if isinstance(el, tuple) and el and el[0] == 'kwstar':
                keywords.append(ast.keyword(arg=None, value=ensure_expr(el[1])))
                continue

            # regular positional argument
            args.append(ensure_expr(el))

        return (args, keywords)

    def funccall(self, items):
        func = items[0]
        args = []; keywords = []
        if len(items) > 1 and isinstance(items[1], tuple):
            args, keywords = items[1]
        return ast.Call(func=func, args=args, keywords=keywords)
    
    def return_stmt(self, items):
        """
        items: list of expressions after 'return', or empty if just 'return'
        returns: ast.Return node
        """
        if not items:
            # plain 'return' with no value
            return ast.Return(value=None)
        elif len(items) == 1:
            # single expression
            return ast.Return(value=items[0])
        else:
            # multiple expressions -> tuple
            return ast.Return(value=ast.Tuple(elts=items, ctx=ast.Load()))
        

class FunctionMixin(CallMixin, LambdaMixin):
    pass