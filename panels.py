import bpy

class ADDON1_PT_Panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Import geojson file'
    bl_context = 'objectmode'
    bl_category = 'Arcade'
    bl_idname = "VIEW3D_PT_addon1_panel"

    def draw(self, context):
        layout = self.layout

        # Add tick-boxes
        layout.prop(context.scene.my_addon_props, "tick_box_1")
        layout.prop(context.scene.my_addon_props, "tick_box_2")

        # Add the button
        layout.operator("my_addon.check_options")

        layout.operator("import.myop_operator")






class ADDON2_PT_Panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Building data'
    bl_context = 'objectmode'
    bl_category = 'Arcade'
    bl_idname = "VIEW3D_PT_addon2_panel"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        objType = getattr(context.object, 'type', '')
        if objType  in ['MESH']:
            row = layout.row()
            split = row.split(factor=0.5)  # Split the row into two equal parts

            # Add the label in the first column and align to the right
            col1 = split.column()
            col1.alignment = 'RIGHT'  # Align the label to the right
            col1.label(text="Age of construction:")

            # Add the property box for age in the second column
            col2 = split.column()
            col2.prop(obj.my_properties, "age", text="")

            # Add the usage property box with a separate label and box
            row = layout.row()
            split = row.split(factor=0.5)  # Split the row into two equal parts

            # Add the label in the first column and align to the right
            col1 = split.column()
            col1.alignment = 'RIGHT'  # Align the label to the right
            col1.label(text="Building usage:")

            # Add the property box for usage in the second column
            col2 = split.column()
            col2.prop(obj.my_properties, "usage", text="")

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
    bl_idname = 'VIEW3D_PT_addon3_panel'
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


class SUB_ADDON1_PT_Panel(bpy.types.Panel):
    bl_label = "Option 1 Settings"
    bl_idname = "VIEW3D_PT_my_addon_submenu"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Arcade"
    bl_parent_id = "VIEW3D_PT_addon1_panel"

    @classmethod
    def poll(cls, context):
        props = context.scene.my_addon_props
        return props.tick_box_1  # Show this panel only if Option 1 is selected

    def draw(self, context):
        layout = self.layout  # Initialize layout
        props = context.scene.my_addon_props  # Access scene properties

        # Add property for Option 1
        layout.prop(props, "probability", text="Probability")
