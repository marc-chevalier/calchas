import typing
import ply.yacc as yacc
from .latexLex import tokens, latexLexer
from .latexPreprocessing import preprocess_latex
from .latexTranslate import translate_call, translate_id
from calchas_datamodel import Sum, Prod, Pow, Fact, IntegerLiteralCalchasExpression as Int, \
    FloatLiteralCalchasExpression as Float, Ceiling, Floor, Abs, C, Sqrt, Cos, Sin, Log, Exp, Tan, Series, BigProd, \
    Integrate, Limit, Mod, AbstractExpression

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
    """primary_expression : LPAREN expression RPAREN
                          | LBRACE expression RBRACE
                          | LFLOOR expression RFLOOR
                          | LCEIL  expression RCEIL
                          | VERT   expression VERT """
    #  0                    1      2          3
    token_to_func = {'\\lceil': Ceiling,
                     '\\lfloor': Floor,
                     '\\vert': Abs,
                     }
    if p[1] in ['(', '{']:
        p[0] = p[2]
    else:
        p[0] = token_to_func[p[1]]([p[2]], {})


def p_postfix_expression_call(p):
    """postfix_expression_call : postfix_expression LPAREN argument_list RPAREN
                               | postfix_expression LPAREN RPAREN
                               """
    #  0                         1                  2      3             4
    if len(p) == 5:
        args, opts = p[3]
        lists = []
    else:
        args, opts, lists = [], {}, []
    p[0] = translate_call(p[1], args, opts, lists)


def p_postfix_expression_fact(p):
    """postfix_expression_fact : postfix_expression EXCL"""
    #  0                         1                  2

    p[0] = Fact([p[1]], {})


def p_postfix_expression_binary(p):
    """postfix_expression_binary : BINARY LBRACE argument_list RBRACE LBRACE argument_list RBRACE"""
    #  0                           1      2      3             4      5      6             7
    if p[1] == '\\frac':
        p[0] = Prod([p[3][0][0], Pow([p[6][0][0], Int(-1)], {})], {})
    elif p[1] == '\\binom':
        p[0] = C([p[3][0][0], p[6][0][0]], {})


def p_postfix_expression_unary(p):
    """postfix_expression_unary : UNARY LBRACKET argument_list RBRACKET LBRACE argument_list RBRACE
                                | UNARY LBRACE   argument_list RBRACE
                                | UNARY LPAREN   argument_list RPAREN
                                | UNARY ID
                                """
    #  0                          1     2          3             4        5      6             7
    token_to_func = {'\\sqrt': Sqrt,
                     '\\log': Log,
                     '\\exp': Exp,
                     '\\cos': Cos,
                     '\\sin': Sin,
                     '\\tan': Tan,
                     }
    if len(p) == 8:
        if p[1] == '\\sqrt':
            p[0] = Pow([p[6][0][0], Pow([p[3][0][0], Int(-1)], {})], {})
    elif len(p) == 5:
        p[0] = token_to_func[p[1]](*p[3])
    else:
        p[0] = token_to_func[p[1]]([p[2]], {})


def p_postfix_expression(p):
    """postfix_expression : postfix_expression_call
                          | postfix_expression_fact
                          | postfix_expression_binary
                          | postfix_expression_unary
                          | primary_expression
                          """
    #  0                    1
    p[0] = p[1]


def p_argument_list(p):
    """argument_list : argument
                     | argument COMMA argument_list"""
    #  0               1        2     3
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1][0] + p[3][0], {**p[1][1], **p[3][1]}


def p_argument(p):
    """argument : expression"""
    #  0          1
    p[0] = [p[1]], {}


def p_pow_expression(p):
    """pow_expression : postfix_expression POW LBRACE expression RBRACE
                      | postfix_expression
                      """
    #  0                1                  2   3      4          5
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Pow([p[1], p[4]], {})


def p_expr_unary(p):
    """unary_expression : MINUS          unary_expression %prec NEG
                        | PLUS           unary_expression %prec NEG
                        | pow_expression
                        """
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
                                 | multiplicative_expression MOD    unary_expression
                                 | BIGPROD DOWN LBRACE ID EQ expression RBRACE POW LBRACE expression RBRACE unary_expression
                                 | unary_expression
                                 """
    #  0                           1       2    3      4  5  6          7      8  9      10         11     12
    if len(p) == 13:
            p[0] = BigProd([p[12], translate_id(p[4]), p[6], p[10]], {})
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] in ['*', '\\times']:
            p[0] = Prod([p[1], p[3]], {})
        elif p[2] == '/':
            p[0] = Prod([p[1], Pow([p[3], Int(-1)], {})], {})
        elif p[2] == '\\%':
            p[0] = Mod([p[1], p[3]], {})


def p_additive_expression(p):
    """additive_expression : additive_expression       PLUS  multiplicative_expression
                           | additive_expression       MINUS multiplicative_expression
                           | BIGSUM DOWN LBRACE ID EQ expression RBRACE POW LBRACE expression RBRACE multiplicative_expression
                           | BIGINT DOWN LBRACE ID EQ expression RBRACE POW LBRACE expression RBRACE multiplicative_expression
                           | multiplicative_expression
                           """
    #  0                     1      2    3      4  5  6          7      8   9      10         11     12
    if len(p) == 13:
        if p[1] == "\\int":
            p[0] = Integrate([p[12], translate_id(p[4]), p[6], p[10]], {})
        else:
            p[0] = Series([p[12], translate_id(p[4]), p[6], p[10]], {})
    elif len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == '+':
            p[0] = Sum([p[1], p[3]], {})
        elif p[2] == '-':
            p[0] = Sum([p[1], Prod([Int(-1), p[3]], {})], {})


def p_limit_expression(p):
    """limit_expression : LIMIT DOWN LBRACE ID TO expression RBRACE additive_expression
                        | additive_expression"""
    #  0                  1     2    3      4  5  6          7      8
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Limit([p[8], translate_id(p[4]), p[6]], {})


def p_expression(p):
    """expression : limit_expression"""
    p[0] = p[1]


def p_error(p):
    pass

latexParser = yacc.yacc(debug=True, write_tables=False, optimize=True)


def parse_latex(s: str, debug: bool = False) -> typing.Optional[AbstractExpression]:
    return latexParser.parse(preprocess_latex(s), lexer=latexLexer, debug=debug)
