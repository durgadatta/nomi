import ast 

class ClassMixin:
    def classdef(self, items):
        # assuming items[0] is the NAME token, items[1] is bases, items[2] is body
        # name = str(items[0])
        # bases = items[1] if len(items) > 1 else []
        # body = items[2] if len(items) > 2 else []

        name, args, body = items
        if args:
            bases, keywords = args
        else:
            bases, keywords = [], []
        return ast.ClassDef(
            name=name,
            bases=list(bases),
            keywords=keywords,
            body=body,
            decorator_list=[]
        )
    
    def getattr(self, items):
        obj, attr_name = items
        return ast.Attribute(value=obj, attr=attr_name, ctx=ast.Load())
    
    def yield_stmt(self, items):
        #NOTE: this appears in the lhs of grammar so is an "statement"
        # ast.Expr is actually for statements/not expression
        #   it evaluates the expression but does not assign
        return ast.Expr(value=items[0])

    def yield_expr(self, items):
        value = items[0] if len(items) > 0 else None
        return ast.Yield(value=value)

    def yield_from(self, items):
        value = items[0]
        return ast.YieldFrom(value=value)
        