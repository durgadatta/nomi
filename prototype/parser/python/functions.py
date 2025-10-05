import ast
from lark.lexer import Token
from prototype.parser.python import ensure_expr, ensure_arg, ensure_name, tokval

# functions.py
# Grammar-faithful implementation of function-related constructs
# for the official Python grammar in Lark.
# Converts Lark Trees -> Python ast nodes.

import ast
from prototype.parser.python.utils import ensure_expr


class FunctionMixin():
    def typedparam(self, items):
        name = items[0]
        annotation = items[1] if len(items) > 1 else None
        return ast.arg(arg=ensure_name(name), annotation=annotation)

    def paramvalue(self, items):
        if len(items) == 2:
            return (items[0], ensure_expr(items[1]))
        return items[0]

    def starparam(self, items):
        return ('vararg', ensure_arg(items[0]))

    def starguard(self, items):
        return ('star', None)

    def poststarparams(self, items):
        out = []
        for it in items:
            if isinstance(it, list):
                out.extend(it)
            else:
                out.append(it)
        return out

    def kwparams(self, items):
        return ('kwarg', ensure_arg(items[0]))
    

    def parameters(self, items):
        """
        Convert Lark parameter items into ast.arguments.
        Correctly match Python ast.parse:
        - posonlyargs: before '/'
        - args: positional-or-keyword after '/'
        - vararg: *args
        - kwonlyargs: keyword-only args after '*' or *args
        - kwarg: **kwargs
        - defaults: only last N positional args that have defaults
        - kw_defaults: one per kwonlyarg
        """
        posonlyargs = []
        args = []
        kwonlyargs = []
        defaults_for_args = []
        kw_defaults = []
        vararg = None
        kwarg = None

        #pos_or_kw, / pos_only, *|*args, kw_only
        mode = "pos_or_kw"

        # Flatten nested lists
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

        # Normalize: pair name + default when separate
        normalized = []
        i = 0
        while i < len(flat):
            it = flat[i]
            if isinstance(it, (ast.arg, Token, str)):
                if (i + 1 < len(flat)) and isinstance(flat[i + 1], ast.expr):
                    normalized.append((it, flat[i + 1]))
                    i += 2
                    continue
                normalized.append(it)
                i += 1
                continue
            normalized.append(it)
            i += 1

        for it in normalized:
            # Slash → switch to posonlyargs
            if (isinstance(it, Token) and it.type == "SLASH") or (it == '/'):
                mode = "posonly"
                posonly_cut = len(posonlyargs) + len(args)
                continue

            # Bare '*' → switch to keyword-only mode
            if (isinstance(it, Token) and it.type == "STAR") or (isinstance(it, tuple) and it[0] == "star"):
                mode = "kwonly"
                continue

            # *args
            if isinstance(it, tuple) and it[0] == "vararg":
                vararg = it[1] if isinstance(it[1], ast.arg) else ensure_arg(it[1])
                mode = "kwonly"
                continue

            # **kwargs
            if isinstance(it, tuple) and it[0] == "kwarg":
                kwarg = it[1] if isinstance(it[1], ast.arg) else ensure_arg(it[1])
                continue

            # argument with default
            if isinstance(it, tuple) and len(it) == 2 and isinstance(it[0], (ast.arg, Token, str)):
                a = it[0] if isinstance(it[0], ast.arg) else ensure_arg(it[0])
                d = ensure_expr(it[1])
                if mode in ("pos_or_kw", "posonly"):
                    args.append(a) if mode == "pos_or_kw" else posonlyargs.append(a)
                    defaults_for_args.append(d)
                else:  # kwonly
                    kwonlyargs.append(a)
                    kw_defaults.append(d)
                continue

            # argument without default
            if isinstance(it, (ast.arg, Token, str)):
                a = it if isinstance(it, ast.arg) else ensure_arg(it)
                if mode == "pos_or_kw":
                    args.append(a)
                elif mode == "posonly":
                    posonlyargs.append(a)
                else:
                    kwonlyargs.append(a)
                    kw_defaults.append(None)
                continue

            raise ValueError(f"Unexpected parameter item: {it!r}")

        # Align defaults: only last N positional args get defaults
        n_defaults = len(defaults_for_args)
        if n_defaults > 0:
            defaults = [None] * (len(args) - n_defaults) + defaults_for_args
        else:
            defaults = []

        # keyword-only defaults: one per kwonlyarg
        while len(kw_defaults) < len(kwonlyargs):
            kw_defaults.append(None)

        return ast.arguments(
            posonlyargs=posonlyargs,
            args=args,
            vararg=vararg,
            kwonlyargs=kwonlyargs,
            kw_defaults=kw_defaults,
            kwarg=kwarg,
            defaults=defaults
        )

    def funcdef(self, items):
        name = None; args_node = None; returns = None; body = None
        for it in items:
            if isinstance(it, Token) and it.type == 'NAME':
                name = it.value
            elif isinstance(it, ast.arguments):
                args_node = it
            elif isinstance(it, list):
                body = it
            elif isinstance(it, ast.expr):
                returns = it
            elif isinstance(it, str) and name is None:
                name = it
        if args_node is None:
            args_node = ast.arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[])
        if body is None:
            body = []
        return ast.FunctionDef(name=name, args=args_node, body=body, decorator_list=[], returns=returns, type_comment=None)


# ---------- Calls ----------
class CallMixin(FunctionMixin):
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
