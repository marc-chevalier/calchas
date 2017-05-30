from .pattern import Pattern
from .abstractExpression import AbstractExpression
from typing import Optional


class Rewriting:
    def __init__(self, before: Pattern, after: AbstractExpression):
        self.before = before
        self.after = after

    def subst(self, tree) -> Optional[AbstractExpression]:
        subst = self.before.match_and_get_subst(tree)
        if subst is None:
            return None
        return subst.apply(self.after)
