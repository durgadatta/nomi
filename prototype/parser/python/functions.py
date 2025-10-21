import ast
from typing import List, Optional, Tuple
from lark import Tree, Token

class FunctionDefMixin:
    """
    Unified mixin for both function definitions and lambdas.
    Converts Lark Trees into Python ast.FunctionDef or ast.Lambda.

    Reuses the same _build_arguments() logic for both.
    """

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

            # Handle section markers (now processed by parameters method)
            if it == "SLASH":
                seen_slash = True
                current_list = args
                continue
            if it == "STAR":
                seen_star = True
                current_list = kwonlyargs
                continue

            # *args - from starparam: ("vararg", ast.arg)
            if isinstance(it, tuple) and it[0] == "vararg":
                vararg = it[1]  # ast.arg or None for bare *
                if vararg is not None:  # Only set seen_star if we actually have *args
                    seen_star = True
                    current_list = kwonlyargs
                continue

            # **kwargs - from kwparams: ("kwarg", ast.arg)  
            if isinstance(it, tuple) and it[0] == "kwarg":
                kwarg = it[1]  # Always ast.arg
                continue

            # Normal parameter - guaranteed (ast.arg, default_expr)
            if isinstance(it, tuple) and len(it) == 2:
                arg_obj, default_expr = it
            else:
                # Should not happen with consistent types
                continue

            if not arg_obj:
                continue

            current_list.append(arg_obj)
            if seen_star:
                kw_defaults.append(default_expr)  # Can be None
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
        paramvalue: typedparam ("=" test)?
        Now typedparam returns ast.arg, so we need to handle that
        """
        # items[0] is now ast.arg from typedparam (not inline content)
        arg_node = items[0]  # Already ast.arg
        default = items[1] if len(items) > 1 else None
        
        return (arg_node, default)  # (ast.arg, default_expr)
        
    def starparam(self, items):
        """
        starparam: "*" typedparam  # typedparam is inlined, so we get its content directly
        items: [name] or [name, annotation] from inline typedparam
        """
        # Handle inline typedparam content
        name = items[0]
        annotation = items[1] if len(items) > 1 else None
        
        # Always return proper ast.arg
        arg_obj = ast.arg(arg=name, annotation=annotation)
        return ("vararg", arg_obj)

    def kwparams(self, items):
        """
        kwparams: "**" typedparam ","?  # typedparam is inlined
        items: [name] or [name, annotation] from inline typedparam
        """
        name = items[0]
        annotation = items[1] if len(items) > 1 else None
        
        arg_obj = ast.arg(arg=name, annotation=annotation)
        return ("kwarg", arg_obj)

    def typedparam(self, items):
        """
        typedparam: name (":" test)?
        This is only called when used as a proper rule (not inlined)
        """
        name = items[0]
        annotation = items[1] if len(items) > 1 else None
        
        return ast.arg(arg=name, annotation=annotation)
    
    def starparams(self, items):
        """
        starparams: (starparam | starguard) poststarparams
        """
        star_part = items[0]
        poststar_part = items[1] if len(items) > 1 else []
        
        # star_part is either ("vararg", ast.arg) from starparam 
        # or ("vararg", None) from starguard
        # or potentially a raw "*" token that we need to handle
        
        result = []
        
        # If we got a raw "*" token (because no STAR method processed it)
        if isinstance(star_part, Token) and star_part.value == '*':
            result.append(("vararg", None))  # Bare star
        else:
            result.append(star_part)  # Already processed starparam/starguard
        
        if poststar_part:
            if isinstance(poststar_part, list):
                result.extend(poststar_part)
            else:
                result.append(poststar_part)
                
        return result

    def starguard(self, items):
        """
        starguard: "*"
        Returns: ("vararg", None) for bare star
        """
        return ("vararg", None)

    def poststarparams(self, items):
        """
        poststarparams: ("," paramvalue)* ["," kwparams]
        """
        paramvalues = items[0] if items and items[0] is not None else []
        kwparams = items[1] if len(items) > 1 else None
        
        result = []
        if paramvalues:
            if isinstance(paramvalues, list):
                result.extend(paramvalues)
            else:
                result.append(paramvalues)
        if kwparams:
            result.append(kwparams)
        return result

    def parameters(self, items):
        """
        Handle all three forms of parameters:
        1. paramvalue ("," paramvalue)* ["," SLASH ("," paramvalue)*] ["," [starparams | kwparams]]
        2. starparams
        3. kwparams
        """
        processed_items = []
        
        # If we only have one item, it might be Form 2 or 3
        if len(items) == 1:
            # Forms 2 & 3: starparams or kwparams as single item
            return self._build_arguments(items)
        
        # Form 1: Mixed parameters with potential SLASH
        i = 0
        while i < len(items):
            item = items[i]
            
            if item is None:
                i += 1
                continue
                
            # Handle SLASH marker
            if item == "SLASH":
                processed_items.append("SLASH")
                i += 1
                continue
                
            # Handle ast.arg (from typedparam)
            if isinstance(item, ast.arg):
                # Check if next item is a default expression
                if i + 1 < len(items) and isinstance(items[i + 1], ast.expr):
                    processed_items.append((item, items[i + 1]))
                    i += 2
                else:
                    processed_items.append((item, None))
                    i += 1
            
            # Handle raw string parameter names
            elif isinstance(item, str):
                arg_obj = ast.arg(arg=item, annotation=None)
                processed_items.append((arg_obj, None))
                i += 1
                
            # Handle starparams/kwparams in the middle of Form 1
            elif isinstance(item, (tuple, list, dict)):
                processed_items.append(item)
                i += 1
                
            else:
                # Unknown item type, skip it
                i += 1
        
        return self._build_arguments(processed_items)
    
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

        return ast.Return(value=value)


class LambdaMixin(FunctionDefMixin):
    '''
    Try to re-sue FuncDef parts here
    NOTE: why are the grammar different for arguments for FuncDef and Lambda?
    related to precedence?
    '''
   
    def lambda_params(self, items):
        """
        lambda_params: lambda_paramvalue ("," lambda_paramvalue)* ["," [lambda_starparams | lambda_kwparams]]
                    | lambda_starparams
                    | lambda_kwparams
        """
        processed_items = []
        
        # Single item cases
        if len(items) == 1:
            item = items[0]
            if isinstance(item, dict) and "star_name" in item:
                return self._process_lambda_starparams(item)
            elif isinstance(item, list) and item and item[0] == "kwarg":
                return self._build_arguments([("kwarg", item[1])])
            else:
                return self._build_arguments([item])
        
        # Mixed parameters
        for item in items:
            if item is None:
                continue
            if isinstance(item, dict) and "star_name" in item:
                starargs_result = self._process_lambda_starparams(item)
                processed_items.extend(starargs_result)
            elif isinstance(item, list) and item and item[0] == "kwarg":
                processed_items.append(("kwarg", item[1]))
            elif isinstance(item, tuple):
                name, default = item
                arg_obj = ast.arg(arg=name, annotation=None) if isinstance(name, str) else name
                processed_items.append((arg_obj, default))
            elif isinstance(item, str):
                arg_obj = ast.arg(arg=item, annotation=None)
                processed_items.append((arg_obj, None))
        
        return self._build_arguments(processed_items)
    
    def _process_lambda_starparams(self, starparams_dict):
        """Convert lambda_starparams dict to _build_arguments format"""
        result = []
        if starparams_dict["star_name"]:
            result.append(("vararg", ast.arg(arg=starparams_dict["star_name"], annotation=None)))
        for name, default in starparams_dict["after_params"]:
            arg_obj = ast.arg(arg=name, annotation=None) if isinstance(name, str) else name
            result.append((arg_obj, default))
        if starparams_dict["kwparams"]:
            result.append(("kwarg", ast.arg(arg=starparams_dict["kwparams"], annotation=None)))
        return result
    
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
        result = {
            "star_name": items[0] if items and items[0] is not None else None,
            "after_params": [],
            "kwparams": None
        }
        for i in range(1, len(items)):
            item = items[i]
            if isinstance(item, list) and item and item[0] == "kwarg":
                result["kwparams"] = item[1].arg if hasattr(item[1], 'arg') else item[1]
            elif isinstance(item, tuple):
                result["after_params"].append(item)
        return result
    
    def lambda_kwparams(self, items):
        """
        lambda_kwparams: "**" name ","?
        """
        name = items[0]
        return ["kwarg", ast.arg(arg=name, annotation=None) if isinstance(name, str) else name]
    
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