import sympy
import typing
import inspect

from calchas_datamodel import AbstractVisitor, AbstractExpression, Placeholder, IdExpression, FunctionCallExpression, \
    FormulaFunctionExpression, IntegerLiteralCalchasExpression, FloatLiteralCalchasExpression, \
    ConstantValueExpression, ConstantFunctionExpression, GenericConstantFunction, ConstantFunctionCallExpression, \
    GenericConstantValueExpression, UnknownType, FunctionExpression, DictFunctionExpression

from .sympyFunctions import base_constants, base_functions, StdSympyFunction, AbstractSympyFunction


class ForbidenType(Exception):
    pass


def context_from_globals() -> typing.Tuple[typing.Dict[ConstantValueExpression, sympy.Expr],
                                           typing.Dict[ConstantFunctionExpression, AbstractSympyFunction]]:
    var = {}
    fun = {}
    caller_frame = inspect.currentframe().f_back
    caller_globals = {**caller_frame.f_globals, **caller_frame.f_locals}
    diff_keys = set(caller_globals.keys()) - set(caller_frame.f_builtins.keys())
    caller_globals = {k: caller_globals[k] for k in diff_keys}
    for name, value in caller_globals.items():
        if isinstance(value, int):
            var[name] = sympy.Integer(value)
        elif isinstance(value, float):
            var[name] = sympy.Float(value)
        elif isinstance(value, sympy.Expr):
            var[name] = value
        elif isinstance(value, AbstractExpression):
            var[name] = value
    return var, fun


class Translator:
    def __init__(self,
                 context: typing.Optional[typing.Tuple[typing.Dict[ConstantValueExpression, sympy.Expr],
                                                       typing.Dict[ConstantFunctionExpression, AbstractSympyFunction]]]
                 = None):
        self.init_variables = context[0] if context is not None else base_constants
        self.init_functions = context[1] if context is not None else base_functions
        self.context = None
        self.reset()

    def to_sympy_tree(self, tree: AbstractExpression) -> sympy.Expr:
        builder = SympyTreeBuilder(tree, self.context)
        visited = builder.visit()
        if isinstance(visited, list):
            e = [sympy.simplify(e) for e in visited]
        else:
            e = sympy.simplify(visited)
        return e

    def to_calchas_tree(self, tree: sympy.Expr) -> AbstractExpression:
        builder = CalchasTreeBuilder(tree, self.context)
        e = builder.visit()
        return e

    def reset(self):
        self.context = self.init_variables.copy(), self.init_functions.copy()


class CalchasTreeBuilder:
    def __init__(self,
                 tree: sympy.Expr,
                 context: typing.Optional[typing.Tuple[typing.Dict[ConstantValueExpression, sympy.Expr],
                                                       typing.Dict[ConstantFunctionExpression, AbstractSympyFunction]]]
                 = None):
        self.tree = tree
        self.variables = context[0] if context is not None else base_constants
        self.functions = context[1] if context is not None else base_functions

    def _visit_symbol(self, tree: sympy.Symbol, *args) -> AbstractExpression:
        for (k, v) in self.variables.items():
            if v == tree:
                return k
        return IdExpression(tree.name)

    def _visit_int(self, tree: int, *args) -> AbstractExpression:
        return IntegerLiteralCalchasExpression(tree)

    def _visit_rational(self, tree: sympy.Rational, *args) -> AbstractExpression:
        if isinstance(tree, sympy.Integer):
            return IntegerLiteralCalchasExpression(tree.p)
        return FloatLiteralCalchasExpression(tree.p/tree.q)

    def _visit_apply_undef(self, tree: sympy.core.function.AppliedUndef, *args) -> AbstractExpression:
        a = [self.visit(e) for e in tree.args]
        for (k, v) in self.variables.items():
            if v == tree:
                return FunctionCallExpression(k, a)
        return FunctionCallExpression(IdExpression(tree.func.__name__), a)

    def _visit_dict(self, tree: dict, *args) -> AbstractExpression:
        return DictFunctionExpression({self.visit(k): self.visit(v) for (k, v) in tree.items()})

    def _visit_lambda(self, tree: sympy.Lambda, *args) -> AbstractExpression:
        return FormulaFunctionExpression(IdExpression(tree.variables[0].name), self.visit(tree.expr))

    def visit(self, *args):
        if len(args) > 0:
            tree = args[0]
            args = args[1:]
        else:
            tree = self.tree
        iterators = {
            sympy.Symbol: self._visit_symbol,
            sympy.NumberSymbol: self._visit_symbol,
            int: self._visit_int,
            sympy.Integer: self._visit_rational,
            sympy.Rational: self._visit_rational,
            sympy.core.function.AppliedUndef: self._visit_apply_undef,
            dict: self._visit_dict,
            sympy.Lambda: self._visit_lambda,
        }
        for (subtype, iterator) in iterators.items():
            if isinstance(tree, subtype):
                return iterator(tree, *args)
        print("Oh no! Unexpected type in a visitor:", end="")
        print(type(tree))
        print(repr(tree))
        print(tree.__class__.__bases__[0])
        print("That is not supposed to happen.\nPlease contact the dev.")
        raise UnknownType


class SympyTreeBuilder(AbstractVisitor):
    def __init__(self,
                 tree: AbstractExpression,
                 context: typing.Optional[typing.Tuple[typing.Dict[ConstantValueExpression, sympy.Expr],
                                                       typing.Dict[ConstantFunctionExpression, AbstractSympyFunction]]]
                 = None):
        super().__init__(tree)
        self.variables = context[0] if context is not None else base_constants
        self.functions = context[1] if context is not None else base_functions

    def _visit_placeholder(self, tree: Placeholder, *args) -> sympy.Expr:
        raise ForbidenType()

    def _visit_id(self, tree: IdExpression, *args) -> sympy.Expr:
        if tree.id not in self.variables.keys():
            self.variables[tree.id] = sympy.symbols(tree.id)
        if tree.id in self.variables.keys() and isinstance(self.variables[tree.id], AbstractExpression):
            self.variables[tree.id] = self.visit(self.variables[tree.id])
        return self.variables[tree.id]

    def _visit_call(self, tree: FunctionCallExpression, *args) -> sympy.Expr:
        if isinstance(tree, ConstantFunctionCallExpression) or isinstance(tree.fun, GenericConstantFunction):
            f = self.functions[tree.fun]
            if not f.is_arity(len(tree.args)):
                print(f.__class__)
                print(tree)
                raise SyntaxError
            arguments = [self.visit(e, *args) for e in tree.args]
            options = {self.visit(k, *args): self.visit(v, *args) for k, v in tree.options.items()}
            call = f.call_function_with_unrearranged_args(arguments, options)
            return call
        if isinstance(tree.fun, IdExpression):
            if tree.fun.id not in self.functions:
                self.functions[tree.fun.id] = \
                    StdSympyFunction(sympy.symbols(tree.fun.id, cls=sympy.Function), len(tree.args))
            f = self.functions[tree.fun.id]
            if not f.is_arity(len(tree.args)):
                raise SyntaxError
            arguments = [self.visit(e, *args) for e in tree.args]
            options = {self.visit(k, *args): self.visit(v, *args) for k, v in tree.options.items()}
            call = f.call_function_with_unrearranged_args(arguments, options)
            return call
        raise ForbidenType()

    def _visit_fun(self, tree: FunctionExpression, *args) -> sympy.Expr:
        if isinstance(tree, FormulaFunctionExpression):
            return sympy.Lambda(self.visit(tree.var, *args), self.visit(tree.expr, *args))

    def _visit_int(self, tree: IntegerLiteralCalchasExpression, *args) -> sympy.Expr:
        return sympy.Integer(tree.value)

    def _visit_float(self, tree: FloatLiteralCalchasExpression, *args) -> sympy.Expr:
        return sympy.Rational(str(tree.value))

    def _visit_constant_value(self, tree: ConstantValueExpression, *args) -> sympy.Expr:
        if isinstance(tree, GenericConstantValueExpression):
            if tree not in self.variables:
                raise ForbidenType()
            return self.variables[tree]
        raise ForbidenType()

    def _visit_constant_function(self, tree: ConstantFunctionExpression, *args) -> sympy.Expr:
        raise ForbidenType()
