from peco import *


def get_loc(text, pos):
    line = text.count('\n', 0, pos)
    col = pos - text.rfind('\n', 0, pos) - 1
    return line, col


when = lambda f: lambda s: s._replace(ok=f(s.stack[-1]))

mkmove = to(lambda m, x: (m, x))
mkpen = to(lambda m: (m,))
mkrepeat = to(lambda x, b: ('repeat', x, b))
mkcall = to(lambda n: ('call', n))
mkfunc = to(lambda n, b: ('func', n, b))
mkblock = to(lambda b: ('block', b))

ws = eat(r'\s*|#.*')
token = lambda f: memo(seq(ws, f))
tok = lambda c: token(push(eat(c)))
skip = lambda c: token(eat(c))

KW = 'fd bk lt rt pu pd repeat to end'.split()
name = seq(tok(r'[a-zA-Z_][a-zA-Z0-9_]*'), when(lambda x: x not in KW))
num = seq(tok(r'-?[0-9]+'), to(lambda x: float(x)))

cmd = lambda s: cmd(s)
block = seq(group(many(cmd)), mkblock)

cmd = alt(
    seq(tok('fd|bk|lt|rt'), num, mkmove),
    seq(tok('pu|pd'), mkpen),
    seq(skip('repeat'), num, skip(r'\['), block, skip(r'\]'), mkrepeat),
    seq(name, mkcall)
)

func = seq(skip('to'), name, block, skip('end'), mkfunc)
main = seq(group(many(alt(cmd, func))), ws, mkblock)


def test():
    src = '''
    to star
      repeat 5 [fd 100 rt 144]
    end
    star
    '''
    s = parse(src, main)
    result = (('block',
               (('func',
                 'star',
                 ('block',
                  (('repeat',
                    5.0,
                    ('block',
                     (('fd', 100.0),
                      ('rt', 144.0)))),))),
                ('call', 'star'))),)
    assert s.ok and s.stack == result
    err = '''
    to center_top
      pu
      fd 80
      rt !90
      fd 20
      lt 90
      pd
    end
    '''
    s = parse(err, main)
    assert not s.ok and get_loc(s.text, s.glob['err']) == (4, 9)
