# <pep8 compliant>
import bpy
if "bpy" in locals():
	import importlib

	if "preset" in locals():
		importlib.reload(preset)
from . import preset

from bpy.types import Panel, UIList
from bpy.types import Operator

class SCENE_UL_camera_settings(UIList):
	bl_label = "Camera List"
	bl_options = {'HIDE_HEADER'}
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#		assert(isinstance(item, RenderCameraData))

		cameraData = item
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			display_name =""
			if cameraData.camera:
				display_name = str.format("({})", cameraData.camera.name)
			layout.prop(cameraData, "name", icon_value=icon, icon='CAMERA_DATA', emboss=False, text="")
			layout.label(display_name)
			layout.prop(cameraData, "enabled", index=index, text="")
		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label("", icon_value=icon)

class CameraSetPanel:
	bl_space_type = 'PROPERTIES'	
	bl_region_type = 'WINDOW'
	@classmethod
	def poll(cls, context):
		scene = context.scene
		return scene and context.scene.render_camera_set_settings


class SCENE_PT_cameraset(Panel, CameraSetPanel):
	bl_label = "Camera Render Set"
	bl_category = "Rendering"
	bl_context = "scene"

	def draw_header(self, context):
		camera_sett = context.scene.render_camera_set_settings
		self.layout.prop(camera_sett, "enabled", text="")

	def draw(self, context):
		layout = self.layout

		# Get camera settings.
		camera_sett = context.scene.render_camera_set_settings
		layout.active = camera_sett.enabled

		global_layout = layout
		global_layout.alignment = 'LEFT'
		global_layout.label("Global Settings")

		output_row_layout = global_layout.column()

		if camera_sett.use_default_output_directory:
			output_row_layout.active = False
		output_row_layout.prop(camera_sett, "output_directory")
		#output_row_layout.
		output_row_layout.active = True
		output_row_layout.prop(camera_sett, "use_default_output_directory")
		output_row_layout.prop(camera_sett, "pattern")
		#bpy.ops.buttons.context_menu()

		layout.separator()

#prop_search
		# Display the camera list.
		row = layout.row()
		col = row.column()
		
		col.template_list("SCENE_UL_camera_settings", "settings", camera_sett, "cameras",
		                    camera_sett, "affected_settings_idx", rows=3)
		col = row.column()
		sub = col.column(align=True)
		sub.operator("scene.render_camera_set_add", icon='ZOOMIN', text="")
		sub.operator("scene.render_camera_set_remove", icon='ZOOMOUT', text="")
		#col.prop(camera_sett, "use_single_layer", icon_only=True)
		
		#
		# layout.enabled = len(camera_sett.cameras) > 0
		# layout.operator("scene.render_camera_set", text="Camera Render Set")
		col = layout.split(0.5)
		col.operator("scene.render_camera_set_select", text="Add Selected Camera")
		col.operator("scene.render_camera_set_deselect", text="Remove Selected Camera")

		# Display camera target settings.
		if len(camera_sett.cameras) > 0 and camera_sett.affected_settings_idx >= 0:
			layout.separator()
			layout.enabled = len(camera_sett.cameras) > 0
			layout.label("Camera Setting")
			#split = layout.split(0.9)
			cameraData = camera_sett.cameras[camera_sett.affected_settings_idx]
#		        file_format = image_settings.file_format
#        image_settings = rd.image_settings
			layout.prop(cameraData, property="enabled", text="Enabled")
			layout.prop(cameraData, property="camera", text="Camera")
			layout.label(str.format("Output"))
			layout.prop(cameraData, property="filepath", text="")
			layout.prop(cameraData, property="override_rendering_setting")
			# layout.template_image_settings(
			# 	cameraData.image_settings, color_management=False)


classes = (
	SCENE_PT_cameraset,
	SCENE_UL_camera_settings
)
