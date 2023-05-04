# ---- LIBRARIES ----

import library
import combination
import textures

import bpy
import random

# ---- FUNCTIONS ----
def constructor():
    list = library.loadLibraries()
    
    tag1 = "Body"
    obj1 = randomAsset(list, tag1)
    bpy.context.collection.objects.link(obj1)
    
    vgCombine(obj1, tag1, list, None, obj1)

def vgCombine(obj1, tag1, list, usedTag, usedObj):
    nodeGroups = []
    nodeGroups.append({"name": None, "node": textures.newNodeGroup(textures.getMaterial(obj1), tag1), "data": None})
    for vg in obj1.vertex_groups:
        if(vg.name != usedTag):
            tag2 = vg.name
            obj2 = randomAsset(list, tag2)
            nodeGroups.append({"name": tag2, "node": textures.newNodeGroup(textures.getMaterial(obj2), tag2), "data": None})

            bpy.context.collection.objects.link(obj2)
            combination.joinVG(obj1, tag2, obj2, tag1)
            vgCombine(obj2, tag2, list, tag1, obj1)
        else:
            nodeGroups.append({"name": usedTag, "node": textures.newNodeGroup(textures.getMaterial(usedObj), usedTag), "data": None})
    
    newMaterial = textures.createMaterial(nodeGroups, tag1)
    obj1.data.materials.append(newMaterial)
    obj1.active_material = newMaterial

def randomAsset(list, name):
    tags = library.searchTag(list, name)
    return random.choice(tags)