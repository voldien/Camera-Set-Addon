import bpy

#from . import preset


# from progress_report import ProgressReport, ProgressReportSubstep
class RENDER_UL_camera_settings(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		# assert(isinstance(item, (bpy.types.RenderCopySettingsScene, bpy.types.RenderCopySettingsDataSetting)))
		# print(active_propname)
		# print(index)

		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			if isinstance(item, bpy.types.RenderCameraData):
	#			layout.label()
				layout.prop(item, "camera", text=item.camera.name, icon_value=icon, toggle=item.enabled)
				layout.prop(item, "enabled", icon_value=icon)
			# layout.prop(item.filepath, "copy", text="")
			else:  # elif isinstance(item, bpy.types.RenderCopySettingsDataScene):
				layout.prop(item, "enabled", text=item.name, toggle=item.enabled)
		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			if isinstance(item, bpy.types.RenderCameraData):
				layout.label(item.name, icon_value=icon)
				layout.prop(item, "copy", text="")
			else:  # elif isinstance(item, bpy.types.RenderCopySettingsDataScene):
				layout.prop(item, "enabled", text=item.name, toggle=True)


def seListIndexFunction(self, value):
	bpy.ops.generate_markers.change_marker()


class CameraRenderQueueSet(bpy.types.Panel):
	bl_label = "Camera Render Set"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def draw(self, context):
		layout = self.layout

		# Get camera settings.
		camera_sett = context.scene.render_camera_set_settings

		global_layout = layout
		output_row_layout = global_layout.column()
		output_row_layout.prop(camera_sett, "output_directory")
		bpy.ops.buttons.context_menu()
		global_layout.alignment = 'LEFT'
		global_layout.label("Global Settings")
		global_layout.prop(camera_sett, "pattern")


		layout.separator()

		# Display the camera list.
		split = layout.split(1.0)
		split.template_list("RENDER_UL_camera_settings", "settings", camera_sett, "cameras",
		                    camera_sett, "affected_settings_idx", rows=6)

		#		split.prop(context.scene.render_camera_set_settings, "cameras", text="Camera Set")
		# split.prop(self.dummy_object2, "active", text="Object2")

		#
		# layout.enabled = len(camera_sett.cameras) > 0
		# layout.operator("scene.render_camera_set", text="Camera Render Set")
		layout.enabled = True
		col = layout.split(0.5)
		col.operator("scene.render_camera_set_select", text="Add Camera")
		col.operator("scene.render_camera_set_deselect", text="Remove Camera")

		#
		layout.separator()
		layout.enabled = len(camera_sett.cameras) > 0
		layout.label("Output Settings")
		split = layout.split(0.9)
		if len(camera_sett.cameras) > 0:
			split.prop(camera_sett.cameras[camera_sett.affected_settings_idx], property="filepath", text="")
			bpy.ops.buttons.file_browse()
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
