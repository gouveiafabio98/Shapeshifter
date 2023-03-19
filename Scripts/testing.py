import bpy
import random
from pathlib import Path


#--- Library ---#

def clearScene():
    bpy.ops.outliner.orphans_purge()
    used_object_names = set()
    for obj in bpy.context.scene.objects:
        used_object_names.add(obj.name)
    for obj in bpy.data.objects:
        if obj.name not in used_object_names:
            bpy.data.objects.remove(obj, do_unlink=True)

def loadLibraries():
    clearScene()
    
    prefs = bpy.context.preferences
    filepaths = prefs.filepaths
    asset_libraries = filepaths.asset_libraries
    for asset_library in asset_libraries:
        library_path = Path(asset_library.path)
        blend_files = [fp for fp in library_path.glob("**/*.blend") if fp.is_file()]
        for blend_file in blend_files:
            with bpy.data.libraries.load(str(blend_file), assets_only=True) as (data_from, data_to):
                data_to.objects = data_from.objects
    return data_to.objects

def searchTag(assets, tag_name):
    list = []
    for asset in assets:
        if asset not in list:
            for tag in asset.asset_data.tags:
                if tag.name == tag_name:
                    list.append(asset)
    return list

#--- Logic ---#

def constructor():
    list = loadLibraries()

    tag1 = "Body"
    # Select a body element 
    obj1 = randomAsset(list, tag1)
    bpy.context.collection.objects.link(obj1)
    print(obj1.name)
    # Loop his Vertex Groups
    for vg in obj1.vertex_groups:
        tag2 = vg.name
        obj2 = randomAsset(list, vg.name)
        bpy.context.collection.objects.link(obj2)
        print(obj1, tag2, obj2, tag1)


def randomAsset(list, name):
    return random.choice(searchTag(list, name))

constructor()