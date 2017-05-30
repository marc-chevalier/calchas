from abc import ABCMeta, abstractmethod
from sympy import *
import typing

import calchas_datamodel


class AbstractSympyFunction(metaclass=ABCMeta):
    @abstractmethod
    def is_arity(self, nb: int) -> bool:
        pass

    @abstractmethod
    def call_function_with_unrearranged_args(self, args: typing.List[Expr],
                                             opts: typing.Dict[typing.Union[str, Expr], Expr], debug: bool = False):
        pass

    def can_be_implicit(self) -> bool:
        return False


class ArbitraryadicSympyFunction(AbstractSympyFunction):  # Arbitrary arity. Everything is possible !
    def __init__(self, sympy_function, is_arity, arrangement):
        self._sympyFunction = sympy_function
        self._isArity = is_arity
        self._arrangement = arrangement

    def is_arity(self, nb: int) -> bool:
        return self._isArity(nb)

    def call_function_with_unrearranged_args(self, args: typing.List[Expr],
                                             opts: typing.Dict[typing.Union[str, Expr], Expr], debug: bool = False):
        if debug:
            print("ArbitraryadicSympyFunction >\n    call_function_with_unrearranged_args >\n     _sympyFunction: ",
                  end="")
            print(self._sympyFunction)
            print(type(self._sympyFunction))
            print(type(type(self._sympyFunction)))
            print("ArbitraryadicSympyFunction >\n    call_function_with_unrearranged_args >\n     _arrangement(args): ",
                  end="")
            print(self._arrangement(args))
        retres = self._sympyFunction(*self._arrangement(args))
        if debug:
            print("ArbitraryadicSympyFunction >\n    call_function_with_unrearranged_args >\n     retres: ",
                  end="")
            print(retres)
            print(type(retres))
            print(retres.doit())
            print(type(retres.doit()))
        return retres


class VariadicSympyFunction(ArbitraryadicSympyFunction):  # Finite number of possible arities
    def __init__(self, sympy_function, arg_permutations: dict):
        self._sympyFunction = sympy_function
        self._arity = set(arg_permutations.keys())
        self._argPermutations = arg_permutations
        super(VariadicSympyFunction, self).__init__(sympy_function, self.is_arity, self._rearrange_arguments)

    def is_arity(self, nb: int) -> int:
        return nb in self._arity

    @property
    def sympy_function(self):
        return self._sympyFunction

    @property
    def arg_permutations(self):
        return self._argPermutations

    def _rearrange_arguments(self, args: typing.List[Expr]) -> typing.List[Expr]:
        return [args[self._argPermutations[len(args)][i]] for i in range(len(args))]

    def call_function_with_unrearranged_args(self, args: typing.List[Expr],
                                             opts: typing.Dict[typing.Union[str, Expr], Expr], debug: bool = False):
        return self._sympyFunction(*tuple(self._rearrange_arguments(args)))


class SympyFunction(VariadicSympyFunction, metaclass=ABCMeta):
    def __init__(self, sympy_function, arity: int, arg_permutation: [int]):
        VariadicSympyFunction.__init__(self, sympy_function, {arity: arg_permutation})


class StdSympyFunction(SympyFunction):
    def __init__(self, sympy_function, arity: int):
        self.arity = arity
        SympyFunction.__init__(self, sympy_function, arity, list(range(arity)))

    def can_be_implicit(self) -> bool:
        return True

    def get_arity(self):
        return self.arity


class SpecialFunction(VariadicSympyFunction):
    def __init__(self, function_id: str):
        if function_id == "C":
            VariadicSympyFunction.__init__(
                self,
                lambda x, y: Mul(gamma(Add(1, x)),
                                 Pow(
                    Mul(
                        gamma(Add(y, 1)),
                        gamma(Add(Add(x, Mul(y, -1)), 1))),
                    -1)),
                {2: [0, 1]})
        elif function_id == "A":
            VariadicSympyFunction.__init__(
                self,
                lambda x, y: Mul(gamma(Add(1, x)),
                                 Pow(gamma(Add(Add(x, Mul(y, -1)), 1), -1))),
                {2: [0, 1]})
        elif function_id == "log2":
            VariadicSympyFunction.__init__(self, lambda x: Mul(log(x), Pow(log(2), -1)), {1: [0]})
        elif function_id == "log10":
            VariadicSympyFunction.__init__(self, lambda x: Mul(log(x), Pow(log(10), -1)), {1: [0]})
        elif function_id == "factorial":
            VariadicSympyFunction.__init__(self, lambda x: gamma(Add(x, 1)), {1: [0]})


class OptionFunction(AbstractSympyFunction):
    def __init__(self, sympy_function):
        self.sympy_function = sympy_function

    @abstractmethod
    def _merge_args_opts(self, args: typing.List[Expr],
                         opts: typing.Dict[typing.Union[str, Expr], Expr], debug: bool = False) -> typing.List[Expr]:
        pass

    def call_function_with_unrearranged_args(self, args: typing.List[Expr],
                                             opts: typing.Dict[typing.Union[str, Expr], Expr], debug: bool = False):
        return self.sympy_function(*tuple(self._merge_args_opts(args, opts)))


class LimitFunction(OptionFunction):
    def __init__(self):
        super(LimitFunction, self).__init__(limit)

    def is_arity(self, nb: int) -> bool:
        return nb == 1 or (nb - 1) % 2 == 0

    def _merge_args_opts(self, args: typing.List[Expr],
                         opts: typing.Dict[typing.Union[str, Expr], Expr], debug: bool = False):
        for k, v in opts.items():
            args.append(k)
            args.append(v)
        return args


class IntegrateSympyFunction(ArbitraryadicSympyFunction):
    def __init__(self):
        ArbitraryadicSympyFunction.__init__(self, integrate, self.is_integrate_arity, self.integrate_arrangement)

    @staticmethod
    def is_integrate_arity(nb: int) -> bool:
        return nb == 2 or (nb > 3 and (nb-1) % 3 == 0)

    @staticmethod
    def integrate_arrangement(args: tuple) -> tuple:
        if len(args) == 2:
            return args
        else:
            return (args[0],)+tuple((args[3*i+1], (args[3*i+2], args[3*i+3])) for i in range((len(args)-1)//3))


class SumProdSympyFunction(ArbitraryadicSympyFunction):
    def __init__(self, sympy_function):
        ArbitraryadicSympyFunction.__init__(self, sympy_function, self.is_sum_prod_arity, self.sum_prod_arrangement)

    @staticmethod
    def is_sum_prod_arity(nb: int) -> bool:
        return nb > 3 and (nb-1) % 3 == 0

    @staticmethod
    def sum_prod_arrangement(args: tuple) -> tuple:
        if len(args) == 2:
            return args
        else:
            return (args[0],)+tuple((args[3*i+1], args[3*i+2], args[3*i+3]) for i in range((len(args)-1)//3))


class DiffSympyFunction(ArbitraryadicSympyFunction):
    def __init__(self):
        ArbitraryadicSympyFunction.__init__(self, diff, self.is_diff_arity, self.diff_arrangement)

    @staticmethod
    def is_diff_arity(nb: int) -> bool:
        return type(nb) == int

    @staticmethod
    def diff_arrangement(args: tuple) -> tuple:
        return args

# solve


base_constants = {calchas_datamodel.pi: pi,
                  calchas_datamodel.infinity: oo,
                  calchas_datamodel.phi: GoldenRatio,
                  calchas_datamodel.i: I,
                  calchas_datamodel.gamma: EulerGamma,
                  }

base_functions = {calchas_datamodel.A: SpecialFunction("A"),
                  calchas_datamodel.Abs: StdSympyFunction(Abs, 1),
                  calchas_datamodel.Arccos: StdSympyFunction(acos, 1),
                  calchas_datamodel.Argcsch: StdSympyFunction(acosh, 1),
                  calchas_datamodel.Arccot: StdSympyFunction(acot, 1),
                  calchas_datamodel.Argcoth: StdSympyFunction(acot, 1),
                  calchas_datamodel.And: StdSympyFunction(And, 2),
                  calchas_datamodel.Arcsin: StdSympyFunction(asin, 1),
                  calchas_datamodel.Argsinh: StdSympyFunction(asinh, 1),
                  calchas_datamodel.Arctan: StdSympyFunction(atan, 1),
                  calchas_datamodel.Argtanh: StdSympyFunction(atanh, 1),
                  calchas_datamodel.Beta: StdSympyFunction(beta, 1),
                  calchas_datamodel.C: SpecialFunction("C"),
                  calchas_datamodel.Ceiling: StdSympyFunction(ceiling, 1),
                  calchas_datamodel.Cos: StdSympyFunction(cos, 1),
                  calchas_datamodel.Cosh: StdSympyFunction(cosh, 1),
                  calchas_datamodel.Cot: StdSympyFunction(cot, 1),
                  calchas_datamodel.Coth: StdSympyFunction(coth, 1),
                  calchas_datamodel.Csc: StdSympyFunction(csc, 1),
                  calchas_datamodel.Diff: DiffSympyFunction(),
                  calchas_datamodel.Digamma: StdSympyFunction(digamma, 1),
                  calchas_datamodel.Eq: StdSympyFunction(Eq, 2),
                  #   calchas_datamodel.Erf: StdSympyFunction(erf, 1),
                  calchas_datamodel.Exp: StdSympyFunction(exp, 1),
                  calchas_datamodel.Expand: StdSympyFunction(expand, 1),
                  calchas_datamodel.Factor: StdSympyFunction(factor, 1),
                  calchas_datamodel.Fact: SpecialFunction("factorial"),
                  calchas_datamodel.FactorInt: StdSympyFunction(factorint, 1),
                  calchas_datamodel.Floor: StdSympyFunction(floor, 1),
                  calchas_datamodel.Gamma: StdSympyFunction(gamma, 1),
                  calchas_datamodel.Gcd: StdSympyFunction(gcd, 2),
                  calchas_datamodel.Integrate: IntegrateSympyFunction(),
                  #   calchas_datamodel.isPrime: StdSympyFunction(isprime, 1),
                  #   calchas_datamodel.Lambda": StdSympyFunction(Lambda, 2),
                  calchas_datamodel.Lcm: StdSympyFunction(lcm, 2),
                  calchas_datamodel.Limit: LimitFunction(),
                  #   calchas_datamodel.limitl: CompoundFunction("limitl"),
                  #   calchas_datamodel.limitr: CompoundFunction("limitr"),
                  calchas_datamodel.Log: VariadicSympyFunction(log, {1: [0], 2: [0, 1]}),
                  calchas_datamodel.Lb: SpecialFunction("log2"),
                  calchas_datamodel.Lg: SpecialFunction("log10"),
                  calchas_datamodel.Mod: StdSympyFunction(Mod, 2),
                  calchas_datamodel.Approx: VariadicSympyFunction(N, {1: [0], 2: [0, 1]}),
                  calchas_datamodel.Not: StdSympyFunction(Not, 1),
                  calchas_datamodel.Or: StdSympyFunction(Or, 2),
                  calchas_datamodel.Pow: StdSympyFunction(Pow, 2),
                  calchas_datamodel.Prime: StdSympyFunction(prime, 1),
                  calchas_datamodel.BigProd: SumProdSympyFunction(prod),
                  #   calchas_datamodel.satisfiable": StdSympyFunction(satisfiable, 1),
                  calchas_datamodel.Sec: StdSympyFunction(sec, 1),
                  calchas_datamodel.Sech: StdSympyFunction(sech, 1),
                  calchas_datamodel.Sign: StdSympyFunction(sign, 1),
                  calchas_datamodel.Simplify: VariadicSympyFunction(simplify, {1: [0], 2: [0, 1]}),
                  calchas_datamodel.Sin: StdSympyFunction(sin, 1),
                  calchas_datamodel.Sinh: StdSympyFunction(sinh, 1),
                  calchas_datamodel.Solve: StdSympyFunction(solve, 2),
                  calchas_datamodel.Series: SumProdSympyFunction(summation),
                  calchas_datamodel.Sqrt: StdSympyFunction(sqrt, 1),
                  calchas_datamodel.Sum: ArbitraryadicSympyFunction(Add, lambda n: True, lambda x: x),
                  calchas_datamodel.Prod: ArbitraryadicSympyFunction(Mul, lambda n: True, lambda x: x),
                  calchas_datamodel.Tan: StdSympyFunction(tan, 1),
                  calchas_datamodel.Tanh: StdSympyFunction(tanh, 1),
                  }

base_functions = {k().fun: v for (k, v) in base_functions.items()}
