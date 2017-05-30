from unittest import TestCase

from calchas_datamodel import IdExpression as Id, Diff, Cos, FormulaFunctionExpression as Fun, Prod, Sum, \
    IntegerLiteralCalchasExpression as Int

from calchas_transformations import CalchasTreeLambdafier, SimplifyProd, SimplifySum, Transformer


class TestTransformations(TestCase):
    def testLambdafier(self):
        test_list = [(Diff([Id("Cos")], {}),
                      Diff([Fun(Id('_0'), Cos([Id('_0')], {}))], {})),
                     (Cos([Id('x')], {}),
                      Cos([Id('x')], {})),
                     (Diff([Id("Sum")], {}),
                      Diff([Id("Sum")], {})),
                     ]
        for (tree, ret) in test_list:
            transformer = Transformer(tree)
            lambdafier = CalchasTreeLambdafier(prefix="_")
            transformer.apply(lambdafier)
            self.assertEqual(transformer.get_tree(), ret)

    def testProd(self):
        test_list = [(Prod([Int(1), Prod([Int(2), Int(3)], {})], {}),
                      Prod([Int(2), Int(3)], {})),
                     (Prod([Int(1), Prod([Int(2), Prod([Int(3), Int(4)], {})], {})], {}),
                      Prod([Int(2), Int(3), Int(4)], {})),
                     (Prod([Int(1), Prod([Int(6)], {}), Sum([Int(2), Prod([Int(3), Prod([Int(4), Int(5)], {})], {})], {})], {}),
                      Prod([Int(6), Sum([Int(2), Prod([Int(3), Int(4), Int(5)], {})], {})], {})),
                     (Prod([Id('x')], {}),
                      Id('x'))
                     ]
        for (tree, ret) in test_list:
            transformer = Transformer(tree)
            simplifier = SimplifyProd()
            transformer.apply(simplifier)
            self.assertEqual(transformer.get_tree(), ret)

    def testSum(self):
        test_list = [(Sum([Int(1), Sum([Int(2), Int(3)], {})], {}),
                      Sum([Int(1), Int(2), Int(3)], {})),
                     (Sum([Int(0), Sum([Int(2), Sum([Int(3), Int(4)], {})], {})], {}),
                      Sum([Int(2), Int(3), Int(4)], {})),
                     (Sum([Int(0), Int(6), Prod([Int(2), Sum([Int(3), Sum([Int(4), Int(5)], {})], {})], {})], {}),
                      Sum([Int(6), Prod([Int(2), Sum([Int(3), Int(4), Int(5)], {})], {})], {})),
                     (Sum([Id('x')], {}),
                      Id('x'))
                     ]
        for (tree, ret) in test_list:
            transformer = Transformer(tree)
            simplifier = SimplifySum()
            transformer.apply(simplifier)
            self.assertEqual(transformer.get_tree(), ret)
