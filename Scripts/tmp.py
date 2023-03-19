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
from bpy.types import (Panel, Operator)
from bpy.utils import register_class, unregister_class

import logic
import library

# ---- BUTTONS ----

class ButtonGenerate(Operator):
    """Generate New Creature"""
    bl_idname = "button.generate"
    bl_label = "Generate New Creature"
    icon = "RNA"

    def execute(self, context):
        logic.constructor()
        return {'FINISHED'}

class ButtonMarkAsset(Operator):
    """Mark Current Object as Asset"""
    bl_idname = "button.markasset"
    bl_label = "Mark as Asset"
    icon = "PLUS"

    def execute(self, context):
        print("NEW ASSET!!!!!")
        return {'FINISHED'}

# ---- INPUT TEXT ----

items = (("Metal", "Metal", ""),
("Plastic", "Plastic", ""),
("Glass", "Glass", ""),
("Shadow", "Shadow", ""),
)

class InputName(Operator):
    bl_idname = "input.name"
    bl_label = "Asset Name"
    bl_property = "options"

    options: bpy.props.EnumProperty(items = items, name='New Name', default=None)

    @classmethod
    def poll(cls, context):
        return context.scene.material  # This prevents executing the operator if we didn't select a material

    def execute(self, context):
        material = context.scene.material
        material.name = self.options
        return {'FINISHED'}


# ---- PANELS ----

class MainPanel(Panel):
    bl_label = "Shapeshifter"
    
    bl_idname = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shapeshifter"

    def draw(self, context):
        layout = self.layout
        layout.operator(ButtonGenerate.bl_idname)

class SubPanel(Panel):
    bl_label = "Add to Library"
    
    bl_idname = "OBJECT_PT_subpanel"
    bl_parent_id = MainPanel.bl_idname
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shapeshifter"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "material")
        layout.operator(ButtonMarkAsset.bl_idname)

# ---- REGISTER ----

_classes = [
    InputName,
    ButtonGenerate,
    ButtonMarkAsset,
    MainPanel,
    SubPanel
]
    
def register():
    for cls in _classes:
        register_class(cls)

def unregister():
    for cls in reversed(_classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
