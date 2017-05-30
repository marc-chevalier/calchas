from .idExpression import IdExpression
from .functionCallExpression import FunctionCallExpression
from .formulaFunctionExpression import FormulaFunctionExpression
from .integerLiteralCalchasExpression import IntegerLiteralCalchasExpression
from .floatLiteralExpression import FloatLiteralCalchasExpression
from .constantExpression import ConstantValueExpression, ConstantFunctionExpression
from .abstractExpression import AbstractExpression
from .placeholder import Placeholder
from .visitor import AbstractVisitor
from typing import Union, Optional, Dict, TypeVar


T = TypeVar('T')


class Substitution:
    def __init__(self, subst: Dict[T, AbstractExpression]):
        self.subst = subst

    def apply(self, tree: AbstractExpression) -> AbstractExpression:
        substituer = Substituer(self, tree)
        ret = substituer.visit()
        return ret

    def __repr__(self) -> str:
        return str(self.subst)

    def __eq__(self, other) -> bool:
        if isinstance(other, Substitution):
            return self.subst == other.subst
        if isinstance(other, dict):
            return self.subst == other

    def __getitem__(self, item: T) -> AbstractExpression:
        if isinstance(item, Placeholder):
            return self.subst[item]
        return self.subst[Placeholder(item)]

    def __setitem__(self, key: T, value: AbstractExpression):
        if isinstance(key, Placeholder):
            self.subst[key] = value
        else:
            self.subst[Placeholder(key)] = value

    def __iter__(self):
        return iter(self.subst)


class Substituer(AbstractVisitor):
    def __init__(self, subst: Substitution, tree: AbstractExpression):
        super(Substituer, self).__init__(tree)
        self.subst = subst

    def _visit_placeholder(self, tree: Placeholder, *args):
        if tree in self.subst:
            return self.subst[tree]
        return tree

    def _visit_id(self, tree: IdExpression, *args):
        return tree

    def _visit_call(self, tree: FunctionCallExpression, *args):
        d = tree.options
        d_ = {}
        for (key, val) in d.items():
            if isinstance(key, str):
                if isinstance(key, str):
                    d_[key] = val
                else:
                    d_[key] = self.visit(val)
            else:
                if isinstance(key, str):
                    d_[self.visit(key)] = val
                else:
                    d_[self.visit(key)] = self.visit(val)
        return FunctionCallExpression(self.visit(tree.fun),
                                      [self.visit(e) for e in tree.args],
                                      d_)

    def _visit_fun(self, tree: FormulaFunctionExpression, *args):
        return FormulaFunctionExpression(self.visit(tree.var), self.visit(tree.expr))

    def _visit_int(self, tree: IntegerLiteralCalchasExpression, *args):
        return tree

    def _visit_float(self, tree: FloatLiteralCalchasExpression, *args):
        return tree

    def _visit_constant_value(self, tree: ConstantValueExpression, *args):
        return tree

    def _visit_constant_function(self, tree: ConstantFunctionExpression, *args):
        return tree


class Pattern:
    def __init__(self, pattern_: AbstractExpression):
        self.pattern = pattern_
        self.matcher = None

    def match(self, tree: AbstractExpression) -> bool:
        self.matcher = PatternMatcher(self, tree)
        ret = self.matcher.visit()
        if not ret:
            self.matcher.assigment = {}
        return ret

    def match_and_get_subst(self, tree: AbstractExpression) -> Optional[Substitution]:
        self.matcher = PatternMatcher(self, tree)
        ret = self.matcher.visit()
        if not ret:
            return None
        return self.matcher.assigment

    def __repr__(self) -> str:
        return repr(self.pattern)


class PatternMatcher(AbstractVisitor):
    def __init__(self, pattern: Pattern, tree: AbstractExpression):
        super(PatternMatcher, self).__init__(tree)
        self.pattern = pattern
        self.assigment = Substitution({})

    def _handle_placeholder(self, tree, pattern):
        if pattern not in self.assigment:
            self.assigment[pattern] = tree
            return True
        else:
            return self.visit(tree, self.assigment[pattern])

    def _visit_placeholder(self, tree: Placeholder, *args):
        pattern = args[0]
        if isinstance(pattern, Placeholder):
            return self._handle_placeholder(tree, pattern)
        return False

    def _visit_id(self, tree: IdExpression, *args: Union[IdExpression, Placeholder]) -> bool:
        pattern = args[0]
        if isinstance(pattern, Placeholder):
            return self._handle_placeholder(tree, pattern)
        return isinstance(pattern, IdExpression) and pattern == tree

    def _visit_call(self, tree: FunctionCallExpression, *args: Union[FunctionCallExpression, Placeholder]) -> bool:
        pattern = args[0]
        if isinstance(pattern, Placeholder):
            return self._handle_placeholder(tree, pattern)
        if not isinstance(pattern, FunctionCallExpression):
            return False
        if not self.visit(tree.fun, pattern.fun):
            return False
        if len(tree.args) != len(pattern.args) or len(tree.options) != len(pattern.options):
            return False
        for (tree_arg, pattern_arg) in zip(tree.args, pattern.args):
            if not self.visit(tree_arg, pattern_arg):
                return False
        for (k, v), (k2, v2) in zip(tree.options.items(), pattern.options.items()):
            if type(k) == str and type(k2) == str:
                if k != k2:
                    return False
                if type(v) == str and type(v2) == str:
                    return v == v2
                if type(v) == str or type(v2) == str:
                    return False
                if not self.visit(v, v2):
                    return False
            if type(k) == str or type(k2) == str:
                return False
            if not self.visit(k, k2):
                return False
            if not self.visit(v, v2):
                return False
        return True

    def _visit_fun(self, tree: FormulaFunctionExpression,
                   *args: Union[FormulaFunctionExpression, Placeholder]) -> bool:
        pattern = args[0]
        if isinstance(pattern, Placeholder):
            return self._handle_placeholder(tree, pattern)
        return isinstance(pattern, FormulaFunctionExpression) and self.visit(tree.expr, pattern.expr) and \
            self._visit_id(tree.var, pattern.var)

    def _visit_int(self, tree: IntegerLiteralCalchasExpression,
                   *args: Union[IntegerLiteralCalchasExpression, Placeholder]) -> bool:
        pattern = args[0]
        if isinstance(pattern, Placeholder):
            return self._handle_placeholder(tree, pattern)
        return isinstance(pattern, IntegerLiteralCalchasExpression) and tree == pattern

    def _visit_float(self, tree: FloatLiteralCalchasExpression,
                     *args: Union[FloatLiteralCalchasExpression, Placeholder]) -> bool:
        pattern = args[0]
        if isinstance(pattern, Placeholder):
            return self._handle_placeholder(tree, pattern)
        return isinstance(pattern, FloatLiteralCalchasExpression) and tree.value == pattern.value

    def _visit_constant_value(self, tree: ConstantValueExpression,
                              *args: Union[ConstantValueExpression, Placeholder]) -> bool:
        pattern = args[0]
        if isinstance(pattern, Placeholder):
            return self._handle_placeholder(tree, pattern)
        return isinstance(pattern, ConstantValueExpression) and tree == pattern

    def _visit_constant_function(self, tree: ConstantFunctionExpression,
                                 *args: Union[ConstantFunctionExpression, Placeholder]) -> bool:
        pattern = args[0]
        if isinstance(pattern, Placeholder):
            return self._handle_placeholder(tree, pattern)
        return isinstance(pattern, ConstantFunctionExpression) and tree == pattern

    def visit(self, *args):
        if len(args) > 0:
            return super(PatternMatcher, self).visit(*args)
        return super(PatternMatcher, self).visit(self.tree, self.pattern.pattern, *args)
