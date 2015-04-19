#!/usr/bin/python

from sexpy import SExp, tok_STRING

class HtmlNodeType(object):
    def __init__(self, name, allowed_children):
        self.name = name
        self.ac = allowed_children
    def __call__(self, context, *args):
        if self.ac is None: # not specified
            return
        for arg in args:
            if isinstance(arg, SExp):
                if isinstance(arg.tpl[0], HtmlNodeType):
                    if arg.tpl[0].name not in self.ac:
                        raise Exception(arg.tpl[0].name, "not allowed as child of", self.name)
class HtmlAttributeType(HtmlNodeType):
    def __init__(self, name):
        super(HtmlAttributeType, self).__init__(name, [])
    def __call__(self, context, *args):
        super(HtmlAttributeType, self).__call__(context, *args)
        content = []
        for arg in args:
            if isinstance(arg, SExp):
                content.append(arg.eval(context))
            else:
                content.append(arg)
        return HtmlAttribute(self.name, content)
class HtmlElementType(HtmlNodeType):
    def __call__(self, context, *args):
        super(HtmlElementType, self).__call__(context, *args)
        attrs = []
        content = []
        for arg in args:
            if isinstance(arg, SExp):
                val = arg.eval(context)
                if isinstance(val, HtmlElement):
                    content.append(val)
                elif isinstance(val, HtmlAttribute):
                    attrs.append(val)
                else:
                    assert 0, val
            else:
                content.append(str(arg))
        return HtmlElement(self.name, attrs, content)
class HtmlAttribute(object):
    def __init__(self, name, content):
        self.name = name
        self.content = content
    def __str__(self):
        return '%s="%s"'%(self.name, ' '.join(map(str, self.content)))
class HtmlElement(object):
    def __init__(self, name, attrs, content):
        self.name = name
        self.attrs = attrs
        self.content = content
    def __str__(self):
        opentag = ' '.join([self.name,] + map(str, self.attrs))
        if self.content:
            return '<%s>'%opentag + ' '.join(map(str, self.content)) + '</%s>'%(self.name,)
        else:
            return '<%s/>'%opentag

HTML = {'html':HtmlElementType('html', ['head', 'body']),
        'head':HtmlElementType('head', ['title', 'meta', 'script', 'style', 'link']),
        'title':HtmlElementType('title', []),
        'meta':HtmlElementType('meta', ['http-equiv', 'content', 'name', 'scheme', 'charset']),
        'http-equiv':HtmlAttributeType('http-equiv'),
        'content':HtmlAttributeType('content'),
        'name':HtmlAttributeType('name'),
        'scheme':HtmlAttributeType('scheme'),
        'charset':HtmlAttributeType('charset'),
        'script':HtmlElementType('script', ['src', 'type', 'defer']),
        'src':HtmlAttributeType('src'),
        'type':HtmlAttributeType('type'),
        'defer':HtmlAttributeType('defer'),
        'style':HtmlElementType('style', ['type']),
        'link':HtmlElementType('link', ['rel', 'type', 'href']),
        'rel':HtmlAttributeType('rel'),
#        '':HtmlAttributeType(''),
        'body':HtmlElementType('body', None),
        'a':HtmlElementType('a', None),
        'href':HtmlAttributeType('href'),
        'p':HtmlElementType('p', None),
        'h1':HtmlElementType('h1', None),
        'h2':HtmlElementType('h2', None),
        'h3':HtmlElementType('h3', None),
        'h4':HtmlElementType('h4', None),
        'h5':HtmlElementType('h5', None),
        'h6':HtmlElementType('h6', None),
        'br':HtmlElementType('br', []),
        'blockquote':HtmlElementType('blockquote', None),
        'img':HtmlElementType('img', ['src']),
#        '':HtmlElementType('', None),
        }

if __name__ == '__main__':
    test = """(html (head (title SML generated page))
                    (body (h1 SML generated page)
                          (p A simple HTML page generated from SML. (br)
                             (a (href /index.htm) Index)
                          )
                    )
              )"""
    s = SExp.parse(test)
    print s
    print s.eval(HTML)
