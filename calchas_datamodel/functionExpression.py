from abc import ABCMeta, abstractmethod
from .abstractExpression import AbstractExpression


class FunctionExpression(AbstractExpression, metaclass=ABCMeta):
    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def apply(self, e: AbstractExpression) -> AbstractExpression:
        pass
