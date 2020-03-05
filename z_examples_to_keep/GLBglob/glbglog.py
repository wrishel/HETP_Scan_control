import GLB_globals
import sys

GLB = GLB_globals.get()


class A:
    def __init__(self):
        # name = 'aaaname'
        self.given = 'given'

    def amethod(self):
        self.ameth = 'ameth'
        print('amethod')

a = A()
a.amethod()
try:
    GLB.register(a)
except AttributeError as e:
    print('expected error', str(e), file=sys.stderr)

a.name = 'aaaname'
try:
    GLB.register(a)
except AttributeError as e:
    print('error after name', file=sys.stderr)

GLB.aaaname.amethod()
