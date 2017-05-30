from unittest import TestCase

from calchas_datamodel import Sum, Prod, FunctionCallExpression as Call, Pow, IdExpression as Id, Sin, Cos, \
    Fact, IntegerLiteralCalchasExpression as Int, Series, infinity, Integrate, Limit, Arctan, Sqrt, Mod, \
    Diff, And, Or, Not, FormulaFunctionExpression as Fun

from calchas_polyparser import naturalLexer, parse_natural


class TestNatural(TestCase):
    def testLexer(self):
        test_list = [("0",
                      [("INT", "0", 1, 0)]),
                     ("1.",
                      [("FLOAT", "1.", 1, 0)]),
                     (".2",
                      [("FLOAT", ".2", 1, 0)]),
                     ("Sin(x)",
                      [("ID", "Sin", 1, 0),
                       ("LPAREN", "(", 1, 3),
                       ("ID", "x", 1, 4),
                       ("RPAREN", ")", 1, 5)]),
                     ("Arctan(4.)",
                      [("ID", "Arctan", 1, 0),
                       ("LPAREN", "(", 1, 6),
                       ("FLOAT", "4.", 1, 7),
                       ("RPAREN", ")", 1, 9)]),
                     ]
        for (expr, res) in test_list:
            naturalLexer.input(expr)
            out = []
            t = naturalLexer.token()
            while t is not None:
                out.append((t.type, t.value, t.lineno, t.lexpos))
                t = naturalLexer.token()
            self.assertEqual(out, res)

    def testParser(self):
        a = Id('a')
        b = Id('b')
        c = Id('c')
        d = Id('d')
        f = Id('f')
        g = Id('g')
        i = Id('i')
        j = Id('j')
        m = Id('m')
        n = Id('n')
        x = Id('x')
        y = Id('y')
        z = Id('z')
        _d0 = Id('_d0')
        __1 = Int(-1)
        _0 = Int(0)
        _1 = Int(1)
        _2 = Int(2)
        _3 = Int(3)
        _4 = Int(4)
        _6 = Int(6)
        _1024 = Int(1024)
        self.maxDiff = None
        test_list = [("0", _0),
                     ("Sin(x)", Sin([x], {})),
                     ("Arctan(x)", Arctan([x], {})),
                     ("Sqrt(4)", Sqrt([_4], {})),
                     ("ArcTan(x)", Arctan([x], {})),
                     ("x^2", Pow([x, _2], {})),
                     ("a+b", Sum([a, b], {})),
                     ("a*b", Prod([a, b], {})),
                     ("a!", Fact([a], {})),
                     ("2*a!", Prod([_2, Fact([a], {})], {})),
                     ("a!!", Fact([Fact([a], {})], {})),
                     ("-a!", Prod([__1, Fact([a], {})], {})),
                     ("b+a!", Sum([b, Fact([a], {})], {})),
                     ("-a-a", Sum([Prod([__1, a], {}), Prod([__1, a], {})], {})),
                     ("--a", Prod([__1, Prod([__1, a], {})], {})),
                     ("+a", a),
                     ("+-a", Prod([__1, a], {})),
                     ("-+a", Prod([__1, a], {})),
                     ("a*-b", Prod([a, Prod([__1, b], {})], {})),
                     ("-a*b", Prod([Prod([__1, a], {}), b], {})),
                     ("-a^b", Prod([__1, Pow([a, b], {})], {})),
                     ("-c**d", Prod([__1, Pow([c, d], {})], {})),
                     ("a/b", Prod([a, Pow([b, __1], {})], {})),
                     ("a-b", Sum([a, Prod([__1, b], {})], {})),
                     ("a^b", Pow([a, b], {})),
                     ("a^b/c", Prod([Pow([a, b], {}), Pow([c, __1], {})], {})),
                     ("-a^b/c", Prod([Prod([__1, Pow([a, b], {})], {}), Pow([c, __1], {})], {})),
                     ("(a+b)", Sum([a, b], {})),
                     ("(a*b)", Prod([a, b], {})),
                     ("(a/b)", Prod([a, Pow([b, __1], {})], {})),
                     ("(a-b)", Sum([a, Prod([__1, b], {})], {})),
                     ("(a^b)", Pow([a, b], {})),
                     ("(a)^b", Pow([a, b], {})),
                     ("(a+b)*c", Prod([Sum([a, b], {}), c], {})),
                     ("a+(b*c)", Sum([a, Prod([b, c], {})], {})),
                     ("a+b*c", Sum([a, Prod([b, c], {})], {})),
                     ("a^b^c", Pow([a, Pow([b, c], {})], {})),
                     ("a*b/c", Prod([Prod([a, b], {}), Pow([c, __1], {})], {})),
                     ("a+b/c", Sum([a, Prod([b, Pow([c, __1], {})], {})], {})),
                     ("x^n/n!", Prod([Pow([x, n], {}), Pow([Fact([n], {}), __1], {})], {})),
                     ("a^n%b!", Mod([Pow([a, n], {}), Fact([b], {})], {})),
                     ("a!%b^c+d", Sum([Mod([Fact([a], {}), Pow([b, c], {})], {}), d], {})),
                     ("a^g(x)", Pow([a, Call(g, [x], {})], {})),
                     ("f(x)+f(x)", Sum([Call(f, [x], {}), Call(f, [x], {})], {})),
                     ("f(x)^g(x)", Pow([Call(f, [x], {}), Call(g, [x], {})], {})),
                     ("Sin(x)^2+Cos(x)^2", Sum([Pow([Sin([x], {}), _2], {}), Pow([Cos([x], {}), _2], {})], {})),
                     ("Sum(1/i^6, i, 1, Infinity)",
                      Series([Prod([_1, Pow([Pow([i, _6], {}), __1], {})], {}), i, _1, infinity], {})),
                     ("Sum(Sum(j/i^6, i, 1, Infinity), j, 0 , m)",
                      Series([Series([Prod([j, Pow([Pow([i, _6], {}), __1], {})], {}),
                                      i, _1, infinity], {}), j, _0, m], {})),
                     ("Integrate(1/(x^3 + 1), x)",
                      Integrate([Prod([_1, Pow([Sum([Pow([x, _3], {}), _1], {}), __1], {})], {}), x], {})),
                     ("Integrate(1/(x^3 + 1), x, 0, 1)",
                      Integrate([Prod([_1, Pow([Sum([Pow([x, _3], {}), _1], {}), __1], {})], {}), x, _0, _1], {})),
                     ("Integrate(Integrate(Sin(x*y), x, 0, 1), y, 0, x)",
                      Integrate([Integrate([Sin([Prod([x, y], {})], {}), x, _0, _1], {}), y, _0, x], {})),
                     ("Limit(Sin(x)/x, x, 0)",
                      Limit([Prod([Sin([x], {}), Pow([x, __1], {})], {}), x, _0], {})),
                     ("Limit((1+x/n)^n, x, Infinity)",
                      Limit([Pow([Sum([_1, Prod([x, Pow([n, __1], {})], {})], {}), n], {}), x, infinity], {})),
                     ("Pow(1024, 1/2)", Pow([_1024, Prod([_1, Pow([_2, __1], {})], {})], {})),
                     ("cos'(x)", Call(Diff([Fun(_d0, Cos([_d0], {})), _1], {}), [x], {})),
                     ("cos''''(x)", Call(Diff([Fun(_d0, Cos([_d0], {})), _4], {}), [x], {})),
                     ("x | y", Or([x, y], {})),
                     ("~ y", Not([y], {})),
                     ("x & y", And([x, y], {})),
                     ("x | ~z & ~ y", Or([x, And([Not([z], {}), Not([y], {})], {})], {})),
                     ]
        for (expr, res) in test_list:
            self.assertEqual(repr(parse_natural(expr)), repr(res))
