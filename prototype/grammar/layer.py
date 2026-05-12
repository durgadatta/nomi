"""
Layered parse-tree transform pipeline.

Each grammar layer produces an intermediate Lark parse tree.
Layers run in sequence: the output of one layer feeds the next.
The final layer produces the tree that the Python AST transformer consumes.

This keeps each layer self-contained: changes to one layer's grammar or
transform do not affect other layers.  Downstream (AST → desugar → interpreter)
is unchanged.
"""

from lark import Tree, Transformer, v_args


class LayerTransform(Transformer):
    """Base class for a layer transform.

    Operates on a Lark ``Tree`` produced by the assembled grammar.
    Subclasses override ``visit`` / ``visit_<rule>`` / ``<rule>``
    methods to restructure or annotate the tree.

    Each transform receives the **output tree of the previous layer**
    and returns a new tree that feeds the next layer (or the final
    Python AST transformer).
    """

    def __call__(self, tree: Tree) -> Tree:
        return self.transform(tree)


class LayerPipeline:
    """Ordered chain of layer transforms.

    Usage::

        pipeline = LayerPipeline([ExpressionLayer(), PatternLayer(), ...])
        final_tree = pipeline.run(raw_parse_tree)
        python_ast = ast_transformer.transform(final_tree)
    """

    def __init__(self, layers):
        self.layers = list(layers)

    def run(self, tree: Tree) -> Tree:
        for layer in self.layers:
            tree = layer(tree)
        return tree
