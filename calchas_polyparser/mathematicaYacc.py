import typing
import ply.yacc as yacc
from .mathematicaLex import tokens, mathematicaLexer
from .mathematicaTranslate import translate_call, translate_id
from calchas_datamodel import Sum, Prod, Pow, Fact, IntegerLiteralCalchasExpression as Int, \
    FloatLiteralCalchasExpression as Float, Eq, AbstractExpression

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'POW'),
    ('right', 'NEG'),
)

start = 'expression'


def p_primary_expression_int(p):
    """primary_expression : INT"""
    p[0] = Int(p[1])


def p_primary_expression_float(p):
    """primary_expression : FLOAT"""
    p[0] = Float(p[1])


def p_primary_expression_id(p):
    """primary_expression : ID"""
    p[0] = translate_id(p[1])


def p_primary_expression_paren(p):
    """primary_expression : LPAREN expression RPAREN"""
    #  0                    1      2          3
    p[0] = p[2]


def p_postfix_expression(p):
    """postfix_expression : postfix_expression LBRACKET argument_list RBRACKET
                          | postfix_expression LBRACKET RBRACKET
                          | postfix_expression EXCL
                          | primary_expression """
    #  0                    1                  2        3             4
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = Fact([p[1]], {})
    else:
        if len(p) == 5:
            args, opts, lists = p[3]
        else:
            args, opts, lists = [], {}, []
        p[0] = translate_call(p[1], args, opts, lists)


def p_argument_list(p):
    """argument_list : argument
                     | argument COMMA argument_list"""
    #  0               1        2     3
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1][0] + p[3][0], {**p[1][1], **p[3][1]}, p[1][2] + p[3][2]


def p_argument(p):
    """argument : expression
                | expression_list
                | ID              ARROW expression"""
    #  0          1               2     3
    if len(p) == 2:
        if isinstance(p[1], list):
            p[0] = [], {}, [p[1]]
        else:
            p[0] = [p[1]], {}, []
    else:
        p[0] = [], {translate_id(p[1]): p[3]}, []


def p_pow_expression(p):
    """pow_expression : postfix_expression POW pow_expression
                      | postfix_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Pow([p[1], p[3]], {})


def p_expr_unary(p):
    """unary_expression : MINUS          unary_expression %prec NEG
                        | PLUS           unary_expression %prec NEG
                        | pow_expression """
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[1] == '-':
            p[0] = Prod([Int(-1), p[2]], {})
        else:
            p[0] = p[2]


def p_multiplicative_expression(p):
    """multiplicative_expression : multiplicative_expression TIMES  unary_expression
                                 | multiplicative_expression DIVIDE unary_expression
                                 | unary_expression """
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == '*':
            p[0] = Prod([p[1], p[3]], {})
        elif p[2] == '/':
            p[0] = Prod([p[1], Pow([p[3], Int(-1)], {})], {})


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
    """equality_expression : additive_expression EQ additive_expression
                           | additive_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Eq([p[1], p[3]], {})


def p_expression(p):
    """expression : equality_expression"""
    p[0] = p[1]


def p_expression_list(p):
    """expression_list : LBRACE expression_seq RBRACE
                       | LBRACE RBRACE"""
    #  0                 1      2              3
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []


def p_expression_seq(p):
    """expression_seq : expression COMMA expression_seq
                      | expression"""
    if len(p) == 4:
        p[0] = [p[1]]+p[3]
    else:
        p[0] = [p[1]]


def p_error(p):
    pass

mathematicaParser = yacc.yacc(debug=True, write_tables=False, optimize=True)


def parse_mathematica(s: str, debug: bool = False) -> typing.Optional[AbstractExpression]:
    return mathematicaParser.parse(s, lexer=mathematicaLexer, debug=debug)
