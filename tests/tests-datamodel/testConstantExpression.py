from unittest import TestCase
from calchas_datamodel import Sum, Prod, pi


class TestConstantExpression(TestCase):
    def testStr(self):
        tests = [(pi,
                  "pi"),
                 (Sum([pi], {}),
                  "Sum(pi)"),
                 (Prod([pi], {}),
                  "Prod(pi)"),
                 ]
        for (tree, string) in tests:
            self.assertEqual(repr(tree), string)
