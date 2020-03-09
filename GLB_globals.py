"""This is a singleton object that contains values that are are global throughout the run.

   In general it is good practice to have as few as possible, except for constants the
   never change value, where having many are useful in writing adaptable code.

   It's also good to have the the value names defined in the source code rather than
   being dynamically added during execution. This sis useful for IDEs that do preprompting
   when entering references to the objects.

   Most modules that use GLB do so by using these statements:

        import GLB_globals
        GLB = GLB_globals.get()

    And some module that runs early in the execution (such as the main) will aslo need
    to execute this

        GLB.set_object_instances()

   See comments in the code for the justification of its complexity."""

# The following attrubutes are pointers to objects that themselves are user of etp_globals.
# Therefore then cannot be set to their real values until after  this object itself has
# been fully created.
#
# OTOH, we want have the defined attributes in the __dict__ for this object to enable
# IDEs to provide typing assistance. Therefore they are definied here with an initial value
# of None.

# When the objects that will be among the globals then overwrite tne None value with
# a pointer to themselves.
#
# We don't want users of this object to add attributes at run time, because those won't
# be available in the IDEs for type_in assistance. Therefore, after we set _unlocked False
# the object will not accept new attributes.
#
# or perhase there is an introspective way to accomplish the type hint

import re
import sys
import os

_self_initializing = False
_myself = False

class GLBError(Exception): ...

class etp_globals(object):
    _unlocked = True

    def __init__(self):
        global _self_initializing
        if not _self_initializing:
            raise GLBError('GLB must be instantiated with GLB_globals.get()')
        if self._unlocked:
            self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
            self.path_to_etp_ini = 'etp.ini'
            self.img_file_name_match = re.compile(r'(\d\d\d\d\d\d)\.jpe*g$', re.IGNORECASE)

            self.main_window = None
            self.XXXDBG = True              # debugging flag to skip forward over early screens
            if self.XXXDBG: print("XXXDBG IS ON", file=sys.stderr)
            self._registering = False  # back door for the register function
            self._unlocked = False  # Lock the front door
            # print(vars(self))

        else:
            assert False, "Attempt to set a variable while locked."

    def __setattr__(self, name, value):
        if name in self.__dict__ or self._unlocked or self._registering:
            self.__dict__[name] = value
        else:
            raise AttributeError("Only previously-defined attributes are accepted.")

    def register(self, instance, name=None):
        if name is None:
            try:
                name = instance.GLB_name
            except AttributeError as e:
                raise AttributeError(f'GLB registration requires the attribute "GLB_name" but {e}')

        # todo: polishing do we really need the registering flag, we don't assign an attribute, right?
        print('registering', name)
        self._registering = True
        # the code below needs to find the value of the attribute named 'name'
        # if name in self.__dict__ and self.name is not None:
        if name in self.__dict__:
            print('attempt to reregister {name}', file=sys.stderr)
            self._registering = False
            return

        setattr(self, name, instance)
        self._registering = False

def get() -> etp_globals:
    """Assure that there are not multiple etp_global objects."""

    global _myself, _self_initializing
    if not _myself:
        _self_initializing = True
        _myself = etp_globals()
        self_initilizing = False
    return _myself


if __name__ == '__main__':
    GLB = get()
    try:
        GLB.notapredefinedattribute = 0
        assert False
    except AttributeError:
        ...

    class A:
        def __init__(self):
            self.given = 'given'

        def amethod(self):
            self.ameth = 'ameth'
            return(self.ameth)

    a = A()

    # Generate an error registering an object with no name property
    try:
        GLB.register(a)
    except AttributeError as e:
        print('EXPECTED ERROR:', str(e), file=sys.stderr)

    a.name = 'aaaname'
    try:
        GLB.register(a)
    except AttributeError as e:
        print('error after name', file=sys.stderr)

    assert GLB.aaaname.given == 'given', "Failed to access predefined attribute"
    assert GLB.aaaname.amethod() == 'ameth', 'Error accessing amethod'
