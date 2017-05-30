from unittest import TestCase
from calchas_datamodel import FormulaFunctionExpression as Fun
from calchas_datamodel import IdExpression as Id


class TestFunctionExpression(TestCase):
    def testStr(self):
        fun = Fun(Id('x'), Id('y'))
        self.assertEqual(repr(fun), "x -> y")
