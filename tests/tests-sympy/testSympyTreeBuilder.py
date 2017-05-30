import sympy
from unittest import TestCase

from calchas_datamodel import IdExpression as Id, FunctionCallExpression as Call, FormulaFunctionExpression as Fun, \
    IntegerLiteralCalchasExpression as Int, FloatLiteralCalchasExpression as Float, Gcd, Sum, pi, FactorInt, \
    DictFunctionExpression, Series, Prod, Pow, Fact, infinity, Solve, Eq, Exp, Limit, Log

from calchas_sympy import Translator


class TestSympyTreeBuilder(TestCase):
    def testToSympy(self):
        _x = sympy.symbols('x_')
        _y = sympy.symbols('y')
        i = Id('i')
        n = Id('n')
        x = Id('x')
        y = Id('y')
        f = sympy.symbols('f', cls=sympy.Function)
        test_list = [(Id('a'), sympy.Symbol('a')),
                     (Id('pi'), sympy.Symbol('pi')),
                     (pi, sympy.pi),
                     (Int(1), 1),
                     (Float(4.7), sympy.Rational(47, 10)),
                     (Gcd([Int(12), Int(18)]), 6),
                     (Sum([Int(12), Int(18)]), 30),
                     (Sum([Int(12), Int(1), Int(2)]), 15),
                     (Call(Id('f'), [Int(12), Int(18)]), f(12, 18)),
                     (FactorInt([Int(18)]), {2: 1, 3: 2}),
                     (Gcd([Sum([Int(18), Int(18)]), Int(18)]), 18),
                     (pi, sympy.pi),
                     (Fun(Id('x'), Id('x')), sympy.Lambda(_x, _x)),
                     (Series([Prod([Pow([x, n], {}), Pow([Fact([n], {}), Int(-1)], {})], {}), n, Int(0), infinity], {}), sympy.exp(x)),
                     (Solve([Eq([Sum([Prod([Exp([x], {}), Pow([Int(2), Int(-1)], {})], {}),
                                      Prod([Exp([Prod([Int(-1), x], {})], {}),
                                            Pow([Int(2), Int(-1)], {})], {})], {}), y], {}), x], {}),
                      [sympy.log(_y - sympy.sqrt(_y**2 - 1)), sympy.log(_y + sympy.sqrt(_y**2 - 1))]),
                     (Limit([Sum([Series([Prod([Int(1), Pow([i, Int(-1)], {})], {}), i, Int(1), n], {}),
                                  Prod([Int(-1), Log([n], {})], {})], {})], {n: infinity}), sympy.EulerGamma),
                     ]

        for (tree, res) in test_list:
            builder = Translator()
            sympy_tree = builder.to_sympy_tree(tree)
            self.assertEqual(sympy_tree, res)

    def testToCalchas(self):
        x_ = sympy.symbols('x')
        f = sympy.symbols('f', cls=sympy.Function)
        test_list = [(sympy.Symbol('a'), Id('a')),
                     (sympy.pi, pi),
                     (1, Int(1)),
                     (sympy.Rational(47, 10), Float(4.7)),
                     (6, Int(6)),
                     (30, Int(30)),
                     (15, Int(15)),
                     (f(12, 18), Call(Id('f'), [Int(12), Int(18)])),
                     ({2: 1, 3: 2}, DictFunctionExpression({Int(2): Int(1), Int(3): Int(2)})),
                     (18, Int(18)),
                     (sympy.pi, pi),
                     (sympy.Lambda(x_, x_), Fun(Id('x'), Id('x'))),
                     ]

        for (tree, res) in test_list:
            builder = Translator()
            calchas_tree = builder.to_calchas_tree(tree)
            self.assertEqual(calchas_tree, res)
