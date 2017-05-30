from calchas_datamodel.visitor import AbstractVisitor
from calchas_datamodel import AbstractExpression
from calchas_datamodel import IdExpression as Id
from calchas_datamodel import FunctionCallExpression as Call
from calchas_datamodel import FunctionExpression as Fun
from calchas_datamodel import IntegerLiteralCalchasExpression as Int
from calchas_datamodel import FloatLiteralCalchasExpression
from calchas_datamodel import ConstantValueExpression, ConstantFunctionExpression, GenericConstantFunction
from calchas_datamodel import Placeholder
from calchas_datamodel import Sum
from calchas_datamodel.dummy import DummyGen
from .transformation import Transformation
from typing import Union


class SimplifySum(Transformation):
    def __init__(self, prefix: str = "_simplify_sum_", suffix: str = ""):
        self.prefix = prefix
        self.suffix = suffix

    def set_pre_and_suffix(self, dummy_gen: DummyGen):
        dummy_gen.prefix = self.prefix
        dummy_gen.suffix = self.suffix

    def apply(self, tree: AbstractExpression, dummy_gen: DummyGen) -> AbstractExpression:
        return SimplifySumVisitor(tree, dummy_gen).visit()


class SimplifySumVisitor(AbstractVisitor):
    def __init__(self, tree: AbstractExpression, dummy_gen: DummyGen):
        super().__init__(tree)
        self.dummy_gen = dummy_gen

    def _visit_placeholder(self, tree: Placeholder, *args):
        return tree

    def _visit_id(self, tree: Id, *args):
        return tree

    def _visit_call(self, tree: Call, *args):
        def aux(t: Union[AbstractExpression, str]):
            if isinstance(t, str):
                return t
            return self.visit(tree, *args)
        d = {aux(key): aux(value) for (key, value) in tree.options}
        f = self.visit(tree.fun, *args)
        if isinstance(tree, Sum) or tree.fun == GenericConstantFunction("Sum"):
            l = []
            u = False
            for e in tree.args:
                if isinstance(e, Sum) or (isinstance(e, Call) and e.fun == GenericConstantFunction("Sum")):
                    u = True
                    for a in e.args:
                        l.append(a)
                elif e != Int(0):
                    l.append(self.visit(e, *args))
            call = Call(f, l, d)
            if u:
                return self.visit(call, *args)
            elif len(l) == 1:
                return self.visit(l[0], *args)
            return call
        return Call(f, [self.visit(e, *args) for e in tree.args], d)

    def _visit_fun(self, tree: Fun, *args):
        return Fun(tree.var, self.visit(tree.expr))

    def _visit_int(self, tree: Int, *args):
        return tree

    def _visit_float(self, tree: FloatLiteralCalchasExpression, *args):
        return tree

    def _visit_constant_value(self, tree: ConstantValueExpression, *args):
        return tree

    def _visit_constant_function(self, tree: ConstantFunctionExpression, *args):
        return tree
