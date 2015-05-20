#!/usr/bin/python

import re
import math

class SExp(object):
    """Grammar of SExps:
    sexp     ::= '(' ident arg-list? ')'
    arg-list ::= (ident | word | sexp) arg-list?
    
    ident and word both ~= '[^()\s]+'
    """
    def __init__(self, *children):
        if children:
            self.fn = children[0]
        else:
            self.fn = None
        self.args = children[1:]
    @property
    def tpl(self):
        if self.fn is None:
            return ()
        return (self.fn,) + self.args
    @classmethod
    def retok(cls, r, s):
        m = re.match(r, s)
        if m:
            return (m.group(0), m.end())
        return None
    @classmethod
    def parse(cls, string, idents=r'[^()\s]+', atoms=[]):
        def tok_LPAREN(s):
            return (tok_LPAREN, cls.retok(r'\(', s))
        def tok_RPAREN(s):
            return (tok_RPAREN, cls.retok(r'\)', s))
        def tok_IDENT(s):
            return (tok_IDENT, cls.retok(idents, s))
        def tok_WORD(s):
            return (tok_WORD, cls.retok(r'[^()\s]+', s))
        def _tokenise(string):
            tokens = [tok_LPAREN, tok_RPAREN] + atoms + [tok_IDENT, tok_WORD]
            string = string.lstrip()
            if not string:
                return []
            for tok in tokens:
                l, v = tok(string)
                if v:
                    return [(l, v[0])] + _tokenise(string[v[1]:])
            raise ValueError("Untokenisable string", string)
        tokens = _tokenise(string)
        stack = [[]]
        for tok in tokens:
            typ, val = tok
            if len(stack) == 1 and typ != tok_LPAREN:
                raise ValueError("Bare %s, expected LPAREN"%typ.__name__, val)
            if typ == tok_IDENT:
                stack[-1].append(('id', val))
            else:
                if len(stack) > 1 and not stack[-1]:
                    raise ValueError("%s after LPAREN, expected IDENT"%typ.__name__, val)
                if typ == tok_WORD or typ in atoms:
                    stack[-1].append(('wd', val))
                elif typ == tok_LPAREN:
                    stack.append([])
                elif typ == tok_RPAREN:
                    parent = stack[-2]
                    parent.append(stack.pop())
                else:
                    assert 0, typ
        if len(stack) > 1:
            raise ValueError("Reached end of string, expected RPAREN", stack)
        if len(stack[0]) > 1: # e.g. '(a b) (c)', doesn't have a single root
            raise ValueError("Multiple sexps found in string", stack)
        def _build(tree):
            if isinstance(tree, list):
                car = tree[0]
                cdr = tree[1:]
                assert car[0] == 'id'
                return cls(car[1], *map(_build, cdr))
            else:
                return tree[1]
        return _build(stack[0][0])
    def __str__(self):
        if self.fn is None:
            return 'nil'
        def strish(s):
            if isinstance(s, str) and re.search('\s', s):
                return "'%s'"%s
            return str(s)
        return '(%s)'%' '.join(map(strish, (self.fn,)+self.args))
    def __repr__(self):
        if self.fn is None:
            return 'nil'
        return '(%s)'%' '.join(map(repr, (self.fn,)+self.args))
    def eval(self, context):
        """context is a dict mapping identifiers to functions"""
        if self.fn not in context:
            raise IndexError("Undefined identifier", self.fn)
        return context[self.fn](context, *self.args)

def tok_STRING(s):
    m = re.match(r'"((?:[^"]|\")*)"', s)
    if m:
        return (tok_STRING, (m.group(1), m.end()))
    m = re.match(r"'((?:[^']|\')*)'", s)
    if m:
        return (tok_STRING, (m.group(1), m.end()))
    return (tok_STRING, None)

class CSExp(SExp):
    """Grammar of CSExps:
    sexp     ::= '(' ident arg-list? ')'
    arg-list ::= (ident | word | "string" | sexp) arg-list?
    
    ident ~= '[a-zA-Z_]\w*'
    word ~= '[^()\s]+'
    """
    @classmethod
    def parse(cls, string, idents=r'[a-zA-Z_]\w*', atoms=[tok_STRING]):
        return super(CSExp, cls).parse(string, idents=idents, atoms=atoms)

if __name__ == '__main__':
    test = "(times (sqrt 2) (plus (pi) 1))"
    s = CSExp.parse(test)
    print str(s)

    def numeric(context, arg):
        """Interpret a value, which is either an SExp or a string, as a number."""
        if isinstance(arg, SExp):
            return arg.eval(context)
        else:
            return float(arg)
    def dotimes(context, *args):
        if len(args):
            return numeric(context, args[0]) * dotimes(context, *args[1:])
        return 1
    def doplus(context, *args):
        return sum(numeric(context, arg) for arg in args)
    def dosqrt(context, arg):
        return math.sqrt(float(arg))
    val = s.eval({'times':dotimes,
                  'plus':doplus,
                  'sqrt':dosqrt,
                  'pi':lambda _:math.pi})
    print val
    assert val == math.sqrt(2) * (math.pi + 1)
