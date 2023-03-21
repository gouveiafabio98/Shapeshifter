import bpy
import random
# -----------------------------------------------------------------------------
import library
import combination
# -----------------------------------------------------------------------------
def constructor():
    list = library.loadLibraries()
    
    tag1 = "Body"
    obj1 = randomAsset(list, tag1)
    bpy.context.collection.objects.link(obj1)
    
    for vg in obj1.vertex_groups:
        tag2 = vg.name
        obj2 = randomAsset(list, tag2)
        bpy.context.collection.objects.link(obj2)
        combination.joinVG(obj1, tag2, obj2, tag1)


def randomAsset(list, name):
    return random.choice(library.searchTag(list, name))

def listTags():
    assets = library.loadLibraries()
    list = [] 

    for asset in assets:
        for tag in asset.asset_data.tags:
            option = (tag.name, tag.name, "")
            if option not in list:
                list.append(option)
    return list