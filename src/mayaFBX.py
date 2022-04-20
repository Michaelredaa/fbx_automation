#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation:
"""

# @Time : 20-Apr-22
# @File : mayaFBX.py
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
import re
import shutil

from PySide2 import QtWidgets

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

from utils.FileManager import FileManager

# ---------------------------------
# Variables
__python__ = sys.version_info[0]

MayaPlugins = ["fbxmaya.mll"]

TexturesExtensions = ["png", "jpg"]

TexturePatterns = {
    "color": ["(?i)diffuse", "(?i)albedo", "(?i)t_.*_.*_(?i)bc"],
    "roughness": ["(?i)roughness", "(?i)glossinss", "(?i)t_.*_.*_(?i)r"],
    "metallic": ["(?i)metallic", "(?i)metalness", "(?i)t_.*_.*_(?i)m"],
    "normal": ["(?i)normal", "(?i)t_.*_.*_(?i)n"],
    "height": ["(?i)height", "(?i)displacement", "(?i)t_.*_.*_(?i)h"],
    "opacity": ["(?i)opacity", "(?i)t_.*_.*_(?i)o"]
}

Materials = {
    "phong": {
        "color": (".outColor", ".color"),
        "roughness": (".outAlpha", ".cosinePower"),
        "metallic": (".outAlpha", ".reflectivity"),
        "normal": (".outAlpha", ".normalCamera"),
        "opacity": (".outColor", ".transparency"),
    }
}


# ---------------------------------
# start here
# ---------------------------------
def maya_main_window():
    # Return the Maya main window widget as a Python object
    main_window_ptr = omui.MQtUtil.mainWindow()
    mayaWin = wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

    return mayaWin


class MayaFBX(FileManager):
    def __init__(self):
        super(MayaFBX, self).__init__()

        self.maya_window = maya_main_window()
        self.startup()

    def startup(self):
        for plugin in MayaPlugins:
            self.load_plugin(plugin)

    def load_plugin(self, plugin_name="AbcExport.mll"):
        """
        To make sure the plugin is loaded in maya
        :param plugin_name: (str) the plugin name
        :return:
        """
        if not cmds.pluginInfo(plugin_name, q=True, loaded=True):
            cmds.loadPlugin(plugin_name)

    def import_fbx(self, fbx_file_path):
        """
        To import fbx file
        :param fbx_file_path: the fbx filepath
        :return: list of imported objects
        """
        imported_nodes = []
        if not fbx_file_path.endswith("fbx"):
            cmds.warning('"{}" is not a fbx file.'.format(fbx_file_path))
            cmds.warning("Please choose the file endswith fbx to enable to import.")
            return imported_nodes
        before = cmds.ls(assemblies=True)
        cmds.file(fbx_file_path, pr=1, ignoreVersion=1, i=1, type="FBX", importFrameRate=True,
                  importTimeRange="override",
                  options="fbx")
        after = cmds.ls(assemblies=True)
        imported_nodes = list(set(after) - set(before))
        return imported_nodes

    def export_fbx(self, fbx_file_path, objects=None, options="default"):
        """
        TO export objects as fbx files
        :param fbx_file_path: the fbx filepath
        :param objects: list of objects to export
        :param options: the fbx export option
        :return: None
        """

        # check objects
        if not objects:
            objects = cmds.ls(sl=1)

        # default options
        if options == "default":
            options = "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1"

        # set selection to export
        cmds.select(cl=1)
        cmds.select(objects)

        # export fbx
        cmds.file(fbx_file_path, es=1, f=1, typ="FBX export", options=options)

    def makeIdentity(self, geo):
        """
        To reset all transformation of object
        :param geo: the object name
        :return:
        """
        cmds.makeIdentity(geo, apply=1, r=1, s=1, t=1)

    def ck_tex(self, texture_name):
        """
        TO get the map texture type
        :param texture_name: the texture map file name
        :return: the map type name
        """
        for map_type in TexturePatterns:
            if not isinstance(TexturePatterns[map_type], list):
                continue
            for regex in TexturePatterns[map_type]:
                if re.search(regex, texture_name):
                    return map_type

    def get_bind_material(self, geo):
        """
        To get the bind material of given geometry
        :param geo:
        :return: list of materials
        """
        shape_nodes = cmds.listRelatives(geo, c=1, type="mesh")
        if not shape_nodes:
            return
        shape_node = shape_nodes[0]
        sgs = cmds.listConnections(shape_node, type="shadingEngine")

        if not sgs:
            cmds.warning('"{}" has not connected shadingEngine.'.format(shape_node))
            return
        sg_node = sgs[0]
        mtls = cmds.listConnections(sg_node + ".surfaceShader")

        return mtls

    def import_texture(self, tex_path):
        """
        To import the texture inside maya
        """

        if not os.path.isfile(tex_path):
            cmds.warning("System Error: Can not import {} file. It not located.".format(tex_path))
            return False
        tex_name = os.path.basename(tex_path).split(".")[0]

        if not cmds.objExists(tex_name):
            place2d = cmds.shadingNode("place2dTexture", asUtility=True, n="p2d_#")
            file_node = cmds.shadingNode("file", asTexture=True, n=tex_name)
            cmds.defaultNavigation(connectToExisting=True, source=place2d, force=True, destination=file_node)
        else:
            file_node = tex_name

        cmds.setAttr(file_node + ".fileTextureName", tex_path, type="string")
        # ToDo: add configs of UDIMs

        return tex_name

    def import_fbx_with_texture(self, zip_dir):

        # fetch data
        fbx_file_path = ""
        textures = {}
        used_textures = []

        for f_name in os.listdir(zip_dir):
            f_path = os.path.join(zip_dir, f_name)
            if os.path.isdir(f_path):
                continue
            extension = f_name.rsplit(".", 1)[-1]
            if extension == "fbx":
                fbx_file_path = f_path
            elif extension in TexturesExtensions:
                map_type = self.ck_tex(f_name)
                if not map_type in textures:
                    textures[map_type] = []
                textures[map_type].append(f_path)

        # import fbx file
        fbx_nodes = self.import_fbx(fbx_file_path)
        if not fbx_nodes:
            return None, None

        for node in fbx_nodes:
            # reset transformation
            self.makeIdentity(node)

            # bind materials
            mtl_nodes = self.get_bind_material(node)
            if not mtl_nodes:
                self.message(self.maya_window, "Warning", '"{}" does not have any bind material.'.format(node))
                continue

            for mtl_node in mtl_nodes:
                mtl_type = cmds.nodeType(mtl_node)
                mtl_connection = Materials.get(mtl_type)
                if not mtl_connection:
                    self.message(self.maya_window,
                                 "Warning",
                                 '"{}" material type does not have any configuration, please configer it first '.format(
                        mtl_node))
                    continue

                for tex_type in textures:
                    # check the material`s textures
                    for texture_path in textures[tex_type]:
                        if not re.search(mtl_node, os.path.basename(texture_path)):
                            continue

                        # import texture
                        file_node = self.import_texture(texture_path)

                        tex_plug = file_node + mtl_connection[tex_type][0]
                        mtl_plug = mtl_node + mtl_connection[tex_type][-1]

                        # set the default colorspace
                        # ToDo: will configer the colorspace
                        cmds.setAttr(file_node + ".colorSpace", "Raw", type="string")

                        # connect Texture
                        if tex_type == "color":
                            cmds.setAttr(file_node + ".colorSpace", "sRGB", type="string")
                            cmds.setAttr(file_node + ".alphaIsLuminance", 0)
                            cmds.connectAttr(tex_plug, mtl_plug, f=1)

                        elif tex_type == "normal":
                            cmds.setAttr(file_node + ".alphaIsLuminance", 1)

                            # creates bump map
                            normal_name = file_node + '_bump2d'
                            normal_map = cmds.shadingNode('bump2d', n=normal_name, asUtility=1)

                            # connect attributes
                            cmds.connectAttr(tex_plug, normal_map + ".bumpValue", f=1)
                            cmds.connectAttr(normal_map + ".outNormal", mtl_plug, f=1)
                        else:
                            cmds.setAttr(file_node + ".alphaIsLuminance", 1)
                            cmds.connectAttr(tex_plug, mtl_plug, f=1)

                        used_textures.append(file_node)
        return used_textures, fbx_nodes

    def deleteUnsedNodes(self):
        """
        To delete unused nodes in hypershade
        """
        mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
        mel.eval('MLdeleteUnused;')

    def re_export_fbx_file(self, fbx_file_path, tex_nodes, fbx_nodes, options="default"):

        fbx_dir = os.path.dirname(fbx_file_path)
        tex_dir = self.make_dirs(fbx_dir, "textures")

        # move textures
        for tex_node in tex_nodes:
            old_tex_path = cmds.getAttr(tex_node + ".fileTextureName")
            if not old_tex_path:
                continue
            tex_name = os.path.basename(old_tex_path)
            new_tex_path = os.path.join(tex_dir, tex_name)
            shutil.move(old_tex_path, new_tex_path)

            # repath texture
            cmds.setAttr(tex_node + ".fileTextureName", new_tex_path, type="string")

        # export fbx
        self.export_fbx(fbx_file_path, fbx_nodes, options=options)

        cmds.delete(fbx_nodes)
        self.deleteUnsedNodes()


# ---------------------------------
# Main function
def main(*args, **kwargs):
    pass


if __name__ == '__main__':
    print(("-" * 20) + "\nStart of code...\n" + ("-" * 20))
    main()
    print(("-" * 20) + "\nEnd of code.\n" + ("-" * 20))
