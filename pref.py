import bpy
from bpy.props import StringProperty
from bpy.types import AddonPreferences


class saveLocFile(bpy.types.AddonPreferences):
    bl_idname = __package__

    file_path: StringProperty(
        name="EPW File",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "file_path")
