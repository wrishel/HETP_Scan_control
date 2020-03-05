'''Supports transition from one main_panel to the next.

   All panel widgets must provide exit_check method.
   They are expected to put up an error box if they don't approve
   the switch.

   The class name of each panel must be unique.
   '''

import sys

# todo: signal main panel changes

class Transitioner():
    '''Negotiate transition among panel widgets.'''

    def __init__(self, main_panel_widget=None, top_panel=None):
        ...

class Transitioner_for_testing(Transitioner):

    def __init__(self, main_panel_widget=None, top_panel=None):
        super().__init__(main_panel_widget, top_panel)
        0

