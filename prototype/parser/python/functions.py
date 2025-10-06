import ast
from lark.lexer import Token
from lark import Tree
from prototype.parser.python import ensure_expr, ensure_arg, ensure_name

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
        Correctly match Python AST:
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

        mode = "pos_or_kw"  # default mode

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
                    if mode == "pos_or_kw":
                        args.append(a)
                    else:
                        posonlyargs.append(a)
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

        # --- Align defaults correctly: only last N positional args have defaults ---
        n_defaults = len(defaults_for_args)
        if n_defaults > 0:
            defaults = defaults_for_args[-n_defaults:]
            # pad with None for args without defaults not needed!
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

import ast
from lark import Tree, Token

# lambda_mixin.py
import ast
from typing import List, Tuple, Optional

class LambdaMixin:
    """
    Mix into your Lark Transformer. Requires:
      - a method self._to_expr(node) -> ast.expr that converts a 'test' or 'test_nocond'
        subtree into an ast expression node.
      - optionally self._name(token_or_str) -> str (but here we accept plain str).
    """

    # ---------- helpers ----------
    def _name_to_arg(self, name: str) -> ast.arg:
        """Create ast.arg for a name (no annotation for lambda params)."""
        return ast.arg(arg=name, annotation=None)

    def _paramvalue_to_pair(self, item):
        """
        Convert a lambda_paramvalue-like node to (ast.arg, default_expr_or_None).
        Handles cases where item is None (e.g., stray commas or optional params).
        """
        if item is None:
            # Empty slot (e.g. "lambda *: 1" or trailing comma) — skip gracefully.
            return None, None

        # Simple case: already tuple (name, default_tree)
        if isinstance(item, tuple) and len(item) == 2:
            name, default_tree = item
            if name is None:
                return None, None
            arg = self._name_to_arg(str(name))
            default_expr = self._to_expr(default_tree) if default_tree is not None else None
            return arg, default_expr

        # Simple bare name
        if isinstance(item, str):
            return self._name_to_arg(item), None

        # Token (Lark token)
        from lark import Token
        if isinstance(item, Token):
            return self._name_to_arg(item.value), None

        # Sometimes Lark gives a list like ['x'] or ['x', test]
        if isinstance(item, list) and item:
            name = item[0]
            default_tree = item[1] if len(item) > 1 else None
            arg = self._name_to_arg(str(name))
            default_expr = self._to_expr(default_tree) if default_tree is not None else None
            return arg, default_expr

        raise ValueError(f"Unsupported lambda_paramvalue shape: {item!r}")


    # ---------- grammar rule handlers ----------
    def lambdef(self, items):
        """
        lambdef: "lambda" [lambda_params] ":" test
        items: either [params_node, test_node] or [test_node] depending on presence of params.
        Return an ast.Lambda
        """
        if len(items) == 1:
            params_node = None
            test_node = items[0]
        else:
            params_node = items[0]
            test_node = items[1]

        body = self._to_expr(test_node)
        args = self._lambda_params_to_arguments(params_node)
        node = ast.Lambda(args=args, body=body)
        return ast.fix_missing_locations(node)

    def lambdef_nocond(self, items):
        """
        lambdef_nocond: "lambda" [lambda_params] ":" test_nocond
        Same as lambdef but forwards to expression conversion for no-cond test.
        """
        if len(items) == 1:
            params_node = None
            test_node = items[0]
        else:
            params_node = items[0]
            test_node = items[1]

        body = self._to_expr(test_node)  # assume _to_expr handles nocond variant
        args = self._lambda_params_to_arguments(params_node)
        node = ast.Lambda(args=args, body=body)
        return ast.fix_missing_locations(node)

    def lambda_params(self, items):
        """
        lambda_params: lambda_paramvalue ("," lambda_paramvalue)* ["," [lambda_starparams | lambda_kwparams]]
                       | lambda_starparams
                       | lambda_kwparams
        Here we pass through items as-is and handle them inside _lambda_params_to_arguments.
        """
        # return items as a convenience container for _lambda_params_to_arguments
        return items

    def lambda_paramvalue(self, items):
        """
        ?lambda_paramvalue: name ("=" test)?
        We'll return a tuple (name_str, default_tree_or_None) so helper can handle uniformly.
        items: [name] or [name, test_node]
        """
        if len(items) == 1:
            name = items[0]
            return (name, None)
        else:
            name = items[0]
            default_tree = items[1]
            return (name, default_tree)

    def lambda_starparams(self, items):
        """
        lambda_starparams: "*" [name]  ("," lambda_paramvalue)* ["," [lambda_kwparams]]
        We want to represent this structure in a canonical tuple:
           ("star", star_name_or_None, pre_post_list, maybe_lambda_kwparams)
        But simpler: return items as-is: items[0] may be star name or '*' depending on how parser returns it.
        For robustness, we'll return a dict with clear fields.
        items layout (as produced by Lark) may vary; produce a normalized dict here.
        """
        # Items can be like: [maybe_name_or_token, paramvalue1, paramvalue2, lambda_kwparams?]
        # Normalize:
        star_name = None
        rest = []
        kwparams = None
        for it in items:
            # if a plain name string and star_name not set: it's the star's name
            if isinstance(it, str) and star_name is None:
                # `*` token itself generally not included; grammar allows "*" [name]
                # If parser yields literal "*", skip it; expect a name token if provided
                if it == "*":
                    continue
                star_name = it
            # lambda_kwparams may be a dict/tree; detect by shape: grammar lambda_kwparams begins with "**"
            elif hasattr(it, 'data') and getattr(it, 'data', None) == 'lambda_kwparams':
                kwparams = it
            else:
                # probably a lambda_paramvalue tuple
                rest.append(it)
        return {"star_name": star_name, "after_params": rest, "kwparams": kwparams}

    def lambda_kwparams(self, items):
        """
        lambda_kwparams: "**" name ","?
        items likely: [name]
        Return the name string for kwarg.
        """
        if len(items) == 0:
            raise ValueError("lambda_kwparams: expected a name after **")
        name = items[0]
        return name

    def _lambda_params_to_arguments(self, params_node):
        """
        Build ast.arguments for a lambda definition.
        Skips spurious None nodes that may appear from optional commas or empty parameter lists.
        """
        posonlyargs = []
        args = []
        defaults = []
        vararg = None
        kwonlyargs = []
        kw_defaults = []
        kwarg = None

        if not params_node:
            return ast.arguments(
                posonlyargs=[], args=[], vararg=None,
                kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
            )

        # Normalize items: always a list
        items = params_node if isinstance(params_node, list) else [params_node]
        items = [it for it in items if it not in (None, [], '')]  # 🚫 drop empties

        seen_star = False

        for it in items:
            # starparams dict form
            if isinstance(it, dict) and 'star_name' in it:
                seen_star = True
                starinfo = it

                # *name or bare *
                star_name = starinfo.get('star_name')
                if star_name:
                    vararg = self._name_to_arg(star_name)

                # Params after *
                for pv in starinfo.get('after_params', []) or []:
                    pair = self._paramvalue_to_pair(pv)
                    if not pair or pair[0] is None:
                        continue
                    arg_obj, default_expr = pair
                    kwonlyargs.append(arg_obj)
                    kw_defaults.append(default_expr)

                # **kwargs if present
                kwname = starinfo.get('kwparams')
                if kwname:
                    kwarg = self._name_to_arg(kwname)
                continue

            # handle pure **kwparams (no star)
            if isinstance(it, str) and it.startswith("**"):
                kwarg = self._name_to_arg(it.lstrip('*'))
                continue

            # regular or kw-only paramvalue
            pair = self._paramvalue_to_pair(it)
            if not pair or pair[0] is None:
                continue

            arg_obj, default_expr = pair
            if not seen_star:
                args.append(arg_obj)
                if default_expr is not None:
                    defaults.append(default_expr)
            else:
                kwonlyargs.append(arg_obj)
                kw_defaults.append(default_expr)

        # Align kw_defaults length
        if len(kw_defaults) < len(kwonlyargs):
            kw_defaults.extend([None] * (len(kwonlyargs) - len(kw_defaults)))

        return ast.arguments(
            posonlyargs=[],
            args=args,
            vararg=vararg,
            kwonlyargs=kwonlyargs,
            kw_defaults=kw_defaults,
            kwarg=kwarg,
            defaults=defaults,
        )


# ---------- Calls ----------
class CallMixin(LambdaMixin, FunctionMixin):
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
        
