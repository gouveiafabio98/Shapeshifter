# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -------------------------------INFORMAÇÃO------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -------------------------------LIBRARIES-------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

import logic
import library

import bpy
from random import randint
from bpy.types import (Panel, Operator, EnumProperty)
from bpy.utils import register_class, unregister_class
from pathlib import Path

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -------------------------------VARIABLES-------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

options = [
    ("Option 1", "Option 1", "The first option"),
    ("Option 2", "Option 2", "The second option"),
    ("Option 3", "Option 3", "The third option")
]

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# ---------------------------CLASSES INPUTS------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

class ButtonOperator(bpy.types.Operator):
    bl_idname = "monster.shapeshifter"
    bl_label = "Button"

    action = bpy.props.StringProperty()
    label = bpy.props.StringProperty()

    def execute(self, context):
        getattr(self, self.action)(context)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.operator(self.bl_idname, text=self.label)

    def generate(self, context):
        logic.constructor()
        return {'FINISHED'}

    def addLibrary(self, context):
        option = context.scene.selected_option
        object = bpy.context.object
        library.addLibrary(object, option)
        return {'FINISHED'}

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# ---------------------------CLASSES PANELS------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

class CustomPanel(bpy.types.Panel):
    bl_label = "Shapeshifter"
    bl_idname = "OBJECT_PT_blender"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shapeshifter"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        layout.operator(ButtonOperator.bl_idname, text="Blend", icon="RNA").action = "generate"
        #row.operator(Generate.bl_idname, text="Blend", icon='RNA') #Calls class Generate


class SubPanel(bpy.types.Panel):
    bl_label = "Add to Library"
    bl_idname = "OBJECT_PT_subpanel"
    bl_parent_id = "OBJECT_PT_blender"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shapeshifter"
    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "selected_option")
        
        layout.operator(ButtonOperator.bl_idname, text="Add to Library", icon="NONE").action = "addLibrary"

        #layout.operator("monster.add_to_library", text="Add to Library")

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------REGISTER AND UNREGISTER-------------------------------
# ------------------------------CLASSES----------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

_classes = [
    ButtonOperator,
    CustomPanel,
    SubPanel
]
    
def register():
    for cls in _classes:
        register_class(cls)
    
    bpy.types.Scene.selected_option = EnumProperty(items=options, name="Options")

def unregister():
    for cls in reversed(_classes):
        unregister_class(cls)
    
    del bpy.types.Scene.selected_option

if __name__ == "__main__":
    register()
