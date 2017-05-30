from .abstractExpression import AbstractExpression
from .idExpression import IdExpression
from .functionCallExpression import FunctionCallExpression
from .formulaFunctionExpression import FormulaFunctionExpression
from .integerLiteralCalchasExpression import IntegerLiteralCalchasExpression
from .floatLiteralExpression import FloatLiteralCalchasExpression
from .constantExpression import ConstantValueExpression, ConstantFunctionExpression
from .placeholder import Placeholder
from .visitor import AbstractVisitor
from typing import Iterable, Set


class DummyGen:
    def __init__(self, prefix: str = "", suffix: str = "") -> None:
        self.vars = set()
        self.nb = 0
        self.prefix = prefix
        self.suffix = suffix

    def add_var(self, var: IdExpression):
        self.vars.add(var)

    def add_vars(self, var: Iterable[str]):
        for v in var:
            self.vars.add(v)

    def set_vars(self, var: Set[str]):
        self.vars = var

    def add_tree(self, tree: AbstractExpression):
        DummyGenVisitor(tree).visit(tree, self.vars)

    def get_dummy(self):
        dummy = '%s%s%s' % (self.prefix, self.nb, self.suffix)
        while dummy in self.vars:
            self.nb += 1
            dummy = '%s%s%s' % (self.prefix, self.nb, self.suffix)
        self.vars.add(dummy)
        return IdExpression(dummy)

    def reset(self):
        self.vars = set()
        self.nb = 0


class DummyGenVisitor(AbstractVisitor):
    def _visit_placeholder(self, tree: Placeholder, *args):
        pass

    def _visit_id(self, tree: IdExpression, *args):
        args[0].add(tree.id)

    def _visit_call(self, tree: FunctionCallExpression, *args):
        self._default_visit_call(tree, *args)

    def _visit_fun(self, tree: FormulaFunctionExpression, *args):
        args[0].add(tree.var.id)
        self.visit(tree.expr)

    def _visit_int(self, tree: IntegerLiteralCalchasExpression, *args):
        pass

    def _visit_float(self, tree: FloatLiteralCalchasExpression, *args):
        pass

    def _visit_constant_value(self, tree: ConstantValueExpression, *args):
        pass

    def _visit_constant_function(self, tree: ConstantFunctionExpression, *args):
        pass
