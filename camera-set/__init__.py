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

if "bpy" in locals():
	import importlib

	importlib.reload(operator)
	importlib.reload(Panel)
	importlib.reload(translations)

else:
	from . import (
		operator,
		Panel,
		translations,
	)

import bpy
from bpy.props import (
	BoolProperty,
	CollectionProperty,
	PointerProperty,
	StringProperty,
	IntProperty
)

class RenderCameraSetSceneSettings(bpy.types.PropertyGroup):
	#
	allowed = BoolProperty(default=True)


class RenderCameraData(bpy.types.PropertyGroup):
	#
	camera = PointerProperty(name="camera", type=bpy.types.Object, description="")#,
	#update=scene..classes.CameraRenderQueueSet.draw)
	filepath = StringProperty(name="filepath", description="")
	enabled = BoolProperty(name="enabled", default=True, description="")
	affected_settings_idx = IntProperty()


class RenderCameraSetSettings(bpy.types.PropertyGroup):
	#
	cameras = CollectionProperty(type=RenderCameraData, name="cameras")
	# TODO rename
	affected_settings_idx = IntProperty()
	pattern = BoolProperty(name="pattern", description="", default=False)
	render = BoolProperty(name="render", description="", default=False)


classes = (
	          RenderCameraSetSceneSettings,
	          RenderCameraData,
	          RenderCameraSetSettings
          ) + operator.classes + Panel.classes
addon_keymaps = []


def menu_func_render(self, context):
	self.layout.operator("scene.render_camera_set", text="Camera Render Set")


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	#	bpy.app.handlers.version_update.append(version_update.do_versions)

	bpy.types.Scene.render_camera_set_settings = PointerProperty(type=RenderCameraSetSettings)

	bpy.types.RENDER_PT_render.append(menu_func_render)
	#bpy.app.handlers.scene_update_post.append(on_scene_update)
	#	bpy.app.handlers.render_post.append()

	# add keymap default entries
	kcfg = bpy.context.window_manager.keyconfigs.addon
	if kcfg:
		km = kcfg.keymaps.new(name='Screen', space_type='EMPTY')
		kmi = km.keymap_items.new("scene.render_camera_set", 'F12', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))
		kmi = km.keymap_items.new("scene.render_camera_select", 'J', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))
		kmi = km.keymap_items.new("scene.render_camera_deselect", 'I', 'PRESS', ctrl=True, shift=True)
		addon_keymaps.append((km, kmi))

	bpy.app.translations.register(__name__, translations.translations_dict)


def unregister():
	bpy.app.translations.unregister(__name__)

	# remove keymap entries
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

	# Remove layouts.
	bpy.types.RENDER_PT_render.remove(menu_func_render)

	# Delete pointer of the camera set.
	del bpy.types.Scene.render_camera_set
	# unregister the class.
	for cls in classes:
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
