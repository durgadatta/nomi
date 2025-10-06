import ast

import ast

import ast

class ImportMixin:
    def import_stmt(self, items):
        """
        import_stmt: import_name | import_from
        """

        # Case 1: Already a list of aliases (preprocessed by import_name)
        if isinstance(items[0], list):
            return ast.Import(names=items[0])

        # Case 2: Already an AST node
        if isinstance(items[0], (ast.Import, ast.ImportFrom)):
            return items[0]

        # Case 3: Lark Tree (import_name or import_from)
        child = items[0]

        # -------------------
        # import_name
        # -------------------
        if getattr(child, "data", None) == "import_name":
            names_node = child.children[0]
            names = []
            for dotted_as in names_node.children:
                # dotted_as: dotted_name ["as" NAME]
                name_node = dotted_as.children[0]
                if hasattr(name_node, "children"):
                    # dotted_name -> join all parts
                    name = ".".join(n.value for n in name_node.children)
                else:
                    name = name_node.value
                asname = dotted_as.children[1].value if len(dotted_as.children) > 1 else None
                names.append(ast.alias(name=name, asname=asname))
            return ast.Import(names=names)

        # -------------------
        # import_from
        # -------------------
        elif getattr(child, "data", None) == "import_from":
            import_names_node = child.children[-1]

            # Count dots (level)
            level = 0
            if getattr(child.children[0], "data", None) == "dots":
                dots_node = child.children[0]
                level = sum(len(d.value) for d in dots_node.children)

            # Module name
            module = None
            if len(child.children) > 2:
                module_node = child.children[1]
                if getattr(module_node, "data", None) == "dotted_name":
                    module = ".".join(n.value for n in module_node.children)
                else:
                    module = module_node.value

            # Parse imported names
            names = []
            for dotted_as in import_names_node.children:
                name_node = dotted_as.children[0]
                if hasattr(name_node, "children"):
                    name = ".".join(n.value for n in name_node.children)
                else:
                    name = name_node.value
                asname = dotted_as.children[1].value if len(dotted_as.children) > 1 else None
                names.append(ast.alias(name=name, asname=asname))

            return ast.ImportFrom(module=module, names=names, level=level)

        else:
            raise TypeError(f"Unknown import_stmt child: {items[0]}")

class OthersMixin(ImportMixin):
    pass