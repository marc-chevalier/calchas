from unittest import TestCase
from calchas_datamodel import IdExpression as Id, FunctionCallExpression as Call, FormulaFunctionExpression as Fun, \
    IntegerLiteralCalchasExpression as Int, FloatLiteralCalchasExpression as Float, Sum, Pattern, Placeholder as _, \
    Substitution


class TestPattern(TestCase):
    def testPattern(self):
        tests = [(Int(1), Int(1), True),
                 (Float(1), Float(1), True),
                 (_(1), Float(1), True, {_(1): Float(1)}),
                 (_(1), Id('x'), True, {_(1): Id('x')}),
                 (Sum([Int(1), Int(2)], {}), Sum([Int(1), Int(2)], {}), True, {}),
                 (_(1), Sum([Int(1), Int(3)], {}), True, {_(1): Sum([Int(1), Int(3)], {})}),
                 (Sum([_(1), _(1)], {}), Sum([Int(1), Int(1)], {}), True, {_(1): Int(1)}),
                 (Sum([_(1), _(1)], {}), Sum([Int(1), Int(2)], {}), False),
                 (Fun(Id('x'), Call(Id('f'), [], {})), Fun(Id('x'), Call(Id('f'), [], {})), True),
                 (Fun(Id('x'), Call(Id('g'), [], {})), Fun(Id('x'), Call(Id('f'), [], {})), False),
                 (Fun(_(1), Call(_(2), [], {})), Fun(Id('x'), Call(Id('f'), [], {})), True,
                  {_(1): Id('x'), _(2): Id('f')}),
                 (Fun(_(1), _(2)), Fun(Id('x'), Call(Id('f'), [], {})), True,
                  {_(1): Id('x'), _(2): Call(Id('f'), [], {})}),
                 ]
        for e in tests:
            if len(e) == 3:
                pattern, tree, ret = e
                assignment = None
            else:
                pattern, tree, ret, assignment = e
            pattern = Pattern(pattern)
            self.assertEqual(pattern.match(tree), ret)
            if ret and assignment is not None:
                self.assertEqual(assignment, pattern.matcher.assigment)

    def testSubst(self):
        tests = [({_(1): Int(1)}, _(1), Int(1)),
                 ({_(1): Int(1)}, Sum([_(1)], {}), Sum([Int(1)], {})),
                 ]

        for e in tests:
            subst, before, after = e
            s = Substitution(subst)
            self.assertEqual(s.apply(before), after)
