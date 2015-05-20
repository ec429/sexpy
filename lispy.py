#!/usr/bin/python

from sexpy import SExp, tok_STRING
import math
import sys

def numeric(context, arg):
    """Interpret a value, which is either an SExp or a string, as a number."""
    try:
        if isinstance(arg, SExp):
            arg = arg.eval(context)
        return float(arg)
    except:
        sys.stderr.write("arg was %s\n"%(arg,))
        raise
def do_plus(context, *args):
    return sum(numeric(context, arg) for arg in args)
def do_minus(context, car, *cdr):
    return numeric(context, car) - do_plus(context, *cdr)
def do_times(context, *args):
    if len(args):
        return numeric(context, args[0]) * do_times(context, *args[1:])
    return 1
def do_div(context, car, *cdr):
    return numeric(context, car) / do_times(context, *cdr)
def do_sqrt(context, arg):
    return math.sqrt(numeric(context, arg))
def do_map(context, car, cdr):
    return SExp(*[SExp(car, x).eval(context) for x in cdr.eval(context).tpl])
def do__g(context, arg):
    return '%g'%numeric(context, arg)
def do_quote(context, *args):
    return SExp(*args)
def do_quasiquote(context, *args):
    return SExp(*[x.eval(context) if isinstance(x, SExp) else x for x in args])
def do_join(context, car, cdr):
    return car.join(cdr.eval(context).tpl)
def do_apply(context, car, cdr):
    fn = car.eval(context)
    if isinstance(fn, SExp):
        if fn.args:
            raise Exception("First argument to apply", car, "does not yield single item")
        fn = fn.fn
    return SExp(fn, *cdr.eval(context).tpl).eval(context)
def do_setf(context, car, cdr):
    if car in context:
        raise Exception("Redefinition of", car, "as", cdr, " - was", context[car])
    return do_setf_bang(context, car, cdr)
def do_setf_bang(context, car, cdr):
    if isinstance(cdr, SExp):
        cdr = cdr.eval(context)
    if callable(cdr):
        context[car] = cdr
    else:
        def f(_context, *_args):
            if cdr in context:
                return context[cdr](_context, *_args)
            return cdr
        context[car] = f
def do_unsetf(context, car):
    if car not in context:
        raise Exception("Can't unset", car, " - not set!")
    del context[car]
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
def do_cond(context, car, et, enil):
    if car.eval(context):
        return et
    return enil
def do_eval(context, car):
    """It ought to be possible to (setf eval (lambda function (apply function (`)))), but
    do_lambda wraps the variable in one layer of evaluation too many for that to work.
    It turns out do_eval is needed for lambdas to be useful."""
    return car.eval(context).eval(context)

Functions = {'+': do_plus,
             '-': do_minus,
             '*': do_times,
             '/': do_div,
             'sqrt': do_sqrt,
             'pi': lambda _:math.pi,
             'map': do_map,
             '%g': do__g,
             '`': do_quote,
             '#': do_quasiquote,
             'join': do_join,
             'apply': do_apply,
             'setf': do_setf,
             'setf!': do_setf_bang,
             'unsetf':do_unsetf,
             'lambda': do_lambda,
             'car': do_car,
             'cdr': do_cdr,
             'cond': do_cond,
             'eval': do_eval,
             }

if __name__ == '__main__':
    def test(text):
        try:
            s = SExp.parse(text, atoms=[tok_STRING])
            print s
            print '=> %r'%(s.eval(Functions),)
        except Exception as e:
            print '<<', repr(e)
            sys.excepthook(*sys.exc_info())
    test("(setf symb (lambda f (car (car (# (f))))))")
    test('(/ (+ 1 (sqrt 5)) 2)')
    test('(join , (map %g (map sqrt (` 1 2 3 4))))')
    test("(# 'a b' (join + (` c d)))")
    test('(cdr (` 1 2))')
    test('(apply (car (` +)) (cdr (` 1 2)))')
    save = dict(Functions)
    # define a function that behaves like '+', but must have at least one argument
    test('(setf plus (lambda x (+ (car (x)) (apply (symb +) (cdr (x))))))')
    test('(plus 1 2 3)')
    Functions = save
    # define a function that composes other functions
    test('(setf . (lambda x (lambda y (apply (car (x)) (# (apply (car (cdr (x))) (y)))))))')
    # ... and use it
    test('(setf fourth (. sqrt sqrt))')
    test('(fourth 81)')
    # define a nullary function (and appease the tauists)
    test('(setf tau (* 2 (pi)))')
    test('(tau)')
    # demonstrate conditionals (and piss the tauists off again)
    test('(eval (cond (tau sucks) (pi) (tau)))')
    import readline
    try:
        while True:
            line = raw_input()
            try:
                s = SExp.parse(line, atoms=[tok_STRING])
                print '=> %r'%(s.eval(Functions),)
            except Exception as e:
                print '<<', repr(e)
                sys.excepthook(*sys.exc_info())
    except EOFError:
        pass
