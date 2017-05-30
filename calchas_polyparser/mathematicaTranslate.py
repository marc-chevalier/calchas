from calchas_datamodel import *
from typing import List, Dict


def translate_call(function: AbstractExpression,
                   args: List[AbstractExpression],
                   options: Dict[str, AbstractExpression],
                   lists: List[List[AbstractExpression]]) -> FunctionCallExpression:
    def translate_big_op(function_,
                         args_: List[AbstractExpression],
                         options_: Dict[str, AbstractExpression],
                         lists_: List[List[AbstractExpression]]) -> FunctionCallExpression:
        if len(lists_) == 0:
            return function_(args_, options_)
        if len(lists_) == 1:
            return function_(args_+list(lists_[0]), options_)
        expr = translate_big_op(function_, args_, options_, lists_[1:])
        return function_([expr]+list(lists_[0]), options_)

    def translate_diff(args_: List[AbstractExpression],
                       options_: Dict[str, AbstractExpression],
                       lists_: List[List[AbstractExpression]]) -> FunctionCallExpression:
        if len(lists) == 0:
            return Diff(args_, options_)
        expr = translate_diff(args_, options_, lists_[1:])
        Diff([expr]+[lists_[0]], options_)

    mathematica_to_calchas = {
        'Sqrt': (lambda a, o, l: Sqrt(a, o)),
        'Sin': (lambda a, o, l: Sin(a, o)),
        'Cos': (lambda a, o, l: Cos(a, o)),
        'Tan': (lambda a, o, l: Tan(a, o)),
        'Arcsin': (lambda a, o, l: Arcsin(a, o)),
        'Arccos': (lambda a, o, l: Arccos(a, o)),
        'Arctan': (lambda a, o, l: Arctan(a, o)),
        'Sum': (lambda a, o, l: translate_big_op(Series, a, o, l)),
        'Integrate': (lambda a, o, l: translate_big_op(Integrate, a, o, l)),
        'N': (lambda a, o, l: Approx(a, o)),
        'D': (lambda a, o, l: translate_diff(a, o, l)),
        'Exp': (lambda a, o, l: Exp(a, o)),
        'Simplify': (lambda a, o, l: Simplify(a, o)),
        'Power': (lambda a, o, l: Pow(a, o)),
        'Log': (lambda a, o, l: Log(a, o)),
        'Log10': (lambda a, o, l: Lg(a, o)),
        'Log2': (lambda a, o, l: Lb(a, o)),
        'Factorial': (lambda a, o, l: Fact(a, o)),
        'Abs': (lambda a, o, l: Abs(a, o)),
        'Ceiling': (lambda a, o, l: Ceiling(a, o)),
        'Floor': (lambda a, o, l: Floor(a, o)),
        'Limit': (lambda a, o, l: Limit(a, o)),
        'Solve': (lambda a, o, l: Solve(a, o)),
        'Expand': (lambda a, o, l: Expand(a, o)),
        'Factor': (lambda a, o, l: Factor(a, o)),
        'Prime': (lambda a, o, l: Prime(a, o)),
        'PrimeQ': (lambda a, o, l: PrimeQ(a, o)),
    }

    if isinstance(function, IdExpression):
        for (name, translator) in mathematica_to_calchas.items():
            if name == function.get_id():
                return translator(args, options, lists)

    return FunctionCallExpression(function, args + [item for sublist in lists for item in sublist], options)


def translate_id(pre_id: str) -> IdExpression:
    mathematica_to_calchas = {'Infinity': infinity,
                              'I': i,
                              'Pi': pi,
                              'GoldenRatio': phi,
                              'EulerGamma': gamma,
                              }
    return mathematica_to_calchas.get(pre_id, IdExpression(pre_id))
