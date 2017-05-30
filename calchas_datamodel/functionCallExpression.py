from .abstractExpression import AbstractExpression
from functools import reduce
from typing import List, Dict, Union, Optional

T = Union[str, AbstractExpression]
Key_t = T
Val_t = T
Opt_t = Dict[Key_t, Val_t]


class FunctionCallExpression(AbstractExpression):
    def __init__(self,
                 fun_: AbstractExpression,
                 args_: Optional[List[AbstractExpression]] = None,
                 options_: Optional[Opt_t] = None):
        self.fun = fun_
        if args_ is None:
            self.args = []
        else:
            self.args = args_
        if options_ is None:
            self.options = {}
        else:
            self.options = options_

    def __repr__(self) -> str:
        if len(self.args) == 0:
            return '%s()' % repr(self.fun)
        str_args = [repr(e) for e in self.args]
        str_options = ["%s: %s" % (key, repr(value)) for (key, value) in self.options.items()]
        return '%s(%s)' % (repr(self.fun), (', '.join(str_args+str_options)))

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        if isinstance(other, FunctionCallExpression):
            return self.fun == other.fun and self.args == other.args and self.options == other.options
        return False

    def __hash__(self):
        return hash(hash(self.fun) + reduce((lambda x, y: x * hash(y)), self.args) +
                    reduce((lambda x, y: x * hash(y)), self.options))

    def get_fun(self) -> AbstractExpression:
        return self.fun

    def get_function(self) -> AbstractExpression:
        return self.fun

    def get_args(self) -> List[AbstractExpression]:
        return self.args

    def get_arguments(self) -> List[AbstractExpression]:
        return self.args

    def get_options(self) -> Dict[str, AbstractExpression]:
        return self.options
