# ---- LIBRARIES ----

import bpy
from pathlib import Path
from shapeshifter import generation

# ---- FUNCTIONS ----
def clearScene():
    bpy.ops.outliner.orphans_purge()
    for obj in bpy.data.objects:
        if obj.users == 0:
            bpy.data.objects.remove(obj, do_unlink=True)

def deleteSceneObjs(): # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        obj.select_set(True)
    bpy.ops.object.delete()

def loadLibraries(fake = False):
    clearScene()
    prefs = bpy.context.preferences
    filepaths = prefs.filepaths
    asset_libraries = filepaths.asset_libraries
    assets = []
    current_file = bpy.data.filepath

    for asset_library in asset_libraries:
        library_path = Path(asset_library.path)
        blend_files = [fp for fp in library_path.glob("**/*.blend") if fp.is_file()]
        for blend_file in blend_files:
            if str(blend_file) != current_file:
                with bpy.data.libraries.load(str(blend_file), assets_only=True) as (data_from, data_to):
                    data_to.objects = data_from.objects
                    assets.append(data_from.objects)
    asset_list = [asset for list in assets for asset in list]
    for ob in bpy.data.objects:
        if ob.asset_data is not None:
            asset_list.append(ob)
    
    for asset in asset_list:
        setFake(asset, fake)

    return asset_list

def setFake(asset, fake = False):
    asset.use_fake_user = fake

def searchTag(assets, tag_info):
    evaluated = []
    for asset, evaluation in assets:
        if all(tag_info_item in [tag.name for tag in asset.asset_data.tags] for tag_info_item in tag_info):
            evaluated.append([asset, evaluation])
    return evaluated

def addLibrary(obj, tag_names):
    if obj is None:
        return
    
    if obj.asset_data is None:
        obj.asset_mark()

    tags = obj.asset_data.tags
    for tag_name in tag_names:
        tag_identifier, tag_info = tag_name.split(':')
        # Remove leading and trailing spaces from the tag parts
        tag_identifier = tag_identifier.strip()
        tag_info = tag_info.strip()
        # Find existing tags with the same identifier and remove them
        for existing_tag in tags:
            existing_identifier, existing_info = existing_tag.name.split(':')
            existing_identifier = existing_identifier.strip()
            if existing_identifier == tag_identifier:
                tags.remove(existing_tag)
        # Add the new tag
        tags.new(tag_name)

def list_tags(identifier):
    assets = bpy.data.objects
    tag_dict = {}
    
    for asset in assets:
        if asset.asset_data is not None:
            for tag in asset.asset_data.tags:
                tag_name_parts = tag.name.split(':')
                
                if len(tag_name_parts) == 2:
                    tag_identifier = tag_name_parts[0].strip()
                    tag_info = tag_name_parts[1].strip()
                    
                    if tag_identifier == identifier:
                        tag_values = tag_info.split(',')
                        for value in tag_values:
                            value = value.strip()
                            if value not in tag_dict:
                                formatted_value = format_tag_info(value)
                                tag_dict[value] = formatted_value
    
    tag_list = [(value, formatted_value, "") for value, formatted_value in tag_dict.items()]

    if len(tag_list)==0:
        try:
            loadLibraries(False)
        except:
            True

    return tag_list

def format_tag_info(tag_info):
    tag_info = tag_info.replace('_', ' ')
    formatted_tag_info = ' '.join([word.capitalize() for word in tag_info.split()])
    return formatted_tag_info

def format_tags_asset(tags_asset):
    formated_tags = []
    for tag in tags_asset:
        words = format_tag_info(tag).split(' ')
        for i in range(len(words)):
            words[i] = generation.nlp(words[i])[0].lemma_.lower()
        formated_tags.append(words)
    return formated_tags

def create_tag(identifier, information):
    identifier = identifier.strip()
    information = information.strip().lower()
    information = information.replace(', ', ',')
    information = information.replace(' ,', ',')
    information = information.replace(' ', '_')
    return f"{identifier}:{information}"

def get_tags_asset(asset, identifier):
    for tag in asset.asset_data.tags:
        tag_name_parts = tag.name.split(':')
        if len(tag_name_parts) == 2:
            tag_identifier = tag_name_parts[0].strip()
            tag_info = tag_name_parts[1].strip()
            if tag_identifier == identifier:
                tag_values = tag_info.split(',')
    return tag_values

def get_vg_tag(asset):
    return f"{get_tags_asset(asset, 'type')[0]},{get_tags_asset(asset, 'symmetry')[0]}"

def vg_to_tag(tag, self):
    values = tag.split(',')
    
    try:
        values[0] = "type:"+values[0]
    except:
        self.report({"WARNING"}, "Vertex Group 'Type' Does Not Exist.")
    
    try:
        values[1] = "symmetry:"+values[1]
    except:
        self.report({"WARNING"}, "Vertex Group 'Symmetry' Does Not Exist.")
    
    return values

def map_value(value, value_min, value_max, target_min, target_max):
    normalized_value = (value - value_min) / (value_max - value_min)
    mapped_value = target_min + (normalized_value * (target_max - target_min))
    return mapped_value