from typing import TypeVar
from .abstractExpression import AbstractExpression

T = TypeVar('T')


class Placeholder(AbstractExpression):
    def __init__(self, id_: T):
        self.id = id_

    def __repr__(self) -> str:
        return "_(%s)" % self.id

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        return isinstance(other, Placeholder) and self.id == other.id

    def __hash__(self):
        return hash(self.id)
