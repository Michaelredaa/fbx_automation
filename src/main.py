#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation:
"""

# @Time : 20-Apr-22
# @File : main.py
# @User: MICHAEL

__version__ = "1.0.1"
__author__ = "Michael Reda"
__email__ = "eng.michaelreda@gmail.com"
__license__ = "GPL"
__copyright__ = "Michael Reda"
__status__ = "Beta"

# ---------------------------------
# import libraries
from imp import reload

import mayaFBXUI
reload(mayaFBXUI)
from mayaFBXUI import MayaFBXUI
from mayaFBX import maya_main_window


# ---------------------------------
# Main function
def main(*args, **kwargs):
    fbx_window = MayaFBXUI(maya_main_window())
    fbx_window.show()



if __name__ == '__main__':
    print(("-" * 20) + "\nStart of code...\n" + ("-" * 20))
    main()
    print(("-" * 20) + "\nEnd of code.\n" + ("-" * 20))
