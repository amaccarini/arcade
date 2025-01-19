import bpy
from bpy.props import StringProperty
from bpy.types import AddonPreferences


class saveLocFile(bpy.types.AddonPreferences):
    bl_idname = __package__

    folder_path: StringProperty(
        name="Output folder",
        subtype='DIR_PATH',
    )
    file_path: StringProperty(
        name="EPW File",
        subtype='FILE_PATH',
    )
    google_path: StringProperty(
        name="Google API key",
        subtype='NONE',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "folder_path")
        layout.prop(self, "file_path")
        layout.prop(self, "google_path")
