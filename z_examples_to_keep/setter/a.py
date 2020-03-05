
# class C(object):
#     def __init__(self):
#         self.x = 4
#
# c = C()
# c.y = 5
# print(c.__dict__)

class A:
    _unlocked = True
    def __init__(self):
        self.attr1 = 'attr1'
        self._unlocked = False

    def __setattr__(self, name, value):
        if name in self.__dict__ or self._unlocked:
            self.__dict__[name] = value
        else:
            raise AttributeError("Only previously defined attributes are accepted.")

a = A()
print(a.__dict__)
try:
    a.newattr = 'newattribute'
finally:
    print('finally', a.__dict__)

