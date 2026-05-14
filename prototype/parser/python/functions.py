import ast
from typing import List, Optional, Tuple
from lark import Tree, Token

class FunctionDefMixin:
    """
    Unified mixin for both function definitions and lambdas.
    Converts Lark Trees into Python ast.FunctionDef or ast.Lambda.

    Reuses the same _build_arguments() logic for both.
    """

    def _empty_arguments(self):
        return ast.arguments(
            posonlyargs=[], args=[], vararg=None,
            kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        )

    def _flatten_items(self, items):
        flattened_items = []
        for item in items:
            if isinstance(item, list):
                flattened_items.extend(item)
            else:
                flattened_items.append(item)
        return flattened_items

    def _coerce_param_item(self, item):
        if isinstance(item, tuple) and len(item) == 2:
            return item
        if isinstance(item, str):
            return ast.arg(arg=item, annotation=None), None
        if isinstance(item, ast.arg):
            return item, None
        return None, None

    
    def typedparam(self, items):
        """
        ?typedparam: name (":" param_constraint)?
        This method is called → typedparam was proper rule → has BOTH children: [name, annotation]

        NOTE: ?x means x is conditionally inline (when >1 children)
        """
        name, annotation = items
        return ast.arg(arg=name, annotation=annotation)

    def grouped_constraint(self, items):
        """
        grouped_constraint: "(" constraint_list ")"
        Function parameters use parentheses for multi-constraint annotations so
        parameter commas remain unambiguous.
        """
        return items[0]
    
    def paramvalue(self, items):
        """
        paramvalue: typedparam ("=" test)?

        We can't return the parsed node from here because
        arg() does not handle default values, it is handled
        at one level up - parameters
        """
        typedparam, default_expr = items
        
        # Process typedparam result -may/not be parsed already
        if not isinstance(typedparam, ast.arg):
            typedparam = self.typedparam([typedparam, None])
        return (typedparam, default_expr)
        
    def starparam(self, items):
        """
        starparam: "*" typedparam
        """
        typedparam = items[0]
        if not isinstance(typedparam, ast.arg):
            typedparam = self.typedparam([typedparam, None])
        
        return ("vararg", typedparam)
    
    def starguard(self, items):
        """
        starguard: "*"
        Returns: ("vararg", None) for bare star
        """
        return ("vararg", None)

    def kwparams(self, items):
        """
        kwparams: "**" typedparam ","?
        """
        typedparam = items[0]
        if not isinstance(typedparam, ast.arg):
            typedparam = self.typedparam([typedparam, None])
    
        return ("kwarg", typedparam)
    
    def starparams(self, items):
        """
        starparams: (starparam | starguard) poststarparams

        return a flatten list
        """
        star_part, poststar_part = items
        return [star_part] + poststar_part
    
    def poststarparams(self, items):
        """
        poststarparams: ("," paramvalue)* ["," kwparams]

        return a flatten list to process
        """
        *paramvalues, kwparams = items
        if kwparams:
            paramvalues.append(kwparams)
        return paramvalues
    
    def parameters(self, items):
        """
        Simplified parameters processing without complex unpacking
        """
        if not items:
            return self._empty_arguments()
        
        items = self._flatten_items(items)
        
        # Now process items sequentially without complex unpacking
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

        for item in items:
            if item is None:
                continue

            if item == "SLASH":
                seen_slash = True
                current_list = args
                continue
            if item == "STAR":
                seen_star = True
                current_list = kwonlyargs
                continue

            # *args
            if isinstance(item, tuple) and item[0] == "vararg":
                vararg = item[1]
                seen_star = True
                current_list = kwonlyargs
                continue

            # **kwargs
            if isinstance(item, tuple) and item[0] == "kwarg":
                kwarg = item[1]
                continue

            arg_obj, default_expr = self._coerce_param_item(item)
            if arg_obj is None:
                continue

            current_list.append(arg_obj)
            if seen_star:
                kw_defaults.append(default_expr)
            else:
                if default_expr is not None:
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
        name, parameters, returns, suite = items

        return ast.FunctionDef(
            name=name,
            args=parameters or self.parameters([]),
            body=suite,
            decorator_list=[],  # Handled by decorated rule
            returns=returns,    # Can be None
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
   
    def lambda_params(self, items):
        """
        lambda_params: lambda_paramvalue ("," lambda_paramvalue)* ["," [lambda_starparams | lambda_kwparams]]
                    | lambda_starparams
                    | lambda_kwparams
        Use the same logic as parameters but without SLASH support
        """
        return self.parameters(items)
    
    def lambda_paramvalue(self, items):
        """
        lambda_paramvalue: name ("=" test)?
        """
        return self.paramvalue(items)
    
    def lambda_starparams(self, items):
        """
        lambda_starparams: "*" [name] ("," lambda_paramvalue)* ["," [lambda_kwparams]]
        Convert to same format as starparams + poststarparams
        """        
        starparam, *others, kwparams = items 
        if starparam:
            others.append(("vararg", ast.arg(arg=starparam)))
        if kwparams:
            others.append(("kwarg", kwparams[1]))

        return others

    
    def lambda_kwparams(self, items):
        """
        lambda_kwparams: "**" name ","?
        Same as kwparams
        """
        return self.kwparams(items)
    
    def lambdef(self, items):
        """
        lambdef: "lambda" [lambda_params] ":" test
        """
        return ast.Lambda(args=items[0], body=items[1])
    
    def lambdef_nocond(self, items):
        """
        lambdef_nocond: "lambda" [lambda_params] ":" test_nocond
        NOTE: why is this there in the grammar?
        """
        return self.lambdef(items)



class CallMixin:
    def argvalue(self, items):
        """
        argvalue: test ("=" test)?
        Returns either:
        - positional argument (test) 
        - keyword argument (ast.keyword)
        """
        if len(items) == 2:
            # Keyword argument: name=value
            # items[0] should be a name node for the keyword
            if isinstance(items[0], ast.Name):
                return ast.keyword(arg=items[0].id, value=items[1])
            else:
                # Fallback for non-name keywords
                return ast.keyword(arg=None, value=items[1])
        else:
            # Positional argument
            return items[0]

    def stararg(self, items):
        """
        stararg: "*" test
        """
        return ast.Starred(value=items[0], ctx=ast.Load())

    def kwargs(self, items):
        """
        kwargs: "**" test ("," argvalue)*
        Returns a list of keyword arguments including the **kwargs
        """
        # First item is the **kwargs expression
        kwargs_keyword = ast.keyword(arg=None, value=items[0])
        result = [kwargs_keyword]
        
        # Add any additional keyword arguments
        for item in items[1:]:
            if isinstance(item, ast.keyword):
                result.append(item)
        
        return result

    def starargs(self, items):
        """
        starargs: stararg ("," stararg)* ("," argvalue)* ["," kwargs]
        Returns a flat list of all arguments (positional, starred, and keywords)
        """
        # Just return a flat list - let arguments() handle the categorization
        *others, kwargs = items 
        if kwargs:
            others.extend(kwargs)
        return others

    def arguments(self, items):
        """
        arguments: argvalue ("," argvalue)*  ("," [ starargs | kwargs])?
                 | starargs
                 | kwargs
                 | comprehension{test}
        
        Returns: (args, keywords) tuple
        """
        args = []
        keywords = []
        
        if not items:
            return args, keywords
        
        # Flatten any nested structures first
        flat_items = []
        for item in items:
            if isinstance(item, list):
                flat_items.extend(item)
            else:
                flat_items.append(item)
        
        # Process all items in sequence
        for item in flat_items:
            if isinstance(item, ast.Starred):
                args.append(item)
            elif isinstance(item, ast.keyword):
                keywords.append(item)
            elif isinstance(item, ast.comprehension):
                # Handle comprehension case
                # This would need special handling based on your comprehension implementation
                args.append(item)
            else:
                # Regular positional argument
                args.append(item)
        
        return args, keywords

    def funccall(self, items):
        """
        atom_expr: atom_expr "(" [arguments] ")" -> funccall
        """
        func, arguments = items
        args, keywords = [], []
        if arguments:
            args, keywords = arguments
        return ast.Call(func=func, args=args, keywords=keywords)

class FunctionMixin(CallMixin, LambdaMixin):
    pass
