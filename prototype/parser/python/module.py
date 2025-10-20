import ast

class ModuleMixin:
    def import_name(self, items):
        """
        items: dotted_as_names
        returns: ast.Import
        """
        # items[0] is the Tree of dotted_as_name
        dotted_tree = items[0]
        names = []
        for dotted_item in dotted_tree.children:
            if isinstance(dotted_item, tuple) and len(dotted_item) == 2:
                dotted, alias = dotted_item
                # FIX: Convert dotted_name AST to string
                name_str = self._dotted_name_to_string(dotted)
                names.append(ast.alias(name=name_str, asname=alias))
        return ast.Import(names=names)

    def import_from(self, items):
        """
        items: [module_path, imported]
        module_path: list of names and optional leading dots
        imported: "*" or list of (name, alias)
        """
        module_item = items[0]
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
                    # FIX: Convert module name AST to string
                    name_parts.append(self._dotted_name_to_string(p))
            module_name = ".".join(name_parts) if name_parts else None
        else:
            # FIX: Convert single module name AST to string
            module_name = self._dotted_name_to_string(module_item)

        # Build list of aliases
        if imported == "*":
            names = [ast.alias(name="*", asname=None)]
        else:
            names = []
            for import_item in imported.children:
                if isinstance(import_item, tuple) and len(import_item) == 2:
                    name, alias = import_item
                    # FIX: Convert imported name to string
                    name_str = name if isinstance(name, str) else self._dotted_name_to_string(name)
                    names.append(ast.alias(name=name_str, asname=alias))
        return ast.ImportFrom(module=module_name, names=names, level=level)

    def _dotted_name_to_string(self, node):
        """
        Convert dotted_name AST node to string.
        Handles both string names and AST nodes.
        """
        if isinstance(node, str):
            return node
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # Recursively build the dotted name
            value_str = self._dotted_name_to_string(node.value)
            return f"{value_str}.{node.attr}"
        elif isinstance(node, list):
            # List of name parts
            return ".".join(str(part) for part in node)
        else:
            return str(node)
    
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



