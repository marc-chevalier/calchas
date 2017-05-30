from typing import Dict
from .functionExpression import FunctionExpression
from .abstractExpression import AbstractExpression
from .visitor import AbstractVisitor
from .functionCallExpression import FunctionCallExpression
from .integerLiteralCalchasExpression import IntegerLiteralCalchasExpression
from .floatLiteralExpression import FloatLiteralCalchasExpression
from .constantExpression import ConstantValueExpression, ConstantFunctionExpression
from .placeholder import Placeholder
from .idExpression import IdExpression


class DictFunctionExpression(FunctionExpression):
    def __init__(self, d: Dict[AbstractExpression, AbstractExpression]):
        self.d = d.copy()

    def __repr__(self) -> str:
        return repr(self.d)

    def __eq__(self, other) -> bool:
        if other is self:
            return True
        if isinstance(other, DictFunctionExpression):
            return self.d == other.d
        return False

    def __hash__(self):
        pass

    def apply(self, e: AbstractExpression) -> AbstractExpression:
        pass
