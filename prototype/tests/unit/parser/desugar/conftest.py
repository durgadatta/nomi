import ast


def find_node(tree, node_type):
    for node in ast.walk(tree):
        if isinstance(node, node_type):
            return node
    return None


def is_store(node):
    return isinstance(node.ctx, ast.Store)


def is_load(node):
    return isinstance(node.ctx, ast.Load)
