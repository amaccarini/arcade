import bpy

class ADDON1_PT_Panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Generate geoJSON file'
    bl_context = 'objectmode'
    bl_category = 'Arcade'
    bl_idname = "VIEW3D_PT_addon1_panel"

    def draw(self, context):
        layout = self.layout

        props = context.scene.my_addon_props

        # Add the button to open the browser
        layout.operator("myaddon.open_browser", text="Find urban area boundaries")

        # Add a separator for padding
        layout.separator(factor=0.5)

        # Create a "darker" grey box
        box = layout.box()
        box.ui_units_x = 12  # Optional: Adjust box width

        # Top row with centered Max Lat
        row = box.row()
        row.alignment = 'CENTER'
        row.prop(props, "lat_max", text="Max Lat")

        # Second row: split into two columns for Min Lon and Max Lon
        split = box.split(factor=0.5)
        col_left = split.column()
        col_right = split.column()
        col_left.prop(props, "lon_min", text="Min Lon")
        col_right.prop(props, "lon_max", text="Max Lon")

        # Third row with centered Min Lat
        row = box.row()
        row.alignment = 'CENTER'
        row.prop(props, "lat_min", text="Min Lat")


        # Add tick-boxes
        layout.prop(context.scene.my_addon_props, "tick_box_1")
        layout.prop(context.scene.my_addon_props, "tick_box_2")


        if props.tick_box_1:
            layout.separator()
            layout.label(text="Settings for Probabilistic Method:", icon="TOOL_SETTINGS")

            # Create a dark grey box
            box = layout.box()
            box.ui_units_x = 12 # Can be adjusted

            row = box.row()
            split = row.split(factor=0.75)  # Split the row into two equal parts

            # Add the label in the first column and align to the right
            col1 = split.column()
            col1.alignment = 'RIGHT'  # Align the label to the right
            col1.label(text="Average age of buildings")

            # Add the property box for age in the second column
            col2 = split.column()
            col2.prop(props, "avg_age", text="")


            row = box.row()
            split = row.split(factor=0.75)  # Split the row into two equal parts

            # Add the label in the first column and align to the right
            col1 = split.column()
            col1.alignment = 'RIGHT'  # Align the label to the right
            col1.label(text="Age variation (Std Dev)")

            # Add the property box for age in the second column
            col2 = split.column()
            col2.prop(props, "std_age", text="")

            layout.separator()

            row = box.row()
            split = row.split(factor=0.75)  # Split the row into two equal parts

            # Add the label in the first column and align to the right
            col1 = split.column()
            col1.alignment = 'RIGHT'  # Align the label to the right
            col1.label(text="Average number of stories")

            # Add the property box for age in the second column
            col2 = split.column()
            col2.prop(props, "avg_nfloor", text="")


            row = box.row()
            split = row.split(factor=0.75)  # Split the row into two equal parts

            # Add the label in the first column and align to the right
            col1 = split.column()
            col1.alignment = 'RIGHT'  # Align the label to the right
            col1.label(text="Number of stories variation (Std Dev)")

            # Add the property box for age in the second column
            col2 = split.column()
            col2.prop(props, "std_nfloor", text="")


        # Add the button for creating the geojson file
        layout.operator("generate.myop_operator", icon="FILE_NEW")





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


            # Add the number of stories box with a separate label and box
            row = layout.row()
            split = row.split(factor=0.5)  # Split the row into two equal parts

            # Add the label in the first column and align to the right
            col1 = split.column()
            col1.alignment = 'RIGHT'  # Align the label to the right
            col1.label(text="Number of stories:")

            # Add the property box for usage in the second column
            col2 = split.column()
            col2.prop(obj.my_properties, "num_stories", text="")


    @classmethod
    def poll(cls, context):
        objs = context.selected_objects

        # Ensure exactly one object is selected and active
        if len(objs) == 1:
            obj = objs[0]  # Since there's only one selected, it's also active
            if obj.type == 'MESH':
                return True

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
        # Get the list of selected objects
        objs = context.selected_objects

        # Return False if no objects are selected
        if len(objs) == 0:
            return False

        # Try to get the active object, or fallback to the first selected object
        obj = context.active_object if context.active_object else objs[0]

        # Check if the active object (or fallback) is of type MESH
        if obj.type == 'MESH':
            return True

        return False

class ADDON4_PT_Panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_idname = 'VIEW3D_PT_addon4_panel'
    bl_label = 'Import geoJSON file'
    bl_context = 'objectmode'
    bl_category = 'Arcade'

    def draw(self, context):
        layout = self.layout
        props = context.scene.my_addon_props

        # Row for label and file path input
        row = layout.row()
        split = row.split(factor=0.5)  # Split the row into two equal parts

        # Add the label in the first column
        col1 = split.column()
        col1.label(text="Select GeoJSON File:")

        # Add the property box and folder icon in the second column
        col2 = split.column(align=True)
        col2.prop(props, "file_path", text="")

        layout.operator("import.open_file", icon="IMPORT")
