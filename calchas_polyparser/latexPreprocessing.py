import ply.lex as lex

tokens = (
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'EXCL',
    'UP',
    'DOWN',
    'EQ',
    'VERT',
    'MOD',
    'ID',
    'KEYWORD',
    'INT',
    'FLOAT',
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_EXCL = r'!'
t_UP = r'\^'
t_MOD = r'\\\%'
t_EQ = r'='
t_VERT = r'\|'
t_DOWN = r'_'


def t_FLOAT(t):
    r"""([0-9]*\.[0-9]+ | [0-9]+\.[0-9]*)"""
    return t


def t_INT(t):
    r"""([0-9]+)"""
    return t


def t_ID(t):
    r"""[a-zA-Z]+"""
    return t


def t_KEYWORD(t):
    r"""\\[a-zA-Z]+"""
    return t


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'


def t_error(t):
    print(t)
    print("Ignoring it...\033[0m")
    t.lexer.skip(1)

latexPreLexer = lex.lex()

UPDOWNKEYWORD = ['UP', 'DOWN', 'KEYWORD']
MEANINGLESS = ['\\limits', '\\left', '\\right']


def preprocess_implicit_braces(formula: str) -> str:
    latexPreLexer.input(formula)
    previous = latexPreLexer.token()
    if not previous:
        return ""
    output = ""
    if previous.value not in MEANINGLESS:
        output = "%s " % previous.value
    while True:
        tok = latexPreLexer.token()
        if not tok:
            break
        if tok.value not in MEANINGLESS:
            if previous.type in UPDOWNKEYWORD and tok.type in ["FLOAT", "INT", "ID"]:
                output = '%s{%s}%s ' % (output, tok.value[0], tok.value[1:])
            elif previous.type in UPDOWNKEYWORD and tok.type in ["KEYWORD"]:
                output = '%s{%s} ' % (output, tok.value)
            else:
                output = '%s%s ' % (output, tok.value)
        previous = tok
    return output


def preprocess_implicit_times(formula: str) -> str:
    latexPreLexer.input(formula)
    previous = latexPreLexer.token()
    if not previous:
        return ""
    output = ""
    if previous.value not in MEANINGLESS:
        output = "%s " % previous.value
    while True:
        tok = latexPreLexer.token()
        if not tok:
            break
        if tok.value not in MEANINGLESS:
            if (previous.type in ["RPAREN", "RCEIL", "INT", "FLOAT"] and
                tok.type in ["LPAREN", "ID", "INT", "FLOAT", "KEYWORD"]) or \
               (previous.type in ["ID"] and tok.type in ["ID", "INT", "FLOAT"]):
                output = '%s*%s ' % (output, tok.value)
            else:
                output = '%s%s ' % (output, tok.value)
        previous = tok
    return output


def preprocess_latex(formula: str) -> str:
    return preprocess_implicit_times(
        preprocess_implicit_braces(
            formula
        )
    )
