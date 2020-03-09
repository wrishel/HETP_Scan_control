"""Utilites including msgBpx. DateTimeEditUpdater, construct_list_text, ETP file paths"""

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QDateTimeEdit
# from PyQt5.QtCore import QTimer, QDateTime
import GLB_globals

GLB = GLB_globals.get()

def subpath_to_image(num):
    """Break up num into a directory/file name combo, without the file type suffix.

       Num should be an integer in numeric or string form, <= 999999."""

    fname = ('00000' + str(num))[-6:]
    dir = fname[:3]
    return dir, fname

def fullpath_to_image(num):
    base = GLB.config['Election']['pathtoimages']
    dir, fname = subpath_to_image(num)
    return  f"{base}/{dir}/{fname}.jpg"   # todo: polishing: this is ugly and scanner-specific

GLB.register(subpath_to_image, "subpath_to_image")
GLB.register(fullpath_to_image, "fullpath_to_image")



# FOLLOWING DEPRECATED IN FAVOR OF PUTTING THE SAME CODE IN-LINE

def msgBox(msgText, msgInformativeText, msgIcon, msgDetailText, msgButtons, msgDefaultButton):
    """DEPRECATED Display a message box and return the code indicating which button was pressed."""

    msg = QMessageBox()
    msg.setWindowTitle("Notification")
    msg.setText(msgText)
    msg.setInformativeText(msgInformativeText)
    msg.setDetailedText(msgDetailText)
    msg.setIcon(msgIcon)
    msg.setStandardButtons(msgButtons)
    msg.setDefaultButton(msgDefaultButton)
    x = msg.exec()
    return x

# cheat sheet for QMessageBox constants
"""
BUTTONS
-------
QMessageBox.Ok
QMessageBox.Open
QMessageBox.Save
QMessageBox.Cancel
QMessageBox.Close
QMessageBox.Discard
QMessageBox.Apply
QMessageBox.Reset
QMessageBox.RestoreDefaults
QMessageBox.Help
QMessageBox.SaveAll
QMessageBox.Yes
QMessageBox.YesToAll
QMessageBox.No
QMessageBox.NoToAll
QMessageBox.Abort
QMessageBox.Retry
QMessageBox.Ignore

ICONS
-----
QMessageBox.Question        For asking a question during normal operations.
QMessageBox.Information     For reporting information about normal operations.
QMessageBox.Warning         For reporting non-critical errors.
QMessageBox.Critical        For reporting critical errors.
"""


def construct_list_text(list):
    """Return the Oxford comma expression of the items in list, with 'and'.

       If the list ie empty, return an empty string"""

    conjunction = 'and'
    locallist = list.copy()
    l = len(locallist)
    res = ''
    if l == 1:
        res = locallist[0]
    elif l>1:
        locallist[-1] = conjunction + ' ' + locallist[-1]
        pmark = ' '
        if l > 2:
            pmark = ', '
        res = pmark.join(locallist)

    return res

if __name__ == '__main__':

    # test the construct_list_text function

    list = []
    assert  construct_list_text(list) == '', f'construct_list_text Failed on {list}'
    list.append('One')
    assert  construct_list_text(list) == 'One', f'construct_list_text Failed on {list}'
    list.append('Two')
    assert  construct_list_text(list) == 'One and Two', f'construct_list_text Failed on {list}'
    list.append('Three')
    assert  construct_list_text(list) == 'One, Two, and Three', f'construct_list_text Failed on {list}'
    list += ['Four', 'Five']
    assert construct_list_text(list) == 'One, Two, Three, Four, and Five', f'construct_list_text Failed on {list}'

