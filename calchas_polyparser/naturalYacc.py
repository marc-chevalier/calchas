import typing
import ply.yacc as yacc
from .naturalLex import tokens, naturalLexer
from .naturalTranslate import translate_call, translate_id
from .naturalPreprocessing import preprocess_natural
from calchas_datamodel.dummy import DummyGen
from calchas_datamodel import Sum, Prod, Pow, Fact, IntegerLiteralCalchasExpression as Int, \
    FloatLiteralCalchasExpression as Float, Eq, And, Or, Not, Diff, Mod, FormulaFunctionExpression as Fun, \
    IdExpression as Id, FunctionCallExpression as Call, AbstractExpression

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'POW'),
    ('right', 'NEG'),
)

start = 'expression'
dummy_gen = DummyGen(prefix="_d")


def p_primary_expression_int(p):
    """primary_expression : INT"""
    p[0] = Int(p[1])


def p_primary_expression_float(p):
    """primary_expression : FLOAT"""
    p[0] = Float(p[1])


def p_primary_expression_id(p):
    """primary_expression : ID"""
    dummy_gen.add_vars(str(p[1]))
    p[0] = translate_id(p[1])


def p_primary_expression_paren(p):
    """primary_expression : LPAREN expression RPAREN"""
    #  0                    1      2          3
    p[0] = p[2]


def p_postfix_expression(p):
    """postfix_expression : postfix_expression list_apostrophe LPAREN        argument_list RPAREN
                          | postfix_expression LPAREN          argument_list RPAREN
                          | postfix_expression LPAREN          RPAREN
                          | postfix_expression EXCL
                          | primary_expression """
    #  0                    1                  2               3             4             5
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = Fact([p[1]], {})
    else:
        if len(p) == 6:
            args, opts, lists = p[4]
            call = translate_call(p[1], args, opts, lists)
            fun = call.get_fun()
            args = call.get_args()
            opts = call.get_options()
            dummy = dummy_gen.get_dummy()
            lambda_fn = Fun(dummy, Call(fun, [dummy], opts))
            diff_fn = Diff([lambda_fn, Int(p[2])], {})
            p[0] = Call(diff_fn, args, opts)
        else:
            if len(p) == 5:
                args, opts, lists = p[3]
            else:
                args, opts, lists = [], {}, []
            p[0] = translate_call(p[1], args, opts, lists)


def p_list_apostrophe(p):
    """list_apostrophe : APOSTROPHE list_apostrophe
                       | APOSTROPHE"""
    if len(p) == 2:
        p[0] = 1
    else:
        p[0] = p[2]+1


def p_argument_list(p):
    """argument_list : argument
                     | argument COMMA argument_list"""
    #  0               1        2     3
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1][0] + p[3][0], {**p[1][1], **p[3][1]}, p[1][2] + p[3][2]


def p_argument(p):
    """argument : expression"""
    #  0          1               2     3
    if len(p) == 2:
        if isinstance(p[1], list):
            p[0] = [], {}, [p[1]]
        else:
            p[0] = [p[1]], {}, []
    else:
        p[0] = [], {p[1]: p[3]}, []


def p_pow_expression(p):
    """pow_expression : postfix_expression POW    pow_expression
                      | postfix_expression DTIMES pow_expression
                      | postfix_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Pow([p[1], p[3]], {})


def p_expr_unary(p):
    """unary_expression : MINUS          unary_expression %prec NEG
                        | PLUS           unary_expression %prec NEG
                        | NOT            unary_expression %prec NEG
                        | pow_expression """
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[1] == '-':
            p[0] = Prod([Int(-1), p[2]], {})
        elif p[1] == '+':
            p[0] = p[2]
        else:
            p[0] = Not([p[2]], {})


def p_multiplicative_expression(p):
    """multiplicative_expression : multiplicative_expression TIMES  unary_expression
                                 | multiplicative_expression DIVIDE unary_expression
                                 | multiplicative_expression MOD unary_expression
                                 | unary_expression """
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == '*':
            p[0] = Prod([p[1], p[3]], {})
        elif p[2] == '/':
            p[0] = Prod([p[1], Pow([p[3], Int(-1)], {})], {})
        elif p[2] == '%':
                p[0] = Mod([p[1], p[3]], {})


def p_additive_expression(p):
    """additive_expression : additive_expression       PLUS  multiplicative_expression
                           | additive_expression       MINUS multiplicative_expression
                           | multiplicative_expression """
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == '+':
            p[0] = Sum([p[1], p[3]], {})
        elif p[2] == '-':
            p[0] = Sum([p[1], Prod([Int(-1), p[3]], {})], {})


def p_equality_expression(p):
    """equality_expression : equality_expression EQ additive_expression
                           | equality_expression EQ EQ additive_expression
                           | additive_expression"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = Eq([p[1], p[3]], {})
    else:
        p[0] = Eq([p[1], p[4]], {})


def p_and_expression(p):
    """and_expression : and_expression AND equality_expression
                      | equality_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = And([p[1], p[3]], {})


def p_or_expression(p):
    """or_expression : or_expression OR and_expression
                     | and_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Or([p[1], p[3]], {})


def p_expression(p):
    """expression : or_expression"""
    p[0] = p[1]


def p_error(p):
    pass


naturalParser = yacc.yacc(debug=True, write_tables=False, optimize=True)


def parse_natural(expr: str) -> typing.Optional[AbstractExpression]:
    dummy_gen.reset()
    return naturalParser.parse(preprocess_natural(expr), lexer=naturalLexer)
