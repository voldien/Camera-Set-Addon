import time

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


def valid_camera_object(obj):
	return obj.type != 'CAMERA'

def check_object_in_set(camera_set_sett, selected_objects):
	pass


class RenderCameraDesetSelect(bpy.types.Operator):
	"""Apply some presets of render settings to copy to other scenes"""
	bl_idname = "scene.render_camera_set_deselect"
	bl_label = "Render: Remove selected camera"
	bl_description = ""
	bl_option = {'REGISTER', 'UNDO'}

	# object = bpy.props.PointerProperty(type=bpy.types.Object)

	@classmethod
	def poll(cls, context):
		return context.scene is not None and valid_poll_object(bpy.context.selected_objects) and len(bpy.context.selected_objects) > 0

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

	@classmethod
	def poll(cls, context):
		return context.scene is not None and valid_poll_object(bpy.context.selected_objects)and len(bpy.context.selected_objects) > 0

	def execute(self, context):
		camera_set_sett = context.scene.render_camera_set_settings
		selected_objects = bpy.context.selected_objects

		for obj in selected_objects:
			if valid_camera_object(obj):
				pass

		item = camera_set_sett.cameras.add()
		item.camera = bpy.context.selected_objects[0]

		# context.scene.update()
		# self.__class__.run += 1
		# self.report({'INFO'}, str(self.__class__.run))
		#		camera_set_sett.cameras.append(selected_objects)
		return {"FINISHED"}

	def invoke(self, context, event):
		# self.object = bpy.context.selected_objects[0]
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

class RenderCameraSetGL(Operator):
	bl_idname = "scene.render_camera_set_gl"
	bl_label = "Render Camera Set"
	bl_description = "Render all camera in the camera set."
	bl_options = {'REGISTER', 'UNDO'}
	pass

class RenderCameraSet(Operator):
	"""Create mesh plane(s) from image files with the appropriate aspect ratio"""
	bl_idname = "scene.render_camera_set"
	bl_label = "Render Camera Set"
	bl_description = "Render all camera in the camera set."
	bl_options = {'REGISTER'}

	# Perform rendering
	def execute(self, context):
		window = bpy.context.window_manager.windows[0]
		# Camera set settings.
		current_scene = context.scene
		camera_set_settings = current_scene.render_camera_set_settings
		if camera_set_settings.enabled:

			# ---------------------
			# Get current render setting copy.
			# -----------------
			
			rendersettings_properties = [p.identifier for p in current_scene.render.bl_rna.properties
						if not p.is_readonly]
			current_render_camera = current_scene.camera
			current_slot = bpy.data.images['Render Result'].render_slots.active_index
			# Get current rendering settings.
			print(rendersettings_properties)

			# Iterate through each camera.
			time_start = time.time()
			try:
				for i, set in enumerate(camera_set_settings.cameras):
					if set.enabled and set.camera is not None and not set.camera.hide_render:
						# Override rendering settings.
						current_scene.camera = set.camera
						if not camera_set_settings.use_default_output_directory:
							current_scene.render.filepath = str.format("{}/{}", camera_set_settings.output_directory, set.filepath)
						else:
							current_scene.render.filepath = str.format(
								"{}/{}", current_scene.render.filepath, set.filepath)
						# Use overrided rendering settings.
						# if set.override_rendering_settings:
						# 	if current_scene.render.engine == "CYCLE":
						# 		pass
						# 	else:
						# 		pass
							#set.data = rendersettings_properties.copy()


						# Invoke rendering.
						bpy.data.images['Render Result'].render_slots.active_index = i
						self.report({'INFO'}, str.format("Rendering Camera: {}.", set.camera.name))

						#bpy.ops.render.view_show('INVOKE_DEFAULT')
						bpy.ops.render.render('INVOKE_DEFAULT', use_viewport=True, write_still=True)
						bpy.data.images['Render Result'].render_slots.active_index = i

						bpy.ops.image.open(
							filepath=bpy.path.basename(
								(current_scene.render.filepath), directory=current_scene.render.filepath, show_multiview=False)
			except Exception as inst:
				self.report({'ERROR'}, str(inst))
	#			bpy.data.
			finally:
				# -------------------------
				# Reset the configuration.
				# -------------------------
				for k in rendersettings_properties:
					target_attr_value = getattr(current_scene.render, k)
					setattr(current_scene.render, k, target_attr_value)
				# Reset slot view and main camera.
				bpy.data.images['Render Result'].render_slots.active_index = current_slot
				current_scene.camera = current_render_camera

				# 
				total_time = time.time() - time_start
				self.report({'INFO'}, str(total_time))

				#
				bpy.ops.render.view_show('INVOKE_DEFAULT')


		return {'FINISHED'}

	@classmethod
	def poll(cls, context):


		return context.scene is not None and len(context.scene.render_camera_set_settings.cameras) > 0

	def cancel(self, context):
		pass


classes = (
	RenderCameraSet,  #
	RenderCameraOption,  #
	RenderCameraSetSelect,  #
	RenderCameraDesetSelect  #
)
