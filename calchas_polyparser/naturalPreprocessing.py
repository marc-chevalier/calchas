from .naturalLex import naturalLexer


def preprocess_implicit_multiplication(formula: str) -> str:
    naturalLexer.input(formula)
    previous = naturalLexer.token()
    output = previous.value
    while True:
        tok = naturalLexer.token()
        if not tok:
            break
        if (previous.type == 'RPAREN' and tok.type == 'LPAREN') or \
           (previous.type == 'RPAREN' and tok.type in ['ID', 'FLOAT', 'INT']) or \
           (previous.type in ['FLOAT', 'INT'] and tok.type == 'LPAREN') or \
           (previous.type in ['ID', 'FLOAT', 'INT'] and tok.type in ['ID', 'FLOAT', 'INT']):
            output = '%s*' % output
        output = output + tok.value
        previous = tok
    return output


def preprocess_natural(formula: str) -> str:
    return preprocess_implicit_multiplication(formula)
