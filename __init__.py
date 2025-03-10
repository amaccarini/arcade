# ==============================================================================
#Arcade
#Author: Alessandro Maccarini
#License: TBD
#Version: 0.1.0
#Date: 15-10-2024
# ==============================================================================
from .module_loader import refresh
refresh()


bl_info = {
    "name" : "Arcade",
    "author" : "Alessandro Maccarini",
    "description" : "",
    "blender" : (4, 2, 0),
    "version" : (0, 1, 0),
    "location" : "View3D",
    "warning" : "",
    "category" : "Import-Export"
}

import bpy
from .panels import ADDON1_PT_Panel, ADDON2_PT_Panel, ADDON3_PT_Panel, ADDON4_PT_Panel
from .operators import ADDON1_OT_Operator, ADDON2_OT_Operator, ADDON3_OT_Operator, ADDON4_OT_Operator, ADDON5_OT_Operator
from .properties import MyPropertyGroup, MyAddonProperties
from .pref import saveLocFile


classes=[MyPropertyGroup, ADDON1_PT_Panel,ADDON2_PT_Panel, ADDON3_PT_Panel, ADDON4_PT_Panel, ADDON1_OT_Operator, ADDON2_OT_Operator,ADDON3_OT_Operator, ADDON4_OT_Operator, ADDON5_OT_Operator, saveLocFile, MyAddonProperties]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Object.my_properties = bpy.props.PointerProperty(type=MyPropertyGroup)
    bpy.types.Scene.my_addon_props = bpy.props.PointerProperty(type=MyAddonProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Object.my_properties
    del bpy.types.Scene.my_addon_props
