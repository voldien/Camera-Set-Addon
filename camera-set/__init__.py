

bl_info = {
	"name": "Camera Render Set",
	"author": "Valdemar Lindberg",
	"version": (0, 1, 0),
	"blender": (2, 79, 0),
	"location": "Properties > Render",
	"description": "Render a camera set.",
	"warning": "",
	"wiki_url": "",
	"category": "Render",
}
import bpy
if "bpy" in locals():
	import importlib
	if "Panel" in locals():
		importlib.reload(Panel)
	if "operator" in locals():
		importlib.reload(operator)
	if "translations" in locals():
		importlib.reload(translations)


from . import operator, Panel, translations
from bpy.props import (
	BoolProperty,
	CollectionProperty,
	PointerProperty,
	StringProperty,
	IntProperty
)


from bpy.types import RenderSettings, ImageFormatSettings
class RenderCameraSetSceneSettings(bpy.types.PropertyGroup):
	#
	allowed = BoolProperty(default=True)


class OverrideRenderSetting(RenderSettings):
	pass	

class RenderCameraData(bpy.types.PropertyGroup):
	name = StringProperty(name="name", default="", description="Name of the camera target.")
	camera = PointerProperty(name="camera", type=bpy.types.Object, description="Camera Targets")  # ,
	filepath = StringProperty(
		name="filepath", default='', subtype='FILE_PATH', description="")
	use_name = BoolProperty(name="", default=True)
	#
	image_reference = PointerProperty(type=bpy.types.Image)
	enabled = BoolProperty(name="enabled", default=True, description="Target enabled for as a render target.")
	override_rendering_setting = BoolProperty(
            name="Override Rendering Setting", description="Override the default rendering setting.")
	render_setting = PointerProperty(
		name="RenderSetting", description="Rendering setting.", type=bpy.types.CyclesRenderSettings)
	affected_settings_idx = IntProperty()

class RenderCameraSetSettings(bpy.types.PropertyGroup):
	#
	cameras = CollectionProperty(
		type=RenderCameraData, name="cameras", description="")
	# TODO rename
	affected_settings_idx = IntProperty()
	pattern = BoolProperty(name="pattern", description="", default=False)
	render = BoolProperty(name="render", description="", default=False)
	output_directory = StringProperty(
		name="Output Directory", description="", default="", subtype='DIR_PATH')
	use_default_output_directory = BoolProperty(
		"Default Output", description="", default=True)
	enabled = BoolProperty(name="Enabled", description="", default=False)


classes = (
	          #RenderCameraSetSceneSettings,
	          RenderCameraData,
	          RenderCameraSetSettings
          ) + operator.classes + Panel.classes
addon_keymaps = []


def menu_func_render(self, context):
	camera_sett = context.scene.render_camera_set_settings
	if camera_sett.enabled:
		self.layout.operator("scene.render_camera_set", text="Render Camera Set")


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.render_camera_set_settings = PointerProperty(type=RenderCameraSetSettings)

	# Create menus.
	if bpy.app.version >= (2, 80, 0):
		bpy.types.RENDER_PT_render.append(menu_func_render)
		bpy.types.TOPBAR_MT_render.append(menu_func_render)
	else:
		bpy.types.RENDER_PT_render.append(menu_func_render)
		bpy.types.INFO_MT_render.append(menu_func_render)

	# bpy.app.handlers.scene_update_post.append(on_scene_update)
	#	bpy.app.handlers.render_post.append()

	# add keymap default entries
	kcfg = bpy.context.window_manager.keyconfigs.addon
	if kcfg:
		km = kcfg.keymaps.new(name='Screen', space_type='EMPTY')
		kmi = km.keymap_items.new("scene.render_camera_set", 'F12', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))
		kmi = km.keymap_items.new("scene.render_camera_set_select", 'J', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))
		kmi = km.keymap_items.new("scene.render_camera_set_deselect", 'I', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))

	bpy.app.translations.register(__name__, translations.translations_dict)


def unregister():
	bpy.app.translations.unregister(__name__)

	# remove keymap entries
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

	# Remove layouts.
	if bpy.app.version >= (2, 80, 0):
		bpy.types.RENDER_PT_render.remove(menu_func_render)
		bpy.types.TOPBAR_MT_render.remove(menu_func_render)
	else:
		bpy.types.RENDER_PT_render.remove(menu_func_render)
		bpy.types.INFO_MT_render.remove(menu_func_render)

	# Delete pointer of the camera set.
	del bpy.types.Scene.render_camera_set_settings
	# unregister the class.
	for cls in classes[::-1]:
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
