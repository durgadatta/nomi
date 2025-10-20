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

    def starparams(self, items):
        """
        starparams: (starparam | starguard) poststarparams
        """
        star_part = items[0]
        poststar_part = items[1] if len(items) > 1 else []
        
        # FIX: Return a flat list that _build_arguments can process
        result = [star_part]
        
        if poststar_part:
            # If poststar_part is a Tree, extract its children
            if isinstance(poststar_part, Tree):
                poststar_part = poststar_part.children
            
            # If it's a list, extend the result with its items
            if isinstance(poststar_part, list):
                # Flatten any nested structures in poststar_part
                for item in poststar_part:
                    if item is None:
                        continue
                    if isinstance(item, list):
                        result.extend(item)
                    else:
                        result.append(item)
            else:
                result.append(poststar_part)
                
        return result

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

        # FIX: First, flatten the entire items list to handle nested structures
        def flatten_items(items_list):
            flattened = []
            for item in items_list:
                if item is None:
                    continue
                if isinstance(item, list):
                    flattened.extend(flatten_items(item))
                else:
                    flattened.append(item)
            return flattened

        flat_items = flatten_items(items)

        for it in flat_items:
            if it is None:
                continue

            # Handle section markers
            if it == "SLASH":
                seen_slash = True
                current_list = args
                continue
            if it == "STAR":
                seen_star = True
                current_list = kwonlyargs
                continue

            # *args
            if isinstance(it, tuple) and it[0] == "vararg":
                vararg = ensure_arg(it[1])
                seen_star = True
                current_list = kwonlyargs
                continue

            # **kwargs
            if isinstance(it, tuple) and it[0] == "kwarg":
                kwarg = ensure_arg(it[1])
                continue

            # lambda_starparams dict form
            if isinstance(it, dict) and "star_name" in it:
                seen_star = True
                if it["star_name"]:
                    vararg = self._name_to_arg(it["star_name"])
                for pv in it.get("after_params", []):
                    if isinstance(pv, tuple) and len(pv) == 2:
                        arg_obj, default_expr = pv
                    else:
                        arg_obj, default_expr = pv, None
                        
                    if arg_obj:
                        kwonlyargs.append(arg_obj)
                        if default_expr is not None:
                            kw_defaults.append(default_expr)
                if it.get("kwparams"):
                    kwarg = self._name_to_arg(it["kwparams"])
                continue

            # Convert string parameters to ast.arg
            if isinstance(it, str):
                it = ast.arg(arg=it, annotation=None)

            # Normal parameter
            if isinstance(it, tuple) and len(it) == 2:
                arg_obj, default_expr = it
            else:
                arg_obj, default_expr = it, None

            # Ensure arg_obj is ast.arg, not string
            if isinstance(arg_obj, str):
                arg_obj = ast.arg(arg=arg_obj, annotation=None)

            if not arg_obj:
                continue

            current_list.append(arg_obj)
            if seen_star:
                if default_expr is not None:
                    kw_defaults.append(default_expr)
                else:
                    kw_defaults.append(None)
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
   
    def paramvalue(self, items):
        """
        Process a parameter, e.g., 'x' or 'y=5'.
        Returns: name (for no default) or (name, default) tuple.
        """
        if len(items) == 2:
            return (items[0], items[1])  # e.g., (y, 5)
        return items[0]  # e.g., x

    def typedparam(self, items):
        """
        Process a typed parameter, e.g., 'y: int' or 'y: int = 5'.
        Returns: ast.arg with optional annotation and default passed to _build_arguments.
        """
        name = items[0]
        annotation = items[1] if len(items) > 1 else None
        default = items[2] if len(items) > 2 else None
        arg = ast.arg(arg=ensure_name(name), annotation=ensure_expr(annotation) if annotation else None)
        
        # FIX: Return both the arg AND the default so _build_arguments can see it
        if default is not None:
            return (arg, default)
        return arg

    def starparam(self, items):
        """
        starparam: "*" typedparam
        Returns: ("vararg", ast.arg)
        """
        # items[0] is already an ast.arg from typedparam
        return ("vararg", items[0])

    def poststarparams(self, items):
        """
        poststarparams: ("," paramvalue)* ["," kwparams]
        """
        paramvalues = items[0] if items and items[0] is not None else []
        kwparams = items[1] if len(items) > 1 else None
        
        # FIX: Ensure we return a flat list, not nested structures
        result = []
        if paramvalues:
            if isinstance(paramvalues, list):
                result.extend(paramvalues)
            else:
                result.append(paramvalues)
        if kwparams:
            result.append(kwparams)
        return result

    def starguard(self, _):
        """Bare star marker"""
        return "STAR"

    def kwparams(self, items):
        """
        kwparams: "**" typedparam ","?
        Returns: ("kwarg", ast.arg)
        """
        # items[0] is already an ast.arg from typedparam
        return ("kwarg", items[0])

    def parameters(self, items):
        """Build arguments from parameters"""
        return self._build_arguments(items)
    
    def decorator(self, items):
        """
        decorator: "@" dotted_name [ "(" [arguments] ")" ] _NEWLINE
        """
        # items[0] is already an AST expression from dotted_name
        decorator_expr = items[0]

        if len(items) > 1 and items[1]:
            # items[1] is already (args, keywords) from arguments
            args, keywords = items[1]
            return ast.Call(func=decorator_expr, args=args, keywords=keywords)

        return decorator_expr

    def decorated(self, items):
        """
        decorated: decorators (classdef | funcdef | async_funcdef)
        """
        decorator_nodes = items[0].children  # Already a list of decorator expressions
        target_node = items[1]      # Already a classdef/funcdef/async_funcdef AST node

        if not hasattr(target_node, 'decorator_list'):
            raise TypeError(f"Target does not accept decorators: {type(target_node)}")

        target_node.decorator_list = decorator_nodes
        return target_node

    def funcdef(self, items):
        """
        funcdef: "def" name "(" [parameters] ")" ["->" test] ":" suite
        items: [name, parameters, return_annotation, suite] (all 4 items always present, None if optional)
        """
        name = items[0]
        parameters = items[1]
        returns = items[2]  # None if no return annotation
        suite = items[3]

        return ast.FunctionDef(
            name=name,
            args=parameters or self._build_arguments([]),
            body=suite,
            decorator_list=[],  # Handled by decorated rule
            returns=returns,    # Can be None
            type_comment=None
        )

    def async_funcdef(self, items):
        """
        async_funcdef: "async" funcdef
        """
        # items[0] is already a funcdef AST node
        func_def = items[0]
        
        return ast.AsyncFunctionDef(
            name=func_def.name,
            args=func_def.args,
            body=func_def.body,
            decorator_list=func_def.decorator_list,
            returns=func_def.returns,
            type_comment=None
        )

    def return_stmt(self, items):
        """
        return_stmt: "return" [testlist]
        """
        if not items:
            return ast.Return(value=None)

        # items[0] is already processed testlist expression
        value = items[0]

        return ast.Return(value=ensure_expr(value))


class LambdaMixin(FunctionDefMixin):
   
    def lambda_params(self, items):
        """
        lambda_params: lambda_paramvalue ("," lambda_paramvalue)* ["," [lambda_starparams | lambda_kwparams]]
                    | lambda_starparams
                    | lambda_kwparams
        """
        # Use _build_arguments directly with flattened structure
        flat_items = []
        
        for item in items:
            if isinstance(item, ast.arguments):
                # Unpack arguments structure into flat markers
                if item.vararg:
                    flat_items.append(("vararg", item.vararg))
                for kwarg, kw_default in zip(item.kwonlyargs, item.kw_defaults):
                    if kw_default is not None:
                        flat_items.append((kwarg, kw_default))
                    else:
                        flat_items.append(kwarg)
                if item.kwarg:
                    flat_items.append(("kwarg", item.kwarg))
            else:
                flat_items.append(item)
        
        return self._build_arguments(flat_items)
    
    def lambda_paramvalue(self, items):
        """
        lambda_paramvalue: name ("=" test)?
        """
        if len(items) == 2:
            return (items[0], items[1])
        return items[0]
    
    def lambda_starparams(self, items):
        """
        lambda_starparams: "*" [name] ("," lambda_paramvalue)* ["," [lambda_kwparams]]
        """
        # Convert to format that _build_arguments understands
        flat_items = []
        
        # Add *args marker
        if items and items[0] is not None:
            flat_items.append(("vararg", ast.arg(arg=items[0])))
        else:
            flat_items.append("STAR")  # Bare star marker
        
        # Add keyword-only parameters
        for i in range(1, len(items)):
            item = items[i]
            if isinstance(item, ast.arguments):
                # **kwargs
                flat_items.append(("kwarg", item.kwarg))
            elif isinstance(item, tuple):
                # (name, default)
                name, default = item
                flat_items.append((ast.arg(arg=name), default))
            elif item is not None:
                # name only
                flat_items.append(ast.arg(arg=item))
        
        return self._build_arguments(flat_items)
    
    def lambda_kwparams(self, items):
        """
        lambda_kwparams: "**" name ","?
        """
        return self._build_arguments([("kwarg", ast.arg(arg=items[0]))])
    
    def lambdef(self, items):
        """
        lambdef: "lambda" [lambda_params] ":" test
        """
        if len(items) == 2:
            return ast.Lambda(args=items[0], body=items[1])
        else:
            return ast.Lambda(args=self._build_arguments([]), body=items[0])
    
    def lambdef_nocond(self, items):
        """
        lambdef_nocond: "lambda" [lambda_params] ":" test_nocond
        """
        if len(items) == 2:
            return ast.Lambda(args=items[0], body=items[1])
        else:
            return ast.Lambda(args=self._build_arguments([]), body=items[0])
class CallMixin:
    def argvalue(self, items):
        """
        argvalue: test ("=" test)?
        """
        if len(items) == 2:
            if hasattr(items[0], 'id'):
                key = items[0].id
            else:
                key = str(items[0])
            return ast.keyword(arg=key, value=items[1])
        else:
            return items[0]

    def stararg(self, items):
        """
        stararg: "*" test
        """
        return ast.Starred(value=items[0], ctx=ast.Load())

    def kwargs(self, items):
        """
        kwargs: "**" test ("," argvalue)*
        """
        # First item is the **kwargs expression
        kwargs_keyword = ast.keyword(arg=None, value=items[0])
        
        result = [kwargs_keyword]
        
        # Remaining items are additional keyword arguments (if any)
        # items[1:] will contain any additional argvalues after the **kwargs
        for i in range(1, len(items)):
            argvalue = items[i]
            if isinstance(argvalue, ast.keyword):
                result.append(argvalue)
        
        return result

    def starargs(self, items):
        """
        starargs: stararg ("," stararg)* ("," argvalue)* ["," kwargs]
        """
        args = []
        keywords = []
        
        for item in items:
            if isinstance(item, ast.Starred):
                args.append(item)
            elif isinstance(item, ast.keyword):
                keywords.append(item)
            elif isinstance(item, list):  # From kwargs
                keywords.extend(item)
        
        return (args, keywords)

    def arguments(self, items):
        """
        arguments: argvalue ("," argvalue)*  ("," [ starargs | kwargs])?
                 | starargs
                 | kwargs
                 | comprehension{test}
        """
        args = []
        keywords = []

        if not items:
            return args, keywords

        # Handle different cases based on the number and type of items
        if len(items) == 1:
            # Single item case: starargs, kwargs, or comprehension
            item = items[0]
            if isinstance(item, tuple) and len(item) == 2:
                # From starargs: (args, keywords)
                args.extend(item[0])
                keywords.extend(item[1])
            elif isinstance(item, list):
                # From kwargs: list of keywords
                keywords.extend(item)
            elif isinstance(item, ast.Starred):
                args.append(item)
            elif isinstance(item, ast.keyword):
                keywords.append(item)
            else:
                # Positional argument or comprehension
                args.append(item)
        else:
            # Multiple items: argvalue ("," argvalue)* ("," [starargs | kwargs])?
            # Process all items
            for item in items:
                if item is None:
                    continue
                if isinstance(item, tuple) and len(item) == 2:
                    # From starargs
                    args.extend(item[0])
                    keywords.extend(item[1])
                elif isinstance(item, list):
                    # From kwargs
                    keywords.extend(item)
                elif isinstance(item, ast.Starred):
                    args.append(item)
                elif isinstance(item, ast.keyword):
                    keywords.append(item)
                else:
                    # Positional argument
                    args.append(item)

        return args, keywords

    def funccall(self, items):
        """
        atom_expr: atom_expr "(" [arguments] ")" -> funccall
        """
        func = items[0]
        
        if len(items) > 1 and items[1] is not None:
            args, keywords = items[1]
        else:
            args, keywords = [], []
            
        return ast.Call(func=func, args=args, keywords=keywords)

class FunctionMixin(CallMixin, LambdaMixin):
    pass