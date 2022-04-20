#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation:
"""

# @Time : 20-Apr-22
# @File : install.py
# @User: MICHAEL

__version__ = "1.0.1"
__author__ = "Michael Reda"
__email__ = "eng.michaelreda@gmail.com"
__license__ = "GPL"
__copyright__ = "Michael Reda"
__status__ = "Beta"

# ---------------------------------
# import libraries
import sys
import os

# ---------------------------------
# Variables
__python__ = sys.version_info[0]

try:
    import maya.mel
    import maya.cmds
    isMaya = True
except ImportError:
    isMaya = False


# ---------------------------------
# start here
# ---------------------------------
def onMayaDroppedPythonFile(*args, **kwargs):
    """This function is only supported since Maya 2017 Update 3"""
    pass


def _onMayaDropped():
    """Dragging and dropping this file into the scene executes the file."""

    src_path = os.path.join(os.path.dirname(__file__), 'src')
    icon_path = os.path.join(src_path, 'icons', 'logo.png')

    src_path = os.path.normpath(src_path)
    icon_path = os.path.normpath(icon_path)

    if not os.path.exists(icon_path):
        raise IOError('Cannot find ' + icon_path)


    command = '''
# ---------------------------------
# To automate the download and bind texture with fbx file
# www.cgtrader.com
# -----------------------------------


import sys
root_path = r'{path}'
if not root_path in sys.path:
    sys.path.append(root_path)

sys.argv = [r'{path}\main.py']
with open(r'{path}\main.py', 'r') as f:
    exec(f.read())

                '''.format(path=src_path)

    shelf = maya.mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = maya.cmds.tabLayout(shelf, query=True, selectTab=True)
    maya.cmds.shelfButton(
        command=command,
        annotation='FBX Automation Tool',
        sourceType='Python',
        image=icon_path,
        image1=icon_path,
        parent=parent
    )


if isMaya:
    _onMayaDropped()

