import ply.lex as lex

tokens = (
    'INT',
    'FLOAT',
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
    'ID',
    'EXCL',
    'POW',
    'ARROW',
    'EQ',
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
t_POW = r'\^'
t_ARROW = r'->'
t_EQ = r'=='


def t_FLOAT(t):
    r"""([0-9]*\.[0-9]+ | [0-9]+\.[0-9]*)"""
    return t


def t_INT(t):
    r"""([0-9]+)"""
    return t


def t_ID(t):
    r"""[a-zA-Z][a-zA-Z0-9]*"""
    return t


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'


def t_error(t):
    print("\033[91mWTF is this?! (mathematicaLex.py:64)")
    print(t)
    print("Ignoring it...\033[0m")
    t.lexer.skip(1)

mathematicaLexer = lex.lex()
