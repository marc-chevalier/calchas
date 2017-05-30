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

    latex_to_calchas = {
        'sqrt': (lambda a, o, l: Sqrt(a, o)),
        'sin': (lambda a, o, l: Sin(a, o)),
        'cos': (lambda a, o, l: Cos(a, o)),
        'tan': (lambda a, o, l: Tan(a, o)),
        'arcsin': (lambda a, o, l: Arcsin(a, o)),
        'arccos': (lambda a, o, l: Arccos(a, o)),
        'arctan': (lambda a, o, l: Arctan(a, o)),
        'sum': (lambda a, o, l: translate_big_op(Series, a, o, l)),
        'integrate': (lambda a, o, l: translate_big_op(Integrate, a, o, l)),
        'N': (lambda a, o, l: Approx(a, o)),
        'D': (lambda a, o, l: translate_diff(a, o, l)),
        'exp': (lambda a, o, l: Exp(a, o)),
        'simplify': (lambda a, o, l: Simplify(a, o)),
        'power': (lambda a, o, l: Pow(a, o)),
        'log': (lambda a, o, l: Log(a, o)),
        'log10': (lambda a, o, l: Lg(a, o)),
        'log2': (lambda a, o, l: Lb(a, o)),
        'factorial': (lambda a, o, l: Fact(a, o)),
        'abs': (lambda a, o, l: Abs(a, o)),
        'ceiling': (lambda a, o, l: Ceiling(a, o)),
        'floor': (lambda a, o, l: Floor(a, o)),
        'limit': (lambda a, o, l: Limit(a, o)),
        'solve': (lambda a, o, l: Solve(a, o)),
        'expand': (lambda a, o, l: Expand(a, o)),
        'factor': (lambda a, o, l: Factor(a, o)),
        'prime': (lambda a, o, l: Prime(a, o)),
        'primeQ': (lambda a, o, l: PrimeQ(a, o)),
    }

    if isinstance(function, IdExpression):
        for (name, translator) in latex_to_calchas.items():
            if name == function.get_id():
                return translator(args, options, lists)

    return FunctionCallExpression(function, args + [item for sublist in lists for item in sublist], options)


def translate_id(pre_id: str) -> IdExpression:
    mathematica_to_calchas = {'\\infty': infinity,
                              'I': i,
                              '\\pi': pi,
                              '\\varphi': phi,
                              '\\gamma': gamma,
                              }
    return mathematica_to_calchas.get(pre_id, IdExpression(pre_id))
