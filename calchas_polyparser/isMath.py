import re

from calchas_datamodel import AutoEnum

CARACTERISTIC_SYMBOLS = ['sqrt'] + list(r'*+!\_^[]{}%')
LATEX_CARACTERISTIC_SYMBOLS = ['\\']
MAYBE_CARACTERISTIC_SYMBOLS = list(r'-/()0123456789=')
ANTI_CARACTERISTIC_SYMBOLS = list(r'?"éàèùçÉÀÈÙÇâêîôûäëïöüÂÊÎÔÛÄËÏÖÜñ')
ANTI_CARACTERISTIC_WORDS = ['Who', 'who', 'Whom', 'whom', 'When', 'when', 'What', 'what', 'Where', 'where', 'Which',
                            'which', 'How', 'how', 'Why', 'why', 'is', 'Is', 'of', 'in', 'the']
ANTI_CARACTERISTIC_REGEX = ['sum', 'derivative', 'product', 'limit', 'antiderivative', 'integrate', 'approx',
                            'approximation']


class IsMath(AutoEnum):
    No = ()
    Maybe = ()
    Yes = ()


def is_math(formula: str) -> IsMath:
    is_caract = any(e in formula for e in CARACTERISTIC_SYMBOLS)
    is_anti = any(e+' ' in formula for e in ANTI_CARACTERISTIC_WORDS)
    is_anti = is_anti or any(e in formula for e in ANTI_CARACTERISTIC_SYMBOLS)
    is_anti = is_anti or any(re.search(r'%s\s+[^(]' % e, formula) is not None for e in ANTI_CARACTERISTIC_REGEX)
    if is_caract and not is_anti:
        return IsMath.Yes
    if is_anti:
        return IsMath.No
    if re.fullmatch(r'[A-Za-z ]+\??', formula):
        return IsMath.No
    if any(e in formula for e in MAYBE_CARACTERISTIC_SYMBOLS):
        return IsMath.Yes
    return IsMath.Maybe


def is_latex(formula):
    return any(e in formula for e in LATEX_CARACTERISTIC_SYMBOLS)


def is_interesting(input_formula, output_formula):
    for match in re.finditer(r"(?P<base>[a-zA-Z]+)\*\*(?P<exp>\d+)", output_formula):
        output_formula = output_formula.replace('%s**%s' % (match.group("base"), match.group("exp")),
                                                match.group("base")*int(match.group("exp")))
    forbiden_char = list(r' .*+')
    for c in forbiden_char:
        input_formula = input_formula.replace(c, "")
    input_formula = sorted(input_formula)
    for c in forbiden_char:
        output_formula = output_formula.replace(c, "")
    output_formula = sorted(output_formula)
    return input_formula != output_formula


def relevance(input_string, output_string):
    len_output = len(output_string)
    if len_output != 0:
        return len(input_string)/len_output
    return 0
