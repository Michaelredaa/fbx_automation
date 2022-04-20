#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation:
"""

# @Time : 20-Apr-22
# @File : mayaFBXUI.py
# @User: MICHAEL

__version__ = "1.0.1"
__author__ = "Michael Reda"
__email__ = "eng.michaelreda@gmail.com"
__license__ = "GPL"
__copyright__ = "Michael Reda"
__status__ = "Beta"

# ---------------------------------
# import libraries
import sys, os
import json

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from utils.MayaToolSettingsUI import Ui_ToolSettings
from utils.FileManager import FileManager
from mayaFBX import MayaFBX
# ---------------------------------
# Variables
__python__ = sys.version_info[0]
Icons = os.path.join(os.path.dirname(sys.argv[0]), "icons")

SizeObject = QDesktopWidget().screenGeometry(-1)
ScreenHeight = SizeObject.height()
ScreenWidth = SizeObject.width()


# ---------------------------------
# start here
# ---------------------------------
class MayaFBXUI(QMainWindow, Ui_ToolSettings, FileManager):
    def __init__(self, parent=None):
        super(MayaFBXUI, self).__init__(parent)
        self.setupUi(self)

        self.setMinimumSize(ScreenHeight * 0.5, ScreenHeight * 0.1)
        self.init_ui()
        self.connectEvents()
        self.get_user_data()

    def set_title(self, title):
        self.setWindowTitle(title)

    def set_icon(self, icon):
        self.setWindowIcon(QIcon(os.path.join(Icons, icon)))

    def browse_files(self, title="Choose a file", base_dir="", filter="Text (*.txt)"):
        return QFileDialog.getOpenFileName(self, title, base_dir, filter)[0]

    def browse_dirs(self, title="Choose a directory", base_dir=""):
        return QFileDialog.getExistingDirectory(self, title, base_dir)

    def ui_browse_row(self, gbox, row):

        label = QLabel("text")
        text_filed = QLineEdit()
        btn = QPushButton("")
        btn.setIconSize(QSize(10, 10))
        btn.setFlat(True)
        btn.setIconSize(QSize(20, 20))
        gbox.addWidget(label, row, 0, 1, 1, Qt.AlignRight)
        gbox.addWidget(text_filed, row, 1, 1, 1)
        gbox.addWidget(btn, row, 2, 1, 1)

        return label, text_filed, btn

    def init_ui(self):
        self.set_title("FBX Automation Tool::CGTrader(task)")
        self.set_icon("logo.png")

        # links list
        gbox = QGridLayout(self)

        self.l_links, self.le_links, self.pb_links = self.ui_browse_row(gbox, 0)
        self.pb_links.setIcon(QIcon(os.path.join(Icons, "file.png")))
        self.l_links.setText("Links List: ")

        self.l_downloads, self.le_downloads, self.pb_downloads = self.ui_browse_row(gbox, 1)
        self.pb_downloads.setIcon(QIcon(os.path.join(Icons, "folder.png")))
        self.l_downloads.setText("Download Directory: ")

        self.l_output, self.le_output, self.pb_output = self.ui_browse_row(gbox, 2)
        print(os.path.join(Icons, "folder.png"))
        self.pb_output.setIcon(QIcon(os.path.join(Icons, "folder.png")))
        self.l_output.setText("Output Directory: ")
        self.vl_space.addLayout(gbox)

        self.vl_space.addItem(QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

    def connectEvents(self):
        self.pb_cancle.clicked.connect(lambda: self.close())
        self.pb_apply.clicked.connect(self.onApply)
        self.pb_save.clicked.connect(self.onSave)

        self.pb_links.clicked.connect(lambda: self.onBrowse(self.le_links, "Select file with urls", False))
        self.pb_downloads.clicked.connect(lambda: self.onBrowse(self.le_downloads, "Select download Directory", True))
        self.pb_output.clicked.connect(lambda: self.onBrowse(self.le_output, "Select FBX output directory", True))

        self.actionReset_Settings.triggered.connect(self.onRestSettings)
        self.actionSave_Settings.triggered.connect(self.onSaveSettings)
        self.actionAbout.triggered.connect(self.onHelp)

    def onSave(self):
        self.onApply()
        self.close()

    def onApply(self):
        self.onSaveSettings()

        # download files
        links_list_path = self.le_links.text()
        download_dir = self.le_downloads.text()
        output_dir = self.le_output.text()

        # validate paths
        if not os.path.isfile(links_list_path):
            self.message(self, "Error", '"{}" does not exist on system'.format(links_list_path))
            return
        self.make_dirs(download_dir)
        self.make_dirs(output_dir)

        with open(links_list_path, "r") as file:
            for url in file.readlines():
                zip_file = self.download_file(url.strip(), download_dir)
                if not zip_file:
                    self.message(self, "Error", 'Download Error!\n"{}" is not valid'.format(url))
                    continue

                # Extract zip file
                zip_name = os.path.basename(zip_file).rsplit(".", 1)[0]
                out_zip_extract = self.extract_zip(zip_file)
                fbx = MayaFBX()
                tex_nodes, fbx_nodes = fbx.import_fbx_with_texture(out_zip_extract)

                if not fbx_nodes:
                    self.message(self,"warring", '{} does not have a fbx file'.format(url))
                    continue

                fbx_file_dir = self.make_dirs(os.path.join(output_dir, zip_name))
                fbx_file_path = os.path.join(fbx_file_dir, zip_name + ".fbx")
                fbx.re_export_fbx_file(fbx_file_path, tex_nodes, fbx_nodes)

    def onBrowse(self, lineEdit_object=None, title="Select directory", directory=True):

        if lineEdit_object is None:
            pass
        else:
            le_text = lineEdit_object.text()

            if (le_text is None) or not os.path.isdir(le_text):
                le_text = QDir.rootPath()

            if os.path.isfile(le_text):
                le_text = os.path.dirname(le_text)

            self.make_dirs(le_text)

            if directory:
                new_dir = self.browse_dirs(title, le_text)
            else:
                new_dir = self.browse_files(title, le_text)
            if new_dir:
                lineEdit_object.setText(new_dir)

    def onSaveSettings(self, ):
        # TODO: adding presets

        ui_data = {}
        ui_data["le_links"] = self.le_links.text()
        ui_data["le_downloads"] = self.le_downloads.text()
        ui_data["le_output"] = self.le_output.text()
        self.set_user_data(**ui_data)
        pass

    def onRestSettings(self):
        # TODO: adding presets
        pass

    def onHelp(self):
        imagePath = os.path.join(Icons, r"cgtrader.png")
        about = QMessageBox(self)
        about.setWindowTitle("CGTrader Tools")
        text = "CGTrader Tools-FBX Automation Tool"
        about.setInformativeText(
            '<center><h1 style="font-size:49;">{}</h1>&#0000;</center><img src={}></center><p>Version {}<br/>Copyright &copy;www.cgtrader.com</p>'.format(
                text, imagePath, __version__))
        about.exec_()

    def user_cfg_file(self):
        # get user cfg
        user_cfg_dir = os.path.join(os.path.expanduser("~"), "CGTrader")
        self.make_dirs(user_cfg_dir)
        user_cfg_path = os.path.join(user_cfg_dir, "fbx_tool.json")
        return user_cfg_path

    def set_user_data(self, **kwargs):
        user_cfg_path = self.user_cfg_file()

        if os.path.exists(user_cfg_path):
            with open(user_cfg_path, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        for key in kwargs:
            data[key] = kwargs[key]

        with open(user_cfg_path, 'w') as f:
            return json.dump(data, f, indent=4)

    def get_user_data(self):
        user_cfg_path = self.user_cfg_file()
        with open(user_cfg_path, 'r') as f:
            data = json.load(f)
        try:
            self.le_links.setText(data.get("le_links"))
            self.le_downloads.setText(data.get("le_downloads"))
            self.le_output.setText(data.get("le_output"))
        except:
            pass




# ---------------------------------
# Main function
def main(*args, **kwargs):
    pass


if __name__ == '__main__':
    print(("-" * 20) + "\nStart of code...\n" + ("-" * 20))
    main()
    print(("-" * 20) + "\nEnd of code.\n" + ("-" * 20))
