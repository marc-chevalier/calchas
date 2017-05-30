from .abstractExpression import AbstractExpression
from abc import ABCMeta


class AbstractLiteralExpression(AbstractExpression, metaclass=ABCMeta):
    """
    AbstractLiteralExpression ::= IntegerLiteralExpression
    | FloatLiteralExpression
    """
    pass
