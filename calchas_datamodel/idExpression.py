from .abstractExpression import AbstractExpression
from typing import TypeVar

T = TypeVar('T')


class IdExpression(AbstractExpression):
    def __init__(self, id_: T):
        self.id = id_

    def __repr__(self) -> str:
        return str(self.id)

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        if type(other) == IdExpression:
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def get_id(self) -> T:
        return self.id
