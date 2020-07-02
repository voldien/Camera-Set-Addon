import bpy
import argparse
import sys

if __name__ == '__main__':
	for scene in bpy.data.scenes:
		scene.scene.scene.render_camera_set()