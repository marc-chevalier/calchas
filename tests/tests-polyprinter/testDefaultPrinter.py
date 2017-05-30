from unittest import TestCase

from calchas_datamodel import ConstantFunctionCallExpression as Call, IdExpression as Id, \
    FormulaFunctionExpression as Fun, IntegerLiteralCalchasExpression as Int, FloatLiteralCalchasExpression as Float, \
    Sum

from calchas_polyprinter import DefaultPrinter


class TestDefaultPrinter(TestCase):
    def test(self):
        test_list = [(Id('x'),
                      "x"),
                     (Call(Id('f'), [Int(4)], {}),
                      "f(Int(4))"),
                     (Fun(Id('x'), Sum([Float(1), Id('x')], {})),
                      "x -> Sum(Float(1), x)"),
                     ]

        for (tree, string) in test_list:
            printer = DefaultPrinter()
            self.assertEqual(printer.to_str(tree), string)
