# ---- INFO ----

bl_info = {
    "name": "Shapeshifter",
    "author": "Fabio Gouveia Silva",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Creature",
    "description": "Creature Blender",
    "warning": "",
    "doc_url": "https://github.com/gouveiafabio98/Shapeshifter",
    "category": "Creature Combination",
}

# ---- LIBRARIES ----

import bpy
import sys
import os

from bpy.types import Panel, Operator, PropertyGroup
from bpy.utils import register_class, unregister_class
import bpy.props

from shapeshifter import logic
from shapeshifter import library
from shapeshifter import generation
from shapeshifter import loopcut

# ---- OPERATORS ----

class ButtonGenerate(Operator):
    """Generate New Creature"""

    bl_idname = "button.generate"
    bl_label = "Generate"

    def execute(self, context):
        symmetry = context.scene.SymmetryCheckbox.enable_asset_symmetry
        blend = context.scene.BlendCheckbox.enable_texture_blend
        delFace = context.scene.VgRemoveCheckbox.enable_remove_faces
        collapse = context.scene.CollapseCheckbox.enable_vertice_collapse
        mutation = context.scene.MutationSlider.slider
        clean = context.scene.CleanScene.clean_scene

        preprocess_input = []
        for prompt_data in context.scene.prompt_data:
            preprocess_input.append({
                "prompt": generation.preprocess_input(prompt_data.prompt),
                "type": prompt_data.prompt_type,
                "threshold": prompt_data.prompt_threshold
                })

        if clean:
            library.deleteSceneObjs()
            library.clearScene()

        assets_evaluated = generation.assets_evaluation(
            preprocess_input, library.loadLibraries(False)
        )

        logic.constructor(self, assets_evaluated, symmetry, mutation, blend, delFace, collapse)

        return {"FINISHED"}

class LibraryRefresh(Operator):
    """Library Refresh"""

    bl_idname = "button.lib_refresh"
    bl_label = "Library Refresh"

    def execute(self, context):
        library.loadLibraries(False)
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
            tag_list.append(library.create_tag("symmetry", symmetry_list.current_symmetry_list))

        object = bpy.context.object
        library.addLibrary(object, tag_list)
        return {"FINISHED"}

class ButtonSelectionCut(Operator):
    """Separate Asset by Selection"""

    bl_idname = "button.selectioncut"
    bl_label = "Selection Cut"

    def execute(self, context):
        types_one = context.scene.SelectedCutEnumAssetType
        if types_one.enable_custom_cut_type and types_one.new_cut_type != "":
            type_one = types_one.new_cut_type
        else:
            type_one = types_one.current_cut_type_list
        symmetrys_one = context.scene.SelectedCutEnumAssetSymmetry
        if symmetrys_one.enable_custom_cut_symmetry and symmetrys_one.new_cut_symmetry != "":
            symmetry_one = symmetrys_one.new_cut_symmetry
        else:
            symmetry_one = symmetrys_one.current_cut_symmetry_list
        tag_one = f"{type_one},{symmetry_one}"

        types_two = context.scene.UnselectedCutEnumAssetType
        if types_two.enable_custom_cut_type and types_two.new_cut_type != "":
            type_two = types_two.new_cut_type
        else:
            type_two = types_two.current_cut_type_list
        
        symmetrys_two = context.scene.UnselectedCutEnumAssetSymmetry
        if symmetrys_two.enable_custom_cut_symmetry and symmetrys_two.new_cut_symmetry != "":
            symmetry_two = symmetrys_two.new_cut_symmetry
        else:
            symmetry_two = symmetrys_two.current_cut_symmetry_list
        tag_two = f"{type_two},{symmetry_two}"

        loopcut.selection_cut(self, tag_two, tag_one)
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
    def list_items(self, context):
        return library.list_tags("type")
    current_type_list: bpy.props.EnumProperty(
        name="Type List",
        description="Choose the type identifier",
        items=list_items
    )

class EnumAssetSymmetry(PropertyGroup):
    enable_custom_symmetry: bpy.props.BoolProperty(name="Custom Symmetry", default=False)
    new_symmetry: bpy.props.StringProperty(name="New Symmetry", default="")
    def list_items(self, context):
        return library.list_tags("symmetry")
    current_symmetry_list: bpy.props.EnumProperty(
        name="Symmetry List",
        description="Choose the symmetry identifier",
        items=list_items
    )

class SelectedCutEnumAssetType(PropertyGroup):
    enable_custom_cut_type: bpy.props.BoolProperty(name="Custom Type", default=False)
    new_cut_type: bpy.props.StringProperty(name="New Type", default="")
    def list_items(self, context):
        return library.list_tags("type")
    current_cut_type_list: bpy.props.EnumProperty(
        name="Type List",
        description="Choose the type identifier",
        items=list_items
    )

class SelectedCutEnumAssetSymmetry(PropertyGroup):
    enable_custom_cut_symmetry: bpy.props.BoolProperty(name="Custom Symmetry", default=False)
    new_cut_symmetry: bpy.props.StringProperty(name="New Symmetry", default="")
    def list_items(self, context):
        return library.list_tags("symmetry")
    current_cut_symmetry_list: bpy.props.EnumProperty(
        name="Symmetry List",
        description="Choose the symmetry identifier",
        items=list_items
    )

class UnselectedCutEnumAssetType(PropertyGroup):
    enable_custom_cut_type: bpy.props.BoolProperty(name="Custom Type", default=False)
    new_cut_type: bpy.props.StringProperty(name="New Type", default="")
    def list_items(self, context):
        return library.list_tags("type")
    current_cut_type_list: bpy.props.EnumProperty(
        name="Type List",
        description="Choose the type identifier",
        items=list_items
    )

class UnselectedCutEnumAssetSymmetry(PropertyGroup):
    enable_custom_cut_symmetry: bpy.props.BoolProperty(name="Custom Symmetry", default=False)
    new_cut_symmetry: bpy.props.StringProperty(name="New Symmetry", default="")
    def list_items(self, context):
        return library.list_tags("symmetry")
    current_cut_symmetry_list: bpy.props.EnumProperty(
        name="Symmetry List",
        description="Choose the symmetry identifier",
        items=list_items
    )

class SymmetryCheckbox(PropertyGroup):
    enable_asset_symmetry: bpy.props.BoolProperty(
        name="Enable Asset Symmetry", default=True
    )

class BlendCheckbox(PropertyGroup):
    enable_texture_blend: bpy.props.BoolProperty(
        name="Enable Texture Blend", default=True
    )

class VgRemoveCheckbox(PropertyGroup):
    enable_remove_faces: bpy.props.BoolProperty(
        name="Remove Unused Faces", default=True
    )

class CleanScene(PropertyGroup):
    clean_scene: bpy.props.BoolProperty(
        name="Clean Scene", default=True
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
    def list_items(self, context):
        return [("ALL", "Everything", "Apply to Everything"), *library.list_tags("type")]
    prompt_type: bpy.props.EnumProperty(
        name="Type",
        description="Prompt type",
        items=list_items
    )

    prompt_threshold: bpy.props.FloatProperty(
        name="Threshold", description="Prompt Threshold", default=0.5, min=0.0, max=1.0
    )
    index: bpy.props.IntProperty()

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

class VGSelectionNameInput(PropertyGroup):
    vg_name: bpy.props.StringProperty(
        name="Select",
        default="",
        description="Selected Vertex Group Name"
    )

class VGUnselectionNameInput(PropertyGroup):
    vg_name: bpy.props.StringProperty(
        name="Unselect",
        default="",
        description="Unselected Vertex Group Name"
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
        draw_title_divider(layout, "Generate New Creature", "GHOST_ENABLED")
        layout.operator(ButtonGenerate.bl_idname, icon="RNA")
        layout.prop(scene.MutationSlider, "slider", slider=True)
        layout.row().separator()
        for index, prompt_data in enumerate(scene.prompt_data):
            box = layout.box()
            row = box.row()
            row.prop(prompt_data, "prompt", text="", icon="TEXT")
            row = box.row()
            row.prop(prompt_data, "prompt_type", text="")
            row.prop(prompt_data, "prompt_threshold", text="Threshold")
            row.operator("button.remove_prompt_operator", text="", icon="TRASH").input_index = index

        layout.operator("button.add_prompt_operator", text="Add Prompt", icon="ADD")
        layout.row().separator()

class SettingsPanel(Panel):
    bl_label = "Generation Settings"
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
        cleanScene = scene.CleanScene
        collapseCheckbox = scene.CollapseCheckbox
        layout.prop(simetryCheckbox, "enable_asset_symmetry", text="Enable Asset Symmetry")
        layout.prop(cleanScene, "clean_scene", text="Clean Scene Every Generation")
        layout.prop(collapseCheckbox, "enable_vertice_collapse", text="Vertice Collapse")
        if collapseCheckbox.enable_vertice_collapse:
            row = layout.row()
            row.prop(vgRemoveCheckbox, "enable_remove_faces", text="Remove Unused Faces")
            row = layout.row()
            row.prop(blendCheckbox, "enable_texture_blend", text="Enable Texture Blend")
        else:
            row = layout.row()
            row.enabled = False
            row.prop(vgRemoveCheckbox, "enable_remove_faces", text="Remove Unused Faces")
            row = layout.row()
            row.enabled = False
            row.prop(blendCheckbox, "enable_texture_blend", text="Enable Texture Blend")
        layout.row().separator()
        layout.operator(LibraryRefresh.bl_idname, icon="FILE_REFRESH")

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
        layout.row().separator()
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
        layout.row().separator()
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
        layout.row().separator()
        # Add Button
        layout.operator(ButtonMarkAsset.bl_idname, icon="CHECKMARK")

class CutPanel(Panel):
    bl_label = "Separate Assets"
    bl_idname = "OBJECT_PT_settingspanel"
    bl_parent_id = MainPanel.bl_idname
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shapeshifter"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        assetTypes = scene.SelectedCutEnumAssetType
        assetSymmetry = scene.SelectedCutEnumAssetSymmetry

        assetTypes2 = scene.UnselectedCutEnumAssetType
        assetSymmetry2 = scene.UnselectedCutEnumAssetSymmetry

        draw_title_divider(layout, "Selected Area", "RADIOBUT_ON")
        # Type Identifier
        row = layout.row()
        row.prop(assetTypes, "enable_custom_cut_type", text="Custom Type")
        if assetTypes.enable_custom_cut_type:
            row = layout.row()
            row.prop(assetTypes, "new_cut_type", text="New Type")
            row = layout.row()
            row.enabled = False
            row.prop(assetTypes, "current_cut_type_list", text="Type List")
        else:
            row = layout.row()
            row.enabled = False
            row.prop(assetTypes, "new_cut_type", text="New Type")
            row = layout.row()
            row.prop(assetTypes, "current_cut_type_list", text="Type List")
        # Symmetry Identifier
        layout.row().separator()
        row = layout.row()
        row.prop(assetSymmetry, "enable_custom_cut_symmetry", text="Custom Symmetry")
        if assetSymmetry.enable_custom_cut_symmetry:
            row = layout.row()
            row.prop(assetSymmetry, "new_cut_symmetry", text="New Symmetry")
            row = layout.row()
            row.enabled = False
            row.prop(assetSymmetry, "current_cut_symmetry_list", text="Symmetry List")
        else:
            row = layout.row()
            row.enabled = False
            row.prop(assetSymmetry, "new_cut_symmetry", text="New Symmetry")
            row = layout.row()
            row.prop(assetSymmetry, "current_cut_symmetry_list", text="Symmetry List")
        layout.row().separator()

        draw_title_divider(layout, "Unselected Area", "RADIOBUT_OFF")
        # Type Identifier
        row = layout.row()
        row.prop(assetTypes2, "enable_custom_cut_type", text="Custom Type")
        if assetTypes2.enable_custom_cut_type:
            row = layout.row()
            row.prop(assetTypes2, "new_cut_type", text="New Type")
            row = layout.row()
            row.enabled = False
            row.prop(assetTypes2, "current_cut_type_list", text="Type List")
        else:
            row = layout.row()
            row.enabled = False
            row.prop(assetTypes2, "new_cut_type", text="New Type")
            row = layout.row()
            row.prop(assetTypes2, "current_cut_type_list", text="Type List")
        # Symmetry Identifier
        layout.row().separator()
        row = layout.row()
        row.prop(assetSymmetry2, "enable_custom_cut_symmetry", text="Custom Symmetry")
        if assetSymmetry2.enable_custom_cut_symmetry:
            row = layout.row()
            row.prop(assetSymmetry2, "new_cut_symmetry", text="New Symmetry")
            row = layout.row()
            row.enabled = False
            row.prop(assetSymmetry2, "current_cut_symmetry_list", text="Symmetry List")
        else:
            row = layout.row()
            row.enabled = False
            row.prop(assetSymmetry2, "new_cut_symmetry", text="New Symmetry")
            row = layout.row()
            row.prop(assetSymmetry2, "current_cut_symmetry_list", text="Symmetry List")
        layout.row().separator()

        layout.operator(ButtonSelectionCut.bl_idname, icon="MOD_UVPROJECT")
        layout.row().separator()

# ---- FUNCTIONS ----

def draw_title_divider(layout, text, icon):
    row = layout.row(align=True)
    row.label(text=text, icon=icon)
    row.separator()

# ---- REGISTER ----

_classes = [
    EnumAssetType,
    EnumAssetSymmetry,
    SelectedCutEnumAssetType,
    SelectedCutEnumAssetSymmetry,
    UnselectedCutEnumAssetType,
    UnselectedCutEnumAssetSymmetry,
    ButtonGenerate,
    ButtonMarkAsset,
    ButtonSelectionCut,
    MutationSlider,
    SymmetryCheckbox,
    BlendCheckbox,
    VgRemoveCheckbox,
    CleanScene,
    CollapseCheckbox,
    MainPanel,
    SettingsPanel,
    AssetPanel,
    CutPanel,
    PromptData,
    AddPromptOperator,
    RemovePromptOperator,
    LibraryRefresh
]

def register():
    for cls in _classes:
        register_class(cls)

    bpy.types.Scene.EnumAssetType = bpy.props.PointerProperty(type=EnumAssetType)
    bpy.types.Scene.EnumAssetSymmetry = bpy.props.PointerProperty(type=EnumAssetSymmetry)
    bpy.types.Scene.SelectedCutEnumAssetType = bpy.props.PointerProperty(type=SelectedCutEnumAssetType)
    bpy.types.Scene.SelectedCutEnumAssetSymmetry = bpy.props.PointerProperty(type=SelectedCutEnumAssetSymmetry)
    bpy.types.Scene.UnselectedCutEnumAssetType = bpy.props.PointerProperty(type=UnselectedCutEnumAssetType)
    bpy.types.Scene.UnselectedCutEnumAssetSymmetry = bpy.props.PointerProperty(type=UnselectedCutEnumAssetSymmetry)
    bpy.types.Scene.infoInput = bpy.props.StringProperty(name="Asset Info", default="")
    bpy.types.Scene.SymmetryCheckbox = bpy.props.PointerProperty(type=SymmetryCheckbox)
    bpy.types.Scene.BlendCheckbox = bpy.props.PointerProperty(type=BlendCheckbox)
    bpy.types.Scene.VgRemoveCheckbox = bpy.props.PointerProperty(type=VgRemoveCheckbox)
    bpy.types.Scene.CleanScene = bpy.props.PointerProperty(type=CleanScene)
    bpy.types.Scene.CollapseCheckbox = bpy.props.PointerProperty(type=CollapseCheckbox)
    bpy.types.Scene.MutationSlider = bpy.props.PointerProperty(type=MutationSlider)

    bpy.types.Scene.prompt_data = bpy.props.CollectionProperty(type=PromptData)

def unregister():
    for cls in reversed(_classes):
        unregister_class(cls)

    del bpy.types.Scene.EnumAssetType
    del bpy.types.Scene.EnumAssetSymmetry
    del bpy.types.Scene.SelectedCutEnumAssetType
    del bpy.types.Scene.SelectedCutEnumAssetSymmetry
    del bpy.types.Scene.UnselectedCutEnumAssetType
    del bpy.types.Scene.UnselectedCutEnumAssetSymmetry
    del bpy.types.Scene.infoInput
    del bpy.types.Scene.SymmetryCheckbox
    del bpy.types.Scene.BlendCheckbox
    del bpy.types.Scene.VgRemoveCheckbox
    del bpy.types.Scene.CleanScene
    del bpy.types.Scene.CollapseCheckbox
    del bpy.types.Scene.MutationSlider
    del bpy.types.Scene.prompt_data

if __name__ == "__main__":
    register()
    