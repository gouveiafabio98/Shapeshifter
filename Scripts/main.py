# ---- INFO ----

bl_info = {
    "name": "Shapeshifter",
    "author": "Fabio Gouveia Silva",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Monster",
    "description": "Monster Blender",
    "warning": "",
    "doc_url": "",
    "category": "",
}

# ---- LIBRARIES ----

import bpy
from bpy.types import (Panel, Operator, PropertyGroup)
from bpy.utils import register_class, unregister_class

import logic
import library

# ---- ACTION BUTTONS ----

class ButtonGenerate(Operator):
    """Generate New Creature"""
    bl_idname = "button.generate"
    bl_label = "Generate New Creature"

    def execute(self, context):
        print(logic.listTags())
        logic.constructor()
        return {'FINISHED'}

# ---- MARK ASSET ----

class ButtonMarkAsset(Operator):
    """Mark Current Object as Asset"""
    bl_idname = "button.markasset"
    bl_label = "Mark as Asset"

    def execute(self, context):
        clist = context.scene.enumAssetName
        object = bpy.context.object
        
        if clist.enable_custom_asset_name and clist.new_asset_name != "" and object != None:
            library.addLibrary(object, clist.new_asset_name)
        else:
            print(clist.current_asset_list)
            print("TO DO")
        return {'FINISHED'}

class EnumAssetName(PropertyGroup):
    enable_custom_asset_name: bpy.props.BoolProperty(name="Custom Asset Name", default=False)
    new_asset_name: bpy.props.StringProperty(name="New Asset Name", default="")
    current_asset_list: bpy.props.EnumProperty(
        name="Current Asset List",
        description="Choose the asset name identifier",
        items=()
    )

# ---- PANELS ----

class MainPanel(Panel):
    bl_label = "Shapeshifter"
    
    bl_idname = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shapeshifter"


    def draw(self, context):
        layout = self.layout
        layout.operator(ButtonGenerate.bl_idname, icon = "RNA")

class SubPanel(Panel):
    bl_label = "Add to Library"
    
    bl_idname = "OBJECT_PT_subpanel"
    bl_parent_id = MainPanel.bl_idname
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shapeshifter"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        assetNames = scene.enumAssetName

        row = layout.row()
        row.prop(assetNames, "enable_custom_asset_name", text="Custom Asset Name")
        if assetNames.enable_custom_asset_name:
            row = layout.row()
            row.prop(assetNames, "new_asset_name", text="New Asset Name")
            row = layout.row()
            row.enabled = False
            row.prop(assetNames, "current_asset_list", text="Current Asset List")
        else:
            row = layout.row()
            row.enabled = False
            row.prop(assetNames, "new_asset_name", text="New Asset Name")
            row = layout.row()
            row.prop(assetNames, "current_asset_list", text="Current Asset List")

        layout.operator(ButtonMarkAsset.bl_idname, icon = "PLUS")

# ---- REGISTER ----

_classes = [
    EnumAssetName,
    ButtonGenerate,
    ButtonMarkAsset,
    MainPanel,
    SubPanel
]
    
def register():
    for cls in _classes:
        register_class(cls)
    
    bpy.types.Scene.enumAssetName = bpy.props.PointerProperty(type=EnumAssetName)

def unregister():
    for cls in reversed(_classes):
        unregister_class(cls)
    
    del bpy.types.Scene.enumAssetName

if __name__ == "__main__":
    register()
