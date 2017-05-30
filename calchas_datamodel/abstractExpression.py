from abc import ABCMeta, abstractmethod


class AbstractExpression(metaclass=ABCMeta):
    """
    AbstractExpression ::= IdExpression   Id('x')
    | FunctionCallExpression              f(x, a: b)
    | FunctionExpression                  x -> y
    | AbstractLiteralExpression           42
    | ConstantExpression                  Pi, Sum
    | Placeholder                         _1, _2
    """

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __hash__(self):
        pass
