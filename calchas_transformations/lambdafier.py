from calchas_datamodel.visitor import AbstractVisitor
from calchas_datamodel import AbstractExpression
from calchas_datamodel import IdExpression as Id
from calchas_datamodel import FunctionCallExpression as Call
from calchas_datamodel import FormulaFunctionExpression as Fun
from calchas_datamodel import IntegerLiteralCalchasExpression
from calchas_datamodel import FloatLiteralCalchasExpression
from calchas_datamodel import ConstantValueExpression, ConstantFunctionExpression
from calchas_datamodel import Placeholder
from calchas_datamodel.constantExpression import constant_functions
from calchas_datamodel.dummy import DummyGen
from .transformation import Transformation


class CalchasTreeLambdafier(Transformation):
    def __init__(self, prefix: str = "_lambdafier_", suffix: str = ""):
        self.prefix = prefix
        self.suffix = suffix

    def set_pre_and_suffix(self, dummy_gen: DummyGen):
        dummy_gen.prefix = self.prefix
        dummy_gen.suffix = self.suffix

    def apply(self, tree: AbstractExpression, dummy_gen: DummyGen) -> AbstractExpression:
        return CalchasTreeLambdafierVisitor(tree, dummy_gen).visit()


class CalchasTreeLambdafierVisitor(AbstractVisitor):
    def __init__(self, tree: AbstractExpression, dummy_gen: DummyGen):
        super().__init__(tree)
        self.dummy_gen = dummy_gen

    def _visit_placeholder(self, tree: Placeholder, *args):
        return tree

    def _visit_id(self, tree: Id, *args):
        if tree.id in constant_functions:
            fun = constant_functions[tree.id]
            dummy_var = self.dummy_gen.get_dummy()
            if fun.can_be_implicit() and fun.arity() == 1:
                return Fun(dummy_var, fun([dummy_var], {}))
        return tree

    def _visit_call(self, tree: Call, *args):
        return self._default_visit_call(tree, *args)

    def _visit_fun(self, tree: Fun, *args):
        return Fun(tree.var, self.visit(tree.expr))

    def _visit_int(self, tree: IntegerLiteralCalchasExpression, *args):
        return tree

    def _visit_float(self, tree: FloatLiteralCalchasExpression, *args):
        return tree

    def _visit_constant_value(self, tree: ConstantValueExpression, *args):
        return tree

    def _visit_constant_function(self, tree: ConstantFunctionExpression, *args):
        return tree
