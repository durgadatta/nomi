import ast 

class ClassMixin:
    def classdef(self, items):
        # assuming items[0] is the NAME token, items[1] is bases, items[2] is body
        name = str(items[0])
        bases = items[1] if len(items) > 1 else []
        body = items[2] if len(items) > 2 else []

        bases = bases or [] # NOTE: see comment at for_stmt
        return ast.ClassDef(
            name=name,
            bases=bases,
            keywords=[],
            body=body,
            decorator_list=[]
        )
    
    def getattr(self, items):
        obj, attr_name = items
        return ast.Attribute(value=obj, attr=attr_name, ctx=ast.Load())