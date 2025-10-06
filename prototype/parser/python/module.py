import ast
from prototype.parser.python import ensure_arg, ensure_expr, ensure_name

class ModuleMixin:
    # -----------------------------
    # import X [, Y as Z]
    # -----------------------------
    def import_name(self, items):
        """
        items: dotted_as_names
        returns: ast.Import
        """
        # items[0] is the list of dotted_as_name
        dotted_list = items[0]
        names = []
        for dotted, alias in dotted_list:
            # dotted can be list of names -> join with '.'
            name_str = ".".join(dotted) if isinstance(dotted, list) else dotted
            names.append(ast.alias(name=name_str, asname=alias))
        return ast.Import(names=names)

    # -----------------------------
    # from X import Y [, Z as ...] or *
    # -----------------------------
    def import_from(self, items):
        """
        items: [dots? + dotted_name?, imported_names]
        imported_names: "*" or list of (name, alias)
        """
        # first item: module path
        mod_item = items[0]
        # module name string
        if isinstance(mod_item, tuple) or isinstance(mod_item, list):
            # may include leading dots for relative import
            dots = mod_item[0] if isinstance(mod_item[0], str) and mod_item[0] in (".", "...") else ""
            name_list = mod_item[1] if len(mod_item) > 1 else []
            module_name = ".".join(name_list) if name_list else None
            # compute level: count dots
            level = len([c for c in mod_item if c in (".", "...")])
        else:
            module_name = mod_item
            level = 0

        imported = items[1]
        # "*" import
        if imported == "*":
            names = [ast.alias(name="*", asname=None)]
        else:
            names = []
            for name, alias in imported:
                names.append(ast.alias(name=name, asname=alias))

        return ast.ImportFrom(module=module_name, names=names, level=level)

    # -----------------------------
    # import_as_name: name ["as" name]
    # returns tuple (name_str, alias_str_or_None)
    # -----------------------------
    def import_as_name(self, items):
        if len(items) == 1:
            return (items[0], None)
        return (items[0], items[1])

    # -----------------------------
    # dotted_as_name: dotted_name ["as" name]
    # dotted_name is list of names
    # -----------------------------
    def dotted_as_name(self, items):
        if len(items) == 1:
            return (items[0], None)
        return (items[0], items[1])

    # -----------------------------
    # dotted_name: name ("." name)*
    # returns list of strings
    # -----------------------------
    def dotted_name(self, items):
        return [str(i) for i in items]

    # -----------------------------
    # import_as_names / dotted_as_names
    # returns list of tuples (name_or_dotted, alias)
    # -----------------------------
    def import_as_names(self, items):
        return items

    def dotted_as_names(self, items):
        return items


