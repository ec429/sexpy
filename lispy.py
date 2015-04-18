#!/usr/bin/python

from sexpy import SExp
import math

def numeric(context, arg):
    """Interpret a value, which is either an SExp or a string, as a number."""
    if isinstance(arg, SExp):
        return arg.eval(context)
    else:
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

Functions = {'+': doplus,
			 '-': dominus,
			 '*': dotimes,
			 '/': dodiv,
			 'sqrt': dosqrt,
			 'pi': lambda _:math.pi,
			 'map': domap,
			 '%g': do_g,
			 '`': do_quote,
			 }

if __name__ == '__main__':
	s = SExp.parse('(/ (+ 1 (sqrt 5)) 2)')
	print s.eval(Functions)
	s = SExp.parse('(map %g (map sqrt (` 1 2 3 4)))')
	print repr(s.eval(Functions))
