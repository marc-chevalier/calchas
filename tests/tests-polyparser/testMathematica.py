from unittest import TestCase

from calchas_datamodel import Sum, Prod, FunctionCallExpression as Call, Pow, IdExpression as Id, Sin, Cos, \
    Fact, IntegerLiteralCalchasExpression as Int, Series, infinity, Integrate, Limit, Solve, Eq

from calchas_polyparser import mathematicaParser, mathematicaLexer


class TestMathematica(TestCase):
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
            mathematicaLexer.input(expr)
            out = []
            t = mathematicaLexer.token()
            while t is not None:
                out.append((t.type, t.value, t.lineno, t.lexpos))
                t = mathematicaLexer.token()
            self.assertEqual(out, res)

    def testParser(self):
        a = Id('a')
        b = Id('b')
        c = Id('c')
        e = Id('e')
        i = Id('i')
        j = Id('j')
        m = Id('m')
        n = Id('n')
        x = Id('x')
        y = Id('y')
        test_list = [("0", Int(0)),
                     ("Sin[x]", Sin([x], {})),
                     ("Arctan[x]", Call(Id('Arctan'), [x], {})),
                     ("Sqrt[4]", Call(Id('Sqrt'), [Int(4)], {})),
                     ("ArcTan[x]", Call(Id('ArcTan'), [x], {})),
                     ("x^2", Pow([x, Int(2)], {})),
                     ("a+b", Sum([a, b], {})),
                     ("a+b+c", Sum([Sum([a, b], {}), c], {})),
                     ("a*b", Prod([a, b], {})),
                     ("a!", Fact([a], {})),
                     ("2*a!", Prod([Int(2), Fact([a], {})], {})),
                     ("a!!", Fact([Fact([a], {})], {})),
                     ("-a!", Prod([Int(-1), Fact([a], {})], {})),
                     ("b+a!", Sum([b, Fact([a], {})], {})),
                     ("-a-a", Sum([Prod([Int(-1), a], {}), Prod([Int(-1), a], {})], {})),
                     ("--a", Prod([Int(-1), Prod([Int(-1), a], {})], {})),
                     ("+a", a),
                     ("+-a", Prod([Int(-1), a], {})),
                     ("-+a", Prod([Int(-1), a], {})),
                     ("a*-b", Prod([a, Prod([Int(-1), b], {})], {})),
                     ("-a*b", Prod([Prod([Int(-1), a], {}), b], {})),
                     ("a/b", Prod([a, Pow([b, Int(-1)], {})], {})),
                     ("a-b", Sum([a, Prod([Int(-1), b], {})], {})),
                     ("a^b", Pow([a, b], {})),
                     ("a^b/c", Prod([Pow([a, b], {}), Pow([c, Int(-1)], {})], {})),
                     ("-a^b/c", Prod([Prod([Int(-1), Pow([a, b], {})], {}), Pow([c, Int(-1)], {})], {})),
                     ("(a+b)", Sum([a, b], {})),
                     ("(a*b)", Prod([a, b], {})),
                     ("(a/b)", Prod([a, Pow([b, Int(-1)], {})], {})),
                     ("(a-b)", Sum([a, Prod([Int(-1), b], {})], {})),
                     ("(a^b)", Pow([a, b], {})),
                     ("(a)^b", Pow([a, b], {})),
                     ("(a+b)*c", Prod([Sum([a, b], {}), c], {})),
                     ("a+(b*c)", Sum([a, Prod([b, c], {})], {})),
                     ("a+b*c", Sum([a, Prod([b, c], {})], {})),
                     ("a^b^c", Pow([a, Pow([b, c], {})], {})),
                     ("a*b/c", Prod([Prod([a, b], {}), Pow([c, Int(-1)], {})], {})),
                     ("a+b/c", Sum([a, Prod([b, Pow([c, Int(-1)], {})], {})], {})),
                     ("x^n/n!", Prod([Pow([x, n], {}), Pow([Fact([n], {}), Int(-1)], {})], {})),
                     ("a^G[x]", Pow([a, Call(Id('G'), [x], {})], {})),
                     ("f[x]+f[x]", Sum([Call(Id('f'), [x], {}), Call(Id('f'), [x], {})], {})),
                     ("f[x]^G[x]", Pow([Call(Id('f'), [x], {}), Call(Id('G'), [x], {})], {})),
                     ("Sin[x]^2+Cos[x]^2", Sum([Pow([Sin([x], {}), Int(2)], {}), Pow([Cos([x], {}), Int(2)], {})], {})),
                     ("Sum[1/i^6, {i, 1, Infinity}]",
                      Series([Prod([Int(1), Pow([Pow([i, Int(6)], {}), Int(-1)], {})], {}), i, Int(1), infinity], {})),
                     ("Sum[j/i^6, {i, 1, Infinity}, {j, 0 , m}]",
                      Series([Series([Prod([j, Pow([Pow([i, Int(6)], {}), Int(-1)], {})], {}), j, Int(0), m], {}),
                              i, Int(1), infinity], {})),
                     ("Integrate[1/(x^3 + 1), x]",
                      Integrate([Prod([Int(1), Pow([Sum([Pow([x, Int(3)], {}), Int(1)], {}), Int(-1)], {})], {}),
                                 x], {})),
                     ("Integrate[1/(x^3 + 1), {x, 0, 1}]",
                      Integrate([Prod([Int(1), Pow([Sum([Pow([x, Int(3)], {}), Int(1)], {}), Int(-1)], {})], {}),
                                 x, Int(0), Int(1)], {})),
                     ("Integrate[Sin[x*y], {x, 0, 1}, {y, 0, x}]",
                      Integrate([Integrate([Sin([Prod([x, y], {})], {}), y, Int(0), x], {}), x, Int(0), Int(1)],  {})),
                     ("Limit[e, x->a]", Limit([e], {x: a})),
                     ("Limit[Sin[x]/x, x->0]", Limit([Prod([Sin([x], {}), Pow([x, Int(-1)], {})], {})], {x: Int(0)})),
                     ("Limit[(1+x/n)^n, x->Infinity]",
                      Limit([Pow([Sum([Int(1), Prod([x, Pow([n, Int(-1)], {})], {})], {}), n], {})], {x: infinity})),
                     ("Solve[x^2==1, x]", Solve([Eq([Pow([x, Int(2)], {}), Int(1)], {}), x], {})),
                     ("1+2+", None),
                     ]
        for test in test_list:
            if len(test) == 2:
                expr, res = test
                d = False
            else:
                expr, res, d = test
            self.assertEqual(repr(mathematicaParser.parse(expr, lexer=mathematicaLexer, debug=d)), repr(res))
