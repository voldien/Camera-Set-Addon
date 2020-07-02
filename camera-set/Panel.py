import bpy
if "bpy" in locals():
	import importlib

	if "preset" in locals():
		importlib.reload(preset)
from . import preset

from bpy.types import Panel, UIList

class RENDER_UL_camera_settings(UIList):
	bl_label = "Camera List"
	bl_options = {'HIDE_HEADER'}
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		assert(isinstance(item, bpy.types.RenderCameraData))

		cameraData = item
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
		
			layout.prop(cameraData, "name", icon_value=icon, icon='CAMERA_DATA', emboss=False, text="")
			layout.prop(cameraData, "enabled", index=index, text="")
		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label("", icon_value=icon)


def seListIndexFunction(self, value):
	bpy.ops.generate_markers.change_marker()


# class RenderCameaSetButtonsPanel:
#     bl_space_type = 'PROPERTIES'
#     bl_region_type = 'WINDOW'
#     bl_context = "render_layer"
#     # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

#     @classmethod
#     def poll(cls, context):
#         scene = context.scene
#         return scene and (scene.render.engine in cls.COMPAT_ENGINES)

class CameraRenderQueueSet(Panel):
	bl_label = "Camera Render Set"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	#bl_category = "Rendering"
	bl_context = "scene"
	#bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(cls, context):
		return context.scene is not None

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
		output_row_layout.prop(camera_sett, "output_directory", icon='FILESEL')
		#output_row_layout.
		output_row_layout.prop(camera_sett, "use_default_output_directory")
		output_row_layout.prop(camera_sett, "pattern")
		#bpy.ops.buttons.context_menu()

		layout.separator()

#prop_search
		# Display the camera list.
		row = layout.row()
		col = row.column()
		
		col.template_list("RENDER_UL_camera_settings", "settings", camera_sett, "cameras",
		                    camera_sett, "affected_settings_idx", rows=6)
		col = row.column()
		sub = col.column(align=True)
		sub.operator("scene.render_camera_set_select", icon='ZOOMIN', text="")
		sub.operator("scene.render_camera_set_deselect", icon='ZOOMOUT', text="")
		col.prop(camera_sett, "use_single_layer", icon_only=True)
		
		#
		# layout.enabled = len(camera_sett.cameras) > 0
		# layout.operator("scene.render_camera_set", text="Camera Render Set")
		layout.enabled = True
		col = layout.split(0.5)
		col.operator("scene.render_camera_set_select", text="Add Camera")
		col.operator("scene.render_camera_set_deselect", text="Remove Camera")
#layout.template_image_settings(image_settings, color_management=False)
		#
		layout.separator()

		layout.enabled = len(camera_sett.cameras) > 0
		layout.label("Camera Setting")
		# 
		if len(camera_sett.cameras) > 0 and camera_sett.affected_settings_idx >= 0:
			#split = layout.split(0.9)
			cameraData = camera_sett.cameras[camera_sett.affected_settings_idx]
#		        file_format = image_settings.file_format
#        image_settings = rd.image_settings
			layout.prop(cameraData, property="enaled", text="Enabled")
			layout.prop(cameraData, property="camera", text="Camera")
			layout.label(str.format("Output Settings {}", cameraData.camera.name))
			layout.prop(cameraData, property="filepath", text="")
#			layout.template_image_settings(image_settings, color_management=False)
#		        layout.template_image_settings(
#		        	image_settings, color_management=False)
			#bpy.ops.buttons.file_browse()
		# bpy.ops.buttons.file_browse()
		layout.enabled = True
		#			split.prop

		#		split.prop(camera_sett, )

		#
		col = layout.row()
		col.prop(camera_sett, "pattern")
		col.prop(camera_sett, "render")

# all_set = {sett.strid for sett in cp_sett.affected_settings if sett.copy}
# for p in preset.presets:
# 	label = ""
# 	if p.elements & all_set == p.elements:
# 		label = "Clear {}".format(p.ui_name)
# 	else:
# 		label = "Set {}".format(p.ui_name)
# 	col.operator("scene.render_camera_option", text=label).presets = {p.rna_enum[0]}

# layout.prop(cp_sett, "filter_scene")
# if len(cp_sett.allowed_scenes):
# 	layout.label("Camera Scenes:")
# 	layout.template_list("RENDER_UL_camera_settings", "scenes", cp_sett, "allowed_scenes",
# 	                     #                                 cp_sett, "allowed_scenes_idx", rows=6, type='GRID')
# 	                     cp_sett, "allowed_scenes_idx", rows=6)  # XXX Grid is not nice currently...
# else:
# 	layout.label(text="No Affectable Scenes!", icon="ERROR")


classes = (
	CameraRenderQueueSet,
	RENDER_UL_camera_settings
)
