from calchas_datamodel import AbstractExpression
from calchas_datamodel.dummy import DummyGen
from .transformation import Transformation


class Transformer:
    def __init__(self, tree: AbstractExpression):
        self.tree = tree
        self.dummy_gen = DummyGen()
        self.dummy_gen.add_tree(self.tree)

    def apply(self, transformation: Transformation):
        transformation.set_pre_and_suffix(self.dummy_gen)
        self.tree = transformation.apply(self.tree, self.dummy_gen)

    def get_tree(self) -> AbstractExpression:
        return self.tree
