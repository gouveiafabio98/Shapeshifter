# ---- LIBRARIES ----

import library
import combination
import textures

import bpy
import random
import mathutils
import math

# ---- FUNCTIONS ----
def constructor(assets_evaluated, simmetry, mutation, blend, delFace, collapse):
    global used_assets
    global asset_simmetry
    global asset_mutation
    global asset_blend
    global asset_delFace
    global asset_collapse
    used_assets = []
    asset_simmetry = simmetry
    asset_blend = blend
    asset_delFace = delFace
    asset_mutation = mutation
    asset_collapse = collapse

    # Select the first piece randomly
    tag1 = "body,center"
    obj1 = randomAsset(assets_evaluated.copy(), tag1)
    obj1 = addObject(obj1)

    # Place the piece in world
    bpy.context.collection.objects.link(obj1)

    # Boot the combination
    vgCombine(obj1, tag1, assets_evaluated, None, obj1)


def vgCombine(obj1, tag1, list, usedTag, obj2):
    global asset_blend
    global asset_delFace
    global asset_collapse
    # Create a node group for each piece
    nodeGroups = []

    # Append the base material
    nodeGroups.append({
        "name": None,
        "node": textures.newNodeGroup(textures.getMaterial(obj1), tag1),
        "uv": obj1.data.uv_layers.active.name,
    })

    # Loop all available VG
    for vg in obj1.vertex_groups:
        # Store the current VG
        tag2 = vg.name
        if tag2 != usedTag:
            # Select a random asset with the vg name (ex.: "body,center")
            obj2 = randomAsset(list.copy(), tag2)
            # Check if the random asset has the tag1, if not select a new one
            new_tag = get_vertex_group_with_tag(obj2, tag1)
            # Append the new obj material
            nodeGroups.append({
                "name": tag2,
                "node": textures.newNodeGroup(textures.getMaterial(obj2), tag2),
                "uv": tag2+new_tag,
            })
            
            obj2 = addObject(obj2)

            bpy.context.collection.objects.link(obj2)
            
            combination.joinVG(obj1, tag2, obj2, new_tag, asset_blend, asset_delFace, asset_collapse)
            vgCombine(obj2, tag2, list, new_tag, obj1)
        else:
            nodeGroups.append({
                "name": usedTag,
                "node": textures.newNodeGroup(textures.getMaterial(obj2), usedTag),
                "uv": tag1+usedTag,
            })

    # Create the new material and assign it to the piece
    if asset_blend:
        newMaterial = textures.createMaterial(nodeGroups, tag1)
        obj1.active_material = newMaterial


def randomAsset(assets, vg):
    global used_assets
    global asset_simmetry
    global asset_mutation
    # Random chance of mutate
    mutation = False
    if random.random() < asset_mutation:
        mutation = True
    # If not mutate search for the tag in assets
    tag = library.vg_to_tag(vg)
    if not mutation:
        assets = library.searchTag(assets, tag)
    # Check asset simmetry
    asset = None
    if asset_simmetry:
        asset = check_simmetry(assets, tag)
    # If no asset simetry choose a random asset
    if asset == None:
        asset = random_weight(assets)
    # Store the used asset in the list
    used_assets.append(asset)
    # Return the new asset
    return asset

def random_weight(assets):
    values = []
    weights = []
    for asset in assets:
        value = asset[0]
        weight = asset[1]
        if weight > 0:
            values.append(value)
            weights.append(weight)
    
    if not values:
        return random.choice([asset[0] for asset in assets])
    return random.choices(values, weights)[0]

def check_simmetry(assets, tag):
    global used_assets
    tag_type = tag[0].split(':')[1]

    for used_asset in used_assets:
        used_type = library.get_tags_asset(used_asset, 'type')[0]
        if tag_type == used_type:
            used_info = library.get_tags_asset(used_asset, 'info')

            for asset, weight in assets:
                if used_info == library.get_tags_asset(asset, 'info'):
                    return asset
    return None

def get_vertex_group_with_tag(obj, tag):
    vertex_groups = obj.vertex_groups
    
    # Check if the tag exists in any of the vertex groups
    for vg in vertex_groups:
        if tag.lower() in vg.name.lower():
            return vg.name
    
    # If the tag is not found, return a random existing vertex group
    if len(vertex_groups) > 0:
        vg = random.choice(vertex_groups)
        return vg.name

def addObject(obj):
    obj = obj.copy()
    obj.data = obj.data.copy()
    #obj.data.use_auto_smooth = True
    set_shade_smooth(obj)

    return obj

def set_shade_smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True