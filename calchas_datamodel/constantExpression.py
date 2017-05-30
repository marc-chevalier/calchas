from .abstractExpression import AbstractExpression
from .functionCallExpression import FunctionCallExpression
from abc import ABCMeta
import typing

T = typing.Union[str, AbstractExpression]
Key_t = T
Val_t = T
Opt_t = typing.Dict[Key_t, Val_t]


class ConstantExpression(AbstractExpression, metaclass=ABCMeta):
    """Everything that is a constant in math. Like pi, or the exp function."""
    pass


class ConstantValueExpression(ConstantExpression, metaclass=ABCMeta):
    """Constant value, ie. not function."""
    pass


class GenericConstantValueExpression(ConstantValueExpression):
    """Constant values with no special information except a name.
    Most values of this type should be improved."""
    def __init__(self, name_: str):
        self.name = name_

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        return isinstance(other, GenericConstantValueExpression) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

constant_values = {}


def make_constant_value_expression(*args):
    value_name = args[0]
    obj = GenericConstantValueExpression(value_name)
    constant_values[value_name] = obj
    return obj


# Values
pi = make_constant_value_expression("pi")
infinity = make_constant_value_expression("infinity")
i = make_constant_value_expression("i")
gamma = make_constant_value_expression("gamma")
phi = make_constant_value_expression("phi")

# Sets
Reals = make_constant_value_expression("R")
Complexes = make_constant_value_expression("C")


class ConstantFunctionExpression(ConstantExpression, metaclass=ABCMeta):
    """Constant expression which are function, for instance, exp."""
    pass


class GenericConstantFunction(ConstantFunctionExpression):
    """Constant function expression with no special information except a name.
    Most values of this type should be improved."""
    def __init__(self, name_: str):
        self.name = name_

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        return isinstance(other, GenericConstantFunction) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ConstantFunctionCallExpression(FunctionCallExpression):
    """A class to ease call to a generic constant function."""
    def __init__(self,
                 fun_: AbstractExpression,
                 args_: typing.Optional[typing.List[AbstractExpression]] = None,
                 options_: typing.Optional[Opt_t] = None):
        super().__init__(fun_, args_, options_)

constant_functions = {}


def make_constant_function_call_expression(*args, **kwargs):
    class_name = args[0]
    ar = args[1]
    can_be_implicit = kwargs["implicit"] if "implicit" in kwargs else True
    function_name = args[2] if len(args) >= 3 else class_name

    def init(fun: ConstantFunctionCallExpression,
             arguments: typing.Optional[typing.List[AbstractExpression]] = None,
             options: typing.Optional[Opt_t] = None):
        super(ConstantFunctionCallExpression, fun).__init__(GenericConstantFunction(function_name), arguments, options)

    def implicit():
        return can_be_implicit

    def arity():
        return ar

    cl = type(
            class_name,
            (ConstantFunctionCallExpression, ),
            {"__init__": init,
             "can_be_implicit": implicit,
             "arity": arity,
             })

    constant_functions[function_name] = cl

    return cl

# Computation
Sum = make_constant_function_call_expression("Sum", 2)
Prod = make_constant_function_call_expression("Prod", 2)
Pow = make_constant_function_call_expression("Pow", 2)
Diff = make_constant_function_call_expression("Diff", 1)
Series = make_constant_function_call_expression("Series", 4)
BigProd = make_constant_function_call_expression("BigProd", 4)
Integrate = make_constant_function_call_expression("Integrate", 4)
Limit = make_constant_function_call_expression("Limit", 2)

# Logic
Eq = make_constant_function_call_expression("Eq", 2)
And = make_constant_function_call_expression("And", 2)
Or = make_constant_function_call_expression("Or", 2)
Not = make_constant_function_call_expression("Not", 2)

# Arithmetic
Mod = make_constant_function_call_expression("Mod", 2)
Fact = make_constant_function_call_expression("Fact", 1)
FactorInt = make_constant_function_call_expression("FactorInt", 1)
Prime = make_constant_function_call_expression("Prime", 1)
PrimeQ = make_constant_function_call_expression("PrimeQ", 1)
A = make_constant_function_call_expression("A", 2)
C = make_constant_function_call_expression("C", 2)
Gcd = make_constant_function_call_expression("gcd", 2)
Lcm = make_constant_function_call_expression("lcm", 2)

# Trigo
Sin = make_constant_function_call_expression("Sin", 1)
Cos = make_constant_function_call_expression("Cos", 1)
Tan = make_constant_function_call_expression("Tan", 1)
Csc = make_constant_function_call_expression("Csc", 1)
Sec = make_constant_function_call_expression("Sec", 1)
Cot = make_constant_function_call_expression("Cot", 1)
Arcsin = make_constant_function_call_expression("Arcsin", 1)
Arccos = make_constant_function_call_expression("Arccos", 1)
Arctan = make_constant_function_call_expression("Arctan", 1)
Arccsc = make_constant_function_call_expression("Arccsc", 1)
Arcsec = make_constant_function_call_expression("Arcsec", 1)
Arccot = make_constant_function_call_expression("Arccot", 1)

# Trigoh
Sinh = make_constant_function_call_expression("Sinh", 1)
Cosh = make_constant_function_call_expression("Cosh", 1)
Tanh = make_constant_function_call_expression("Tanh", 1)
Csch = make_constant_function_call_expression("Csch", 1)
Sech = make_constant_function_call_expression("Sech", 1)
Coth = make_constant_function_call_expression("Coth", 1)
Argsinh = make_constant_function_call_expression("Argsinh", 1)
Argcosh = make_constant_function_call_expression("Argcosh", 1)
Argtanh = make_constant_function_call_expression("Argtanh", 1)
Argcsch = make_constant_function_call_expression("Argcsch", 1)
Argsech = make_constant_function_call_expression("Argsech", 1)
Argcoth = make_constant_function_call_expression("Argcoth", 1)

# Real functions
Sqrt = make_constant_function_call_expression("Sqrt", 1)
Abs = make_constant_function_call_expression("Abs", 1)
Exp = make_constant_function_call_expression("Exp", 1)
Log = make_constant_function_call_expression("Log", 1)
Lb = make_constant_function_call_expression("Lb", 1)
Lg = make_constant_function_call_expression("Lg", 1)
Gamma = make_constant_function_call_expression("Gamma", 1)
Digamma = make_constant_function_call_expression("Digamma", 2)
Beta = make_constant_function_call_expression("Beta", 2)
Ceiling = make_constant_function_call_expression("Ceiling", 1)
Floor = make_constant_function_call_expression("Floor", 1)
Sign = make_constant_function_call_expression("Sign", 1)

# CAS directives
Approx = make_constant_function_call_expression("Approx", 1, implicit=False)
Simplify = make_constant_function_call_expression("Simplify", 1, implicit=False)
Solve = make_constant_function_call_expression("Solve", 1, implicit=False)
Expand = make_constant_function_call_expression("Expand", 1, implicit=False)
Factor = make_constant_function_call_expression("Factor", 1, implicit=False)
