from typing import Union
from .functionExpression import FunctionExpression
from .abstractExpression import AbstractExpression
from .visitor import AbstractVisitor
from .functionCallExpression import FunctionCallExpression
from .integerLiteralCalchasExpression import IntegerLiteralCalchasExpression
from .floatLiteralExpression import FloatLiteralCalchasExpression
from .constantExpression import ConstantValueExpression, ConstantFunctionExpression
from .placeholder import Placeholder
from .idExpression import IdExpression


class FormulaFunctionExpression(FunctionExpression):
    def __init__(self, var_: Union[Placeholder, IdExpression], expr_: AbstractExpression):
        self.var = var_
        self.expr = expr_

    def __repr__(self) -> str:
        return '%s -> %s' % (self.var, self.expr)

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        if type(other) == FormulaFunctionExpression:
            return self.expr == other.expr and self.var == other.var  # TODO: alpha equivalence
        return False

    def __hash__(self):
        return hash(hash(self.var) + hash(self.expr))

    def apply(self, e: AbstractExpression) -> AbstractExpression:
        subst = VarSubstituer(self.expr, self.var, e)
        return subst.visit()

    def get_var(self) -> IdExpression:
        return self.var

    def get_expr(self) -> AbstractExpression:
        return self.expr


class VarSubstituer(AbstractVisitor):
    def __init__(self, tree, var, e):
        super(VarSubstituer, self).__init__(tree)
        self.var = var
        self.e = e

    def _visit_placeholder(self, tree: Placeholder, *args):
        return tree

    def _visit_id(self, tree: IdExpression, *args):
        return self.e if tree == self.var else tree

    def _visit_call(self, tree: FunctionCallExpression, *args):
        self._default_visit_call(tree, *args)

    def _visit_fun(self, tree: FunctionExpression, *args):
        if isinstance(tree, FormulaFunctionExpression):
            return tree if tree.var == self.var else FormulaFunctionExpression(tree.var, self.visit(tree.expr, *args))
        else:
            return tree

    def _visit_int(self, tree: IntegerLiteralCalchasExpression, *args):
        return tree

    def _visit_float(self, tree: FloatLiteralCalchasExpression, *args):
        return tree

    def _visit_constant_value(self, tree: ConstantValueExpression, *args):
        return tree

    def _visit_constant_function(self, tree: ConstantFunctionExpression, *args):
        return tree
