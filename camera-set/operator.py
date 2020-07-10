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
from bpy.types import RenderSettings, ImageFormatSettings

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



class RenderCameraBase:
	bl_option = {'REGISTER', 'UNDO'}

	@classmethod
	def valid_poll_object(cls, objects):
		for o in objects:
			if cls.valid_camera_object(o):
				return True
		return False

	@classmethod
	def valid_camera_object(clc, obj):
		return obj.type == 'CAMERA'

	@classmethod
	def check_object_in_set(clc, camera_set_sett, selected_objects):
		for camera_set in camera_set_sett.cameras:
			if camera_set == selected_objects:
				return True
		return False

	
	@classmethod
	def poll_selected(clc, context):
		return context.scene is not None \
			and clc.valid_poll_object(bpy.context.selected_objects) \
            and len(bpy.context.selected_objects) > 0

	@classmethod
	def poll_passive(clc, context):
		return context.scene is not None

	@classmethod
	def addDefaultCameraElement(cls, camera_setting):
		
		pass


class RenderCameraDesetSelect(Operator, RenderCameraBase):
	bl_idname = "scene.render_camera_set_deselect"
	bl_label = "Render: Remove selected camera"
	bl_description = ""
	bl_option = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return cls.poll_selected(context)

	def execute(self, context):
		camera_set_sett = context.scene.render_camera_set_settings
		selected_objects = bpy.context.selected_objects
		item = camera_set_sett.cameras.add()
		item = bpy.context.active_object

		return {"FINISHED"}

	def invoke(self, context, event):
		return self.execute(context)


class RenderCameraSetSelect(Operator, RenderCameraBase):
	"""Apply some presets of render settings to copy to other scenes"""
	bl_idname = "scene.render_camera_set_select"
	bl_label = "Render: Add selected camera"
	bl_description = ""
	bl_option = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return cls.poll_selected(context)

	def execute(self, context):
		camera_set_sett = context.scene.render_camera_set_settings
		selected_objects = bpy.context.selected_objects

		for obj in selected_objects:
			if self.valid_camera_object(obj):
				if not self.check_object_in_set(camera_set_sett, obj):
					item = camera_set_sett.cameras.add()
					item.camera = obj
					item.name = str.format("Element {}", len(camera_set_sett.cameras) - 1)
					item.filepath = ""
		
		return {"FINISHED"}

	def invoke(self, context, event):
		return self.execute(context)


class RenderCameraAdd(Operator, RenderCameraBase):
	bl_idname = "scene.render_camera_set_add"
	bl_label = "Render: Add selected camera"
	bl_description = ""

	@classmethod
	def poll(cls, context):
		return cls.poll_passive(context)

	def execute(self, context):
			camera_set_sett = context.scene.render_camera_set_settings

			item = camera_set_sett.cameras.add()
			item.camera = None
			item.name = str.format("Element {}", len(camera_set_sett.cameras) - 1)
			item.filepath = ""

			return {"FINISHED"}

	def invoke(self, context, event):
		return self.execute(context)

class RenderCameraRemove(bpy.types.Operator, RenderCameraBase):
	bl_idname = "scene.render_camera_set_remove"
	bl_label = "Render: Remove camera element"
	bl_description = "Remove the current selected camera element in the camera list."

	@classmethod
	def poll(cls, context):
		return cls.poll_passive(context)

	def execute(self, context):
		camera_set_sett = context.scene.render_camera_set_settings
		camera_set_sett.cameras.remove(camera_set_sett.affected_settings_idx)
		return {"FINISHED"}

	def invoke(self, context, event):
		return self.execute(context)




class RenderCameraOption(bpy.types.Operator):
	"""Apply some presets of render settings to copy to other scenes"""
	bl_idname = "scene.render_camera_option"
	bl_label = "Render: Copy Settings Preset"
	bl_description = "Apply or clear this preset of render settings"
	bl_option = {'REGISTER', 'UNDO'}

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
			render_setting_copy = {}
			for k in rendersettings_properties:
				target_attr_value = getattr(current_scene.render, k)
				render_setting_copy[k] = target_attr_value

			# 
			current_slot = bpy.data.images['Render Result'].render_slots.active_index
			current_filepath = current_scene.render.filepath

			# Iterate through each camera.
			time_start = time.time()
			try:
				for i, camera_element in enumerate(camera_set_settings.cameras):
					# TODO encapsulate render condition.
					if camera_element.enabled and camera_element.camera is not None and not camera_element.camera.hide_render:

						path_dir = ""
						path_filename = ""
						full_path = ""

						# Compute the directory and file paths.
						path_filename = camera_element.filepath
						if len(path_filename.strip()) == 0:
							path_filename = camera_element.name

						if camera_set_settings.use_default_output_directory == False:
							path_dir = camera_set_settings.output_directory
						else:
							path_dir = current_filepath
						full_path = str.format(
							"{}{}", path_dir, path_filename)

						# Override rendering settings.
						current_scene.camera = camera_element.camera
						current_scene.render.filepath = bpy.path.abspath(full_path)

						# 
						bpy.data.images['Render Result'].render_slots.active_index = i
						#self.report({'INFO'}, str.format("Rendering Camera: {}.", camera_element.camera.name))

						# Invoke rendering.
						bpy.ops.render.render( use_viewport=False, write_still=True, scene=current_scene.name)
						# Possible future feature.
						#bpy.data.images['Render Result'].render_slots.active_index = i
						bpy.ops.render.view_show('INVOKE_DEFAULT')

						# Possible Features - Add image if not existing.
						#bpy.ops.image.open(
						#	filepath=bpy.path.basename(full_path), directory=path_dir, show_multiview=False)
			except Exception as inst:
				self.report({'ERROR'}, str(inst))
			finally:
				# -------------------------
				# Reset the configuration.
				# -------------------------
				for k, v in render_setting_copy.items():
					setattr(current_scene.render, k, v)
				# Reset slot view and main camera.
				bpy.data.images['Render Result'].render_slots.active_index = current_slot

				# Compute the total time.
				total_time = time.time() - time_start
				self.report({'INFO'}, str.format("Total time: {} seconds", str(total_time)))

				#
				bpy.ops.render.view_show('INVOKE_DEFAULT')

		return {'FINISHED'}

	@classmethod
	def poll(cls, context):
		return context.scene is not None and len(context.scene.render_camera_set_settings.cameras) > 0

	def cancel(self, context):
		bpy.ops.render.view_cancel()
		pass


classes = (
	RenderCameraSet,  #
	RenderCameraOption,  #
	RenderCameraAdd,
	RenderCameraRemove,
	RenderCameraSetSelect,  #
	RenderCameraDesetSelect  #
)
