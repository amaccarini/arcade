import bpy

class ADDON1_PT_Panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Import geojson file'
    bl_context = 'objectmode'
    bl_category = 'Arcade'

    def draw(self, context):
        layout = self.layout
        layout.operator("import.myop_operator")


class ADDON2_PT_Panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Building data'
    bl_context = 'objectmode'
    bl_category = 'Arcade'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        objType = getattr(context.object, 'type', '')
        if objType  in ['MESH']:
            layout.prop(obj.my_properties, "age", text="Age of construction")
            layout.prop(obj.my_properties, "usage", text="Building usage")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        objs = context.selected_objects
        if len(objs) == 0: return False
        if obj.type == 'MESH': return True
        return False

class ADDON3_PT_Panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Calculate heating and coolig loads'
    bl_context = 'objectmode'
    bl_category = 'Arcade'

    def draw(self, context):
        layout = self.layout
        layout.operator("calculate.myop_operator")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        objs = context.selected_objects
        if len(objs) == 0: return False
        if obj.type == 'MESH': return True
        return False
