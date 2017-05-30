from unittest import TestCase

from calchas_datamodel import Sum, Prod, FunctionCallExpression as Call, Pow, IdExpression as Id, Sin, \
    Fact, IntegerLiteralCalchasExpression as Int, Series, infinity, Limit, Sqrt, C, Ceiling, \
    Log, Mod, pi

from calchas_polyparser import latexParser, latexLexer, preprocess_latex


class TestLatex(TestCase):
    def testLexer(self):
        test_list = [("0",
                      [("INT", "0", 1, 0)]),
                     ("1.",
                      [("FLOAT", "1.", 1, 0)]),
                     (".2",
                      [("FLOAT", ".2", 1, 0)]),
                     ("Sin[x]",
                      [("ID", "Sin", 1, 0),
                       ("LBRACKET", "[", 1, 3),
                       ("ID", "x", 1, 4),
                       ("RBRACKET", "]", 1, 5)]),
                     ("Arctan[4.]",
                      [("ID", "Arctan", 1, 0),
                       ("LBRACKET", "[", 1, 6),
                       ("FLOAT", "4.", 1, 7),
                       ("RBRACKET", "]", 1, 9)]),
                     ]
        for (expr, res) in test_list:
            latexLexer.input(expr)
            out = []
            t = latexLexer.token()
            while t is not None:
                out.append((t.type, t.value, t.lineno, t.lexpos))
                t = latexLexer.token()
            self.assertEqual(out, res)

    def testParser(self):
        a = Id('a')
        i = Id('i')
        n = Id('n')
        x = Id('x')
        y = Id('y')
        test_list = [("0", Int(0)),
                     ("sin(x)", Sin([x], {})),
                     ("\\sin{y}", Sin([y], {})),
                     ("\\sqrt{4}", Sqrt([Int(4)], {})),
                     ("\\sqrt{a}", Sqrt([a], {})),
                     ("\\sqrt[n]{a}", Pow([a, Pow([n, Int(-1)], {})], {})),
                     ("\\frac{1}{2}", Prod([Int(1), Pow([Int(2), Int(-1)], {})], {})),
                     ("\\binom{6}{4}", C([Int(6), Int(4)], {})),
                     ("\\lceil sin(x) \\rceil", Ceiling([Sin([x], {})], {})),
                     ("\\lim_{x\\to 0} sin(x)/x",
                      Limit([Prod([Sin([x], {}), Pow([x, Int(-1)], {})], {}), x, Int(0)], {})),
                     ("\\sum _ { i = 0 } ^ { \\infty } (1)", Series([Int(1), i, Int(0), infinity], {})),
                     ("\\sum _ { i = 0 } ^ { \\infty } (1/i^{2}) ",
                      Series([Prod([Int(1), Pow([Pow([i, Int(2)], {}), Int(-1)], {})], {}), i, Int(0), infinity], {})),
                     ("\\frac { \\log ( \\frac { 1 } { 2 } ) } { 2 ^ {2} }",
                      Prod([Log([Prod([Int(1), Pow([Int(2), Int(-1)], {})], {})], {}),
                            Pow([Pow([Int(2), Int(2)], {}), Int(-1)], {})], {})),
                     ("2\\times(1+3)", Prod([Int(2), Sum([Int(1), Int(3)], {})], {})),
                     ]

        for e in test_list:
            if len(e) == 3:
                expr, res, d = e
            else:
                expr, res = e
                d = False
            self.assertEqual(repr(latexParser.parse(expr, lexer=latexLexer, debug=d)), repr(res))

    def testParserWithImplicitBracesOrTimes(self):
        a = Id('a')
        b = Id('b')
        c = Id('c')
        d = Id('d')
        f = Id('f')
        g = Id('g')
        i = Id('i')
        j = Id('j')
        n = Id('n')
        x = Id('x')
        test_list = [("f ( a ) ", "f ( a ) ", Call(f, [a], {})),
                     ("( a ) ", "( a ) ", a),
                     ("( ( a ) ) ", "( ( a ) ) ", a),
                     ("( ( a ) b ) ", "( ( a ) *b ) ", Prod([a, b], {})),
                     ("( ( abc ) b a ^ {n} \\% b ! + c ) ", "( ( abc ) *b *a ^ { n } \\% b ! + c ) ",
                      Sum([Mod([Prod([Prod([Id('abc'), b], {}), Pow([a, n], {})], {}), Fact([b], {})], {}), c], {})),
                     ("f(x)a", "f ( x ) *a ", Prod([Call(f, [x], {}), a], {})),
                     ("g f(n)", "g *f ( n ) ", Prod([g, Call(f, [n], {})], {})),
                     ("((f(a)(a+b)a))a(c+d)d", "( ( f ( a ) *( a + b ) *a ) ) *a ( c + d ) *d ",
                      Prod([Prod([Prod([Prod([Call(f, [a], {}), Sum([a, b], {})], {}), a], {}),
                                  Call(a, [Sum([c, d], {})], {})], {}), d], {})),
                     ("a 2", "a *2 ", Prod([a, Int(2)], {})),
                     ("2 a", "2 *a ", Prod([Int(2), a], {})),
                     ("2 4", "2 *4 ", Prod([Int(2), Int(4)], {})),
                     ("2x", "2 *x ", Prod([Int(2), x], {})),
                     ("x2", "x *2 ", Prod([x, Int(2)], {})),
                     ("a-b", "a - b ", Sum([a, Prod([Int(-1), b], {})], {})),
                     ("a/-b", "a / - b ", Prod([a, Pow([Prod([Int(-1), b], {}), Int(-1)], {})], {})),
                     ("-a/+b", "- a / + b ", Prod([Prod([Int(-1), a], {}), Pow([b, Int(-1)], {})], {})),
                     ("a(b+c)", "a ( b + c ) ", Call(a, [Sum([b, c], {})], {})),
                     ("42(b+c)", "42 *( b + c ) ", Prod([Int(42), Sum([b, c], {})], {})),
                     ("1/2\\pi", "1 / 2 *\\pi ", Prod([Prod([Int(1), Pow([Int(2), Int(-1)], {})], {}), pi], {})),
                     ("\\sum_{i=0}^\\infty i", "\sum _ { i = 0 } ^ { \infty } { i } ",
                      Series([i, i, Int(0), infinity], {})),
                     ("\\sum\\limits_{j=0}^\\infty j", "\sum _ { j = 0 } ^ { \infty } { j } ",
                      Series([j, j, Int(0), infinity], {})),
                     ("\\sum_{i=0}^\\infty(1/i^2) ", "\sum _ { i = 0 } ^ { \infty } ( 1 / i ^ { 2 } ) ",
                      Series([Prod([Int(1), Pow([Pow([i, Int(2)], {}), Int(-1)], {})], {}), i, Int(0), infinity], {})),
                     ("\\sqrt{a}", "\\sqrt { a } ", Sqrt([a], {})),
                     ("\\sqrt[n]{a}", "\\sqrt [ n ] { a } ", Pow([a, Pow([n, Int(-1)], {})], {})),
                     ("\\sqrt {\\sqrt a}", "\\sqrt { \\sqrt { a } } ", Sqrt([Sqrt([a], {})], {})),
                     ]
        for e in test_list:
            if len(e) == 4:
                expr, prep, res, d = e
            else:
                expr, prep, res = e
                d = False
            expr_ = preprocess_latex(expr)
            self.assertEqual(expr_, prep)
            self.assertEqual(repr(latexParser.parse(expr_, lexer=latexLexer, debug=d)), repr(res))
