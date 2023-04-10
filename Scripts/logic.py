# ---- LIBRARIES ----

import library
import combination

import bpy
import random

# ---- FUNCTIONS ----
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
    tags = library.searchTag(list, name)
    print(name, tags)
    return random.choice(tags)