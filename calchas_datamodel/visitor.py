from abc import ABCMeta, abstractmethod
from .abstractExpression import AbstractExpression
from .idExpression import IdExpression
from .functionCallExpression import FunctionCallExpression
from .functionExpression import FunctionExpression
from .abstractLiteralExpression import AbstractLiteralExpression
from .integerLiteralCalchasExpression import IntegerLiteralCalchasExpression
from .floatLiteralExpression import FloatLiteralCalchasExpression
from .constantExpression import ConstantValueExpression, ConstantFunctionExpression
from .constantExpression import ConstantExpression
from .placeholder import Placeholder
from typing import Union


class UnknownType(Exception):
    pass


class AbstractVisitor(metaclass=ABCMeta):
    def __init__(self, tree_):
        self.tree = tree_

    @abstractmethod
    def _visit_placeholder(self, tree: Placeholder, *args):
        pass

    @abstractmethod
    def _visit_id(self, tree: IdExpression, *args):
        pass

    @abstractmethod
    def _visit_call(self, tree: FunctionCallExpression, *args):
        pass

    @abstractmethod
    def _visit_fun(self, tree: FunctionExpression, *args):
        pass

    @abstractmethod
    def _visit_int(self, tree: IntegerLiteralCalchasExpression, *args):
        pass

    @abstractmethod
    def _visit_float(self, tree: FloatLiteralCalchasExpression, *args):
        pass

    @abstractmethod
    def _visit_constant_value(self, tree: ConstantValueExpression, *args):
        pass

    @abstractmethod
    def _visit_constant_function(self, tree: ConstantFunctionExpression, *args):
        pass

    def _visit_literal(self, tree: AbstractLiteralExpression, *args):
        iterators = {
            IntegerLiteralCalchasExpression: self._visit_int,
            FloatLiteralCalchasExpression: self._visit_float,
        }
        for (subtype, iterator) in iterators.items():
            if isinstance(tree, subtype):
                return iterator(tree, *args)

    def _visit_constant(self, tree: ConstantExpression, *args):
        iterators = {
            ConstantValueExpression: self._visit_constant_value,
            ConstantFunctionExpression: self._visit_constant_function,
        }
        for (subtype, iterator) in iterators.items():
            if isinstance(tree, subtype):
                return iterator(tree, *args)

    def visit(self, *args):
        if len(args) > 0:
            tree = args[0]
            args = args[1:]
        else:
            tree = self.tree
        iterators = {
            IdExpression: self._visit_id,
            FunctionCallExpression: self._visit_call,
            FunctionExpression: self._visit_fun,
            AbstractLiteralExpression: self._visit_literal,
            ConstantExpression: self._visit_constant,
            Placeholder: self._visit_placeholder,
        }
        for (subtype, iterator) in iterators.items():
            if isinstance(tree, subtype):
                return iterator(tree, *args)
        print("Oh no! Unexpected type in a visitor:", end="")
        print(type(tree))
        print(repr(tree))
        print("That is not supposed to happen.\nPlease contact the dev.")
        raise UnknownType

    def _default_visit_call(self, tree: FunctionCallExpression, *args):
        def aux(t: Union[AbstractExpression, str]):
            if isinstance(t, str):
                return t
            return self.visit(tree, *args)

        return FunctionCallExpression(self.visit(tree.fun, *args),
                               [self.visit(e, *args) for e in tree.args],
                               {aux(key): aux(value) for (key, value) in tree.options})
