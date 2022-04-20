#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation:
"""

# @Time : 20-Apr-22
# @File : FileManager.py
# @User: MICHAEL

__version__ = "1.0.1"
__author__ = "Michael Reda"
__email__ = "eng.michaelreda@gmail.com"
__license__ = "GPL"
__copyright__ = "Michael Reda"
__status__ = "Beta"

# ---------------------------------
# import libraries
import os
import sys
import zipfile

import requests

from PySide2 import QtWidgets

# ---------------------------------
# Variables
__python__ = sys.version_info[0]


# ---------------------------------
# start here
# ---------------------------------

class FileManager:

    def make_dirs(self, path, *args):
        if not os.path.isdir(os.path.join(path, *args)):
            os.makedirs(os.path.join(path, *args))

        return os.path.join(path, *args).replace("\\", "/")

    def download_file(self, url, output_dir):
        """
        To download a file and localize it on desk
        :param url: (str) the url address of file
        :param output_dir: (str) system path of download directory
        :return: (str) the downloaded file path (bool) if anything wrong with download
        """

        # Make sure you run the server first
        # py - 3.7 - m http.server
        res = requests.get(url)
        try:
            downloaded_file = os.path.join(output_dir, os.path.basename(url))
            # check if the url is exists
            if res.status_code == 200:
                with open(downloaded_file, "wb") as fd:
                    fd.write(res.content)
                return downloaded_file
            else:
                return False
        except:
            return False

    def extract_zip(self, zip_file_file):
        """
        To extract the zip file in the same directory
        :param zip_file_file: (str) the zip file path
        :return: (str) the system directory of extracted folder
        """
        zip_dir = os.path.dirname(zip_file_file)
        zip_name = os.path.basename(zip_file_file)
        with zipfile.ZipFile(zip_file_file, 'r') as zip:
            zip.extractall(zip_dir)

        output_dir = os.path.join(zip_dir, zip_name.rsplit(".")[0])

        return output_dir

    def message(self, parent=None, title="Error", message=""):

        msg = QtWidgets.QMessageBox()
        if parent:
            msg = QtWidgets.QMessageBox(parent)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(title)
        msg.setInformativeText(message)
        msg.setWindowTitle(title)
        msg.exec_()
        QtWidgets.QMessageBox(parent, title, message)


# ---------------------------------
# Main function
def main(*args, **kwargs):
    fm = FileManager()
    fm.extract_zip("58de157a.zip")


if __name__ == '__main__':
    print(("-" * 20) + "\nStart of code...\n" + ("-" * 20))
    main()
    print(("-" * 20) + "\nEnd of code.\n" + ("-" * 20))
