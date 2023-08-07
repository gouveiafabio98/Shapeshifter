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
import sys
import os

current_file_path = bpy.context.space_data.text.filepath
current_directory = os.path.dirname(current_file_path)
if current_directory not in sys.path:
    sys.path.append(current_directory)


from bpy.types import Panel, Operator, PropertyGroup
from bpy.utils import register_class, unregister_class
import bpy.props

import logic
import library
import generation
import loopcut

# ---- OPERATORS ----


class ButtonGenerate(Operator):
    """Generate New Creature"""

    bl_idname = "button.generate"
    bl_label = "Generate New Creature"

    def execute(self, context):
        symmetry = context.scene.SymmetryCheckbox.enable_asset_symmetry
        blend = context.scene.BlendCheckbox.enable_texture_blend
        delFace = context.scene.VgRemoveCheckbox.enable_remove_faces
        collapse = context.scene.CollapseCheckbox.enable_vertice_collapse
        mutation = context.scene.MutationSlider.slider

        preprocess_input = []
        for prompt_data in context.scene.prompt_data:
            preprocess_input.append({
                "prompt": generation.preprocess_input(prompt_data.prompt),
                "type": prompt_data.prompt_type,
                "threshold": prompt_data.prompt_threshold
                })

        assets_evaluated = generation.assets_evaluation(
            preprocess_input, library.loadLibraries()
        )

        logic.constructor(assets_evaluated, symmetry, mutation, blend, delFace, collapse)
        return {"FINISHED"}

class ButtonMarkAsset(Operator):
    """Mark Current Object as an Asset"""

    bl_idname = "button.markasset"
    bl_label = "Mark Asset"

    def execute(self, context):
        info_input = context.scene.infoInput
        type_list = context.scene.EnumAssetType
        symmetry_list = context.scene.EnumAssetSymmetry

        tag_list = []
        tag_list.append(library.create_tag("info", info_input))

        if type_list.enable_custom_type and type_list.new_type != "":
            tag_list.append(library.create_tag("type", type_list.new_type))
        else:
            tag_list.append(library.create_tag("type", type_list.current_type_list))

        if symmetry_list.enable_custom_symmetry and symmetry_list.new_symmetry != "":
            tag_list.append(library.create_tag("symmetry", symmetry_list.new_symmetry))
        else:
            tag_list.append(
                library.create_tag("symmetry", symmetry_list.current_symmetry_list)
            )

        object = bpy.context.object
        library.addLibrary(object, tag_list)
        return {"FINISHED"}

class ButtonCutAsset(Operator):
    """Divide Asset by Edge Loop"""

    bl_idname = "button.cutasset"
    bl_label = "Cut Asset"

    def execute(self, context):
        loopcut.cut_object(self)
        return {"FINISHED"}

class AddPromptOperator(Operator):
    bl_idname = "button.add_prompt_operator"
    bl_label = "Add Prompt"

    def execute(self, context):
        scene = context.scene
        new_input = scene.prompt_data.add()
        new_input.index = len(scene.prompt_data)
        return {"FINISHED"}

class RemovePromptOperator(Operator):
    bl_idname = "button.remove_prompt_operator"
    bl_label = "Remove Prompt"
    input_index: bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        scene.prompt_data.remove(self.input_index)
        return {"FINISHED"}

# ---- INPUTS ----

class EnumAssetType(PropertyGroup):
    enable_custom_type: bpy.props.BoolProperty(name="Custom Type", default=False)
    new_type: bpy.props.StringProperty(name="New Type", default="")
    current_type_list: bpy.props.EnumProperty(
        name="Type List",
        description="Choose the type identifier",
        items=library.list_tags("type"),
    )

class EnumAssetSymmetry(PropertyGroup):
    enable_custom_symmetry: bpy.props.BoolProperty(
        name="Custom Symmetry", default=False
    )
    new_symmetry: bpy.props.StringProperty(name="New Symmetry", default="")
    current_symmetry_list: bpy.props.EnumProperty(
        name="Symmetry List",
        description="Choose the symmetry identifier",
        items=library.list_tags("symmetry"),
    )

class SymmetryCheckbox(PropertyGroup):
    enable_asset_symmetry: bpy.props.BoolProperty(
        name="Enable Asset Symmetry", default=False
    )

class BlendCheckbox(PropertyGroup):
    enable_texture_blend: bpy.props.BoolProperty(
        name="[BETA] Enable Texture Blend", default=False
    )

class VgRemoveCheckbox(PropertyGroup):
    enable_remove_faces: bpy.props.BoolProperty(
        name="Remove Unused Faces", default=True
    )

class CollapseCheckbox(PropertyGroup):
    def on_vertice_collapse_update(self, context):
        scene = context.scene
        collapse_checkbox = scene.CollapseCheckbox

        if not collapse_checkbox.enable_vertice_collapse:
            # Disable the other two checkboxes when the Vertice Collapse Checkbox is unchecked
            scene.BlendCheckbox.enable_texture_blend = False
            scene.VgRemoveCheckbox.enable_remove_faces = False

    enable_vertice_collapse: bpy.props.BoolProperty(
        name="Vertice Collapse", default=True, update = on_vertice_collapse_update
    )

class PromptData(PropertyGroup):
    prompt: bpy.props.StringProperty(default="")
    prompt_type: bpy.props.EnumProperty(
        name="Type",
        description="Prompt type",
        items=[
            ("ALL", "Everything", "Apply to Everything"),
            *library.list_tags("type"),
        ],
        default="ALL",
    )

    prompt_threshold: bpy.props.FloatProperty(
        name="Threshold", description="Prompt Threshold", default=0.5, min=0.0, max=1.0
    )
    index: bpy.props.IntProperty()

class InputText(PropertyGroup):
    enable_custom_type: bpy.props.BoolProperty(name="Custom Asset Name", default=False)
    new_type: bpy.props.StringProperty(name="New Asset Name", default="")
    current_type_list: bpy.props.EnumProperty(
        name="Current Asset List",
        description="Choose the asset name identifier",
        items=library.list_tags("type"),
    )
    user_text_input: bpy.props.StringProperty(name="User Text Input", default="")

class MutationSlider(PropertyGroup):
    """Mutation Slider Chance"""
    bl_idname = "object.mutation"
    bl_label = "Mutation"
    slider: bpy.props.FloatProperty(
        name="Mutation",
        description="Mutation Chance",
        default=0.0,
        min=0.0,
        max=1.0
    )

# ---- PANELS ----

class MainPanel(Panel):
    bl_label = "Shapeshifter"

    bl_idname = "OBJECT_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shapeshifter"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.operator(ButtonGenerate.bl_idname, icon="RNA")
        layout.prop(scene.MutationSlider, "slider", slider=True)
        for index, prompt_data in enumerate(scene.prompt_data):
            box = layout.box()
            row = box.row()
            row.prop(prompt_data, "prompt", text="", icon="TEXT")
            row = box.row()
            row.prop(prompt_data, "prompt_type", text="")
            row.prop(prompt_data, "prompt_threshold", text="Threshold")
            row.operator("button.remove_prompt_operator", text="", icon="TRASH").input_index = index

        layout.operator("button.add_prompt_operator", text="Add Prompt", icon="ADD")

class SettingsPanel(Panel):
    bl_label = "Settings"
    bl_idname = "OBJECT_PT_cutpanel"
    bl_parent_id = MainPanel.bl_idname
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shapeshifter"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        simetryCheckbox = scene.SymmetryCheckbox
        blendCheckbox = scene.BlendCheckbox
        vgRemoveCheckbox = scene.VgRemoveCheckbox
        collapseCheckbox = scene.CollapseCheckbox
        layout.prop(simetryCheckbox, "enable_asset_symmetry", text="Enable Asset Symmetry")
        layout.prop(collapseCheckbox, "enable_vertice_collapse", text="Vertice Collapse")
        if collapseCheckbox.enable_vertice_collapse:
            row = layout.row()
            row.prop(vgRemoveCheckbox, "enable_remove_faces", text="Remove Unused Faces")
            row = layout.row()
            row.prop(blendCheckbox, "enable_texture_blend", text="[BETA] Enable Texture Blend")
        else:
            row = layout.row()
            row.enabled = False
            row.prop(vgRemoveCheckbox, "enable_remove_faces", text="Remove Unused Faces")
            row = layout.row()
            row.enabled = False
            row.prop(blendCheckbox, "enable_texture_blend", text="[BETA] Enable Texture Blend")

class AssetPanel(Panel):
    bl_label = "Mark Asset"
    bl_idname = "OBJECT_PT_assetpanel"
    bl_parent_id = MainPanel.bl_idname
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shapeshifter"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        assetTypes = scene.EnumAssetType
        assetSymmetry = scene.EnumAssetSymmetry
        draw_title_divider(layout, "Asset Information", "MOD_FLUID")
        row = layout.row()
        layout.prop(context.scene, "infoInput")
        # Type Identifier
        draw_title_divider(layout, "Asset Type", "OUTLINER_DATA_ARMATURE")
        row = layout.row()
        row.prop(assetTypes, "enable_custom_type", text="Custom Type")
        if assetTypes.enable_custom_type:
            row = layout.row()
            row.prop(assetTypes, "new_type", text="New Type")
            row = layout.row()
            row.enabled = False
            row.prop(assetTypes, "current_type_list", text="Type List")
        else:
            row = layout.row()
            row.enabled = False
            row.prop(assetTypes, "new_type", text="New Type")
            row = layout.row()
            row.prop(assetTypes, "current_type_list", text="Type List")
        # Symmetry Identifier
        draw_title_divider(layout, "Asset Symmetry", "MOD_MIRROR")
        row = layout.row()
        row.prop(assetSymmetry, "enable_custom_symmetry", text="Custom Symmetry")
        if assetSymmetry.enable_custom_symmetry:
            row = layout.row()
            row.prop(assetSymmetry, "new_symmetry", text="New Symmetry")
            row = layout.row()
            row.enabled = False
            row.prop(assetSymmetry, "current_symmetry_list", text="Symmetry List")
        else:
            row = layout.row()
            row.enabled = False
            row.prop(assetSymmetry, "new_symmetry", text="New Symmetry")
            row = layout.row()
            row.prop(assetSymmetry, "current_symmetry_list", text="Symmetry List")
        # Add Button
        layout.operator(ButtonMarkAsset.bl_idname, icon="CHECKMARK")

class CutPanel(Panel):
    bl_label = "Cut Asset"
    bl_idname = "OBJECT_PT_settingspanel"
    bl_parent_id = MainPanel.bl_idname
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shapeshifter"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator(ButtonCutAsset.bl_idname, icon="LIBRARY_DATA_OVERRIDE")

# ---- FUNCTIONS ----


def draw_title_divider(layout, text, icon):
    row = layout.row(align=True)
    row.label(text=text, icon=icon)
    row.separator()


# ---- REGISTER ----

_classes = [
    EnumAssetType,
    EnumAssetSymmetry,
    ButtonGenerate,
    ButtonMarkAsset,
    ButtonCutAsset,
    MutationSlider,
    SymmetryCheckbox,
    BlendCheckbox,
    VgRemoveCheckbox,
    CollapseCheckbox,
    MainPanel,
    SettingsPanel,
    AssetPanel,
    CutPanel,
    PromptData,
    AddPromptOperator,
    RemovePromptOperator,
]


def register():
    for cls in _classes:
        register_class(cls)

    bpy.types.Scene.EnumAssetType = bpy.props.PointerProperty(type=EnumAssetType)
    bpy.types.Scene.EnumAssetSymmetry = bpy.props.PointerProperty(type=EnumAssetSymmetry)
    bpy.types.Scene.infoInput = bpy.props.StringProperty(name="Asset Info", default="")
    bpy.types.Scene.SymmetryCheckbox = bpy.props.PointerProperty(type=SymmetryCheckbox)
    bpy.types.Scene.BlendCheckbox = bpy.props.PointerProperty(type=BlendCheckbox)
    bpy.types.Scene.VgRemoveCheckbox = bpy.props.PointerProperty(type=VgRemoveCheckbox)
    bpy.types.Scene.CollapseCheckbox = bpy.props.PointerProperty(type=CollapseCheckbox)
    bpy.types.Scene.MutationSlider = bpy.props.PointerProperty(type=MutationSlider)


    bpy.types.Scene.prompt_data = bpy.props.CollectionProperty(type=PromptData)


def unregister():
    for cls in reversed(_classes):
        unregister_class(cls)

    del bpy.types.Scene.EnumAssetType
    del bpy.types.Scene.EnumAssetSymmetry
    del bpy.types.Scene.infoInput
    del bpy.types.Scene.SymmetryCheckbox
    del bpy.types.Scene.BlendCheckbox
    del bpy.types.Scene.VgRemoveCheckbox
    del bpy.types.Scene.CollapseCheckbox
    del bpy.types.Scene.MutationSlider
    del bpy.types.Scene.prompt_data


if __name__ == "__main__":
    register()
