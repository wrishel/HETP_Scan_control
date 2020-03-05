'''Supports transition from one main_panel to the next.

   All panel widgets must provide exit_check method.
   They are expected to put up an error box if they don't approve
   the switch.

   The class name of each panel must be unique.
   '''

import sys
from etpconfig import Scanconfig
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QStackedWidget      # Only for Transitioner_for_testing

import GLB_globals
GLB = GLB_globals.get()


class PanelWidget(object):
    def __init__(self, widget, seq):
        self.GLB_name = 'transitioner'
        self.widget = widget
        self.seq = seq

    def __repr__(self):
        return f"<Panel Widget: widget={self.widget}, seq={self.seq},"

class Transitioner():
    """Negotiate transition among panel widgets."""

    def __init__(self, main_panel_widget, top_panel=None):
        '''main_panel_widget is the stacked widget managed here.'''
        # assert main_panel_widget is not None
        self.GLB_name = 'transitioner'
        self.main_panel_stack = main_panel_widget
        self.main_panels = dict()
        self.current_panel_name = None
        self.new_panel = None       # during a transition, switching to this panel
        self.seq = 0                # sequence number of next panel to be added
        self.top_panel = top_panel

    def add_widget_main_panels(self, widget, widg_name):
        """Add a widget to the main_panel stack, with bookkeeping."""

        if widg_name is None:
            widg_name = self.strip_class_name(widget)
        pw = PanelWidget(widget, self.seq)
        print('Adding:', widg_name, pw, file=sys.stderr)
        self.main_panels[widg_name] = pw
        # self.top_panel.show_active(w.top_panel_category)
        self.main_panel_stack.addWidget(widget)
        self.seq += 1

    def set_current_panel(self, widg_name):
        """Check if it is ok to exit the old panel, set up the new panel unless is says it
           can't be setup, and then activate the new panel. Coordinate with the top panel.

           widg_name is a string."""

        print('Trying to switch to:', widg_name, file=sys.stderr)
        if self.current_panel_name:          # is it OK to close currently open panel?
            if not self.main_panels[self.current_panel_name].widget.exit_check():
                print('\tfailed on old panel final check', file=sys.stderr)
                return False         # curr. panel doesn't want to let go

        self.new_panel = self.main_panels[widg_name]
        if not self.new_panel.widget.entry_check():  # set up the new panel or fail
            print('\tfailed on new panel setup', file=sys.stderr)
            return False

        indx = self.new_panel.seq
        self.main_panel_stack.setCurrentIndex(indx)
        self.current_panel_name = widg_name
        print('\tsucceeded', file=sys.stderr)

        # todo: find if the widget's module has an after_show method. If so
        # call it, for example to open an editable  widget so the first keystroke goes in it.

        return True

    def strip_class_name(self, object):
        """Return the unqualified class name of object"""
        t = str(type(object))[::-1]   # slicing to reverse string
        p = t.find('.')
        if p:
            t = t[0:p][2:]
            t = t[::-1]               # slicing to reverse string
        return t

GLB.register(Transitioner(None))      # Must update main_panel_widget when it's available

class Transitioner_for_testing(Transitioner):
    """Set up a Transitiner with a predefined dummy panel. For unit testing other panels.

       If everything goes well, this will probably end with a key error when the module
       under test tries to call another module.

       Example of usage:

            if __name__== '__main__':
                from transitioner import Transitioner_for_testing

                config = Scanconfig('etp.ini')
                app = QApplication(sys.argv)
                scanner = scanner_control.Scanner(config)
                transitioner = Transitioner_for_testing()
                transitioner.add_widget_main_panels(SysAdmin(config, QCoreApplication.quit,
                                                             "res/ui/sysadmin.ui",
                                                    "Sysadmin")
                transitioner.set_current_panel('Sysadmin')
                window = transitioner.main_panel_stack
                window.show()
                app.exec_()
        """

    def __init__(self, main_panel_widget=None, top_panel=None):
        if main_panel_widget is None:
            main_panel_widget = QStackedWidget()
            main_panel_widget.setMinimumSize(800, 600)
        super().__init__(main_panel_widget, top_panel)
        # todo set the default widget from a UI file that is reasonable sized.

    def set_current_panel(self, requested_panel):
        try:
            super().set_current_panel(requested_panel)
        except KeyError:
            print(f"Test run ended trying to switch to '{requested_panel}'.", file=sys.stderr)
            exit(1)

    def get_main_panel_widget(self):
        return self.widget