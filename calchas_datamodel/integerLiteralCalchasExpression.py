from .abstractLiteralExpression import AbstractLiteralExpression
from typing import TypeVar

T = TypeVar('T')


class IntegerLiteralCalchasExpression(AbstractLiteralExpression):
    def __init__(self, value_: T):
        self.value = value_

    def __repr__(self) -> str:
        return "Int(%s)" % str(self.value)

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        if type(other) == IntegerLiteralCalchasExpression:
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def get_value(self) -> T:
        return self.value
