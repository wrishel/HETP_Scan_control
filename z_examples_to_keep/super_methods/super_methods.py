import types

class A(object):#but seems to work for old style objects too
    ax = 'ax'
    pass

def patch_me(target):
    def method(self, target):
        print (self.ax)
        print ("called from", target)
    target.method = types.MethodType(method,target)
    #add more if needed

a = A()
print(a.ax)
print (a)
#out: <__main__.A object at 0x2b73ac88bfd0>
patch_me(a)    #patch instance
a.method(5)
#out: x= 5
#out: called from <__main__.A object at 0x2b73ac88bfd0>
patch_me(A)
A.method(6)        #can patch class too
#out: x= 6
#out: called from <class '__main__.A'>
a
# out: <__main__.A object at 0x2b73ac88bfd0>
patch_me(a)  # patch instance
a.method(5)
# out: x= 5
# out: called from <__main__.A object at 0x2b73ac88bfd0>
patch_me(A)
A.method(6)  # can patch class too
# out: x= 6
# out: called from <class '__main__.A'>


#
#
# class A(object):
#     def methA(self):
#         print('meth')
#
# class Aa(A):
#     def __init__(self, obj):
#         self = obj
#     def methAA(self):
#         print('methAA')
#
# a = A()
# aa = Aa(a)
# aa.methAA()
# aa.meth()
#
