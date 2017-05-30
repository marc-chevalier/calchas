from calchas_datamodel import AbstractExpression
from abc import abstractmethod, ABCMeta


class AbstractPrinter(metaclass=ABCMeta):
    @abstractmethod
    def to_str(self, tree: AbstractExpression) -> str:
        pass
