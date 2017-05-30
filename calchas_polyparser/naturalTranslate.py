from calchas_datamodel import *
from typing import List, Dict
import re


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

    natural_to_calchas = {
        r'^[aA]bs$': (lambda a, o, l: Abs(a, o)),
        r'^[mM]od$': (lambda a, o, l: Mod(a, o)),
        r'^[sS]ig(n)?$': (lambda a, o, l: Sign(a, o)),
        r'^[sS]gn$': (lambda a, o, l: Sign(a, o)),
        r'^[sS]ignum$': (lambda a, o, l: Sign(a, o)),
        r'^[pP]ow(er)?$': (lambda a, o, l: Pow(a, o)),
        r'^[sS]qrt$': (lambda a, o, l: Sqrt(a, o)),
        r'^[eE]xp$': (lambda a, o, l: Exp(a, o)),
        r'^[lL](n|og)$': (lambda a, o, l: Log(a, o)),
        r'^[lL]og10$': (lambda a, o, l: Lg(a, o)),
        r'^[lL]og2$': (lambda a, o, l: Lb(a, o)),
        r'^[lL]g$': (lambda a, o, l: Lg(a, o)),
        r'^[lL]b$': (lambda a, o, l: Lb(a, o)),
        r'^(Gamma|GAMMA)$': (lambda a, o, l: Gamma(a, o)),
        r'^[fF]act(orial)?$': (lambda a, o, l: Fact(a, o)),
        r'^[cC]os$': (lambda a, o, l: Cos(a, o)),
        r'^[sS]in$': (lambda a, o, l: Sin(a, o)),
        r'^[tT]an$': (lambda a, o, l: Tan(a, o)),
        r'^[cC](osec|sc)$': (lambda a, o, l: Csc(a, o)),
        r'^[sS]ec$': (lambda a, o, l: Sec(a, o)),
        r'^[cC]ot(an)?$': (lambda a, o, l: Cot(a, o)),
        r'^[aA](rc)?[cC]os$': (lambda a, o, l: Arccos(a, o)),
        r'^[aA](rc)?[sS]in$': (lambda a, o, l: Arcsin(a, o)),
        r'^[aA](rc)?[tT]an$': (lambda a, o, l: Arctan(a, o)),
        r'^[aA](rc)?[cC](sc|osec)$': (lambda a, o, l: Arccsc(a, o)),
        r'^[aA](rc)?[sS]ec$': (lambda a, o, l: Arcsec(a, o)),
        r'^[aA](rc)?[cC]ot(an)?$': (lambda a, o, l: Arccot(a, o)),
        r'^[cC](os)?h$': (lambda a, o, l: Cosh(a, o)),
        r'^[sS](in)?h$': (lambda a, o, l: Sinh(a, o)),
        r'^[tT](an)?h$': (lambda a, o, l: Tanh(a, o)),
        r'^[cC](osec|sc)h$': (lambda a, o, l: Csch(a, o)),
        r'^[sS]ech$': (lambda a, o, l: Sech(a, o)),
        r'^[cC]ot(an)?h$': (lambda a, o, l: Coth(a, o)),
        r'^[aA](r[cg]?)?[cC](os)?h$': (lambda a, o, l: Argcosh(a, o)),
        r'^[aA](r[cg]?)?[sS](in)?h$': (lambda a, o, l: Argsinh(a, o)),
        r'^[aA](r[cg]?)?[tT](an)?h$': (lambda a, o, l: Argtanh(a, o)),
        r'^[aA](r[cg]?)?[cC](sc|osec)h$': (lambda a, o, l: Argcsch(a, o)),
        r'^[aA](r[cg]?)?[sS]ech$': (lambda a, o, l: Argsech(a, o)),
        r'^[aA](r[cg]?)?[cC]ot(an)?h$': (lambda a, o, l: Argcoth(a, o)),
        r'^[fF]loor$': (lambda a, o, l: Floor(a, o)),
        r'^[cC]eil(ing)?$': (lambda a, o, l: Ceiling(a, o)),
        r'^[dD]igamma$': (lambda a, o, l: Digamma(a, o)),
        r'^[bB]eta$': (lambda a, o, l: Beta(a, o)),
        r'^[bB]inomial$': (lambda a, o, l: C(a, o)),
        r'^C$': (lambda a, o, l: C(a, o)),
        r'^[cC]omb(ination)?$': (lambda a, o, l: C(a, o)),
        r'^A$': (lambda a, o, l: A(a, o)),
        r'^[pP]artial[pP]ermutation$': (lambda a, o, l: A(a, o)),
        r'^[gG]c[dm]$': (lambda a, o, l: Gcd(a, o)),
        r'^[hH]cf$': (lambda a, o, l: Gcd(a, o)),
        r'^[lL]c[mM]$': (lambda a, o, l: Lcm(a, o)),
        r'^[dD](iff|eriv(e|at(e|ive)))?$': (lambda a, o, l: translate_diff(a, o, l)),
        r'^[iI]nt(egra(te|l))?$': (lambda a, o, l: translate_big_op(Integrate, a, o, l)),
        r'^[aA]ntiderivative$': (lambda a, o, l: translate_big_op(Integrate, a, o, l)),
        r'^[sS]um(mation)?': (lambda a, o, l: translate_big_op(Series, a, o, l)),
        r'^[aA]pprox(imation)?$': (lambda a, o, l: Approx(a, o)),
        r'^N$': (lambda a, o, l: Approx(a, o)),
        r'^[nN]umeric$': (lambda a, o, l: Approx(a, o)),
        r'^[eE]val(f)?$': (lambda a, o, l: Approx(a, o)),
        r'^[sS]impl(if(y|ication))?$': (lambda a, o, l: Simplify(a, o)),
        r'^[sS]ol(ve|ution(s)?)?$': (lambda a, o, l: Solve(a, o)),
        r'^[lL]im(it)?$': (lambda a, o, l: Limit(a, o)),
        r'^[nN](ot|eg)$': (lambda a, o, l: Not(a, o)),
        r'^[aA]nd$': (lambda a, o, l: And(a, o)),
        r'^[oO]r$': (lambda a, o, l: Or(a, o)),
    }

    if isinstance(function, IdExpression):
        for (pattern, translator) in natural_to_calchas.items():
            if re.match(pattern, function.get_id()):
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
