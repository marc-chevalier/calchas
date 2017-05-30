from unittest import TestCase
from calchas_datamodel import FunctionCallExpression as Call
from calchas_datamodel import IdExpression as Id
from calchas_datamodel import Sum


class TestFunctionExpression(TestCase):
    def testRepr(self):
        tests = [(Call(Id('Bla'), [Id('x'), Id('y'), Call(Id('Add'), [Id('x'), Id('y')], {})], {}),
                  "Bla(x, y, Add(x, y))"),
                 (Call(Id('f'), [], {}),
                  "f()"),
                 (Sum([Id('x')], {'bla': Id('z')}),
                  "Sum(x, bla: z)"),
                 ]
        for (tree, string) in tests:
            self.assertEqual(repr(tree), string)
