from abc import ABCMeta, abstractmethod
from calchas_datamodel import AbstractExpression
from calchas_datamodel.dummy import DummyGen


class Transformation(metaclass=ABCMeta):
    @abstractmethod
    def set_pre_and_suffix(self, dummy_gen: DummyGen):
        pass

    @abstractmethod
    def apply(self, tree: AbstractExpression, dummy_gen: DummyGen) -> AbstractExpression:
        pass
