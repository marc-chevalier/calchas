from calchas_datamodel import AbstractExpression
from .abstract_printer import AbstractPrinter


class DefaultPrinter(AbstractPrinter):
    def to_str(self, tree: AbstractExpression) -> str:
        return repr(tree)
