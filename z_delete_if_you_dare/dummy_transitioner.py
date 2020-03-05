'''Dummy version of Transitioner.py to be used in unit testing a module.
   '''

class Transitioner():
    '''Negotiate transition among panel widgets.'''

    def __init__(self):
        ...

    def set_initial_panel(self, widget):
        self.current_panel = widget

    def set_current_panel(self, widget_name):
        assert False, ' you have wandered into the dumpster for old code'
        t = self.current_panel.exit_check()
        print('Switching to %s. exit_check value = %s' % (widget_name, t))