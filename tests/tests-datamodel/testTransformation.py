from unittest import TestCase
from calchas_datamodel import Rewriting, Pattern, IdExpression as Id, FunctionCallExpression as Call, \
    FormulaFunctionExpression as Fun, IntegerLiteralCalchasExpression as Int, FloatLiteralCalchasExpression as Float, \
    Sum, Prod, Placeholder as _


class TestTransformation(TestCase):
    def testTransformation(self):
        tests = [(Sum([_(1), Sum([_(2), _(3)], {})], {}),
                  Sum([_(1), _(2), _(3)], {}),
                  Sum([Int(1), Sum([Int(2), Int(3)], {})], {}),
                  Sum([Int(1), Int(2), Int(3)], {}),),
                 (Prod([_(1), Sum([_(2), _(3)], {})], {}),
                  Sum([Prod([_(1), _(2)], {}), Prod([_(1), _(3)], {})], {}),
                  Prod([Int(1), Sum([Int(2), Int(3)], {})], {}),
                  Sum([Prod([Int(1), Int(2)], {}), Prod([Int(1), Int(3)], {})], {})),
                 (Sum([_(1), _(2)], {}),
                  Sum([_(2), _(1)], {}),
                  Sum([Id('x'), Float(2)], {}),
                  Sum([Float(2), Id('x')], {})),
                 (Fun(_(1), _(1)),
                  Fun(Id('x'), Id('x')),
                  Fun(Id('y'), Id('y')),
                  Fun(Id('x'), Id('x'))),
                 (Fun(_(1), _(1)),
                  Fun(Id('x'), Id('x')),
                  Fun(Id('y'), Id('z')),
                  None),
                 (Call(Sum([_(1), _(2)], {}), [], {}),
                  Sum([Call(_(1), [], {}), Call(_(2), [], {})], {}),
                  Call(Sum([Id('f'), Id('g')], {}), [], {}),
                  Sum([Call(Id('f'), [], {}), Call(Id('g'), [], {})], {})),
                 ]
        for e in tests:
            before, after, tree, ret = e
            trans = Rewriting(Pattern(before), after)
            self.assertEqual(trans.subst(tree), ret)
