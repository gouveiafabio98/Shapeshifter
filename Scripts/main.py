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
from bpy.types import (Panel)
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

class Button ():
    def __init__(self, text, icon, action):
        self.text = text
        self.icon = icon
        self.action = action

    def draw(self, layout):
        layout.operator(
            "myaddon." + self.action,
            text=self.text,
            icon=self.icon
        )

class Panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_panel"
    bl_label = "Shapeshifter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shapeshifter"

    def draw(self, context):
        layout = self.layout
        button1 = Button("Button 1", "MESH_CUBE", "action1")
        button2 = Button("Button 2", "MESH_SPHERE", "action2")
        button1.draw(layout)
        button2.draw(layout)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------REGISTER AND UNREGISTER-------------------------------
# ------------------------------CLASSES----------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

_classes = [
    Button,
    Panel
]
    
def register():
    for cls in _classes:
        register_class(cls)

def unregister():
    for cls in reversed(_classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()