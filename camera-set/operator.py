import bpy
import re
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    CollectionProperty,
)

from bpy.types import Operator
if "bpy" in locals():
	import importlib
	if "preset" in locals():
		importlib.reload(preset)
from . import preset


# class RenderCopySettingsOPPreset(bpy.types.Operator):
#     """Apply some presets of render settings to copy to other scenes"""
#     bl_idname = "scene.render_copy_settings_preset"
#     bl_label = "Render: Copy Settings Preset"
#     bl_description = "Apply or clear this preset of render settings"
#     # Enable undo…
#     bl_option = {'REGISTER', 'UNDO'}
#
#     presets = EnumProperty(items=(p.rna_enum for p in presets.presets),
#                            default=set(),
#                            options={'ENUM_FLAG'})
#
#     @staticmethod
#     def process_elements(settings, elts):
#         setts = []
#         val = True
#         for sett in settings:
#             if sett.strid in elts:
#                 setts.append(sett)
#                 val = val and sett.copy
#         for e in setts:
#             e.copy = not val
#
#     @classmethod
#     def poll(cls, context):
#         return context.scene is not None
#
#     def execute(self, context):
#         cp_sett = context.scene.render_copy_settings
#         for p in presets.presets:
#             if p.rna_enum[0] in self.presets:
#                 self.process_elements(cp_sett.affected_settings, p.elements)
#         return {'FINISHED'}
#
#
# # Real interesting stuff…
#
# def do_copy(context, affected_settings, allowed_scenes):
#     # Stores render settings from current scene.
#     p = {sett: getattr(context.scene.render, sett)
#          for sett in affected_settings}
#     # put it in all other (valid) scenes’ render settings!
#     for scene in bpy.data.scenes:
#         # If scene not in allowed scenes, skip.
#         if scene.name not in allowed_scenes:
#             continue
#         # Propagate all affected settings.
#         for sett, val in p.items():
#             setattr(scene.render, sett, val)

def valid_poll_object(objects):
    for o in objects:
        if o.type != 'CAMERA':
            return False
    return True


def check_object_in_set(camera_set_sett, selected_objects):
    pass

class RenderCameraDesetSelect(bpy.types.Operator):
    """Apply some presets of render settings to copy to other scenes"""
    bl_idname = "scene.render_camera_set_deselect"
    bl_label = "Render: Remove selected camera"
    bl_description = ""
    bl_option = {'REGISTER', 'UNDO'}

    #object = bpy.props.PointerProperty(type=bpy.types.Object)

    @classmethod
    def poll(cls, context):
        return context.scene is not None and valid_poll_object(bpy.context.selected_objects)

    def execute(self, context):
        camera_set_sett = context.scene.render_camera_set_settings
        selected_objects = bpy.context.selected_objects
        item = camera_set_sett.cameras.add()
        item = bpy.context.active_object

        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class RenderCameraSetSelect(bpy.types.Operator):
    """Apply some presets of render settings to copy to other scenes"""
    bl_idname = "scene.render_camera_set_select"
    bl_label = "Render: Add selected camera"
    bl_description = ""
    # Enable undo…
    bl_option = {'REGISTER', 'UNDO'}

    #object = bpy.props.PointerProperty(type=bpy.types.Object)

    @classmethod
    def poll(cls, context):
        return context.scene is not None and valid_poll_object(bpy.context.selected_objects)

    def execute(self, context):
        camera_set_sett = context.scene.render_camera_set_settings
        selected_objects = bpy.context.selected_objects

        item = camera_set_sett.cameras.add()
        item.camera = bpy.context.selected_objects[0]
        #context.scene.update()
        #self.__class__.run += 1
        #self.report({'INFO'}, str(self.__class__.run))
        #		camera_set_sett.cameras.append(selected_objects)
        return {"FINISHED"}

    def invoke(self, context,event):
        #self.object = bpy.context.selected_objects[0]
        return self.execute(context)


class RenderCameraOption(bpy.types.Operator):
    """Apply some presets of render settings to copy to other scenes"""
    bl_idname = "scene.render_camera_option"
    bl_label = "Render: Copy Settings Preset"
    bl_description = "Apply or clear this preset of render settings"
    # Enable undo…
    bl_option = {'REGISTER', 'UNDO'}

    presets = EnumProperty(items=(p.rna_enum for p in preset.presets),
                           default=set(),
                           options={'ENUM_FLAG'})

    @staticmethod
    def process_elements(settings, elts):
        setts = []
        val = True
        for sett in settings:
            if sett.strid in elts:
                setts.append(sett)
                val = val and sett.copy
        for e in setts:
            e.copy = not val

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        cp_sett = context.scene.render_copy_settings
        for p in preset.presets:
            if p.rna_enum[0] in self.presets:
                self.process_elements(cp_sett.affected_settings, p.elements)
        return {'FINISHED'}


class RenderCameraSet(Operator):
    """Create mesh plane(s) from image files with the appropriate aspect ratio"""
    bl_idname = "scene.render_camera_set"
    bl_label = "Render Camera Set"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    linked_scene = None

    # Perform rendering
    def execute(self, context):
        window = bpy.context.window_manager.windows[0]

        # Get current scene.
        current_scene = context.scene

        # Create a tmp scene for overriding the rendering settings.
        bpy.ops.scene.new(type='LINK_OBJECT_DATA')
        # Get new scene reference and its camera set settings.
        linked_scene = context.scene
        linked_scene.name = "Linked-Clone"
        context.screen.scene = linked_scene
        camera_set_settings = linked_scene.render_camera_set_settings

        # Iterate through each camera.
        for i, set in enumerate(camera_set_settings.cameras):
            if set.enabled:
                # Override rendering settings.
                linked_scene.camera = set.camera
                linked_scene.render.filepath = 'camera-set-test' + str(i)

                # Invoke rendering.
                self.report({'INFO'}, "Simple Operator executed.")
                bpy.ops.render.render(scene=linked_scene.name)

        # Reset the config.
        context.screen.scene = current_scene
        bpy.data.scenes.remove(linked_scene, True)
        bpy.ops.render.view_show('INVOKE_DEFAULT')

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and len(context.scene.render_camera_set_settings.cameras) > 0

    def cancel(self, context):
        pass


classes = (
    RenderCameraSet,        #
    RenderCameraOption,     #
    RenderCameraSetSelect,  #
    RenderCameraDesetSelect #
)
