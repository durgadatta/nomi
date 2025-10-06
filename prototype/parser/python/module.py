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
        items: [module_path, imported]
        module_path: list of names and optional leading dots
        imported: "*" or list of (name, alias)
        """
        module_item = items[0]  # could be ['collections'] or ['.', 'collections']
        imported = items[1]

        # Determine level (count leading dots)
        level = 0
        name_parts = []
        if isinstance(module_item, list):
            for p in module_item:
                if p == '.':
                    level += 1
                elif p == '...':  # in case of multiple dots
                    level += 3
                else:
                    name_parts.append(p)
            module_name = ".".join(name_parts) if name_parts else None
        else:
            module_name = str(module_item)

        # Build list of aliases
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


