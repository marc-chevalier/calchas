from unittest import TestCase

from calchas_datamodel import Sum, Prod, FunctionCallExpression as Call, Pow, IdExpression as Id, Fact, \
    IntegerLiteralCalchasExpression as Int, Mod, pi

from calchas_polyparser import preprocess_natural, naturalParser, naturalLexer


class TestNaturalPreprocessing(TestCase):
    def testPreprocessing(self):
        test_list = [("(a)a^n%b!+c", "(a)*a^n%b!+c"),
                     ("f(x)a", "f(x)*a"),
                     ("g f(n)", "g*f(n)"),
                     ("((f(a)(a+b)a))a(c+d)d", "((f(a)*(a+b)*a))*a(c+d)*d"),
                     ("a 2", "a*2"),
                     ("2 a", "2*a"),
                     ("2 4", "2*4"),
                     ("2x", "2*x"),
                     ("x2", "x2"),
                     ("a-b", "a-b"),
                     ("a/-b", "a/-b"),
                     ("-a/+b", "-a/+b"),
                     ("a(b+c)", "a(b+c)"),
                     ("42(b+c)", "42*(b+c)"),
                     ("1/2Pi", "1/2*Pi"),
                     ]
        for (expr, res) in test_list:
            self.assertEqual(preprocess_natural(expr), res)

    def testParserWithImplicitMultiplication(self):
        a = Id('a')
        b = Id('b')
        c = Id('c')
        d = Id('d')
        f = Id('f')
        g = Id('g')
        n = Id('n')
        x = Id('x')
        test_list = [("(a)a^n%b!+c", "(a)*a^n%b!+c",
                      Sum([Mod([Prod([a, Pow([a, n], {})], {}), Fact([b], {})], {}), c], {})),
                     ("f(x)a", "f(x)*a", Prod([Call(f, [x], {}), a], {})),
                     ("g f(n)", "g*f(n)", Prod([g, Call(f, [n], {})], {})),
                     ("((f(a)(a+b)a))a(c+d)d", "((f(a)*(a+b)*a))*a(c+d)*d",
                      Prod([Prod([Prod([Prod([Call(f, [a], {}), Sum([a, b], {})], {}), a], {}),
                                  Call(a, [Sum([c, d], {})], {})], {}), d], {})),
                     ("a 2", "a*2", Prod([a, Int(2)], {})),
                     ("2 a", "2*a", Prod([Int(2), a], {})),
                     ("2 4", "2*4", Prod([Int(2), Int(4)], {})),
                     ("2x", "2*x", Prod([Int(2), x], {})),
                     ("x2", "x2", Id('x2')),
                     ("a-b", "a-b", Sum([a, Prod([Int(-1), b], {})], {})),
                     ("a/-b", "a/-b", Prod([a, Pow([Prod([Int(-1), b], {}), Int(-1)], {})], {})),
                     ("-a/+b", "-a/+b", Prod([Prod([Int(-1), a], {}), Pow([b, Int(-1)], {})], {})),
                     ("a(b+c)", "a(b+c)", Call(a, [Sum([b, c], {})], {})),
                     ("42(b+c)", "42*(b+c)", Prod([Int(42), Sum([b, c], {})], {})),
                     ("1/2Pi", "1/2*Pi", Prod([Prod([Int(1), Pow([Int(2), Int(-1)], {})], {}), pi], {})),
                     ]
        for e in test_list:
            if len(e) == 4:
                expr, prep, res, d = e
            else:
                expr, prep, res = e
                d = False
            expr_ = preprocess_natural(expr)
            self.assertEqual(expr_, prep)
            self.assertEqual(repr(naturalParser.parse(expr_, lexer=naturalLexer, debug=d)), repr(res))
