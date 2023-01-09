import bpy
from random import randint
from bpy.types import (Panel, Operator)
from bpy.utils import register_class, unregister_class
from pathlib import Path
import mathutils

def loadLibraries():
    prefs = bpy.context.preferences
    filepaths = prefs.filepaths
    asset_libraries = filepaths.asset_libraries
    for asset_library in asset_libraries:
        library_name = asset_library.name
        library_path = Path(asset_library.path)
        blend_files = [fp for fp in library_path.glob("**/*.blend") if fp.is_file()]
        for blend_file in blend_files:
            with bpy.data.libraries.load(str(blend_file), assets_only=True) as (data_from, data_to):
                print(data_from.objects)
                data_to.objects = data_from.objects
                return data_to.objects
# -----------------------------------------------------------------------------
def verticesVgroup(a,index):
    vlist = []
    for v in a.data.vertices:
        for g in v.groups:
            if g.group == index:
                vlist.append(v.index)
    return vlist
# -----------------------------------------------------------------------------
def getMiddle(obj, name):
    vgroups = obj.vertex_groups # GET ALL VERTEX GROUPS
    index = vgroups[name].index # GET INDEX OF "GROUP"
    indexGroup = verticesVgroup(obj, index) # GET INDEX OF VERTEX IN GROUP
    
    #CALCULAR O CENTRO DO VERTEXGROUP
    sum = mathutils.Vector((0, 0, 0))
    for i in indexGroup:
        sum += obj.data.vertices[i].co
    
    return sum/len(indexGroup)
# -----------------------------------------------------------------------------
def translateVG(obj1, tag1, obj2, tag2):
    print(obj2.location)
    new = obj1.location + getMiddle(obj1, tag1) - getMiddle(obj2, tag2)
    obj2.location = new
# -----------------------------------------------------------------------------
objs=loadLibraries()

if(len(objs)==2):
    for ob in objs:
        bpy.context.collection.objects.link(ob)
    translateVG(objs[0], "Group", objs[1], "Group")