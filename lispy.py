#!/usr/bin/python

from sexpy import SExp, tok_STRING
import math

def numeric(context, arg):
    """Interpret a value, which is either an SExp or a string, as a number."""
    if isinstance(arg, SExp):
        arg = arg.eval(context)
    return float(arg)
def doplus(context, *args):
    return sum(numeric(context, arg) for arg in args)
def dominus(context, car, *cdr):
    return numeric(context, car) - doplus(context, *cdr)
def dotimes(context, *args):
    if len(args):
        return numeric(context, args[0]) * dotimes(context, *args[1:])
    return 1
def dodiv(context, car, *cdr):
    return numeric(context, car) / dotimes(context, *cdr)
def dosqrt(context, arg):
    return math.sqrt(float(arg))
def domap(context, car, cdr):
    return SExp(*[SExp(car, x).eval(context) for x in cdr.eval(context).tpl])
def do_g(context, arg):
    return '%g'%numeric(context, arg)
def do_quote(context, *args):
    return SExp(*args)
def do_quasiquote(context, *args):
    return SExp(*[x.eval(context) if isinstance(x, SExp) else x for x in args])
def do_join(context, car, cdr):
    return car.join(cdr.eval(context).tpl)
def do_apply(context, car, cdr):
    return SExp(car, *cdr.eval(context).tpl).eval(context)
def do_setf(context, car, cdr):
    if car in context:
        raise Exception("Redefinition of", car, "as", cdr, " - was", context[car])
    def f(_context, _car, _cdr):
        return context[cdr](_context, _car, _cdr)
    if isinstance(cdr, SExp):
        cdr = cdr.eval(context)
    if callable(cdr):
        context[car] = cdr
    else:
        context[car] = f
def do_lambda(context, car, cdr):
    def f(_context, *args):
        ctx = dict(context)
        ctx[car] = lambda __context: SExp(*args)
        return cdr.eval(ctx)
    return f
def do_car(context, arg):
    return arg.eval(context).tpl[0]
def do_cdr(context, arg):
    return SExp(*arg.eval(context).tpl[1:])

Functions = {'+': doplus,
             '-': dominus,
             '*': dotimes,
             '/': dodiv,
             'sqrt': dosqrt,
             'pi': lambda _:math.pi,
             'map': domap,
             '%g': do_g,
             '`': do_quote,
             '#': do_quasiquote,
             'join': do_join,
             'apply': do_apply,
             'setf': do_setf,
             'lambda': do_lambda,
             'car': do_car,
             'cdr': do_cdr,
             }

if __name__ == '__main__':
    def test(text):
        s = SExp.parse(text, atoms=[tok_STRING])
        print s
        print '=>', repr(s.eval(Functions))
    test('(/ (+ 1 (sqrt 5)) 2)')
    test('(join , (map %g (map sqrt (` 1 2 3 4))))')
    test("(# 'a b' (join + (` c d)))")
    test('(cdr (` 1 2))')
    test('(apply + (cdr (` 1 2)))')
    # define a function that behaves like '+', but must have at least one argument
    test('(setf plus (lambda x (+ (car (x)) (apply + (cdr (x))))))')
    test('(plus 1 2 3)')